# Example models

Three models built the way the book asks a reader to build them: from the chapter
packs, connected through a model document, with no application in the middle.

| Model | What it exercises | The finding |
| --- | --- | --- |
| `hiring_pipeline.py` | Chapter 16's delay as a document kind | A delay inside a balancing loop overshoots: target 40, peak 47.5 |
| `support_desk.py` | Chapter 15's lookup as a document kind | Effectiveness below one means nominal parity with demand is not enough |
| `subscription_growth.py` | Both kinds together | Growth erodes the quality that referral depends on |

Each is a function returning a `ModelDocument`. Nothing else is required to run one:

```python
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from examples.hiring_pipeline import hiring_pipeline

result = Runtime(hiring_pipeline(), RunSettings("euler", dt=1.0, horizon=52)).run()
```

## What building them found

Writing these models is the first time the packs were used the way a reader uses
them, and it surfaced four defects that reading could not.

**A lookup refused an input at machine epsilon.** A stock landing on zero arrives
a few epsilons below it, and the domain check rejected `-8.9e-17`. Refusing that
is refusing arithmetic rather than refusing extrapolation. `Lookup` now snaps an
input within a hair of an end to that end and still refuses a real excursion.

**Policy search died on one infeasible draw.** A model that refuses to run under a
draw took the whole comparison with it, losing twenty-four good draws to one bad
one. A refusal is now recorded as a constraint violation, which is what it is: the
policy is not viable in that world.

**Final backlog is a degenerate decision metric.** A desk with enough staff clears
to zero under every draw, so the number stops discriminating between policies.
`ticket_weeks` accumulates the waiting instead, which is what people feel and what
a sensitivity ranking can move.

**A missing floor is invisible until it is not.** Without `min(capacity, open +
arrivals)` the desk closes more tickets than it holds, the stock goes negative,
and the lookup stops the run. The runtime named the time and the variable, and the
fix belonged in the model rather than in the code.

## The refusals are the product

Two of the three models stop rather than answer, under some settings, and that is
the designed behaviour. The support desk refuses when load leaves the range anyone
measured. Extending the curve past the evidence is possible and the variable is
marked `assumed` when you do it, so the run and its provenance disagree loudly
rather than quietly.
