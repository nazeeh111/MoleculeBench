"""Command-line entry point."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from .engine import Config, run
from .report import write_report


MAX_CONFIG_BYTES = 16 * 1024


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate configuration field: {key}")
        result[key] = value
    return result


def load_config(path):
    with path.open("rb") as handle:
        encoded = handle.read(MAX_CONFIG_BYTES + 1)
    if len(encoded) > MAX_CONFIG_BYTES:
        raise ValueError("configuration exceeds the 16 KiB size limit")
    try:
        return json.loads(encoded.decode("utf-8"), object_pairs_hook=_unique_fields)
    except RecursionError as error:
        raise ValueError("configuration nesting is too deep") from error


def main():
    parser = argparse.ArgumentParser(description="Compute a validated H2 molecular report locally.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("config", help="print the default JSON configuration")
    command = sub.add_parser("run", help="compute results into a new output directory")
    command.add_argument("--config", type=Path)
    command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "config":
        print(json.dumps(asdict(Config()), indent=2))
        return 0
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("output already exists; choose a new directory")
        raw = load_config(args.config) if args.config else {}
        if not isinstance(raw, dict):
            raise ValueError("configuration must be a JSON object")
        config = Config(**raw)
        data = run(config)
        destination = write_report(data, args.output)
        print(json.dumps({"output": str(destination.resolve()), "all_converged": True,
                          "seconds": data["provenance"]["elapsed_seconds"]}))
        return 0
    except (ValueError, TypeError, OSError, RuntimeError) as error:
        print(f"MoleculeBench: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
