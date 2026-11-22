import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from smart_file_organizer.cli import main
from smart_file_organizer.organizer import (
    execute_moves, plan_moves, unique_destination)
from smart_file_organizer.scanner import (
    DirectoryError, scan_directory, validate_directory)


def make_files(root: Path, names):
    for name in names:
        (root / name).write_text(f"content of {name}")


class ScannerTests(unittest.TestCase):
    def test_skips_hidden_folders_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_files(root, ["b.txt", "A.txt", ".hidden"])
            (root / "subdir").mkdir()
            names = [p.name for p in scan_directory(root)]
            self.assertEqual(names, ["A.txt", "b.txt"])

    def test_include_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_files(root, [".hidden"])
            self.assertEqual(len(scan_directory(root, include_hidden=True)), 1)

    def test_invalid_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DirectoryError):
                validate_directory(Path(tmp) / "missing")
            make_files(Path(tmp), ["file.txt"])
            with self.assertRaises(DirectoryError):
                validate_directory(Path(tmp) / "file.txt")


class UniqueDestinationTests(unittest.TestCase):
    def test_free_name_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "a.jpg"
            self.assertEqual(unique_destination(dest, set()), dest)

    def test_existing_file_gets_counter(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "a.jpg"
            dest.write_text("x")
            self.assertEqual(unique_destination(dest, set()).name, "a (1).jpg")

    def test_reserved_names_are_respected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "a.jpg"
            reserved = {str(dest).lower()}
            self.assertEqual(unique_destination(dest, reserved).name, "a (1).jpg")


class PlanAndExecuteTests(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_files(root, ["a.jpg", "b.pdf"])
            moves = plan_moves(scan_directory(root), root)
            summary = execute_moves(moves, dry_run=True)
            self.assertEqual(len(summary.moved), 2)
            self.assertTrue((root / "a.jpg").exists())
            self.assertFalse((root / "Images").exists())

    def test_real_run_moves_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_files(root, ["a.jpg", "b.pdf", "c.xyz"])
            moves = plan_moves(scan_directory(root), root)
            summary = execute_moves(moves)
            self.assertEqual(summary.failed, [])
            self.assertTrue((root / "Images" / "a.jpg").exists())
            self.assertTrue((root / "Documents" / "b.pdf").exists())
            self.assertTrue((root / "Others" / "c.xyz").exists())
            self.assertFalse((root / "a.jpg").exists())

    def test_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Images").mkdir()
            (root / "Images" / "a.jpg").write_text("ORIGINAL")
            make_files(root, ["a.jpg"])
            execute_moves(plan_moves(scan_directory(root), root))
            self.assertEqual((root / "Images" / "a.jpg").read_text(), "ORIGINAL")
            self.assertEqual(
                (root / "Images" / "a (1).jpg").read_text(), "content of a.jpg")

    def test_planned_rename_does_not_collide_with_other_source(self):
        """A planned rename must not collide with another source filename."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Images").mkdir()
            (root / "Images" / "a.jpg").write_text("ORIGINAL")
            make_files(root, ["a.jpg", "a (1).jpg"])
            moves = plan_moves(scan_directory(root), root)
            destinations = {m.destination for m in moves}
            self.assertEqual(len(destinations), 2)
            execute_moves(moves)
            self.assertEqual(len(list((root / "Images").iterdir())), 3)

    def test_running_twice_is_harmless(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_files(root, ["a.jpg"])
            execute_moves(plan_moves(scan_directory(root), root))
            self.assertEqual(scan_directory(root), [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_bad_directory_returns_error_code(self):
        code, _, err = self.run_cli("/definitely/not/here")
        self.assertEqual(code, 2)
        self.assertIn("does not exist", err)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = self.run_cli(tmp)
            self.assertEqual(code, 0)
            self.assertIn("Nothing to organize", out)

    def test_dry_run_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_files(Path(tmp), ["a.jpg"])
            code, out, _ = self.run_cli(tmp, "--dry-run")
            self.assertEqual(code, 0)
            self.assertIn("DRY RUN", out)
            self.assertIn("would be moved", out)
            self.assertTrue((Path(tmp) / "a.jpg").exists())


if __name__ == "__main__":
    unittest.main()
