# Reviewed workflow implementation checks

This is the internal verification record for the offline teaching workflow.

Tests were added before implementation. The first attempt placed the missing
module assertion in a pytest fixture, producing five setup errors. Moving that
assertion into a helper called from each test produced the intended RED result:
`5 failed`, each with `The offline reviewed workflow has not been implemented`.
After implementation: `1 failed, 4 passed`, with the remaining failure identifying
the missing recorded report. The captured CLI output was then added as the
expected report. The GREEN run passed all 76 tests across
tests/test_reviewed_workflow.py, tests/test_examples.py,
tests/chapters/test_model_document.py, tests/chapters/test_model_runtime.py and
tests/chapters/test_agent_packs.py. Ruff checks passed for both new Python files.

The five acceptance tests cover deterministic replay and exact CLI output,
source immutability, stale hashes, evidence preservation, bounded scope,
actual use of the corrected parameter, numeric steps and stock balances,
partial costs and denial of external authority. The expected report is a
regression snapshot; independent arithmetic checks provide additional evidence.

Implementation paths are examples/reviewed_workflow.py,
tests/test_reviewed_workflow.py and examples/workflow/ containing
synthetic_inputs.csv, proposals.json, prompt.txt, expected_report.json and README.md.
The documentation cleanup additionally creates this file. No chapter pack defaults
were changed. No commits or pushes are part of this task. Main coordinates final
verification and Chapter 40 prose using the recorded values and limitations.

The reader README now distinguishes AI-assisted authorship from runtime service
calls: the workflow does not call a live AI service, and its proposal is an
authored teaching fixture rather than a captured separate live experiment.
The documentation cleanup does not change implementation, fixtures or numbers.
