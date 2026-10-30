"""命令列介面。"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .demo import build_demo_repo
from .garden import grow
from .gitlog import GitError, read_commits
from .render_ascii import render_ascii, render_legend
from .render_svg import THEMES, render_svg
from .stats import render_stats


def _repo_name(repo: str) -> str:
    return Path(repo).resolve().name or "garden"


def _want_color(mode: str, writing_file: bool) -> bool:
    if mode == "always":
        return True
    if mode == "never" or writing_file:
        return False
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _cmd_grow(args: argparse.Namespace) -> int:
    commits = read_commits(args.repo, limit=args.limit)
    if not commits:
        print("這座花園還是一片空地：沒有任何 commit 可以種。", file=sys.stderr)
        return 0

    plants = grow(commits)
    title = args.title or _repo_name(args.repo)
    if args.format == "svg":
        result = render_svg(plants, per_row=args.per_row or 30, title=title, theme=args.theme)
    else:
        color = _want_color(args.color, writing_file=bool(args.output))
        result = render_ascii(
            plants, per_row=args.per_row or 24, color=color, title=title, legend=not args.no_legend
        )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result + "\n", encoding="utf-8")
        print(f"已輸出到 {out}")
    else:
        print(result)
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    commits = read_commits(args.repo, limit=args.limit)
    print(render_stats(commits, _repo_name(args.repo)))
    return 0


def _cmd_legend(args: argparse.Namespace) -> int:
    print(render_legend(color=_want_color(args.color, writing_file=False)))
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    path = build_demo_repo(args.dir, commits=args.commits)
    print(f"示範 repo 已建立：{path}")
    print(f"接著試試：commit-garden grow {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="commit-garden", description="把 git commit 歷史種成一座花園。")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<指令>")

    grow_p = sub.add_parser("grow", help="種出花園（不給指令時的預設動作）")
    grow_p.add_argument("repo", nargs="?", default=".", help="git repo 路徑（預設：目前目錄）")
    grow_p.add_argument("-n", "--limit", type=int, default=48, help="只種最近 N 個 commit（預設 48）")
    grow_p.add_argument("--per-row", type=int, default=None, help="每一畦種幾株（ASCII 預設 24，SVG 預設 30）")
    grow_p.add_argument("-f", "--format", choices=["ascii", "svg"], default="ascii", help="輸出格式")
    grow_p.add_argument("-o", "--output", help="輸出到檔案，而不是印在螢幕上")
    grow_p.add_argument("--title", help="花園標題（預設：repo 資料夾名稱）")
    grow_p.add_argument("--theme", choices=sorted(THEMES), default="light", help="SVG 主題")
    grow_p.add_argument("--color", choices=["auto", "always", "never"], default="auto", help="ASCII 是否上色")
    grow_p.add_argument("--no-legend", action="store_true", help="ASCII 模式不顯示圖例")
    grow_p.set_defaults(func=_cmd_grow)

    stats_p = sub.add_parser("stats", help="花園統計：物種分布與多樣性")
    stats_p.add_argument("repo", nargs="?", default=".", help="git repo 路徑（預設：目前目錄）")
    stats_p.add_argument("-n", "--limit", type=int, default=None, help="只統計最近 N 個 commit")
    stats_p.set_defaults(func=_cmd_stats)

    legend_p = sub.add_parser("legend", help="顯示所有植物的圖例")
    legend_p.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    legend_p.set_defaults(func=_cmd_legend)

    demo_p = sub.add_parser("demo", help="建立一個示範用的 git repo")
    demo_p.add_argument("dir", help="要建立 repo 的資料夾（必須是新的或空的）")
    demo_p.add_argument("--commits", type=int, default=48, help="commit 數量（預設 48）")
    demo_p.set_defaults(func=_cmd_demo)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        args = parser.parse_args(["grow"])
    try:
        return args.func(args)
    except GitError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
