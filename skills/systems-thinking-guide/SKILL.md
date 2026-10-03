---
name: systems-thinking-guide
description: "Route a question about systems thinking, system dynamics modelling, feedback, stocks and flows, delays, calibration or policy comparison to the right chapter of Systems Thinking with AI by Jason Karpeles, then use that chapter's skill and notebook to answer it with the reader's own numbers."
---

# Systems Thinking with AI: guide

*Systems Thinking with AI* by Jason Karpeles teaches system dynamics as working models: behaviour over time, feedback, stocks and flows, delays and nonlinearity, then the numerical and software discipline that keeps a model honest, then fitting to public records and comparing policies under uncertainty. This repository has one notebook and one skill for each of the 24 chapters with a computed model. Interactive version: https://karpeles.com/companions/systems-thinking-with-ai/

## How to route a question

1. If the reader names a chapter, use that chapter's skill.
2. Otherwise identify what they are stuck on: describing behaviour, choosing a structure, implementing a mechanism, checking a numerical result, fitting a record, or choosing a policy. Match it against the table below and open the chapter skill in `skills/`.
3. A good answer often crosses chapters: structure (Chapters 4, 12, 13), then mechanism (14 to 18), then numerical checks (19), then fitting and policy (29, 30, 35). Each chapter skill names its handoffs.
4. If no chapter fits, say so. Do not force an unrelated question into the book.

## Chapters

| Chapter | Use it when | Skill | Notebook |
|---|---|---|---|
| 3. Events Are Not Explanations | A trend, spike or curve is being explained by one event; naming the shape (growth, decay, goal seeking, oscillation, S-shape, overshoot) before the cause | `skills/st-03-reference-modes/SKILL.md` | `notebooks/03-reference-modes.ipynb` |
| 4. The Bathtub Most People Misread | A level and its rates are confused; "inflow is falling, so the stock must be falling"; conservation checks on a balance | `skills/st-04-bathtub/SKILL.md` | `notebooks/04-bathtub.ipynb` |
| 5. The Beer Game and the Cost of Local Rationality | Orders swing far more than demand along a supply chain; bullwhip; whether to count goods already ordered | `skills/st-05-beer-game/SKILL.md` | `notebooks/05-beer-game.ipynb` |
| 8. Causal-Loop Diagrams Without Causal Theater | Drawing or auditing a causal loop diagram; link polarity; whether a loop is reinforcing or balancing; evidence for each arrow | `skills/st-08-causal-graph/SKILL.md` | `notebooks/08-causal-graph.ipynb` |
| 9. System Archetypes as Hypothesis Templates | A familiar pattern such as limits to growth, fixes that fail or shifting the burden; whether the limit sits inside or outside the boundary | `skills/st-09-archetypes/SKILL.md` | `notebooks/09-archetypes.ipynb` |
| 12. Stocks, Flows, Sources, and Sinks | Turning a story into stocks, flows, sources and sinks; units and dt; whether a quantity is a stock or an auxiliary | `skills/st-12-stocks-flows/SKILL.md` | `notebooks/12-stocks-flows.ipynb` |
| 13. Auxiliaries, Parameters, and Decision Rules | Writing auxiliaries, parameters and decision rules; how fast a rule closes a gap; safe expression evaluation | `skills/st-13-expressions/SKILL.md` | `notebooks/13-expressions.ipynb` |
| 14. Feedback and Loop Dominance | Which feedback loop is in charge, and when that changes; loop knockouts and dominance | `skills/st-14-dominance/SKILL.md` | `notebooks/14-dominance.ipynb` |
| 15. Nonlinearity and Lookup Functions | A nonlinear response, saturation, threshold or congestion curve; lookup tables and their domain | `skills/st-15-lookups/SKILL.md` | `notebooks/15-lookups.ipynb` |
| 16. Material and Information Delays | Delays: pipeline versus first-order, material versus information, delay order and the delay inside a feedback loop | `skills/st-16-delays/SKILL.md` | `notebooks/16-delays.ipynb` |
| 17. Cohorts, Aging Chains, and Coflows | Headcount versus capability; aging chains and cohorts; experience leaving with people; hiring surges that dilute | `skills/st-17-cohorts/SKILL.md` | `notebooks/17-cohorts.ipynb` |
| 18. Events, Queues, Agents, and Hybrid Models | Joining an aggregate model to a queue or agent model; how often the two exchange numbers; the seam as part of the model | `skills/st-18-hybrid/SKILL.md` | `notebooks/18-hybrid.ipynb` |
| 19. Numerical Integration Is Part of the Model | Numerical integration: Euler versus RK4, step size, a simulated overshoot that may be a solver artifact | `skills/st-19-integration/SKILL.md` | `notebooks/19-integration.ipynb` |
| 25. Turn Models into Management Flight Simulators | Management flight simulators and scenario comparison; why an average of scenarios is not a scenario | `skills/st-25-flight-sim/SKILL.md` | `notebooks/25-flight-sim.ipynb` |
| 29. The AI as Experiment Designer | Which uncertain input matters most; one-at-a-time swings; what to measure next and at what cost | `skills/st-29-experiments/SKILL.md` | `notebooks/29-experiments.ipynb` |
| 30. The AI as Policy Searcher | Choosing among policies under uncertainty with hard limits; excluded options; worst case versus average | `skills/st-30-policy-search/SKILL.md` | `notebooks/30-policy-search.ipynb` |
| 32. Growth Can Destroy the Engine of Growth | Growth that erodes service quality and drives churn; hiring that lags demand; intake throttles | `skills/st-32-service-growth/SKILL.md` | `notebooks/32-service-growth.ipynb` |
| 33. Technical Debt as a Stock | Technical debt as a stock; repayment versus pushing features; rework share and review horizons | `skills/st-33-technical-debt/SKILL.md` | `notebooks/33-technical-debt.ipynb` |
| 34. Hybrid Case: Hospital Capacity and Patient Flow | Hospital or service queues: staffing rules, priority rules, waits by patient group and equity | `skills/st-34-hospital-hybrid/SKILL.md` | `notebooks/34-hospital-hybrid.ipynb` |
| 35. Fitting Is Not Confirming | Calibrating a model to a record; how many parameters a short record supports; holdout tests; fit is not confirmation | `skills/st-35-calibration/SKILL.md` | `notebooks/35-calibration.ipynb` |
| 36. Elective Backlogs as a Stock | Elective waiting lists and backlogs from public records; recovery dates; why a fitted model can fail its holdout | `skills/st-36-elective-backlog/SKILL.md` | `notebooks/36-elective-backlog.ipynb` |
| 37. Hiring Is a Pipeline, Not a Number | Hiring as a pipeline from vacancies to capable staff; ramp-up time; headcount targets versus capability | `skills/st-37-hiring-pipeline/SKILL.md` | `notebooks/37-hiring-pipeline.ipynb` |
| 38. Capacity Arrives When the Price Has Gone | Investment cycles, capacity arriving after the price has gone; construction and perception delays; period versus date | `skills/st-38-capacity-cycle/SKILL.md` | `notebooks/38-capacity-cycle.ipynb` |
| 39. Delay Is a Curve, Not a Line | Delay that rises as a curve with load, airport or network congestion; caps and what they cost in lost movements | `skills/st-39-congestion-curve/SKILL.md` | `notebooks/39-congestion-curve.ipynb` |

The book's other chapters (the policy and factory cases that open it, the decision contract, boundaries and evidence, the model document, compiler, runtime, registry and interchange formats, the AI interview, compiler and critic roles, the model repository and the capstone) are covered in the book itself; their methods appear here only where a notebook chapter uses them.

## Working with the reader's own case

- Ask what decision the model is for, and for the units, time base, initial values and horizon. Do not fill gaps with the chapter's example numbers without saying so.
- Keep constructed teaching examples separate from the reader's data, and say which is which.
- Run the chapter notebook (Run All), then call its functions with the reader's values in a new cell. Reproduce one of the chapter's reference numbers first, so a wrong setup shows up before it matters.
- State what each check establishes. A balance that closes shows the accounting is complete; a smaller step that agrees shows the solver is adequate; a holdout that passes shows the fit carries to new data. None of them proves the causal story or authorises a policy.
- Answer the question first, then give the chapters used, the assumptions that carry the conclusion, the calculation and its check, and the next observation that would change the answer.

Copyright Jason Karpeles. All rights reserved.
