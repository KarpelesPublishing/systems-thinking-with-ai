# Systems Thinking with AI

This is a private development repository.

Its first release is a general systems-modeling factory teaching reconstruction.
It cannot execute external actions.

## Setup

Requires Python 3.11 or newer and `uv`. Run commands from the repository root.
This private snapshot is not the final reader release. Public download access and
the book QR code are not available yet. A code license has not yet been selected.

```sh
uv sync --locked
uv run pytest
uv run ruff check .
```

To include all figure tests, use `uv sync --locked --group figures`, then
`uv run --group figures pytest`. The default setup can skip figure tests.
The six derived CSV files are included; raw downloads are not needed for offline tests.
See [data sources and checksums](data/README.md).

## Run an example

From the repository root:

```sh
uv run python -c 'from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime; from examples.hiring_pipeline import hiring_pipeline; print(Runtime(hiring_pipeline(), RunSettings("euler", dt=1.0, horizon=52)).run())'
```

See [example models](examples/README.md) for the three worked examples.
These are teaching models, not validated operational decision systems.

## Snapshot scope

Includes current chapter packs, shared runtime, examples, tests, derived data,
source attribution, and figure generators with their outputs. It excludes the
manuscript, book PDF and EPUB, raw downloads, local environments and caches,
old Git history, and the manuscript-only figure-reference checker.
The original working repository is unchanged. Chapter 40's capstone is a teaching
design, not an executable pack. Public release remains subject to the
[release policy](docs/release-policy.md), license selection, and book review fixes.

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

Run these checks before creating or updating the private GitHub repository:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/validate_skills.py
```

A release is blocked by a failed test, invalid skill package, unsupported empirical claim, missing
provenance, unauthorized tool call, or any capability that attempts external execution.
