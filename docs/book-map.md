# Book map

## FM1: Reader contract

- Repository artifact: README.md
- Governance artifacts: AGENTS.md and CLAUDE.md
- Reader outcome: AI proposes and humans approve.

## FM2: How to use the book, skills, and companion repository

- Repository artifact: docs/architecture.md
- Tool registry: tooling/catalog.yaml
- Skill registry: skills/
- Reader outcome: run a model, inspect a tool policy, and understand the review boundary.

## Chapter 2: The Factory Cycle That Was Not the Business Cycle

- Atomic code pack: `chapters/chapter_02_factory_cycle/`
- Atomic code index: `chapters/chapter_02_factory_cycle/code/README.md`
- Unique tool directory: `src/stai/tools/unique/`
- Tool source index: `src/stai/tools/README.md`
- Model: models/factory-cycle.yaml
- Case contract: cases/factory-cycle/problem-contract.yaml
- Experiment: cases/factory-cycle/experiments/baseline.yaml
- Policy proposal: cases/factory-cycle/policy-proposal.yaml
- Tool policy: cases/factory-cycle/tool-policy.yaml
- Skills: modeling-interview, model-compiler, model-critic
- Tests: tests/integration/test_factory_cycle.py and tests/tools/test_verification.py
- Additional tests: tests/chapters/test_factory_cycle_atoms.py and
  tests/tools/test_unique_tool_surface.py
- Reader outcome: inspect individual stock-flow functions, assemble them into a direct simulation,
  distinguish a teaching reconstruction from an empirical forecast, and replay a stock-and-flow
  simulation through the optional tool surface.

## Chapter 1: A Policy That Made Things Worse

- No pack. The numbers come from `chapters/chapter_34_hospital_hybrid/` and are pinned in
  tests/chapters/test_case_models.py.
- Reader outcome: see a reasonable policy fail for a structural reason before any notation exists.

## Chapter 35: Fitting Is Not Confirming

- Atomic code pack: `chapters/chapter_35_calibration/`
- Atomic code index: `chapters/chapter_35_calibration/code/README.md`
- Tests: tests/chapters/test_calibration.py and tests/chapters/test_calibration_chapter.py
- Reader outcome: fit a document to a record with a grid, mark the result inferred, and report a
  holdout as a separate number.

## Chapters 36 to 39: the fitted cases

| Chapter | Pack | Record | Tests |
| --- | --- | --- | --- |
| 36 Elective Backlogs as a Stock | `chapters/chapter_36_elective_backlog/` | `data/nhs_rtt/` | tests/chapters/test_case_elective_backlog.py |
| 37 Hiring Is a Pipeline, Not a Number | `chapters/chapter_37_hiring_pipeline/` | `data/bls_jolts/` | tests/chapters/test_case_hiring_pipeline.py |
| 38 Capacity Arrives When the Price Has Gone | `chapters/chapter_38_capacity_cycle/` | `data/fred_capacity/` | tests/chapters/test_case_capacity_cycle.py |
| 39 Delay Is a Curve, Not a Line | `chapters/chapter_39_congestion_curve/` | `data/bts_ontime/` | tests/chapters/test_case_congestion_curve.py |

- Each pack exposes `record()`, `document()`, `knobs()`, `targets()`, `fit()`, and
  `fitted_document()`, and every number its chapter prints is pinned by
  `test_chapter_NN_prints_the_numbers_this_run_produces`.
- Figures for every chapter: `build/figures/`, tested by tests/figures.
- Reader outcome: refit a book model to a public record and read what the fit can and cannot claim.
