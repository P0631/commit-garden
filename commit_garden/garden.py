"""把 commit 變成植物：決定品種、高度與種子。"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass
from typing import List, Sequence

from .gitlog import Commit
from .species import Species, classify

MAX_HEIGHT = 7


@dataclass(frozen=True)
class Plant:
    commit: Commit
    species: Species
    height: int

    @property
    def seed(self) -> int:
        """由 commit hash 衍生的固定數字，讓同一個 commit 永遠長一樣。"""
        return zlib.crc32(self.commit.sha.encode("utf-8"))


def height_for(churn: int, max_height: int = MAX_HEIGHT) -> int:
    """改動量越大長越高，但用對數壓縮，避免一個大 commit 把圖撐爆。"""
    level = 1 + int(math.log2(1 + max(churn, 0)) / 2)
    return max(1, min(max_height, level))


def grow(commits: Sequence[Commit], max_height: int = MAX_HEIGHT) -> List[Plant]:
    return [Plant(c, classify(c.subject), height_for(c.churn, max_height)) for c in commits]


def chunk(plants: Sequence[Plant], per_row: int) -> List[List[Plant]]:
    """把植物切成一畦一畦的花圃。"""
    if per_row < 1:
        raise ValueError("per_row 必須 >= 1")
    return [list(plants[i : i + per_row]) for i in range(0, len(plants), per_row)]
