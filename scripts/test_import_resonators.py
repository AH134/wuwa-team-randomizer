import unittest

from import_resonators import apply_record, normalize_slug, parse_enum_list


class ImportResonatorsTests(unittest.TestCase):
    def test_normalize_slug_replaces_spaces_and_underscores(self):
        self.assertEqual(normalize_slug("Yangyang_Xuanling"), "yangyang-xuanling")
        self.assertEqual(normalize_slug("Yangyang Xuanling"), "yangyang-xuanling")

    def test_normalize_slug_does_not_allow_path_separators(self):
        self.assertEqual(normalize_slug("../../Hsin"), "hsin")

    def test_parse_enum_list_accepts_multiple_genders(self):
        self.assertEqual(
            parse_enum_list("Female and Male", {"male", "female"}, "gender"),
            ["female", "male"],
        )

    def test_apply_record_appends_with_next_consecutive_id(self):
        source = """import { type Character } from "../types/types";

export const characters: Character[] = [
    {
        id: 0,
        slug: "first",
        displayName: "First",
        weapon: "sword",
        rarity: 4,
        attribute: ["aero"],
        gender: ["female"],
        selected: true,
    },
];
"""
        metadata = {
            "displayName": "Second",
            "weapon": "rectifier",
            "rarity": 5,
            "attribute": ["glacio"],
            "gender": ["female"],
        }

        updated = apply_record(source, "second", metadata)

        self.assertIn('id: 1,\n        slug: "second"', updated)
        self.assertIn('weapon: "rectifier"', updated)
        self.assertIn('attribute: ["glacio"]', updated)

    def test_apply_record_updates_existing_slug_without_changing_id(self):
        source = """export const characters = [
    {
        id: 0,
        slug: "first",
        displayName: "First",
        weapon: "sword",
        rarity: 4,
        attribute: ["aero"],
        gender: ["female"],
        selected: false,
    },
];
"""
        metadata = {
            "displayName": "First Updated",
            "weapon": "rectifier",
            "rarity": 5,
            "attribute": ["glacio"],
            "gender": ["male"],
        }

        updated = apply_record(source, "first", metadata)

        self.assertIn("id: 0,", updated)
        self.assertIn('displayName: "First Updated"', updated)
        self.assertIn("selected: false,", updated)
        self.assertIn('gender: ["male"]', updated)


if __name__ == "__main__":
    unittest.main()
