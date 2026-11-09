"""
Shared pytest fixtures for the redaction test-suite.

These fixtures load the REAL project code (no re-implementation):
  * `redactor`     -> the redact_real_docs module, configured for the recommended v4
                      detector exactly as `python redact_real_docs.py v4` configures it
                      (document-consistent scrub ON, locale-aware/bilingual recognizers ON).
  * `evaluator`    -> evaluate_real_docs, whose extract()/classify() are the same functions
                      that produce evaluation_*.txt / failed_cases_*.csv.
  * `detector_v4`  -> pipelines.make_detector("v4")  (the recommended detector)
  * `detector_v1`  -> pipelines.make_detector("v1")  (Presidio defaults; English-only NER)

redact_real_docs reads its version from sys.argv AT IMPORT TIME and creates an output
directory in the current working directory, so the `redactor` fixture imports it with a
controlled argv while chdir'd into a throwaway temp dir, then restores both. This is why the
suite can drive the production pipeline without copying any of its logic.
"""

import os
import sys

import pytest

# Make the project root importable regardless of where pytest is launched from.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def redactor(tmp_path_factory):
    """The real redact_real_docs pipeline, configured for v4 (the recommended detector)."""
    saved_argv = sys.argv
    saved_cwd = os.getcwd()
    sys.argv = ["redact_real_docs.py", "v4"]
    os.chdir(tmp_path_factory.mktemp("rr_import"))  # absorb the import-time makedirs()
    try:
        import redact_real_docs as rr
        import evaluate_real_docs as ev  # noqa: F401  (import under a clean argv too)
    finally:
        sys.argv = saved_argv
        os.chdir(saved_cwd)
    # Sanity: v4 means document-consistent scrubbing is on.
    assert rr.CONSISTENT is True, "redactor fixture must be configured for v4"
    return rr


@pytest.fixture(scope="session")
def evaluator():
    """evaluate_real_docs: the same extract()/classify() used to score every approach."""
    import evaluate_real_docs as ev
    return ev


@pytest.fixture(scope="session")
def detector_v4():
    from pipelines import make_detector
    return make_detector("v4")


@pytest.fixture(scope="session")
def detector_v1():
    from pipelines import make_detector
    return make_detector("v1")
