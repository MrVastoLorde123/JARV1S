"""M24.1 cockpit foundation contract tests."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "ui"


class M24CockpitFoundationTests(unittest.TestCase):
    def test_required_surface_files_exist(self):
        for name in ("index.html", "styles.css", "app.js"):
            with self.subTest(name=name):
                self.assertTrue((UI / name).is_file())

    def test_cockpit_exposes_operational_state_and_authority_boundary(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        for marker in ("OPERATIONAL COCKPIT", "OPERATIONAL STATE", "ACTIVITY", "SYSTEM HEALTH", "AUTHORITY BOUNDARY"):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        self.assertIn("PLANNING</span><b>≠</b><span>AUTHORIZATION", html)
        self.assertIn("EXECUTION</span><b>≠</b><span>VERIFICATION", html)

    def test_cockpit_demo_is_inert(self):
        script = (UI / "app.js").read_text(encoding="utf-8")
        self.assertIn("No tools invoked; no authority exercised", script)
        self.assertNotIn("fetch(", script)
        self.assertNotIn("XMLHttpRequest", script)


if __name__ == "__main__":
    unittest.main()
