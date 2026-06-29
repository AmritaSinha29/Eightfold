"""Command-line interface entry point.

Run the pipeline from the command line:

    python -m src.cli INPUT [INPUT ...] [OPTIONS]

Examples:
    # Default schema, print to stdout
    python -m src.cli sample_inputs/recruiter.csv sample_inputs/notes.txt

    # Custom config, write to file
    python -m src.cli sample_inputs/recruiter.csv \\
        --config configs/example_custom_config.json \\
        --output sample_outputs/custom_output.json

    # Include a GitHub profile
    python -m src.cli sample_inputs/recruiter.csv https://github.com/octocat
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from src.pipeline import Pipeline

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("inputs", nargs=-1, required=True, metavar="INPUT...")
@click.option(
    "--config",
    "-c",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Runtime output config JSON. Uses default schema if omitted.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(dir_okay=False),
    help="Write JSON to this file instead of stdout.",
)
@click.option(
    "--pretty/--compact",
    default=True,
    show_default=True,
    help="Pretty-print output JSON (default) or compact single-line.",
)
@click.option(
    "--ats-field-map",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="JSON file mapping ATS field names to canonical names.",
)
@click.option(
    "--github-token",
    default=None,
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token (or set GITHUB_TOKEN env var).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose logging (INFO level).",
)
def main(
    inputs: tuple[str, ...],
    config: Optional[str],
    output: Optional[str],
    pretty: bool,
    ats_field_map: Optional[str],
    github_token: Optional[str],
    verbose: bool,
) -> None:
    """Multi-Source Candidate Data Transformer.

    Accepts one or more INPUT paths (CSV, JSON, PDF, DOCX, TXT) or
    GitHub profile URLs and emits a canonical candidate profile as JSON.
    """
    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    # TODO: If ats_field_map: ATSJsonAdapter.load_field_map(ats_field_map) → pass to adapter
    # TODO: pipeline = Pipeline(github_token=github_token)
    # TODO: results = pipeline.run(list(inputs), config_path=config)
    # TODO: Serialize: json.dumps(results, indent=2 if pretty else None, default=str)
    # TODO: Write to output file or click.echo to stdout
    # TODO: On ValueError (config/validation errors): click.echo to stderr, sys.exit(1)

    pipeline = Pipeline(github_token=github_token)

    try:
        results = pipeline.run(list(inputs), config_path=config)
    except NotImplementedError:
        click.echo(
            "Pipeline not yet implemented — run after completing the TODOs.",
            err=True,
        )
        sys.exit(0)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Unexpected error: {exc}", err=True)
        sys.exit(1)

    indent = 2 if pretty else None
    json_str = json.dumps(results, indent=indent, default=str)

    if output:
        Path(output).write_text(json_str, encoding="utf-8")
        click.echo(f"Output written to {output}", err=True)
    else:
        click.echo(json_str)


if __name__ == "__main__":
    main()
