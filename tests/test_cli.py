import contextlib
import io
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from commit_garden.cli import main

HAS_GIT = shutil.which("git") is not None


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


@unittest.skipUnless(HAS_GIT, "需要安裝 git")
class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "garden-demo"
        code, _, _ = run(["demo", str(self.repo), "--commits", "20"])
        self.assertEqual(code, 0)

    def test_grow_ascii(self):
        code, out, _ = run(["grow", str(self.repo), "--color", "never"])
        self.assertEqual(code, 0)
        self.assertIn("garden-demo", out)
        self.assertNotIn("\x1b[", out)

    def test_grow_svg_to_file(self):
        target = self.tmp / "out" / "garden.svg"
        code, out, _ = run(["grow", str(self.repo), "-f", "svg", "-o", str(target), "--theme", "dark"])
        self.assertEqual(code, 0)
        self.assertIn("garden.svg", out)
        ET.fromstring(target.read_text(encoding="utf-8"))

    def test_stats(self):
        code, out, _ = run(["stats", str(self.repo)])
        self.assertEqual(code, 0)
        self.assertIn("物種分布", out)

    def test_legend(self):
        code, out, _ = run(["legend", "--color", "never"])
        self.assertEqual(code, 0)
        self.assertIn("向日葵", out)

    def test_not_a_repo_returns_error_code(self):
        code, _, err = run(["grow", str(self.tmp)])
        self.assertEqual(code, 1)
        self.assertIn("錯誤", err)

    def test_demo_twice_fails_cleanly(self):
        code, _, err = run(["demo", str(self.repo)])
        self.assertEqual(code, 1)
        self.assertIn("錯誤", err)


if __name__ == "__main__":
    unittest.main()
