"""讀取並解析 git log。"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

# 用 git 內建的 %x1e / %x1f 當分隔符號，跨平台不用在命令列塞控制字元
_FORMAT = "%x1e%H%x1f%an%x1f%aI%x1f%s"
_REC = "\x1e"
_SEP = "\x1f"
_INS = re.compile(r"(\d+) insertions?\(\+\)")
_DEL = re.compile(r"(\d+) deletions?\(-\)")
_EMPTY_REPO_HINTS = ("does not have any commits", "bad default revision", "unknown revision")


class GitError(RuntimeError):
    """git 指令失敗時拋出。"""


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    date: datetime
    subject: str
    insertions: int = 0
    deletions: int = 0

    @property
    def churn(self) -> int:
        """這個 commit 動了多少行（新增 + 刪除）。"""
        return self.insertions + self.deletions


def parse_log(raw: str) -> List[Commit]:
    """解析 `git log --shortstat` 的輸出，保持原始順序（新 -> 舊）。"""
    commits: List[Commit] = []
    for chunk in raw.split(_REC):
        if not chunk.strip():
            continue
        header, _, rest = chunk.partition("\n")
        parts = header.split(_SEP)
        if len(parts) != 4:
            continue
        sha, author, date, subject = parts
        ins = _INS.search(rest)
        dele = _DEL.search(rest)
        commits.append(
            Commit(
                sha=sha,
                author=author,
                date=datetime.fromisoformat(date),
                subject=subject,
                insertions=int(ins.group(1)) if ins else 0,
                deletions=int(dele.group(1)) if dele else 0,
            )
        )
    return commits


def read_commits(repo: Union[str, Path] = ".", limit: Optional[int] = None) -> List[Commit]:
    """讀取 repo 的 commit，回傳「由舊到新」的清單。limit 代表只取最近 N 個。"""
    cmd = ["git", "-C", str(repo), "log", "--no-merges", "--shortstat", f"--pretty=format:{_FORMAT}"]
    if limit:
        cmd.append(f"--max-count={limit}")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise GitError("找不到 git 指令，請先安裝 git") from exc

    if proc.returncode != 0:
        err = proc.stderr.strip()
        if any(hint in err for hint in _EMPTY_REPO_HINTS):
            return []
        if "not a git repository" in err:
            raise GitError(f"{repo} 不是 git repository")
        raise GitError(err or "git log 執行失敗")

    commits = parse_log(proc.stdout)
    commits.reverse()
    return commits
