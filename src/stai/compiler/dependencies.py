import ast

from .expressions import validate_expression


class DependencyCycleError(ValueError):
    """Raised when an expression graph cannot be evaluated in dependency order."""


def expression_dependencies(expression: str) -> set[str]:
    tree = validate_expression(expression)
    return {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id not in {"abs", "max", "min"}
    }


def topological_order(
    dependencies: dict[str, set[str]],
    known_inputs: set[str],
) -> list[str]:
    pending = {name: set(values) for name, values in dependencies.items()}
    resolved = set(known_inputs)
    order: list[str] = []

    while pending:
        ready = sorted(name for name, values in pending.items() if values.issubset(resolved))
        if not ready:
            unresolved = ", ".join(sorted(pending))
            raise DependencyCycleError(
                f"Dependency cycle or unknown dependency among: {unresolved}."
            )
        for name in ready:
            order.append(name)
            resolved.add(name)
            del pending[name]
    return order
