"""終端機 ASCII 渲染：每株植物佔 3 個字元寬。"""
from __future__ import annotations

from typing import List, Optional, Sequence

from .garden import Plant, chunk
from .species import SPECIES

CELL = 3
_LEAVES = (" | ", "/| ", " |\\", "/|\\")


def _paint(text: str, code: str, color: bool) -> str:
    return f"\x1b[{code}m{text}\x1b[0m" if color else text


def _cell(plant: Plant, level: int, color: bool) -> str:
    if level == plant.height:
        sp = plant.species
        return _paint(f" {sp.head} ", sp.ansi, color)
    if level == 1:
        stem = " | "
    else:
        # 葉子的長法由 commit hash 決定，所以每次畫都一樣
        stem = _LEAVES[(plant.seed >> (2 * level)) & 3]
    return _paint(stem, "32", color)


def render_legend(plants: Optional[Sequence[Plant]] = None, color: bool = False) -> str:
    present = {p.species.key for p in plants} if plants is not None else None
    items: List[str] = []
    for key, sp in SPECIES.items():
        if present is not None and key not in present:
            continue
        items.append(f"{_paint(sp.head, sp.ansi, color)} {sp.name_zh}({key})")
    return "  ".join(items)


def render_ascii(
    plants: Sequence[Plant],
    per_row: int = 24,
    color: bool = False,
    title: Optional[str] = None,
    legend: bool = True,
) -> str:
    lines: List[str] = []
    if title:
        lines += [title, ""]

    for row in chunk(plants, per_row):
        height = max(p.height for p in row)
        for level in range(height, 0, -1):
            cells = [_cell(p, level, color) if level <= p.height else " " * CELL for p in row]
            lines.append("".join(cells).rstrip())
        lines.append(_paint("=" * (CELL * len(row)), "33", color))
        lines.append(f"{row[0].commit.date:%Y-%m-%d} ~ {row[-1].commit.date:%Y-%m-%d}")
        lines.append("")

    if legend:
        lines.append(render_legend(plants, color))
    return "\n".join(lines).rstrip("\n")
