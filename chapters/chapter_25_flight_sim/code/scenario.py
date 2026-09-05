"""A scenario runner that records enough to reproduce and to argue with."""

from dataclasses import dataclass, field

from chapters.chapter_20_model_document.code.document import ModelDocument
from chapters.chapter_22_runtime.code.runtime import Result, RunSettings, Runtime


@dataclass(frozen=True)
class Constraint:
    """A bound the scenario is not permitted to violate, checked after the run."""

    variable: str
    low: float | None = None
    high: float | None = None

    def breaches(self, series: list[float]) -> list[str]:
        out = []
        if self.low is not None and min(series) < self.low:
            out.append(f"{self.variable} fell to {min(series):.4g}, below {self.low}")
        if self.high is not None and max(series) > self.high:
            out.append(f"{self.variable} reached {max(series):.4g}, above {self.high}")
        return out


@dataclass
class ScenarioRecord:
    """Everything needed to replay a scenario and to check what was claimed about it."""

    label: str
    model_hash: str
    overrides: dict[str, float]
    settings: RunSettings
    outputs: dict[str, float]
    breaches: list[str] = field(default_factory=list)


class ScenarioRunner:
    """Runs named scenarios against one model and logs each one."""

    def __init__(self, document: ModelDocument, constraints: list[Constraint] | None = None):
        self.document = document
        self.constraints = constraints or []
        self.log: list[ScenarioRecord] = []

    def run(self, label: str, overrides: dict[str, float] | None = None,
            settings: RunSettings | None = None, report: tuple[str, ...] = ()) -> ScenarioRecord:
        overrides = overrides or {}
        settings = settings or RunSettings()
        document = self._with_overrides(overrides)
        result: Result = Runtime(document, settings).run()
        breaches = [
            message
            for constraint in self.constraints
            if constraint.variable in result.series
            for message in constraint.breaches(result.series[constraint.variable])
        ]
        record = ScenarioRecord(
            label=label,
            model_hash=result.model_hash,
            overrides=dict(overrides),
            settings=settings,
            outputs={name: result.final(name) for name in report if name in result.series},
            breaches=breaches,
        )
        self.log.append(record)
        return record

    def _with_overrides(self, overrides: dict[str, float]) -> ModelDocument:
        known = {v.id for v in self.document.variables}
        unknown = set(overrides) - known
        if unknown:
            raise ValueError(f"cannot override variables that do not exist: {sorted(unknown)}")
        variables = []
        for v in self.document.variables:
            if v.id in overrides:
                if v.kind not in ("parameter", "stock"):
                    raise ValueError(f"'{v.id}' is a {v.kind} and cannot be set by a scenario")
                variables.append(type(v)(**{**v.__dict__, "value": overrides[v.id]}))
            else:
                variables.append(v)
        return type(self.document)(
            name=self.document.name, version=self.document.version, variables=variables,
            horizon=self.document.horizon, horizon_unit=self.document.horizon_unit,
            time_step=self.document.time_step,
        )

    def compare(self, name: str) -> dict[str, float]:
        """The named output across every scenario run so far."""
        return {r.label: r.outputs[name] for r in self.log if name in r.outputs}


def supported_by_record(statement_variables: set[str], record: ScenarioRecord) -> list[str]:
    """Which variables in a proposed narrative the replay record cannot support."""
    available = set(record.outputs) | set(record.overrides)
    return sorted(statement_variables - available)
