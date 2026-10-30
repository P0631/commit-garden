"""產生一個示範用的 git repo，讓沒有現成 repo 的人也能馬上看到花園。"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union

from .gitlog import GitError

_AUTHORS = ["Ada", "Linus", "Grace"]

_MESSAGES = [
    "feat: add user login",
    "feat(api): add search endpoint",
    "fix: handle empty input",
    "fix(parser): off-by-one in tokenizer",
    "docs: update README",
    "docs: add usage examples",
    "test: cover edge cases",
    "test(api): add integration tests",
    "refactor: split big function",
    "refactor(core): simplify config loading",
    "chore: bump dependencies",
    "chore: update .gitignore",
    "perf: cache lookups",
    "style: format code",
    "ci: add workflow",
    "feat: implement dark mode",
    'Revert "add search endpoint"',
    "wip: scratch notes",
    "fix: crash on startup",
    "feat(ui): add settings page",
    "docs: fix typo in readme",
    "build: pin python version",
    "perf: lazy load assets",
    "feature: export to csv",
]


def _git(path: Path, *args: str, env: dict = None) -> None:
    proc = subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=path, capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} 失敗")


def build_demo_repo(path: Union[str, Path], commits: int = 48) -> Path:
    """在 path 建立一個有 N 個 commit 的假 repo（每次產生的內容都一樣）。"""
    root = Path(path)
    if (root / ".git").exists():
        raise GitError(f"{root} 已經是 git repository，請換一個空目錄")
    root.mkdir(parents=True, exist_ok=True)
    try:
        _git(root, "init", "-q")
    except FileNotFoundError as exc:
        raise GitError("找不到 git 指令，請先安裝 git") from exc

    base = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
    for i in range(commits):
        subject = f"{_MESSAGES[(i * 5) % len(_MESSAGES)]} (#{i + 1})"
        author = _AUTHORS[i % len(_AUTHORS)]
        lines = 1 + (i * 37) % 60
        if i % 9 == 4:
            lines *= 6  # 偶爾來一個大 commit

        target = root / f"module_{i % 4}.txt"
        with target.open("a", encoding="utf-8") as fh:
            fh.writelines(f"line {i}-{j}\n" for j in range(lines))

        when = (base + timedelta(hours=i * 17 + i % 3)).isoformat()
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": f"{author.lower()}@example.com",
            "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": f"{author.lower()}@example.com",
            "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
        }
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", subject, env=env)
    return root
