"""Command line interface for Spout."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .core import SpoutDetector, SpoutGenerator
from .generators import GENERATORS
from .models.cli_input import DetectInput, GenerateInput


@click.group()
@click.version_option()
def main():
    """Spout - Generate TypeScript clients from Python web frameworks."""
    pass


@main.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
    help="Path to the Python project directory",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    default=Path("client.ts"),
    required=False,
    help="Path for the generated TypeScript client file",
)
@click.option(
    "--client-type",
    "-c",
    type=click.Choice(list(GENERATORS.keys())),
    default="fetch",
    help="Type of TypeScript client to generate",
)
@click.option("--base-url", "-b", default=None, help="Base URL for API calls")
@click.option(
    "--no-types", is_flag=True, help="Do not include TypeScript type definitions"
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def generate(
    input_path: Path,
    output_path: Path,
    client_type: str,
    base_url: Optional[str],
    no_types: bool,
    config: Optional[Path],
    verbose: bool,
):
    """Generate TypeScript client from Python web framework."""

    # Load configuration if provided
    config_data = {}
    if config:
        try:
            with open(config, "r") as f:
                config_data = json.load(f)
            if verbose:
                click.echo(f"Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            sys.exit(1)

    final_config = GenerateInput(
        project_path=str(input_path),
        output_path=str(output_path),
        client_type=client_type,
        base_url=base_url,
        include_types=not no_types,
        config=config_data,
    )
    if verbose:
        click.echo("Final configuration:")
        for key, value in final_config.dict().items():
            click.echo(f"  {key}: {value}")

    # Initialize generator
    try:
        generator = SpoutGenerator(final_config)
    except Exception as e:
        click.echo(f"Error initializing generator: {e}", err=True)
        sys.exit(1)
    client_code = generator.generate_client()

    # Generate client
    if verbose:
        click.echo(f"Generating {final_config.client_type} client...")

    # Write output
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(client_code, encoding="utf-8")
        click.echo(f"✅ TypeScript client generated successfully: {output_path}")
    except Exception as e:
        click.echo(f"Error writing output file: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
    help="Path to the Python project directory",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def detect(input_path: Path, verbose: bool):
    """Detect web framework in a Python project."""

    config = DetectInput(project_path=str(input_path), verbose=verbose)

    detector = SpoutDetector(config)
    try:
        framework_info = detector.framework_info
    except Exception as e:
        click.echo(f"Error during detection: {e}", err=True)
        sys.exit(1)

    if framework_info:
        click.echo(f"✅ Framework detected: {framework_info.name}")
        click.echo(f"   Confidence: {framework_info.confidence:.2f}")
        click.echo(f"   Files: {len(framework_info.detected_files)}")

        if framework_info.detected_files:
            click.echo("   Detected in:")
            for file_path in framework_info.detected_files[:5]:  # Show first 5
                click.echo(f"     - {file_path}")
            if len(framework_info.detected_files) > 5:
                click.echo(
                    f"     ... and {len(framework_info.detected_files) - 5} more"
                )
    else:
        click.echo("❌ No supported framework detected")
        click.echo("Supported frameworks: FastAPI, Django Ninja")
        sys.exit(1)


@main.command()
def list_generators():
    """List available TypeScript client generators."""

    click.echo("Available TypeScript client generators:")
    for name, generator_class in GENERATORS.items():
        click.echo(f"  - {name}: {generator_class.__doc__ or 'No description'}")


if __name__ == "__main__":
    main()
