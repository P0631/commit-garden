"""物種定義：每一種 commit 類型對應一種植物。"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Species:
    key: str       # commit 類型（例如 feat）
    name_zh: str   # 植物中文名
    name_en: str   # 植物英文名
    head: str      # ASCII 模式的頭部字元
    ansi: str      # ASCII 模式的 ANSI 色碼
    color: str     # SVG 模式的顏色
    shape: str     # SVG 模式的圖形名稱


_ALL = [
    Species("feat", "向日葵", "sunflower", "@", "33", "#f4b400", "flower"),
    Species("fix", "蘑菇", "mushroom", "m", "31", "#e5484d", "mushroom"),
    Species("docs", "青草", "grass", "w", "32", "#4caf50", "grass"),
    Species("refactor", "藤蔓", "vine", "&", "36", "#17a2b8", "vine"),
    Species("test", "三葉草", "clover", "%", "92", "#2e9e5b", "clover"),
    Species("perf", "松樹", "pine", "^", "32", "#1b7f4c", "pine"),
    Species("style", "蘆葦", "reed", "~", "96", "#8ab4a0", "reed"),
    Species("ci", "竹子", "bamboo", "#", "35", "#7cb342", "bamboo"),
    Species("chore", "石頭", "pebble", "o", "90", "#9aa0a6", "pebble"),
    Species("revert", "枯枝", "withered twig", "x", "37", "#8d6e63", "dead"),
    Species("other", "野花", "wildflower", "*", "95", "#d96ad0", "weed"),
]

SPECIES: Dict[str, Species] = {s.key: s for s in _ALL}
OTHER = SPECIES["other"]

_CONVENTIONAL = re.compile(r"^(?P<type>[A-Za-z]+)(?:\([^)]*\))?!?:")

_ALIASES = {
    "feature": "feat",
    "features": "feat",
    "bugfix": "fix",
    "hotfix": "fix",
    "bug": "fix",
    "doc": "docs",
    "documentation": "docs",
    "tests": "test",
    "testing": "test",
    "build": "ci",
    "deps": "chore",
    "release": "chore",
    "performance": "perf",
    "cleanup": "refactor",
}

# 沒有遵守 Conventional Commits 時，退而求其次用關鍵字猜（順序有意義）
_KEYWORDS = [
    ("fix", r"\b(fix|fixes|fixed|bug|patch)\b"),
    ("docs", r"\b(docs?|readme|documentation)\b"),
    ("test", r"\b(tests?|testing|spec)\b"),
    ("refactor", r"\b(refactor|clean ?up|rename|simplify)\b"),
    ("perf", r"\b(perf|performance|optimi[sz]e|speed ?up)\b"),
    ("style", r"\b(style|format|lint|prettier)\b"),
    ("ci", r"\b(ci|workflow|pipeline|build)\b"),
    ("chore", r"\b(chore|bump|deps|dependency|dependencies)\b"),
    ("feat", r"\b(add|adds|added|feat|feature|implement|support|introduce)\b"),
]
_KEYWORDS = [(key, re.compile(pat, re.IGNORECASE)) for key, pat in _KEYWORDS]


def classify(subject: str) -> Species:
    """根據 commit 標題決定這是哪一種植物。"""
    text = subject.strip()
    if re.match(r"revert\b", text, re.IGNORECASE):
        return SPECIES["revert"]

    match = _CONVENTIONAL.match(text)
    if match:
        kind = match.group("type").lower()
        kind = _ALIASES.get(kind, kind)
        if kind in SPECIES and kind != "other":
            return SPECIES[kind]

    for key, pattern in _KEYWORDS:
        if pattern.search(text):
            return SPECIES[key]
    return OTHER
