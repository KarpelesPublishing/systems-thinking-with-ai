---
name: st-05-beer-game
description: "Explain or audit Beer Game order amplification, complete outstanding-order accounting, and station-level service tradeoffs when the supply line enters the ordering rule. Runs the chapter's model on the user's own inputs with notebooks/05-beer-game.ipynb."
---

# Chapter 5: The Beer Game and the Cost of Local Rationality

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/05-beer-game.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/05-beer-game/reader.html.

## Method

Fix the demand history, initial chain, order and shipment delays, smoothing time, adjustment time, and policy target. Define outstanding supply as orders in transit plus supplier backlog plus shipments in transit. Do not drop an order when it reaches the supplier but remains unfilled. The factory's external source is unlimited in this teaching model.

Explain each station's information and the simultaneous weekly update. Compare a chain-wide policy change on the same demand history before interpreting a single station's outcome. Measure order swing, inventory, and backlog at all four stations. Flat demand has zero customer swing, so an amplification ratio is undefined rather than a useful stability statistic.

Counting the supply line changes the target's effective meaning to inventory position. In the published experiment the target stays twelve and adds no desired pipeline allowance. That makes orders smoother while retailer peak backlog worsens. Do not convert an order-variance improvement into a service recommendation. A separate target experiment needs its own service and cost measures.

Report the horizon's recording convention: stock rows are starting states, with the last row before the fiftieth update. Mark outputs as teaching-model results, not evidence of human-player behavior or a particular real supply chain.

Handoffs: Chapter 4 for accumulation, Chapter 13 for perception and decision rules, Chapter 16 for delay structures, Chapter 30 for constrained policy comparisons.

## Apply it to the user's inputs

1. Open `notebooks/05-beer-game.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `swing(series: list[float])`: Peak-to-trough range of a series.
- `amplification_ratio(customer_orders: list[float], stage_orders: list[float])`: Return the stage's order swing divided by the customer's.
- `stage_variability(history: dict[str, list[list[float]]])`: Standard deviation of each stage's order stream, retailer first.
- `class Stage`: One link in the chain: what it holds, what it owes, and what is in transit to it.
- `class ChainParameters`: One policy, applied identically at every stage.
- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `smooth_demand(expected: float, observed: float, smoothing_time: float)`: Update a stage's belief about demand by closing part of the gap to what it just saw.
- `order_quantity(expected_demand: float, inventory: float, backlog: float, supply_line: float, target_inventory: float, inventory_adjustment_time: float, supply_line_weight: float=0.0)`: Replace expected demand, correct the inventory gap, and discount the supply line.
- `ship(stage: Stage, requested: float)`: Ship what is asked for, or everything on hand. What is missed becomes backlog.
- `step_chain(stages: list[Stage], customer_order: float, parameters: ChainParameters)`: Advance every stage by one week and return the new state plus the orders placed.
- `run_chain(customer_demand: list[float], parameters: ChainParameters | None=None)`: Run the chain over a demand history and return every stage's weekly record.

Demonstrations in the notebook, with the chapter's settings:

1. One station's order, with and without the supply line: `ordering_rule(supply_line_weight=0.0, inventory_adjustment_time=4.0)`. Settings offered: `supply_line_weight` in [0.0, 0.5, 1.0]; `inventory_adjustment_time` in [1.0, 4.0].
2. Expected demand lags a step in orders: `smoothing(smoothing_time=4.0, observed=8.0)`. Settings offered: `smoothing_time` in [1.0, 2.0, 4.0, 8.0]; `observed` in [8.0, 12.0].
3. A four-case step grows at every station upstream: `chain_amplification(pipeline_weeks=2)`. Settings offered: `pipeline_weeks` in [1, 2, 3, 4].
4. The supply-line fix lands three stations away: `supply_line_fix(supply_line_weight=1.0, inventory_adjustment_time=4.0)`. Settings offered: `supply_line_weight` in [0.0, 0.5, 1.0]; `inventory_adjustment_time` in [4.0, 1.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Effective stock (cases) 2.0; Gap (cases) 10.0; Order before the floor (cases) 10.5; Order placed (cases) 10.5
- Demonstration 2: Smoothing time (weeks) 4; Expected demand after week 1 5.00; Expected demand after week 4 6.73; Expected demand after week 20 7.99; First week within 1 case of the orders seen 5
- Demonstration 3: Weeks of delay each way 2; Retailer order swing (x customer) 6.2; Wholesaler order swing (x customer) 17.5; Distributor order swing (x customer) 36.8; Factory order swing (x customer) 52.9; Factory peak order (cases) 212
- Demonstration 4: Supply line weight 1.0; Inventory adjustment time (weeks) 4; Retailer swing, ignored then chosen 6.2 then 2.1; Factory swing, ignored then chosen 52.9 then 2.7; Factory peak order (cases) 11

Copyright Jason Karpeles. All rights reserved.
