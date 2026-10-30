"""花園統計：物種分布、多樣性、最勤勞的園丁。"""
from __future__ import annotations

import math
import unicodedata
from collections import Counter
from typing import List, Sequence

from .gitlog import Commit
from .species import SPECIES, classify

_WEEKDAYS = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
_BAR_WIDTH = 20


def _display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def _pad(text: str, width: int) -> str:
    return text + " " * max(0, width - _display_width(text))


def shannon(counts: Sequence[int]) -> float:
    """Shannon 多樣性指數：物種越多、分布越平均，數值越高。"""
    total = sum(counts)
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log(c / total) for c in counts if c)


def render_stats(commits: Sequence[Commit], name: str) -> str:
    if not commits:
        return f"{name}：還沒有任何 commit。"

    species_count = Counter(classify(c.subject).key for c in commits)
    authors = Counter(c.author for c in commits)
    weekdays = Counter(c.date.weekday() for c in commits)
    active_days = len({c.date.date() for c in commits})
    top = max(species_count.values())
    diversity = shannon(list(species_count.values()))

    lines: List[str] = [
        f"花園：{name}",
        f"commit 數量：{len(commits)}（{commits[0].date:%Y-%m-%d} ~ {commits[-1].date:%Y-%m-%d}，共 {active_days} 個有種植的日子）",
        f"物種多樣性 (Shannon)：{diversity:.2f} / {math.log(len(SPECIES)):.2f}",
        "",
        "物種分布：",
    ]
    for key, count in species_count.most_common():
        sp = SPECIES[key]
        label = _pad(f"{sp.head} {sp.name_zh}", 10)
        bar = "█" * max(1, round(count / top * _BAR_WIDTH))
        lines.append(f"  {label}{key:<9}{count:>4}  {bar}")

    lines += ["", "最勤勞的園丁："]
    for author, count in authors.most_common(5):
        lines.append(f"  {_pad(author, 16)}{count:>4}")

    busiest = weekdays.most_common(1)[0][0]
    lines += ["", f"最常澆水的日子：{_WEEKDAYS[busiest]}"]
    return "\n".join(lines)
