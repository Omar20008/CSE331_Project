"""
run_all_real.py
CSE331 - Project 09

Runs the whole real-documents experiment in order, with the same scripts for every approach:
  1) redact with v1, v2, v3, v4
  2) metadata-only baseline (strip_metadata.py)
  3) evaluate residual disclosure: original, v1, v2, v3, v4, meta
  4) detection quality (precision / recall per entity) for every detector version
  5) adversarial re-identification attack (anonymity-set / linkage) on every approach

Usage (from the project folder):
    python run_all_real.py
"""

import subprocess
import sys

STEPS = [
    ["redact_real_docs.py", "v1"],
    ["redact_real_docs.py", "v2"],
    ["redact_real_docs.py", "v3"],
    ["redact_real_docs.py", "v4"],
    ["strip_metadata.py"],
    ["evaluate_real_docs.py", "original"],
    ["evaluate_real_docs.py", "v1"],
    ["evaluate_real_docs.py", "v2"],
    ["evaluate_real_docs.py", "v3"],
    ["evaluate_real_docs.py", "v4"],
    ["evaluate_real_docs.py", "meta"],
    ["detection_quality.py"],
    ["attack_real_docs.py", "original"],
    ["attack_real_docs.py", "meta"],
    ["attack_real_docs.py", "v1"],
    ["attack_real_docs.py", "v2"],
    ["attack_real_docs.py", "v3"],
    ["attack_real_docs.py", "v4"],
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
    print("\nAll steps finished.")
    print("  Residual disclosure : evaluation_real_<version>.txt + failed_cases_real_<version>.csv")
    print("  Detection quality   : detection_quality.txt")
    print("  Re-identification   : attack_report_<version>.txt + attack_findings_<version>.csv")


if __name__ == "__main__":
    main()