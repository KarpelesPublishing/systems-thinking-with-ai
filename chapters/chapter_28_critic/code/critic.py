"""Tests a critic can generate from a model contract, and run."""

from dataclasses import dataclass

from chapters.chapter_12_stocks_flows.code.system import SINK, SOURCE, Flow, System
from chapters.chapter_20_model_document.code.document import ModelDocument
from chapters.chapter_21_compiler.code.compiler import algebraic_loops, edges
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime

CATEGORIES = ("structural", "dimensional", "extreme", "regression")


@dataclass(frozen=True)
class Finding:
    """One defect, with the category that says which kind of check found it."""

    category: str
    variable: str
    message: str

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")


def as_system(document: ModelDocument) -> System:
    """The document as Chapter 12's stock-and-flow system.

    Chapter 12 states its structural rules against its own objects, and a model
    document is a different shape, so the rules could not reach a document until
    something translated one into the other. A flow with sign +1 comes from a
    source outside the model; one with sign -1 goes to a sink outside it.
    """
    stocks = {v.id: float(v.value) for v in document.variables if v.kind == "stock"}
    flows = []
    for variable in document.variables:
        if variable.kind != "flow" or not variable.target:
            continue
        origin = SOURCE if variable.sign == 1 else variable.target
        destination = variable.target if variable.sign == 1 else SINK
        flows.append(Flow(variable.id, origin, destination, variable.unit))
    return System(stocks=stocks, flows=flows)


def conservation_findings(document: ModelDocument) -> list[Finding]:
    """Chapter 12's structural rules, applied to a document through `as_system`.

    This is the missing-sink family: a stock that can only grow, or only shrink.
    The schema cannot catch these, because each variable is individually valid.
    """
    system = as_system(document)
    out = []
    for name in system.unsunk_stocks():
        out.append(Finding("structural", name,
                           "no outflow: it can only grow, which is right only for a "
                           "cumulative counter and a defect otherwise"))
    for name in system.unsourced_stocks():
        out.append(Finding("structural", name,
                           "no inflow: it can only shrink, which is right only for a "
                           "depleting reserve and a defect otherwise"))
    return out


def structural_findings(document: ModelDocument) -> list[Finding]:
    """Loops that cannot resolve, and variables nothing reads."""
    out = [
        Finding("structural", " -> ".join(loop), "algebraic loop with no stock in it")
        for loop in algebraic_loops(document)
    ]
    graph = edges(document)
    read_by_something = {name for reads in graph.values() for name in reads}
    targeted = {v.target for v in document.variables if v.kind == "flow" and v.target}
    for variable in document.variables:
        if variable.kind in ("auxiliary", "parameter") and variable.id not in read_by_something:
            out.append(Finding("structural", variable.id, "nothing reads this variable"))
        if variable.kind == "stock" and variable.id not in targeted:
            out.append(Finding("structural", variable.id, "no flow changes this stock"))
    return out


def dimensional_findings(document: ModelDocument) -> list[Finding]:
    """Unit defects a shallow check can reach."""
    out = []
    units = {v.id: v.unit for v in document.variables}
    for variable in document.variables:
        if variable.kind == "flow" and "/" not in variable.unit:
            out.append(Finding("dimensional", variable.id, "a flow's unit needs a time base"))
        if variable.kind == "stock" and "/" in variable.unit:
            out.append(Finding("dimensional", variable.id, "a stock's unit must not be a rate"))
        if variable.kind == "flow" and variable.target:
            stock_unit = units.get(variable.target, "")
            if stock_unit and not variable.unit.startswith(stock_unit + "/"):
                out.append(Finding(
                    "dimensional", variable.id,
                    f"unit '{variable.unit}' does not match '{stock_unit}' per time",
                ))
    return out


def extreme_condition_findings(
    document: ModelDocument, stock: str, floor: float = 0.0
) -> list[Finding]:
    """Run the model from an extreme start and see whether it behaves impossibly."""
    out = []
    for label, value in (("empty", floor), ("very large", 1e6)):
        probe = ModelDocument(
            name=document.name, version=document.version, horizon=document.horizon,
            horizon_unit=document.horizon_unit, time_step=document.time_step,
            variables=[
                type(v)(**{**v.__dict__, "value": value}) if v.id == stock else v
                for v in document.variables
            ],
        )
        try:
            result = Runtime(probe, RunSettings("euler", 1.0, 10.0)).run()
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            out.append(Finding("extreme", stock, f"from {label}: {type(exc).__name__}: {exc}"))
            continue
        series = result.series[stock]
        if min(series) < floor - 1e-9:
            out.append(Finding("extreme", stock, f"from {label}: fell to {min(series):.4g}"))
    return out


def regression_findings(
    document: ModelDocument, baseline: dict[str, float], tolerance: float = 1e-6
) -> list[Finding]:
    """Compare named outputs against recorded values from an accepted run."""
    result = Runtime(document, RunSettings("euler", 1.0, float(document.horizon))).run()
    return [
        Finding("regression", name,
                f"expected {expected:.6g}, got {result.final(name):.6g}")
        for name, expected in baseline.items()
        if name in result.series and abs(result.final(name) - expected) > tolerance
    ]


def defect_report(findings: list[Finding]) -> dict[str, list[str]]:
    """Group findings by category so a human can dispose of them in batches."""
    report: dict[str, list[str]] = {c: [] for c in CATEGORIES}
    for finding in findings:
        report[finding.category].append(f"{finding.variable}: {finding.message}")
    return {k: v for k, v in report.items() if v}
