"""CLI entry point for running the multi-agent content pipeline."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from pipeline import ContentPipeline


def load_env_file(env_path: Path = Path(".env")) -> None:
    """Loads simple KEY=VALUE pairs from a local .env file."""
    if not env_path.exists() or not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    """Creates the CLI parser."""
    parser = argparse.ArgumentParser(description="Run the multi-agent content pipeline.")
    parser.add_argument("topic", help="Topic used to generate the article")
    parser.add_argument(
        "--destination",
        default="markdown",
        choices=["markdown", "wordpress", "gdocs"],
        help="Publication destination",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where markdown output is written",
    )
    return parser


def main() -> int:
    """Runs the pipeline from CLI arguments."""
    load_env_file()

    parser = build_parser()
    args = parser.parse_args()

    pipeline = ContentPipeline(output_dir=args.output_dir)
    result = pipeline.run(topic=args.topic, destination=args.destination)

    print("\nPipeline completed successfully.")
    print(f"Topic: {result.topic}")
    print(f"Output file: {result.output_path}")
    print(f"Created at (UTC): {result.created_at.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
