from datetime import datetime, timedelta, timezone

from commit_garden.gitlog import Commit
from commit_garden.garden import grow

SUBJECTS = [
    "feat: add login", "fix: crash", "docs: readme", "refactor: tidy", "test: more",
    "perf: faster", "style: format", "ci: workflow", "chore: bump", 'Revert "x"', "wip",
]


def make_commit(i, subject=None, insertions=10, deletions=0):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return Commit(
        sha="%040x" % (i + 1),
        author="Tester",
        date=base + timedelta(days=i),
        subject=subject if subject is not None else SUBJECTS[i % len(SUBJECTS)],
        insertions=insertions,
        deletions=deletions,
    )


def make_plants(n, **kwargs):
    return grow([make_commit(i, **kwargs) for i in range(n)])
