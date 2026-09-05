# Reviewed offline hiring workflow

From the repository root, run exactly:

```sh
uv run python -m examples.reviewed_workflow
```

The command prints the deterministic JSON in [expected_report.json](expected_report.json).
It does not save files, call an AI service, require an API key, or deploy anything.
The Python environment must already be provisioned for offline use: uv may otherwise
need a first-time dependency download. The workflow itself uses only local files
and the existing chapter APIs.

This practical technical edition assumes Python literacy. It is a teaching
reconstruction, not evidence about a real employer. No real organization data is
included. The workflow does not call a live AI service. Its proposal is an authored
teaching fixture, not a captured response from a separate live experiment.

## Follow the review

1. Inspect [synthetic_inputs.csv](synthetic_inputs.csv). Only initial headcount is
   labeled synthetic fixture evidence. The target, attrition, response and empty
   training pipeline are assumptions. Eight weeks is an assumed mean training
   delay inherited from the hiring example, not a measured duration.
2. Read [prompt.txt](prompt.txt), the exact illustrative AI prompt. It is supplied
   for inspection, not sent anywhere. [proposals.json](proposals.json) contains
   an authored illustrative AI response and a human-authored correction. Neither
   is historical live AI output. The deliberately flawed response violates the
   prompt: 0.8/week exceeds the bound and its observed label has no support.
3. `build_model()` reuses the existing hiring structure and replaces its fictional
   source labels with the CSV values using structured `Variable` data. `_proposal`
   wraps each fixture as an `Edit` in a `Patch` against this source's hash.
4. Inspect each `review_packet` in the report. Both proposals pass structural
   validation. `applied: true` means a candidate could be constructed for review,
   not that the source changed or any action was approved. The diff identifies
   aggression; the exact values and evidence fields are in proposals.json.
5. The illustrative human review rejects the flawed proposal and authorizes
   simulation of the corrected 0.10/week candidate. The example-specific review
   checks scope, finite bounds and proposed evidence. It replays a teaching
   decision, not a real person's signature. The repository's generic patch API
   accepts explicit evidence overrides, so this review does not rely on that API
   to prevent unsupported promotion. Simulation leaves the correction proposed.
6. `apply_patch` produces a new document. `Runtime` runs the baseline and corrected
   documents with explicit `RunSettings`: Euler, dt=1 week, horizon=52 weeks,
   seed=0. A patch against the old hash cannot be reused on the candidate.

## Results and costs

| Quantity | Baseline 0.25/week | Corrected 0.10/week |
| :--- | ---: | ---: |
| Productive people at week 52 | 38.673280 | 36.421090 |
| Peak productive people | 47.655969 | 38.648394 |
| Trainees at week 52 | 0.495275 | 2.317715 |
| Cumulative recruited people | 40.102811 | 35.944368 |
| Cumulative joining people | 39.607536 | 33.626653 |
| Cumulative departures | 20.934255 | 17.205563 |
| Assumed recruiting cost, USD | 40102.810840 | 35944.368370 |

Rates are summed at times 0 through 51 and multiplied by dt. Time 52 is an
endpoint, not an extra recruiting interval. The productive balance is
`20 + cumulative joining - cumulative departures`. The trainee balance is
`0 + cumulative recruiting - cumulative joining`. Both residuals print as zero
after rounding to six decimals. Tests check the unrounded identities as well.
Cost uses unrounded recruited people times the assumed USD 1000/person.
Multiplying rounded report values can differ slightly in the last decimals.

There are zero API calls and zero API charges. Local compute and review labor
are not priced. Recruiting cost excludes wages, training and vacancy costs.
The correction reduces overshoot and this partial cost, but also leaves fewer
productive people at week 52. This is a tradeoff, not an established best policy.

## Debrief and exercises with answers

1. Why does a structurally valid proposal get rejected? Answer: structural
   validation cannot establish evidence provenance or enforce this lesson's
   parameter bounds. The flawed proposal fails both review checks.
2. Does simulation approval make 0.10/week observed? Answer: no. It remains
   proposed even after a successful run. New real evidence would need separate
   collection and review; no such collection is authorized here.
3. Calculate week 1 and week 2 productive stocks. Answer: week 1 is 19.8 for
   both policies because the pipeline starts empty. Week 2 is 20.227 for the
   baseline and 19.852 for the correction. Initial recruiting is 5 versus 2
   people/week; the next week's arriving rates are 0.625 versus 0.25.
4. Why does a lower response help overshoot? Answer: recruiting responds to
   today's productive gap while previous recruits remain in training. Slower
   response commits fewer additional recruits before those already in training
   arrive. It can also slow closure of the gap.
5. Can these results approve a real hiring change? Answer: no. Both decisions
   explicitly deny deployment and external action. There is no external action
   adapter, authentication system or real decision-maker signature in this demo.
6. What happens if you apply the same patch to its candidate? Answer: a stale
   hash error, because the patch names the source model's content hash.

## Limits to carry into Chapter 40

People are continuous quantities. Training is a first-order exponential delay,
not an eight-week fixed cohort delay. The empty initial pipeline, fixed target,
constant attrition and unlimited recruiting are assumptions. Selection quality,
fairness, training capacity and labor-market feedback are absent. The fixture
is not a longitudinal dataset and provides no empirical calibration or validation.
No uncertainty, sensitivity or numerical convergence study is performed.
The explicit Euler step divides this horizon exactly; these reported totals are
specific to those settings. A seed is recorded but this model is not stochastic.
The document validator does not prove dimensional consistency or empirical truth;
no units-checker guarantee is claimed. Partial cost is not net benefit.
Hashes identify model content, not the prompt, fixture files or reviewer identity.
The local review function is a teaching rule, not a security boundary.
