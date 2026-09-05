---
name: model-compiler
description: Use when an accepted systems problem needs a proposed declarative model patch with explicit stocks, flows, units, and experiment.
---

# Model compiler

1. Read the accepted problem contract, active case policy, and applicable capability pack.
2. Propose stocks, auxiliaries, flows, units, expressions, and an experiment; do not infer an
   unsupported modeling language.
3. Use `model.validate` and `model.compile` only when the active case policy permits them.
4. Report every unresolved unit, evidence, capability, or structural question.
5. Save only a proposed patch until a human approves it.
6. Do not alter an approved model or execute an external action.
