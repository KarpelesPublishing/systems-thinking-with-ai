---
name: st-08-causal-graph
description: "Audit a causal-loop diagram for link polarity, closed loops, evidence status, delays, and falsifiers, while distinguishing a diagram hypothesis from causal validation. Runs the chapter's model on the user's own inputs with notebooks/08-causal-graph.ipynb."
---

# Chapter 8: Causal-Loop Diagrams Without Causal Theater

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/08-causal-graph.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/08-causal-graph/reader.html.

## Method

Take the named variables, directed links, polarity claims, horizon, and source record. Define each sign ceteris paribus: more of the source changes the target relative to what it otherwise would have been. Count negative links around the whole loop; even means reinforcing and odd means balancing. Neither label determines the time path without strength and delay.

Build a link record with evidence level, locator or source sentence, delay estimate, falsifier, and owner. A missing delay is unknown, not instantaneous. Mark extracted additions as proposed until reviewed. Check that every supposed loop closes with actual links and that rotations have not been counted as different loops.

Use the chapter code audit to locate assumed or proposed links and missing time semantics. Its Link fields do not implement the full evidence record; keep source, strength, falsifier, owner, and detailed delay alongside it. A low unsupported count does not validate the labels or detect all omitted links.

For an audit, remove a weak link and state which loops cease to close, then compare conclusions, outcome levels, and feasibility where a runnable model exists. An unchanged ranking alone does not establish that the arrow is irrelevant. Return the diagram's hypotheses and a measurement plan, not causal acceptance.

Handoffs: Chapter 9 for rival archetypes, Chapter 11 for claim provenance, Chapter 14 for loop dominance, Chapter 21 for dependencies extracted from expressions.

## Apply it to the user's inputs

1. Open `notebooks/08-causal-graph.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Link`: One causal claim: source, target, sign, how it is known, and whether it is delayed.
- `simple_cycles(outgoing: dict[str, list[str]] | dict[str, set[str]])`: Every simple cycle in a directed graph, each reported once from its lowest node.
- `find_loops(links: list[Link])`: Enumerate every simple feedback loop, each reported once from its lowest node.
- `loop_polarity(loop: list[str], links: list[Link])`: Reinforcing when the loop holds an even number of negative links, balancing otherwise.
- `unsupported_links(links: list[Link])`: Links resting on assumption or proposal rather than observation or inference.
- `links_without_time_semantics(links: list[Link])`: Links where nobody recorded whether the effect is immediate or delayed.
- `audit(links: list[Link])`: Summarize what the diagram is resting on.

Demonstrations in the notebook, with the chapter's settings:

1. Two negative links make a reinforcing loop: `two_link_loop(overtime_to_morale=-1, morale_to_overtime=-1)`. Settings offered: `overtime_to_morale` in [-1, 1]; `morale_to_overtime` in [-1, 1].
2. An audit counts what the picture rests on: `audit_picture(evidence_inventory_to_shipments='assumed', evidence_shipments_to_inventory='proposed', time_record='unrecorded')`. Settings offered: `evidence_inventory_to_shipments` in ['assumed', 'observed']; `evidence_shipments_to_inventory` in ['proposed', 'inferred']; `time_record` in ['unrecorded', 'recorded'].
3. One more arrow closes loops nobody counted: `extra_arrow(extra='shipments to backlog', polarity=1)`. Settings offered: `extra` in ['shipments to backlog', 'inventory to backlog', 'production to shipments']; `polarity` in [1, -1].
4. Remove the weakest arrow: `remove_arrow(removed='none', flip='negative')`. Settings offered: `removed` in ['none', 'inventory to shipments', 'shipments to inventory']; `flip` in ['negative', 'positive'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Overtime to morale opposite direction (-); Morale to overtime opposite direction (-); Negative links in the loop 2; Loop polarity reinforcing
- Demonstration 2: Links 6; Loops 3; Reinforcing 0; Balancing 3; Unsupported 2; No time semantics 2
- Demonstration 3: Extra arrow shipments to backlog (+); Loops before 3; Loops after 4; New loops 1; Reinforcing 1; Balancing 3
- Demonstration 4: Arrow removed none; Links 6; Loops 3; Reinforcing 0; Balancing 3; Unsupported 2; No time semantics 2

Copyright Jason Karpeles. All rights reserved.
