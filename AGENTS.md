# Repository agent rules

1. Read the applicable skill before changing a case or model.
2. Use only tool IDs allowed by the active case tool policy.
3. Write tool-produced artifacts only beneath the active case policy roots; keep candidate model and
   case changes in proposed state until a human approves promotion.
4. Run relevant tests before reporting success.
5. Do not execute external actions.
6. Preserve teaching-reconstruction labels and evidence status.
7. Report status, summary, next actions, and artifact paths.
8. Changing a chapter pack's default parameters requires re-running `uv run --group figures pytest tests/figures` and updating the figure generator's asserts and the chapter prose in the same change. A figure that no longer matches its chapter is a defect.
9. Never write an em dash, an en dash, or a double hyphen in prose, docstrings, captions, or comments.
