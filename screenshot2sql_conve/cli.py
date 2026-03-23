"""CLI entry point for screenshot2sql."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

from . import __version__

console = Console()
err_console = Console(stderr=True)

VALID_FORMATS = (
    "sql", "json", "mermaid", "sqlalchemy",
    "prisma", "typescript", "markdown", "csv",
    "all",
)


def _print_banner() -> None:
    """Print the Rich startup banner with project name, version, and attribution."""
    banner = (
        f"[bold cyan]Screenshot2SQL[/bold cyan]  [dim]v{__version__}[/dim]\n"
        "[dim]Convert UI screenshots to production-ready SQL schemas[/dim]\n"
        "[dim]Built autonomously by [link=https://heyneo.so]NEO[/link] · https://heyneo.so[/dim]"
    )
    console.print(Panel(banner, border_style="cyan", padding=(0, 2)))


def _success(msg: str) -> None:
    """Print a green success message to stderr."""
    err_console.print(f"[green]✓[/green] {msg}")


def _warn(msg: str) -> None:
    """Print a yellow warning message to stderr."""
    err_console.print(f"[yellow]⚠[/yellow]  {msg}")


def _error(msg: str) -> None:
    """Print a red error message to stderr."""
    err_console.print(f"[red]✗[/red] {msg}")


def _info(msg: str) -> None:
    """Print a dim informational message to stderr."""
    err_console.print(f"[dim]{msg}[/dim]")


def _print_stats_table(stats: dict) -> None:
    """Render a Rich table summarising the analysis stats."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key", style="bold")
    table.add_column("Value")

    table.add_row("UI type", stats["ui_type"])
    table.add_row("Confidence", f"{stats['confidence']:.0%}")
    table.add_row("Tables", str(stats["table_count"]))
    table.add_row("Columns", str(stats["total_columns"]))
    table.add_row("Foreign keys", str(stats["fk_count"]))
    table.add_row("Sample queries", str(stats["query_count"]))
    if stats.get("model"):
        table.add_row("Model", stats["model"])
    if stats.get("is_mock"):
        table.add_row("Mode", "[yellow]demo/mock[/yellow]")

    err_console.print(table)


def _print_entities_table(entities: list) -> None:
    """Render a Rich table listing the detected entities and their column counts."""
    table = Table(title="Detected tables", box=box.ROUNDED, border_style="cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Table", style="bold")
    table.add_column("Columns", justify="right")
    table.add_column("Description", style="dim")

    for i, entity in enumerate(entities, 1):
        col_count = len(entity.get("fields", []))
        desc = entity.get("description", "")
        table.add_row(str(i), entity["name"], str(col_count), desc)

    err_console.print(table)


def _print_batch_results(results: list) -> None:
    """Render a Rich table with the batch processing summary."""
    table = Table(title="Batch results", box=box.ROUNDED, border_style="cyan")
    table.add_column("File", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("UI type")
    table.add_column("Tables", justify="right")
    table.add_column("Confidence", justify="right")

    for r in results:
        status = r["status"]
        if status == "ok":
            status_cell = "[green]ok[/green]"
        elif status == "skipped":
            status_cell = "[yellow]skipped[/yellow]"
        else:
            status_cell = "[red]error[/red]"

        table.add_row(
            r["file"],
            status_cell,
            r.get("ui_type", "—"),
            str(r["tables"]) if "tables" in r else "—",
            f"{r['confidence']:.0%}" if "confidence" in r else "—",
        )

    console.print(table)


def main() -> None:
    """Main CLI entry point for screenshot2sql."""
    parser = argparse.ArgumentParser(
        prog="screenshot2sql",
        description="Convert UI screenshots to SQL schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output formats:
  sql          CREATE TABLE DDL + sample queries (default)
  json         Raw analysis result as JSON
  mermaid      Mermaid erDiagram notation for ER diagrams
  sqlalchemy   SQLAlchemy 2.x ORM model code (Python)
  prisma       Prisma schema (schema.prisma)
  typescript   TypeScript interfaces (.ts)
  markdown     Markdown data dictionary (docs-friendly)
  csv          CSV data dictionary (spreadsheet-friendly)
  all          Write all formats to --output-dir

Examples:
  screenshot2sql screen.png
  screenshot2sql screen.png --format mermaid
  screenshot2sql screen.png --format prisma --output schema.prisma
  screenshot2sql screen.png --format markdown --output data_dict.md
  screenshot2sql screen.png --indexes
  screenshot2sql screen.png --format all --output-dir ./out
  screenshot2sql screen.png --compare screen2.png
  screenshot2sql --batch ./screenshots/ --output-dir ./schemas/
  screenshot2sql --demo
""",
    )
    parser.add_argument(
        "image",
        nargs="?",
        help="Path to screenshot image file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"screenshot2sql {__version__}",
        help="Print version and exit",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Launch the Streamlit demo app",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout). Use with single-format output.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for output files (used with --format all or --batch)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=VALID_FORMATS,
        default=os.getenv("OUTPUT_FORMAT", "sql"),
        help="Output format (default: sql, or $OUTPUT_FORMAT env var)",
    )
    parser.add_argument(
        "--db",
        help="Create a SQLite .db file at this path",
    )
    parser.add_argument(
        "--hint",
        help="Text hint to improve detection in demo/mock mode",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force demo/mock mode even if API key is set",
    )
    parser.add_argument(
        "--compare",
        metavar="IMAGE2",
        help="Second screenshot to compare schemas (outputs a diff report)",
    )
    parser.add_argument(
        "--batch",
        metavar="DIR",
        help="Analyze all images in a directory",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=None,
        help="Max API retries on transient errors (default: $MAX_RETRIES or 3)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Claude model ID (default: $CLAUDE_MODEL or claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--indexes",
        action="store_true",
        default=os.getenv("SHOW_INDEXES", "").lower() in ("1", "true", "yes"),
        help="Append index recommendations to SQL output (or $SHOW_INDEXES=true)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=float(os.getenv("CONFIDENCE_THRESHOLD", "0.0")),
        metavar="THRESHOLD",
        help=(
            "Minimum confidence (0.0–1.0) required to proceed. "
            "Warn if below threshold, error if below half threshold. "
            "(default: 0.0, or $CONFIDENCE_THRESHOLD)"
        ),
    )
    args = parser.parse_args()

    if args.demo:
        _print_banner()
        app_path = Path(__file__).parent / "app.py"
        _info("Launching Screenshot2SQL Streamlit app...")
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            check=False,
        )
        return

    # ── Batch mode ──────────────────────────────────────────────────────────
    if args.batch:
        _print_banner()
        _run_batch(args)
        return

    if not args.image:
        _print_banner()
        parser.print_help()
        sys.exit(1)

    _print_banner()

    # ── Single-image mode ────────────────────────────────────────────────────
    from .analyzer import ScreenshotAnalyzer
    from .schema import SchemaGenerator
    from .exporter import MermaidExporter, SQLAlchemyExporter
    from .index_advisor import IndexAdvisor
    from .data_dict import DataDictExporter
    from .prisma_exporter import PrismaExporter

    analyzer = ScreenshotAnalyzer(
        mock_mode=args.mock if args.mock else None,
        max_retries=args.retries,
        model=args.model,
    )
    generator = SchemaGenerator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=err_console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Analyzing [cyan]{args.image}[/cyan]...", total=None)
        analysis = analyzer.analyze(image_path=args.image, hint=args.hint)
        progress.update(task, completed=True)

    if not analysis.get("is_ui", False):
        _error(analysis.get("error", "No UI detected"))
        sys.exit(1)

    stats = generator.get_stats(analysis)

    # ── Confidence threshold check ───────────────────────────────────────────
    confidence = stats["confidence"]
    threshold = args.confidence
    if threshold > 0.0:
        if confidence < threshold / 2:
            _error(
                f"Confidence {confidence:.0%} is far below threshold {threshold:.0%}. "
                "The image may not be a recognizable UI. Use --confidence 0 to bypass."
            )
            sys.exit(1)
        elif confidence < threshold:
            _warn(
                f"Confidence {confidence:.0%} is below threshold {threshold:.0%}. "
                "Results may be inaccurate."
            )

    _success(f"Detected [bold]{stats['ui_type']}[/bold]")
    _print_stats_table(stats)
    _print_entities_table(analysis.get("entities", []))

    # ── Schema comparison / diff ─────────────────────────────────────────────
    if args.compare:
        _run_compare(args, analysis, analyzer, generator)
        return

    # ── Format output ────────────────────────────────────────────────────────
    try:
        if args.format == "all":
            _write_all_formats(args, analysis, generator)
        else:
            output = _format_analysis(
                args.format, analysis, generator,
                MermaidExporter(), SQLAlchemyExporter(),
                DataDictExporter(), PrismaExporter(),
            )

            # Append index recommendations to SQL output when --indexes is set
            if args.indexes and args.format == "sql":
                advisor = IndexAdvisor()
                recs = advisor.recommend(analysis)
                output = output.rstrip("\n") + "\n\n" + advisor.format_sql(recs)
                _info(f"Index recommendations: {len(recs)} index(es) appended")

            if args.output:
                Path(args.output).write_text(output)
                _success(f"Output written to [cyan]{args.output}[/cyan]")
            else:
                print(output)
    except ValueError as exc:
        _error(f"Error generating output: {exc}")
        sys.exit(1)

    # ── Standalone index recommendations ─────────────────────────────────────
    if args.indexes and args.format != "sql":
        advisor = IndexAdvisor()
        recs = advisor.recommend(analysis)
        _info(f"\nIndex recommendations ({len(recs)}):")
        for r in recs:
            err_console.print(f"  [dim]{r.describe()}[/dim]")

    if args.db:
        db_path = generator.generate_sqlite_db(analysis, db_path=args.db)
        _success(f"SQLite database created at [cyan]{db_path}[/cyan]")


def _format_analysis(
    fmt: str, analysis: dict, generator,
    mermaid_exp, sqlalchemy_exp,
    data_dict_exp=None, prisma_exp=None,
) -> str:
    """Convert an analysis result to the requested output format string."""
    if fmt == "sql":
        return generator.format_full_output(analysis)
    if fmt == "json":
        return generator.format_json_output(analysis)
    if fmt == "mermaid":
        return mermaid_exp.generate(analysis)
    if fmt == "sqlalchemy":
        return sqlalchemy_exp.generate(analysis)
    if fmt == "prisma":
        if prisma_exp is None:
            from .prisma_exporter import PrismaExporter
            prisma_exp = PrismaExporter()
        return prisma_exp.generate_prisma(analysis)
    if fmt == "typescript":
        if prisma_exp is None:
            from .prisma_exporter import PrismaExporter
            prisma_exp = PrismaExporter()
        return prisma_exp.generate_typescript(analysis)
    if fmt == "markdown":
        if data_dict_exp is None:
            from .data_dict import DataDictExporter
            data_dict_exp = DataDictExporter()
        return data_dict_exp.generate_markdown(analysis)
    if fmt == "csv":
        if data_dict_exp is None:
            from .data_dict import DataDictExporter
            data_dict_exp = DataDictExporter()
        return data_dict_exp.generate_csv(analysis)
    raise ValueError(f"Unknown format: {fmt}")


def _write_all_formats(args, analysis: dict, generator) -> None:
    """Write all output formats to --output-dir."""
    from .exporter import MermaidExporter, SQLAlchemyExporter
    from .data_dict import DataDictExporter
    from .prisma_exporter import PrismaExporter
    from .index_advisor import IndexAdvisor

    mermaid_exp = MermaidExporter()
    sqlalchemy_exp = SQLAlchemyExporter()
    data_dict_exp = DataDictExporter()
    prisma_exp = PrismaExporter()

    out_dir = Path(args.output_dir) if args.output_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    ui_slug = analysis.get("ui_type", "schema").lower().replace(" ", "_").replace("/", "_")

    files = {
        "sql":         out_dir / f"{ui_slug}.sql",
        "json":        out_dir / f"{ui_slug}.json",
        "mermaid":     out_dir / f"{ui_slug}.mmd",
        "sqlalchemy":  out_dir / f"{ui_slug}_models.py",
        "prisma":      out_dir / f"{ui_slug}_schema.prisma",
        "typescript":  out_dir / f"{ui_slug}.d.ts",
        "markdown":    out_dir / f"{ui_slug}_data_dict.md",
        "csv":         out_dir / f"{ui_slug}_data_dict.csv",
    }

    table = Table(title="Output files", box=box.ROUNDED, border_style="cyan")
    table.add_column("Format", style="bold")
    table.add_column("Path", style="cyan")
    table.add_column("Size", justify="right", style="dim")

    for fmt, path in files.items():
        content = _format_analysis(
            fmt, analysis, generator,
            mermaid_exp, sqlalchemy_exp, data_dict_exp, prisma_exp,
        )
        # Append indexes to SQL output
        if fmt == "sql" and getattr(args, "indexes", False):
            advisor = IndexAdvisor()
            recs = advisor.recommend(analysis)
            content = content.rstrip("\n") + "\n\n" + advisor.format_sql(recs)
        path.write_text(content)
        table.add_row(fmt, str(path), f"{len(content):,} chars")

    err_console.print(table)


def _run_compare(args, analysis1: dict, analyzer, generator) -> None:
    """Analyze the comparison image and print a schema diff report."""
    from .differ import SchemaDiffer

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=err_console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Analyzing [cyan]{args.compare}[/cyan] for comparison...", total=None)
        analysis2 = analyzer.analyze(image_path=args.compare, hint=args.hint)
        progress.update(task, completed=True)

    if not analysis2.get("is_ui", False):
        _error(
            f"Second image has no UI detected: "
            f"{analysis2.get('error', 'No UI')}"
        )
        sys.exit(1)

    differ = SchemaDiffer()
    diff = differ.compare(analysis1, analysis2)

    output = diff.to_markdown()
    if args.output:
        Path(args.output).write_text(output)
        _success(f"Diff report written to [cyan]{args.output}[/cyan]")
    else:
        print(output)


def _run_batch(args) -> None:
    """Process all images in a directory, writing SQL schemas for each."""
    from .analyzer import ScreenshotAnalyzer
    from .schema import SchemaGenerator

    batch_dir = Path(args.batch)
    if not batch_dir.is_dir():
        _error(f"--batch path is not a directory: {batch_dir}")
        sys.exit(1)

    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    images = [p for p in batch_dir.iterdir() if p.suffix.lower() in image_exts]

    if not images:
        _warn(f"No images found in {batch_dir}")
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else batch_dir / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)

    analyzer = ScreenshotAnalyzer(
        mock_mode=args.mock if args.mock else None,
        max_retries=args.retries,
        model=args.model,
    )
    generator = SchemaGenerator()

    _info(f"Batch processing {len(images)} image(s) → {out_dir}")

    results = []
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        TimeElapsedColumn(),
        console=err_console,
    ) as progress:
        task = progress.add_task("Processing images", total=len(images))

        for img_path in sorted(images):
            progress.update(task, description=f"[dim]{img_path.name}[/dim]")
            try:
                analysis = analyzer.analyze(image_path=str(img_path), hint=img_path.stem)
                if not analysis.get("is_ui", False):
                    results.append({"file": img_path.name, "status": "skipped", "reason": "no_ui"})
                    progress.advance(task)
                    continue

                stats = generator.get_stats(analysis)
                stem = img_path.stem
                sql_path = out_dir / f"{stem}.sql"
                sql_path.write_text(generator.format_full_output(analysis))

                results.append(
                    {
                        "file": img_path.name,
                        "status": "ok",
                        "ui_type": stats["ui_type"],
                        "confidence": stats["confidence"],
                        "tables": stats["table_count"],
                        "output": str(sql_path),
                    }
                )
            except Exception as exc:
                results.append({"file": img_path.name, "status": "error", "reason": str(exc)})

            progress.advance(task)

    _print_batch_results(results)

    # Write summary JSON
    summary_path = out_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(results, indent=2))
    _success(f"Summary written to [cyan]{summary_path}[/cyan]")

    ok = sum(1 for r in results if r["status"] == "ok")
    if ok == len(images):
        _success(f"All {ok}/{len(images)} images processed successfully")
    elif ok > 0:
        _warn(f"{ok}/{len(images)} images processed successfully")
    else:
        _error(f"0/{len(images)} images processed successfully")


if __name__ == "__main__":
    main()
