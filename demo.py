"""
Screenshot2SQL Demo — runs in under 60 seconds without any API keys.

Demonstrates:
1. Shopify admin screenshot → Products/Orders/Customers schema
2. Twitter mobile app → Users/Tweets schema
3. GitHub repository → PRs/Issues schema
4. Stripe dashboard → Subscriptions/Payments schema
5. Edge case: Nature photo → "No UI detected" error
6. Mermaid ER diagram export
7. SQLAlchemy ORM model export
8. Schema diff between two UIs
9. Export to SQLite database
10. [NEW] Index advisor — CREATE INDEX recommendations
11. [NEW] Data dictionary — Markdown & CSV documentation
12. [NEW] Prisma schema + TypeScript interfaces
13. [NEW] HubSpot CRM / Jira / Figma / Airtable schemas
"""

import os
import sys
import tempfile

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich import box
from rich.text import Text

from screenshot2sql_conve import __version__
from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.schema import SchemaGenerator
from screenshot2sql_conve.exporter import MermaidExporter, SQLAlchemyExporter
from screenshot2sql_conve.differ import SchemaDiffer
from screenshot2sql_conve.index_advisor import IndexAdvisor
from screenshot2sql_conve.data_dict import DataDictExporter
from screenshot2sql_conve.prisma_exporter import PrismaExporter

console = Console()


def print_header(text: str) -> None:
    """Print a styled section header."""
    console.print()
    console.rule(f"[bold cyan]{text}[/bold cyan]")


def run_demo_case(
    label: str,
    hint: str,
    analyzer: ScreenshotAnalyzer,
    generator: SchemaGenerator,
    expect_no_ui: bool = False,
) -> None:
    """Run a single demo analysis case and display results using Rich."""
    print_header(label)
    console.print(f"  Input hint: [italic]{hint}[/italic]")
    console.print()

    analysis = analyzer.analyze(hint=hint)

    if not analysis.get("is_ui", False):
        error = analysis.get("error", "No UI detected.")
        if expect_no_ui:
            console.print(f"  [green]✓[/green] Expected result: [dim]{error}[/dim]")
        else:
            console.print(f"  [red]✗[/red] Unexpected: {error}")
        return

    stats = generator.get_stats(analysis)
    console.print(
        f"  [green]✓[/green] Detected UI: [bold]{stats['ui_type']}[/bold] "
        f"([cyan]{stats['confidence']:.0%}[/cyan] confidence)"
    )

    # Stats table
    stats_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    stats_table.add_column("Key", style="dim")
    stats_table.add_column("Value", style="bold")
    stats_table.add_row("Tables", str(stats["table_count"]))
    stats_table.add_row("Columns", str(stats["total_columns"]))
    stats_table.add_row("Foreign keys", str(stats["fk_count"]))
    console.print(stats_table)

    # Entities table
    entities_table = Table(box=box.ROUNDED, border_style="dim", show_header=True)
    entities_table.add_column("#", style="dim", width=4)
    entities_table.add_column("Table", style="bold cyan")
    entities_table.add_column("Columns", justify="right")
    for i, e in enumerate(analysis.get("entities", []), 1):
        entities_table.add_row(str(i), e["name"], str(len(e.get("fields", []))))
    console.print(entities_table)

    try:
        schema = generator.generate_schema(analysis)
        is_valid, err = generator.validate_schema(schema)
        if is_valid:
            console.print(f"  [green]✓[/green] Schema validation: Valid SQLite")
        else:
            console.print(f"  [red]✗[/red] Schema validation: {err}")

        queries = generator.generate_sample_queries(analysis)
        if queries:
            console.print(f"  Sample queries: [cyan]{len(queries)}[/cyan]")

    except ValueError as exc:
        console.print(f"  [red]✗[/red] {exc}")


def run_mermaid_demo(analyzer: ScreenshotAnalyzer, mermaid_exp: MermaidExporter) -> None:
    """Demonstrate Mermaid ER diagram export."""
    print_header("BONUS A: Mermaid ER Diagram Export")
    analysis = analyzer.analyze(hint="stripe")
    diagram = mermaid_exp.generate(analysis)
    lines = diagram.split("\n")
    console.print(f"  Generated Mermaid erDiagram ([cyan]{len(lines)}[/cyan] lines)")
    console.print()
    for line in lines[:18]:
        console.print(f"  [dim]{line}[/dim]")
    if len(lines) > 18:
        console.print(f"  [dim]... ({len(lines) - 18} more lines)[/dim]")
    console.print()
    console.print("  Paste into [cyan]https://mermaid.live[/cyan] to visualize")


def run_sqlalchemy_demo(analyzer: ScreenshotAnalyzer, sqlalchemy_exp: SQLAlchemyExporter) -> None:
    """Demonstrate SQLAlchemy ORM model code export."""
    print_header("BONUS B: SQLAlchemy ORM Model Export")
    analysis = analyzer.analyze(hint="linear")
    models = sqlalchemy_exp.generate(analysis)
    lines = models.split("\n")
    console.print(f"  Generated SQLAlchemy models ([cyan]{len(lines)}[/cyan] lines)")
    console.print()
    for line in lines[:20]:
        console.print(f"  [dim]{line}[/dim]")
    if len(lines) > 20:
        console.print(f"  [dim]... ({len(lines) - 20} more lines)[/dim]")


def run_diff_demo(analyzer: ScreenshotAnalyzer, differ: SchemaDiffer) -> None:
    """Demonstrate schema diff between two UI analyses."""
    print_header("BONUS C: Schema Diff — Shopify vs Stripe")
    shopify = analyzer.analyze(hint="shopify")
    stripe = analyzer.analyze(hint="stripe")
    diff = differ.compare(shopify, stripe)

    console.print(f"  [bold]{diff.old_ui_type}[/bold] → [bold]{diff.new_ui_type}[/bold]")
    console.print()

    if diff.added_tables:
        console.print(f"  [green]+ Tables added:[/green] {', '.join(diff.added_tables)}")
    if diff.removed_tables:
        console.print(f"  [red]- Tables removed:[/red] {', '.join(diff.removed_tables)}")
    if diff.modified_tables:
        console.print(f"  [yellow]~ Tables modified:[/yellow] {', '.join(t.name for t in diff.modified_tables)}")
    if not diff.has_changes:
        console.print("  [dim]No structural changes detected.[/dim]")


def run_index_advisor_demo(analyzer: ScreenshotAnalyzer, advisor: IndexAdvisor) -> None:
    """Demonstrate SQL index recommendations."""
    print_header("BONUS E: Index Advisor — CREATE INDEX Recommendations")
    analysis = analyzer.analyze(hint="shopify")
    recs = advisor.recommend(analysis)

    high = sum(1 for r in recs if r.priority == "high")
    medium = sum(1 for r in recs if r.priority == "medium")

    console.print(
        f"  [green]✓[/green] Found [bold]{len(recs)}[/bold] recommendations "
        f"([red]{high} high[/red] / [yellow]{medium} medium[/yellow])"
    )
    console.print()

    rec_table = Table(box=box.ROUNDED, border_style="dim")
    rec_table.add_column("Priority", width=10)
    rec_table.add_column("Table.Column", style="cyan")
    rec_table.add_column("Reason", style="dim")
    for r in recs[:10]:
        icon = {"high": "[red]HIGH[/red]", "medium": "[yellow]MED[/yellow]"}.get(r.priority, r.priority)
        rec_table.add_row(icon, f"{r.table}.{r.column}", r.reason)
    console.print(rec_table)
    if len(recs) > 10:
        console.print(f"  [dim]... ({len(recs) - 10} more)[/dim]")


def run_data_dict_demo(analyzer: ScreenshotAnalyzer, data_dict_exp: DataDictExporter) -> None:
    """Demonstrate Markdown and CSV data dictionary export."""
    print_header("BONUS F: Data Dictionary Export (Markdown & CSV)")
    analysis = analyzer.analyze(hint="hubspot")

    md = data_dict_exp.generate_markdown(analysis)
    csv_out = data_dict_exp.generate_csv(analysis)

    md_lines = md.split("\n")
    csv_lines = csv_out.strip().split("\n")

    console.print(f"  [green]✓[/green] Markdown: [cyan]{len(md_lines)} lines[/cyan]")
    console.print(f"  [green]✓[/green] CSV:      [cyan]{len(csv_lines)} rows[/cyan]")
    console.print()
    console.print("  [bold]Markdown preview:[/bold]")
    for line in md_lines[:12]:
        console.print(f"  [dim]{line}[/dim]")
    if len(md_lines) > 12:
        console.print(f"  [dim]... ({len(md_lines) - 12} more lines)[/dim]")
    console.print()
    console.print("  [bold]CSV preview (first 3 rows):[/bold]")
    for line in csv_lines[:4]:
        console.print(f"  [dim]{line}[/dim]")


def run_prisma_demo(analyzer: ScreenshotAnalyzer, prisma_exp: PrismaExporter) -> None:
    """Demonstrate Prisma schema and TypeScript interface generation."""
    print_header("BONUS G: Prisma Schema + TypeScript Interfaces")
    analysis = analyzer.analyze(hint="jira")

    prisma_schema = prisma_exp.generate_prisma(analysis)
    ts_interfaces = prisma_exp.generate_typescript(analysis)

    p_lines = prisma_schema.split("\n")
    t_lines = ts_interfaces.split("\n")

    console.print(f"  [green]✓[/green] Prisma schema: [cyan]{len(p_lines)} lines[/cyan]")
    console.print(f"  [green]✓[/green] TypeScript:    [cyan]{len(t_lines)} lines[/cyan]")
    console.print()
    console.print("  [bold]Prisma schema preview:[/bold]")
    for line in p_lines[:20]:
        console.print(f"  [dim]{line}[/dim]")
    if len(p_lines) > 20:
        console.print(f"  [dim]... ({len(p_lines) - 20} more lines)[/dim]")


def run_new_platforms_demo(analyzer: ScreenshotAnalyzer, generator: SchemaGenerator) -> None:
    """Show new mock platforms: HubSpot, Jira, Figma, Airtable."""
    print_header("BONUS H: New Platform Support")
    new_platforms = [
        ("hubspot crm pipeline deals contacts", "HubSpot CRM"),
        ("jira sprint issue tracker backlog", "Jira"),
        ("figma design tool component library", "Figma"),
        ("airtable base spreadsheet database", "Airtable"),
    ]
    p_table = Table(box=box.ROUNDED, border_style="dim")
    p_table.add_column("Platform", style="bold cyan")
    p_table.add_column("Tables", justify="right")
    p_table.add_column("Columns", justify="right")
    p_table.add_column("Confidence", justify="right")

    for hint, label in new_platforms:
        analysis = analyzer.analyze(hint=hint)
        stats = generator.get_stats(analysis)
        p_table.add_row(
            stats["ui_type"],
            str(stats["table_count"]),
            str(stats["total_columns"]),
            f"{stats['confidence']:.0%}",
        )

    console.print(p_table)


def main() -> None:
    """Run the full Screenshot2SQL demo suite."""
    console.print()
    console.print(Panel(
        f"[bold cyan]Screenshot2SQL[/bold cyan]  [dim]v{__version__}[/dim]\n"
        "[dim]Reverse-engineer SaaS UIs into SQL schemas — Live Demo[/dim]\n"
        "[dim]Built autonomously by [link=https://heyneo.so]NEO[/link] · https://heyneo.so[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key:
        console.print("[yellow]⚠[/yellow]  ANTHROPIC_API_KEY detected — demo uses mock mode to avoid real API calls")
    else:
        console.print("[dim]No API key found — running in demo/mock mode (no API calls)[/dim]")
    console.print()

    analyzer = ScreenshotAnalyzer(mock_mode=True)
    generator = SchemaGenerator()
    mermaid_exp = MermaidExporter()
    sqlalchemy_exp = SQLAlchemyExporter()
    differ = SchemaDiffer()
    advisor = IndexAdvisor()
    data_dict_exp = DataDictExporter()
    prisma_exp = PrismaExporter()

    run_demo_case("TEST 1: Shopify Admin Screenshot",
                  "shopify admin dashboard products orders inventory", analyzer, generator)

    run_demo_case("TEST 2: Twitter Mobile App Screenshot",
                  "twitter mobile app tweet feed followers", analyzer, generator)

    run_demo_case("TEST 3: GitHub Repository",
                  "github repository pull requests issues", analyzer, generator)

    run_demo_case("TEST 4: Stripe Dashboard",
                  "stripe payment billing subscription", analyzer, generator)

    run_demo_case("TEST 5: Edge Case — Nature Photo (expect: No UI detected)",
                  "nature landscape mountain forest photo", analyzer, generator, expect_no_ui=True)

    run_mermaid_demo(analyzer, mermaid_exp)
    run_sqlalchemy_demo(analyzer, sqlalchemy_exp)
    run_diff_demo(analyzer, differ)
    run_index_advisor_demo(analyzer, advisor)
    run_data_dict_demo(analyzer, data_dict_exp)
    run_prisma_demo(analyzer, prisma_exp)
    run_new_platforms_demo(analyzer, generator)

    # SQLite DB export
    print_header("BONUS D: Export to SQLite Database")
    shopify_analysis = analyzer.analyze(hint="shopify")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False, prefix="screenshot2sql_") as f:
        db_path = f.name

    try:
        path = generator.generate_sqlite_db(shopify_analysis, db_path=db_path)
        size = os.path.getsize(path)
        console.print(f"  [green]✓[/green] SQLite DB created: [cyan]{path}[/cyan] ([dim]{size} bytes[/dim])")
        console.print(f"  Open with: [dim]sqlite3 {path}[/dim]")

        import sqlite3
        conn = sqlite3.connect(path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        console.print(f"  Tables: [cyan]{', '.join(t[0] for t in tables)}[/cyan]")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

    console.print()
    console.rule("[bold green]Demo complete![/bold green]")
    console.print()

    cmd_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    cmd_table.add_column("Command", style="cyan")
    cmd_table.add_column("Description", style="dim")
    cmd_table.add_row("screenshot2sql screen.png --format mermaid", "Export as Mermaid ER diagram")
    cmd_table.add_row("screenshot2sql screen.png --format sqlalchemy", "Export as SQLAlchemy models")
    cmd_table.add_row("screenshot2sql screen.png --format prisma", "Export as Prisma schema")
    cmd_table.add_row("screenshot2sql screen.png --format typescript", "Export as TypeScript interfaces")
    cmd_table.add_row("screenshot2sql screen.png --format markdown", "Export as Markdown data dictionary")
    cmd_table.add_row("screenshot2sql screen.png --format csv", "Export as CSV data dictionary")
    cmd_table.add_row("screenshot2sql screen.png --indexes", "Append index recommendations to SQL")
    cmd_table.add_row("screenshot2sql screen.png --confidence 0.7", "Warn if confidence below 70%")
    cmd_table.add_row("screenshot2sql screen.png --format all --output-dir ./out", "Export all formats")
    cmd_table.add_row("screenshot2sql screen.png --compare screen2.png", "Compare two schemas")
    cmd_table.add_row("screenshot2sql --batch ./screenshots/ --output-dir ./schemas/", "Process a directory")
    cmd_table.add_row("screenshot2sql --demo", "Launch Streamlit web app")
    cmd_table.add_row("screenshot2sql --version", "Print version")
    console.print(cmd_table)
    console.print()
    console.print("[dim]Built autonomously using NEO - your autonomous AI Agent https://heyneo.so[/dim]")
    console.print()


if __name__ == "__main__":
    main()
