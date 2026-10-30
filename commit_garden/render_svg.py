"""SVG 渲染：可以直接放進 README。"""
from __future__ import annotations

import math
from typing import Callable, Dict, Sequence
from xml.sax.saxutils import escape

from .garden import Plant, chunk

CELL = 30
UNIT = 15
MARGIN = 24
HEAD_SPACE = 28
GROUND = 22
TITLE_H = 58

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "sky_top": "#dff1ff", "sky_bottom": "#fff7e0", "ground": "#8b6b4a",
        "grass": "#6aa84f", "stem": "#4a8f52", "leaf": "#62b36b",
        "text": "#37474f", "subtext": "#78909c",
    },
    "dark": {
        "sky_top": "#0d1b2a", "sky_bottom": "#1b263b", "ground": "#4e3b2a",
        "grass": "#3d7a3a", "stem": "#6bbf73", "leaf": "#4fa35a",
        "text": "#e0e1dd", "subtext": "#9aa5b1",
    },
}

FONT = "system-ui, -apple-system, 'Segoe UI', 'Noto Sans TC', sans-serif"


def _f(v: float) -> str:
    return f"{v:.1f}"


def _circle(cx: float, cy: float, r: float, fill: str) -> str:
    return f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"/>'


def _line(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 2) -> str:
    return (
        f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" '
        f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"/>'
    )


def _flower(x: float, y: float, c: str) -> str:
    petals = "".join(
        _circle(x + 5 * math.cos(math.radians(60 * k)), y + 5 * math.sin(math.radians(60 * k)), 3.6, c)
        for k in range(6)
    )
    return petals + _circle(x, y, 3.2, "#7a4b00")


def _mushroom(x: float, y: float, c: str) -> str:
    cap = f'<path d="M{_f(x - 8)},{_f(y + 3)} A8,8 0 0 1 {_f(x + 8)},{_f(y + 3)} Z" fill="{c}"/>'
    return cap + _circle(x - 3, y - 1, 1.5, "#ffffff") + _circle(x + 3, y - 2.5, 1.3, "#ffffff")


def _grass(x: float, y: float, c: str) -> str:
    return _line(x, y + 3, x - 5, y - 6, c) + _line(x, y + 3, x, y - 8, c) + _line(x, y + 3, x + 5, y - 6, c)


def _vine(x: float, y: float, c: str) -> str:
    return (
        f'<path d="M{_f(x - 5)},{_f(y)} A5,5 0 1 1 {_f(x)},{_f(y + 5)} A3,3 0 1 1 {_f(x - 2)},{_f(y + 2)}" '
        f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>'
    )


def _clover(x: float, y: float, c: str) -> str:
    return _circle(x, y - 4, 4, c) + _circle(x - 4, y + 2, 4, c) + _circle(x + 4, y + 2, 4, c)


def _pine(x: float, y: float, c: str) -> str:
    top = f'<polygon points="{_f(x)},{_f(y - 12)} {_f(x - 6.5)},{_f(y - 3)} {_f(x + 6.5)},{_f(y - 3)}" fill="{c}"/>'
    low = f'<polygon points="{_f(x)},{_f(y - 6)} {_f(x - 8)},{_f(y + 5)} {_f(x + 8)},{_f(y + 5)}" fill="{c}"/>'
    return low + top


def _reed(x: float, y: float, c: str) -> str:
    return f'<rect x="{_f(x - 2)}" y="{_f(y - 9)}" width="4" height="13" rx="2" fill="{c}"/>'


def _bamboo(x: float, y: float, c: str) -> str:
    return "".join(
        f'<rect x="{_f(x - 3)}" y="{_f(y + dy)}" width="6" height="5" rx="1.5" fill="{c}"/>'
        for dy in (-11, -5, 1)
    )


def _pebble(x: float, y: float, c: str) -> str:
    return (
        f'<ellipse cx="{_f(x)}" cy="{_f(y + 1)}" rx="7" ry="5" fill="{c}"/>'
        f'<ellipse cx="{_f(x - 2)}" cy="{_f(y - 1)}" rx="2.5" ry="1.4" fill="#ffffff" fill-opacity="0.35"/>'
    )


def _dead(x: float, y: float, c: str) -> str:
    return _line(x - 5, y - 5, x + 5, y + 5, c, 2.5) + _line(x + 5, y - 5, x - 5, y + 5, c, 2.5)


def _weed(x: float, y: float, c: str) -> str:
    spokes = ""
    for angle in (0, 60, 120):
        dx, dy = 6 * math.cos(math.radians(angle)), 6 * math.sin(math.radians(angle))
        spokes += _line(x - dx, y - dy, x + dx, y + dy, c)
    return spokes + _circle(x, y, 1.8, "#ffffff")


_SHAPES: Dict[str, Callable[[float, float, str], str]] = {
    "flower": _flower, "mushroom": _mushroom, "grass": _grass, "vine": _vine,
    "clover": _clover, "pine": _pine, "reed": _reed, "bamboo": _bamboo,
    "pebble": _pebble, "dead": _dead, "weed": _weed,
}


def _plant(p: Plant, cx: float, ground_y: float, theme: Dict[str, str]) -> str:
    seed = p.seed
    top_y = ground_y - p.height * UNIT
    sway = (seed & 7) - 3
    head_x = cx + sway
    stem_color, leaf_color = theme["stem"], theme["leaf"]

    parts = [
        f'<path d="M{_f(cx)},{_f(ground_y)} Q{_f(cx + sway * 2)},{_f((ground_y + top_y) / 2)} '
        f'{_f(head_x)},{_f(top_y)}" fill="none" stroke="{stem_color}" '
        f'stroke-width="2" stroke-linecap="round"/>'
    ]
    for lvl in range(1, p.height):
        side = 1 if (seed >> (lvl + 3)) & 1 else -1
        t = lvl / p.height
        lx = cx + sway * (4 * t - 3 * t * t) + side * 5  # 二次貝茲曲線上的 x
        ly = ground_y - lvl * UNIT + 2
        parts.append(
            f'<ellipse cx="{_f(lx)}" cy="{_f(ly)}" rx="5" ry="2.4" fill="{leaf_color}" '
            f'transform="rotate({-30 * side} {_f(lx)} {_f(ly)})"/>'
        )
    parts.append(_SHAPES[p.species.shape](head_x, top_y - 1, p.species.color))

    tip = f"{p.commit.sha[:7]} · {p.species.name_zh} ({p.species.key}) · {p.commit.subject}"
    return f"<g><title>{escape(tip)}</title>{''.join(parts)}</g>"


def render_svg(
    plants: Sequence[Plant],
    per_row: int = 30,
    title: str = "Commit Garden",
    theme: str = "light",
) -> str:
    if theme not in THEMES:
        raise ValueError(f"unknown theme: {theme}（可用：{', '.join(THEMES)}）")
    t = THEMES[theme]

    rows = chunk(plants, per_row) if plants else []
    cols = max(min(per_row, len(plants)), 12)
    width = MARGIN * 2 + cols * CELL
    max_h = max((p.height for p in plants), default=1)
    band_h = HEAD_SPACE + max_h * UNIT + GROUND
    height = TITLE_H + max(len(rows), 1) * band_h + MARGIN // 2

    species_n = len({p.species.key for p in plants})
    subtitle = f"{len(plants)} commits · {species_n} species"
    if plants:
        subtitle += f" · {plants[0].commit.date:%Y-%m-%d} – {plants[-1].commit.date:%Y-%m-%d}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}" font-family="{FONT}">',
        '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["sky_top"]}"/><stop offset="1" stop-color="{t["sky_bottom"]}"/>'
        "</linearGradient></defs>",
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#sky)"/>',
        f'<text x="{MARGIN}" y="30" font-size="18" font-weight="600" fill="{t["text"]}">{escape(title)}</text>',
        f'<text x="{MARGIN}" y="48" font-size="11" fill="{t["subtext"]}">{escape(subtitle)}</text>',
    ]

    for r, row in enumerate(rows):
        ground_y = TITLE_H + (r + 1) * band_h - GROUND
        gx, gw = MARGIN - 10, cols * CELL + 20
        out.append(f'<rect x="{gx}" y="{_f(ground_y)}" width="{gw}" height="{GROUND}" rx="6" fill="{t["ground"]}"/>')
        out.append(f'<rect x="{gx}" y="{_f(ground_y)}" width="{gw}" height="5" rx="2.5" fill="{t["grass"]}"/>')
        for i, p in enumerate(row):
            out.append(_plant(p, MARGIN + i * CELL + CELL / 2, ground_y, t))

    out.append("</svg>")
    return "\n".join(out)
