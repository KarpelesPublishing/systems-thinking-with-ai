# Systems Thinking with AI

*Build, test, and interrogate dynamic models with human judgment*

Public companion repository published by Karpeles Publishing.

Companion code for Python-literate analysts studying dynamic models and bounded AI review.
The examples are teaching reconstructions, not validated operational decision systems.
The supplied workflow has no deployment adapter or live AI-service dependency.

## Setup

Requires Python 3.11 or newer and `uv`. See the
[official uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
Run commands from the extracted repository root, beside `pyproject.toml` and `uv.lock`.
For book edition 0.1.2, [download the matching ZIP](https://github.com/KarpelesPublishing/systems-thinking-with-ai/archive/refs/tags/v0.1.2.zip).
The book QR code points to the `v0.1.2` snapshot, not the changing default branch.
A code license has not yet been selected. Public availability does not grant an open-source
license or additional permission to redistribute or reuse the code. Third-party data retain
their respective source terms; see their attribution files.

```sh
uv sync --locked
uv run python -m examples.reviewed_workflow
uv run pytest tests/test_reviewed_workflow.py
uv run python scripts/fetch_data.py --verify
```

To include all figure tests, use `uv sync --locked --group figures`, then
`uv run --group figures pytest`. The default setup can skip figure tests.
The six derived CSV files are included; raw downloads are not needed for offline tests.
See [data sources and checksums](data/README.md).

## Start with the complete review workflow

The first-run command prints deterministic JSON. It uses synthetic inputs and an authored
illustrative proposal, not a captured live AI response. A recorded review refuses the flawed
proposal and permits simulation of the corrected candidate. Neither authorizes external action.

The baseline ends with 38.673280 productive people; the corrected candidate ends with 36.421090.
The slower response reduces overshoot but leaves a larger final shortfall. This is a tradeoff,
not an established best hiring policy. See the [full walkthrough and worked answers](examples/workflow/README.md)
and [expected JSON report](examples/workflow/expected_report.json).

No API key is needed. Initial dependency installation may use the network; the replay does not.
If `examples` cannot be imported, check that the terminal is in the repository root and that
the companion copy contains `examples/reviewed_workflow.py`. A checksum failure means the data
do not match the recorded vintage; compare with a fresh edition copy before refetching.

See [example models](examples/README.md) for the three worked examples.
These are teaching models, not validated operational decision systems.

## Snapshot scope

Includes current chapter packs, shared runtime, examples, tests, derived data,
source attribution, and figure generators with their outputs. It excludes the
manuscript, book PDF and EPUB, raw downloads, local environments and caches,
old Git history, and the manuscript-only figure-reference checker.
Chapter 40 includes this small executable replay and a separate, larger service-operation design.
The latter is not a shipped application or a report of a deployment. See the
[release policy](docs/release-policy.md). Companion availability does not certify the book's publication readiness.

Safety boundary: AI proposes and a human approves.

## Read the code in three layers

The book is organized around small, reusable code rather than one hidden application.

- `chapters/` contains the atomic code packs that follow the manuscript chapter by chapter.
- `src/stai/tools/unique/` contains one implementation module for every AI-visible tool.
- `src/stai/` contains the shared contracts, compiler, runtime, provenance, and registry used by
  those surfaces.

For the first case, begin with
`chapters/chapter_02_factory_cycle/code/README.md`. You can import the functions directly, assemble
them in your own program, or invoke the same capabilities through the registry.

## Private release gate

Run these checks before creating or updating a public companion snapshot:

```bash
uv sync --locked --group figures
uv run --group figures ruff check .
uv run --group figures pytest
uv run python scripts/validate_skills.py
uv run python scripts/fetch_data.py --verify
```

A release is blocked by a failed test, invalid skill package, unsupported empirical claim, missing
provenance, unauthorized tool call, or any capability that attempts external execution.
