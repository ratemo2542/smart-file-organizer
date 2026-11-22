import unittest

from smart_file_organizer.categories import (
    DEFAULT_CATEGORY, all_category_names, get_category)


class GetCategoryTests(unittest.TestCase):
    def test_known_extensions(self):
        cases = {
            "photo.jpg": "Images", "scan.png": "Images",
            "report.pdf": "Documents", "notes.txt": "Documents",
            "essay.docx": "Documents", "movie.mp4": "Videos",
            "clip.mkv": "Videos", "song.mp3": "Audio",
            "sound.wav": "Audio", "bundle.zip": "Archives",
            "old.rar": "Archives",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(get_category(name), expected)

    def test_case_insensitive(self):
        self.assertEqual(get_category("PHOTO.JPG"), "Images")

    def test_unknown_and_missing_extension(self):
        self.assertEqual(get_category("program.xyz"), DEFAULT_CATEGORY)
        self.assertEqual(get_category("Makefile"), DEFAULT_CATEGORY)

    def test_double_extension_uses_last_part(self):
        self.assertEqual(get_category("backup.tar.gz"), "Archives")

    def test_category_names_include_default(self):
        self.assertIn("Others", all_category_names())


if __name__ == "__main__":
    unittest.main()
