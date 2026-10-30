import unittest

from commit_garden.garden import MAX_HEIGHT, Plant, chunk, height_for
from commit_garden.species import SPECIES
from helpers import make_commit, make_plants


class GardenTests(unittest.TestCase):
    def test_height_is_monotonic_and_bounded(self):
        heights = [height_for(n) for n in (0, 1, 3, 15, 63, 255, 1023, 10**6)]
        self.assertEqual(heights, sorted(heights))
        self.assertEqual(heights[0], 1)
        self.assertEqual(heights[-1], MAX_HEIGHT)

    def test_negative_churn_is_safe(self):
        self.assertEqual(height_for(-5), 1)

    def test_seed_is_deterministic(self):
        a = Plant(make_commit(1), SPECIES["feat"], 3)
        b = Plant(make_commit(1), SPECIES["feat"], 3)
        c = Plant(make_commit(2), SPECIES["feat"], 3)
        self.assertEqual(a.seed, b.seed)
        self.assertNotEqual(a.seed, c.seed)

    def test_chunk(self):
        plants = make_plants(10)
        self.assertEqual([len(r) for r in chunk(plants, 4)], [4, 4, 2])
        self.assertEqual(chunk([], 4), [])
        with self.assertRaises(ValueError):
            chunk(plants, 0)


if __name__ == "__main__":
    unittest.main()
