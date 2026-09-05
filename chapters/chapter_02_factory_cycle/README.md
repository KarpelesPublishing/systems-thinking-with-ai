# Chapter 2 code pack

This folder is the Chapter 2 teaching surface for the factory-cycle reconstruction. The code is
split into small functions so a reader can inspect one equation, import it directly, or assemble a
different application from the same parts.

The functions are deliberately not a recovered General Electric model. They implement the checked-in
teaching model in `models/factory-cycle.yaml`:

- stocks: `inventory` and `work_in_process`;
- auxiliaries: `desired_inventory` and `inventory_gap`;
- flows: `start_production`, `complete_production`, and `ship_orders`.

Start with [`code/README.md`](code/README.md), then open the individual Python files. The separate
[`advance_factory_cycle.py`](code/advance_factory_cycle.py) file demonstrates composition, while
[`run_factory_cycle.py`](code/run_factory_cycle.py) demonstrates a small direct simulation without
the AI tool registry.
