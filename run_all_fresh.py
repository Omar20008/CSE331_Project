"""
run_all_fresh.py
CSE331 - Project 09

Runs the WHOLE experiment on the FRESH hold-out set (documents_fresh/), using the EXACT
same scripts and the EXACT same v1..v4 detectors as the real set -- only the `fresh`
dataset argument differs. pipelines.py is never touched, so this measures how the unchanged
detectors generalise to 20 people (and five new address locales) they have never seen.

Order (mirrors run_all_real.py):
  1) generate the fresh documents + ground_truth_fresh.json
  2) redact with v1, v2, v3, v4            -> redacted_fresh_v1..v4/
  3) evaluate residual disclosure: original, v1, v2, v3, v4
  4) detection quality (precision / recall per entity) for every detector version
  5) adversarial re-identification attack on original + v1..v4

Separate evidence files are written (evaluation_fresh_*.txt, detection_quality_fresh.txt,
attack_report_fresh_*.txt, ...). The real-set outputs are NOT touched.

The metadata-only baseline (strip_metadata.py) is intentionally skipped here: the brief asks
for the v1..v4 comparison, and strip_metadata.py targets the real set only.

Usage (from the project folder):
    python run_all_fresh.py
"""

import subprocess
import sys

STEPS = [
    ["generate_fresh_docs.py"],
    ["redact_real_docs.py", "v1", "fresh"],
    ["redact_real_docs.py", "v2", "fresh"],
    ["redact_real_docs.py", "v3", "fresh"],
    ["redact_real_docs.py", "v4", "fresh"],
    ["evaluate_real_docs.py", "original", "fresh"],
    ["evaluate_real_docs.py", "v1", "fresh"],
    ["evaluate_real_docs.py", "v2", "fresh"],
    ["evaluate_real_docs.py", "v3", "fresh"],
    ["evaluate_real_docs.py", "v4", "fresh"],
    ["detection_quality.py", "fresh"],
    ["attack_real_docs.py", "original", "fresh"],
    ["attack_real_docs.py", "v1", "fresh"],
    ["attack_real_docs.py", "v2", "fresh"],
    ["attack_real_docs.py", "v3", "fresh"],
    ["attack_real_docs.py", "v4", "fresh"],
]


def main():
    for step in STEPS:
        title = "python " + " ".join(step)
        print("\n" + "#" * 70)
        print(f"# {title}")
        print("#" * 70, flush=True)
        result = subprocess.run([sys.executable] + step)
        if result.returncode != 0:
            print(f"\nSTOPPED: '{title}' failed (exit code {result.returncode}).")
            sys.exit(result.returncode)
    print("\nAll FRESH steps finished.")
    print("  Residual disclosure : evaluation_fresh_<version>.txt + failed_cases_fresh_<version>.csv")
    print("  Detection quality   : detection_quality_fresh.txt")
    print("  Re-identification   : attack_report_fresh_<version>.txt + attack_findings_fresh_<version>.csv")


if __name__ == "__main__":
    main()
