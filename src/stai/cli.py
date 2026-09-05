import argparse
from pathlib import Path

from yaml import YAMLError

from stai.contracts.common import ToolResponse
from stai.tools.model import compile_model_file, validate_model_file
from stai.tools.registry import error_response
from stai.tools.simulation import run_simulation
from stai.tools.verification import run_verification


def print_response(response: ToolResponse) -> int:
    print(response.model_dump_json(indent=2))
    return 0 if response.status.value != "error" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stai")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate-model")
    validate.add_argument("model_path", type=Path)

    compile_command = commands.add_parser("compile-model")
    compile_command.add_argument("model_path", type=Path)

    simulate_command = commands.add_parser("simulate")
    simulate_command.add_argument("model_path", type=Path)
    simulate_command.add_argument("experiment_path", type=Path)
    simulate_command.add_argument("output_path", type=Path)

    verify = commands.add_parser("verify")
    verify.add_argument("model_path", type=Path)
    verify.add_argument("experiment_path", type=Path)
    verify.add_argument("output_path", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-model":
            return print_response(validate_model_file(args.model_path))
        if args.command == "compile-model":
            return print_response(compile_model_file(args.model_path))
        if args.command == "simulate":
            return print_response(
                run_simulation(args.model_path, args.experiment_path, args.output_path)
            )
        return print_response(
            run_verification(args.model_path, args.experiment_path, args.output_path)
        )
    except (OSError, SyntaxError, ValueError, YAMLError) as error:
        return print_response(
            error_response(
                root_cause=f"Command failed: {type(error).__name__}: {error}",
                safe_retry="Correct the referenced path or artifact and rerun the command.",
                stop_condition="Do not use this command result until the input artifact is valid.",
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())
