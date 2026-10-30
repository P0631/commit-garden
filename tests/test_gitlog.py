import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from commit_garden.demo import build_demo_repo
from commit_garden.gitlog import GitError, parse_log, read_commits

HAS_GIT = shutil.which("git") is not None

RAW = (
    "\x1eabc\x1fAda\x1f2026-01-05T09:00:00+00:00\x1ffeat: hi\n\n"
    " 1 file changed, 3 insertions(+), 1 deletion(-)\n"
    "\x1edef\x1fBob\x1f2026-01-06T09:00:00+08:00\x1ffix: x\n"
)


class ParseTests(unittest.TestCase):
    def test_parse_log(self):
        commits = parse_log(RAW)
        self.assertEqual([c.sha for c in commits], ["abc", "def"])
        self.assertEqual((commits[0].insertions, commits[0].deletions), (3, 1))
        self.assertEqual(commits[0].churn, 4)
        self.assertEqual(commits[1].churn, 0)
        self.assertEqual(commits[1].date.utcoffset().total_seconds(), 8 * 3600)

    def test_parse_empty(self):
        self.assertEqual(parse_log(""), [])


@unittest.skipUnless(HAS_GIT, "需要安裝 git")
class RepoTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def test_reads_demo_repo_oldest_first(self):
        repo = build_demo_repo(self.tmp / "r", commits=12)
        commits = read_commits(repo)
        self.assertEqual(len(commits), 12)
        self.assertEqual([c.date for c in commits], sorted(c.date for c in commits))
        self.assertTrue(all(c.churn > 0 for c in commits))

    def test_limit_returns_latest(self):
        repo = build_demo_repo(self.tmp / "r", commits=12)
        everything = read_commits(repo)
        latest = read_commits(repo, limit=5)
        self.assertEqual([c.sha for c in latest], [c.sha for c in everything[-5:]])

    def test_empty_repo_gives_empty_list(self):
        subprocess.run(["git", "init", "-q", str(self.tmp)], check=True)
        self.assertEqual(read_commits(self.tmp), [])

    def test_not_a_repo_raises(self):
        with self.assertRaises(GitError):
            read_commits(self.tmp)

    def test_demo_refuses_existing_repo(self):
        repo = build_demo_repo(self.tmp / "r", commits=2)
        with self.assertRaises(GitError):
            build_demo_repo(repo, commits=2)


if __name__ == "__main__":
    unittest.main()
