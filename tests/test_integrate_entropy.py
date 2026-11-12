import csv
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "origin-science-figures" / "scripts" / "integrate_entropy.py"
EXAMPLES = ROOT / "examples"


class EntropyTest(unittest.TestCase):
    def run_example(self, *options, cp=None, magnetic=False, delta_only=False):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.csv"
            if delta_only:
                basis = ["--delta-only"]
            elif magnetic:
                basis = ["--magnetic-input"]
            else:
                basis = ["--phonon", str(EXAMPLES / "synthetic_phonon.csv")]
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--cp", str(cp or EXAMPLES / "synthetic_cp.csv"),
                 *basis, "--output", str(output), *options],
                capture_output=True, text=True,
            )
            rows = []
            if output.exists():
                with output.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
            return run, rows

    def test_common_grid_and_axis_conversions(self):
        run, rows = self.run_example("--molar-mass", "200", "--molar-volume", "50")
        self.assertEqual(run.returncode, 0, run.stderr)
        for field in ("2.0", "4.0"):
            points = [row for row in rows if row["field_T"] == field]
            self.assertEqual(float(points[0]["temperature_K"]), 3.0)
            self.assertEqual(float(points[0]["minus_delta_Srel_J_mol_K"]), 0.0)
            self.assertEqual(float(points[-1]["temperature_K"]), 6.5)
        end = [row for row in rows if row["field_T"] == "2.0"][-1]
        expected = 2.8 + 0.8 * math.log(6.5 / 3)
        self.assertAlmostEqual(float(end["minus_delta_Srel_J_mol_K"]), expected, places=12)
        self.assertAlmostEqual(float(end["minus_delta_Srel_J_kg_K"]), expected * 5, places=12)
        self.assertAlmostEqual(float(end["minus_delta_Srel_mJ_cm3_K"]), expected * 20, places=12)
        self.assertAlmostEqual(float(end["Srel_reference_J_mol_K"]), 1.7 * 3.5 + math.log(6.5 / 3), places=12)

    def test_pairwise_and_explicit_models(self):
        run, rows = self.run_example("--mode", "pairwise")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual({r["field_T"]: float(r["lower_limit_K"]) for r in rows}, {"2.0": 3.0, "4.0": 2.5})
        refused, _ = self.run_example("--mode", "pairwise", "--start", "2")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("requested start is below supplied overlap", refused.stderr)
        run, rows = self.run_example("--mode", "pairwise", "--allow-modeled")
        self.assertEqual(run.returncode, 0, run.stderr)
        points = [r for r in rows if r["field_T"] == "4.0"]
        self.assertEqual(float(points[0]["lower_limit_K"]), 2.0)
        self.assertEqual(points[1]["interval_uses_modeled_cp"], "1")
        self.assertEqual(points[-1]["interval_uses_modeled_cp"], "0")
        self.assertEqual(points[-1]["cumulative_uses_modeled_cp"], "1")

    def test_total_cp_without_background_reports_only_field_difference(self):
        run, rows = self.run_example(delta_only=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        field = [row for row in rows if row["field_T"] == "2.0"]
        self.assertEqual(float(field[0]["lower_limit_K"]), 3.0)
        self.assertNotIn("Srel_reference_J_mol_K", field[-1])
        self.assertAlmostEqual(float(field[-1]["minus_delta_Srel_J_mol_K"]),
                               2.8 + 0.8 * math.log(6.5 / 3), places=12)

    def test_interior_peak_and_signed_entropy(self):
        with tempfile.TemporaryDirectory() as directory:
            cp = Path(directory) / "crossing.csv"
            cp.write_text(
                "field_T,temperature_K,heat_capacity_J_mol_K,source\n"
                "0,1,2,measured\n0,5,2,measured\n"
                "2,1,-1,measured\n2,5,7,measured\n", encoding="utf-8"
            )
            run, rows = self.run_example(cp=cp, magnetic=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            peak = max(rows, key=lambda row: float(row["minus_delta_Srel_J_mol_K"]))
            self.assertAlmostEqual(float(peak["temperature_K"]), 2.5, places=12)
            self.assertEqual(float(rows[0]["Srel_field_J_mol_K"]), 0.0)
            self.assertAlmostEqual(float(peak["minus_delta_Srel_J_mol_K"]),
                                   5 * math.log(2.5) - 3, places=12)


if __name__ == "__main__":
    unittest.main()
