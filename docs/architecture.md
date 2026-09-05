# Architecture

The repository is a general systems-modeling platform with a vendor-neutral Python engine.

A universal `ProblemContract` defines the decision, authority, evidence, constraints, behavior over
time, and success criteria. A capability pack provides the modeling language. The first pack is
stock-flow. Future packs may support discrete-event, agent-based, hybrid, and policy-search work.

Tools are small, typed, and case-policy controlled. Skills orchestrate tools but cannot approve
artifacts or execute external actions. Every tool response reports status, summary, next actions,
and artifact paths. Failed tools also return a root-cause hint, safe retry, and explicit stop
condition. The registry validates typed requests, rejects unknown or unauthorized tool IDs, and
limits tool-directed writes to the active case policy roots.

## Two ways to use the repository

The repository has two complementary code surfaces.

`chapters/` contains the book-facing atomic code packs. Each chapter can have multiple small Python
files, with one primary operation per file. Readers can import those functions directly and assemble
them into an application without using the AI tool runner. Chapter-specific composition examples
are kept separate from the atomic operations.

`src/stai/tools/unique/` contains the canonical implementation of every AI-visible tool. The
catalog points to each implementation file through `implementation_path`. The registry adds typed
request validation, case-policy checks, and safe write-path handling around those functions.

The tool layer is therefore an optional composition surface. It does not hide or replace the
individual Python functions that the book teaches.
