import unittest
import xml.etree.ElementTree as ET

from commit_garden.garden import grow
from commit_garden.render_ascii import render_ascii, render_legend
from commit_garden.render_svg import render_svg
from helpers import make_commit, make_plants

SVG_NS = "{http://www.w3.org/2000/svg}"


class AsciiTests(unittest.TestCase):
    def test_plain_output_has_no_escape_codes(self):
        out = render_ascii(make_plants(6), per_row=6, color=False, title="demo")
        self.assertNotIn("\x1b[", out)
        self.assertTrue(out.startswith("demo"))
        self.assertIn("=" * 18, out)

    def test_color_output_has_escape_codes(self):
        self.assertIn("\x1b[", render_ascii(make_plants(3), color=True))

    def test_rows_are_wrapped(self):
        out = render_ascii(make_plants(12), per_row=5, legend=False)
        grounds = [line for line in out.splitlines() if line and set(line) == {"="}]
        self.assertEqual([len(g) for g in grounds], [15, 15, 6])

    def test_heads_appear(self):
        out = render_ascii(grow([make_commit(0, "feat: a"), make_commit(1, "fix: b")]), legend=False)
        self.assertIn("@", out)
        self.assertIn("m", out)

    def test_legend_lists_only_present_species(self):
        legend = render_legend(grow([make_commit(0, "feat: a")]))
        self.assertIn("向日葵", legend)
        self.assertNotIn("蘑菇", legend)

    def test_empty_garden(self):
        self.assertEqual(render_ascii([]), "")


class SvgTests(unittest.TestCase):
    def test_is_well_formed_with_one_group_per_plant(self):
        svg = render_svg(make_plants(25), per_row=10, title="demo")
        root = ET.fromstring(svg)
        self.assertEqual(len(root.findall(f"{SVG_NS}g")), 25)

    def test_user_text_is_escaped(self):
        plants = grow([make_commit(0, "<script>alert(1)</script> & co")])
        svg = render_svg(plants, title="a<b>&c")
        self.assertNotIn("<script>", svg)
        root = ET.fromstring(svg)
        titles = [t.text for t in root.iter(f"{SVG_NS}title")]
        self.assertTrue(any("<script>" in (t or "") for t in titles))

    def test_dark_theme_and_invalid_theme(self):
        self.assertIn("#0d1b2a", render_svg(make_plants(3), theme="dark"))
        with self.assertRaises(ValueError):
            render_svg(make_plants(3), theme="neon")

    def test_empty_garden_still_renders(self):
        ET.fromstring(render_svg([]))


if __name__ == "__main__":
    unittest.main()
