# Controlled finish code checks

Changed files:

* `examples/reviewed_workflow.py`
* `tests/test_reviewed_workflow.py`
* `chapters/chapter_22_runtime/code/runtime.py` (RunSettings docstring only)
* `docs/controlled-finish-code-checks.md`

The CSV loader is named `build_model()` in this checkout. It now requires exactly
one row each for productive, target, attrition_rate, aggression, and arriving.
Missing, misspelled, duplicate, and unexpected IDs fail before any values or
provenance merge. Review scope is checked before constructing a candidate packet;
an unexpected field returns a rejection instead of raising TypeError.

Balance accounting uses the document's initial productive stock and initial delay
rate multiplied by delay time. Tests use 25 productive people and a starting
arrival rate of 2 people per week, representing 16 trainees. The independent
52-week oracle computes simultaneous Euler updates directly with arithmetic,
without using Runtime or its evaluator to calculate expected results. It checks
both policies' final stocks, peak productive stock, cumulative flows, and cost.

TDD evidence:

* Initial workflow test run: 6 failed, 6 passed. All four malformed CSV cases
  failed to raise; the unexpected field raised TypeError; productive balance
  incorrectly reported 5 people. Existing fixtures and the independent oracle passed.
* Splitting balance assertions into separate cases before implementation exposed
  both failures: productive error 5 and trainee error 16. That focused run had
  2 failed, 11 deselected.
* After implementation: all 13 workflow tests passed, including byte-for-byte
  equality with the existing expected report.
* Related workflow, chapter runtime, and runtime tests: 47 passed in 0.34 seconds.
  Command: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider tests/test_reviewed_workflow.py tests/chapters/test_model_runtime.py tests/runtime`
* `git diff --check` passed.

RunSettings documentation now describes document defaults, explicit settings,
and the implementation version as a reproduction bundle. No runtime behavior,
model defaults, fixture values, manuscript files, or figure PDFs were changed.
No commits, pushes, or tag operations were performed. The full suite remains for
the main agent, as requested. An unrelated README change appeared during this
task and was left untouched, along with the existing dirty figure PDFs.
