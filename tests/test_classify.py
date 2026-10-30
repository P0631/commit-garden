import unittest

from commit_garden.species import classify


class ClassifyTests(unittest.TestCase):
    def test_conventional_prefix(self):
        self.assertEqual(classify("feat: add login").key, "feat")
        self.assertEqual(classify("fix(api): handle null").key, "fix")
        self.assertEqual(classify("refactor!: drop legacy").key, "refactor")

    def test_aliases(self):
        self.assertEqual(classify("feature: x").key, "feat")
        self.assertEqual(classify("bugfix: y").key, "fix")
        self.assertEqual(classify("documentation: z").key, "docs")
        self.assertEqual(classify("build: w").key, "ci")

    def test_revert_wins(self):
        self.assertEqual(classify('Revert "add search"').key, "revert")
        self.assertEqual(classify("revert: feat: add search").key, "revert")

    def test_keyword_fallback(self):
        self.assertEqual(classify("Fix typo in readme").key, "fix")
        self.assertEqual(classify("Update README").key, "docs")
        self.assertEqual(classify("Add tests for parser").key, "test")
        self.assertEqual(classify("Implement dark mode").key, "feat")
        self.assertEqual(classify("Add CI workflow").key, "ci")

    def test_unknown_becomes_wildflower(self):
        self.assertEqual(classify("wip").key, "other")
        self.assertEqual(classify("").key, "other")
        self.assertEqual(classify("weird: thing").key, "other")


if __name__ == "__main__":
    unittest.main()
