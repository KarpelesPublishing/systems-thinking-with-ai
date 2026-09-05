import ast
import math
from collections.abc import Mapping
from typing import Any


class ExpressionError(ValueError):
    """Raised when a model expression is unsafe or cannot be evaluated safely."""


_ALLOWED_FUNCTIONS = {"abs": abs, "max": max, "min": min}
MAX_EXPRESSION_LENGTH = 512
MAX_EXPRESSION_NODES = 128
MAX_EXPRESSION_DEPTH = 24
MAX_ABSOLUTE_EXPONENT = 100.0
_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Call,
)


def _require_finite_number(value: Any, *, label: str) -> float:
    if type(value) not in (int, float):
        raise ExpressionError(f"{label} must be a finite numeric value.")
    try:
        numeric_value = float(value)
    except OverflowError as error:
        raise ExpressionError(f"{label} must be a finite numeric value.") from error
    if not math.isfinite(numeric_value):
        raise ExpressionError(f"{label} must be a finite numeric value.")
    return numeric_value


def _tree_depth(node: ast.AST) -> int:
    children = list(ast.iter_child_nodes(node))
    return 1 + max((_tree_depth(child) for child in children), default=0)


def validate_expression(
    expression: str,
    *,
    allowed_names: set[str] | None = None,
) -> ast.Expression:
    """Parse and constrain a model expression without evaluating it."""
    if not isinstance(expression, str) or not expression.strip():
        raise ExpressionError("Expression must be a non-empty string.")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ExpressionError("Expression exceeds the maximum permitted length.")
    if allowed_names is not None:
        reserved_names = sorted(set(allowed_names) & set(_ALLOWED_FUNCTIONS))
        if reserved_names:
            raise ExpressionError(
                "Input names cannot use reserved expression functions: "
                f"{', '.join(reserved_names)}."
            )
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ExpressionError(f"Invalid expression: {error.msg}.") from error
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_EXPRESSION_NODES or _tree_depth(tree) > MAX_EXPRESSION_DEPTH:
        raise ExpressionError("Expression exceeds the permitted structural complexity.")
    call_function_nodes = {
        id(node.func)
        for node in nodes
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    for node in nodes:
        if not isinstance(node, _ALLOWED_NODES):
            raise ExpressionError(f"Unsupported expression node: {type(node).__name__}.")
        if isinstance(node, ast.Constant):
            _require_finite_number(node.value, label="Expression constant")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCTIONS:
                raise ExpressionError("Only abs, max, and min calls are permitted.")
            if node.keywords:
                raise ExpressionError("Keyword arguments are not permitted in model expressions.")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            if isinstance(node.right, ast.Constant):
                exponent = _require_finite_number(node.right.value, label="Expression exponent")
                if abs(exponent) > MAX_ABSOLUTE_EXPONENT:
                    raise ExpressionError("Expression exponent exceeds the permitted bound.")
        if isinstance(node, ast.Name):
            if node.id in _ALLOWED_FUNCTIONS:
                if id(node) not in call_function_nodes:
                    raise ExpressionError(
                        f"Reserved expression function {node.id} may only be called."
                    )
            elif allowed_names is not None and node.id not in allowed_names:
                raise ExpressionError(f"Unknown variable in expression: {node.id}.")
    return tree


def _evaluate_node(node: ast.AST, values: Mapping[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return _require_finite_number(node.value, label="Expression constant")
    if isinstance(node, ast.Name):
        if node.id not in values:
            raise ExpressionError(f"Unknown variable in expression: {node.id}.")
        return values[node.id]
    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_node(node.operand, values)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand
    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left, values)
        right = _evaluate_node(node.right, values)
        try:
            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                result = left / right
            elif isinstance(node.op, ast.Pow):
                if abs(right) > MAX_ABSOLUTE_EXPONENT:
                    raise ExpressionError("Expression exponent exceeds the permitted bound.")
                result = left**right
            else:
                raise ExpressionError("Unsupported binary operator.")
        except (ArithmeticError, OverflowError, ValueError) as error:
            raise ExpressionError(f"Expression evaluation failed: {error}.") from error
        return _require_finite_number(result, label="Expression result")
    if isinstance(node, ast.Call):
        assert isinstance(node.func, ast.Name)
        arguments = [_evaluate_node(argument, values) for argument in node.args]
        try:
            result = _ALLOWED_FUNCTIONS[node.func.id](*arguments)
        except (ArithmeticError, TypeError, ValueError) as error:
            raise ExpressionError(f"Expression evaluation failed: {error}.") from error
        return _require_finite_number(result, label="Expression result")
    raise ExpressionError(f"Unsupported expression node: {type(node).__name__}.")


def evaluate_expression(expression: str, values: Mapping[str, float]) -> float:
    """Evaluate a deliberately small arithmetic expression language."""
    safe_values = {
        name: _require_finite_number(value, label=f"Input {name}")
        for name, value in values.items()
    }
    tree = validate_expression(expression, allowed_names=set(safe_values))
    assert isinstance(tree.body, ast.AST)
    return _evaluate_node(tree.body, safe_values)
