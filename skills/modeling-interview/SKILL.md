---
name: modeling-interview
description: Use when a systems problem needs a reviewable dynamic-problem contract and evidence inventory before a model is built.
---

# Modeling interview

1. Ask for the decision, owner, stakeholders, horizon, reference behavior, variables and units,
   capability packs, evidence, constraints, prohibited objectives, authority boundary, success
   criteria, and review requirements.
2. Create a proposed `ProblemContract`; never treat missing information as verified evidence.
3. Use `problem.validate` and `evidence.validate` only when the active case policy permits them.
4. Preserve teaching-reconstruction labels and mark evidence or authority gaps explicitly.
5. Return the proposed artifact plus each `ToolResponse` status, summary, next actions, and paths.
6. Do not approve a contract, make a policy decision, or execute an external action.
