import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from expense_tracker.cli import run


class CliIntegrationTests(unittest.TestCase):
    """Integration tests: CLI -> service -> real SQLite file."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "t.db")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *argv):
        out = io.StringIO()
        code = run(["--db", self.db, *argv], out=out)
        return code, out.getvalue()

    def test_full_workflow(self):
        self.assertEqual(self.cli("add", "12.50", "food", "-d", "2026-10-01", "-n", "lunch")[0], 0)
        self.assertEqual(self.cli("add", "40", "travel", "-d", "2026-10-02")[0], 0)
        code, out = self.cli("list", "-c", "food")
        self.assertIn("12.50", out)
        self.assertNotIn("travel", out)
        code, out = self.cli("summary")
        self.assertIn("TOTAL", out)
        self.assertIn("52.50", out)
        self.cli("budget", "food", "10")
        code, out = self.cli("status", "--month", "2026-10")
        self.assertIn("OVER BUDGET", out)
        self.assertEqual(self.cli("delete", "1")[0], 0)
        self.assertIn("No expenses", self.cli("list", "-c", "food")[1])

    def test_errors_return_nonzero(self):
        self.assertEqual(self.cli("add", "abc", "food")[0], 1)
        self.assertEqual(self.cli("delete", "42")[0], 1)
        self.assertEqual(self.cli("add", "5", "food", "-d", "bad-date")[0], 1)


if __name__ == "__main__":
    unittest.main()
