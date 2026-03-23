"""
04_full_pipeline.py — End-to-end workflow: analyze, export all formats, diff two schemas.

Demonstrates the complete Screenshot2SQL pipeline:
1. Analyze two different UIs (Shopify and Stripe)
2. Generate SQL DDL + validate it against SQLite
3. Export Mermaid ER diagram
4. Export SQLAlchemy ORM models
5. Write all formats to a temp output directory
6. Compare the two schemas and print a diff report

Run:
    python examples/04_full_pipeline.py
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile
from pathlib import Path

from screenshot2sql_conve import (
    ScreenshotAnalyzer,
    SchemaGenerator,
    MermaidExporter,
    SQLAlchemyExporter,
    SchemaDiffer,
)

analyzer = ScreenshotAnalyzer(mock_mode=True)
generator = SchemaGenerator()
mermaid_exp = MermaidExporter()
sqlalchemy_exp = SQLAlchemyExporter()
differ = SchemaDiffer()

# ── Step 1: Analyze two UIs ──────────────────────────────────────────────────
print("Step 1: Analyzing Shopify and Stripe UIs...")
shopify = analyzer.analyze(hint="shopify admin dashboard")
stripe = analyzer.analyze(hint="stripe payment billing")

for name, analysis in [("Shopify", shopify), ("Stripe", stripe)]:
    stats = generator.get_stats(analysis)
    print(f"  {name}: {stats['table_count']} tables, {stats['total_columns']} columns, {stats['fk_count']} FKs")

print()

# ── Step 2: Validate schemas ─────────────────────────────────────────────────
print("Step 2: Validating schemas against SQLite...")
for name, analysis in [("Shopify", shopify), ("Stripe", stripe)]:
    ddl = generator.generate_schema(analysis)
    is_valid, error = generator.validate_schema(ddl)
    status = "VALID" if is_valid else f"INVALID: {error}"
    print(f"  {name}: {status}")

print()

# ── Step 3: Write all formats to a temp directory ───────────────────────────
print("Step 3: Writing all output formats to temp directory...")
with tempfile.TemporaryDirectory(prefix="screenshot2sql_") as out_dir:
    out = Path(out_dir)

    for slug, analysis in [("shopify", shopify), ("stripe", stripe)]:
        ddl = generator.generate_schema(analysis)
        full = generator.format_full_output(analysis)
        json_out = generator.format_json_output(analysis)
        mermaid = mermaid_exp.generate(analysis)
        models = sqlalchemy_exp.generate(analysis)
        db_path = str(out / f"{slug}.db")

        (out / f"{slug}.sql").write_text(full)
        (out / f"{slug}.json").write_text(json_out)
        (out / f"{slug}.mmd").write_text(mermaid)
        (out / f"{slug}_models.py").write_text(models)
        generator.generate_sqlite_db(analysis, db_path=db_path)

        files = list(out.glob(f"{slug}*"))
        print(f"  {slug}: {len(files)} files written")
        for f in sorted(files):
            print(f"    {f.name} ({f.stat().st_size} bytes)")

    print()

    # ── Step 4: Schema diff ──────────────────────────────────────────────────
    print("Step 4: Schema diff — Shopify vs Stripe...")
    diff = differ.compare(shopify, stripe)
    print(f"  {diff.old_ui_type} → {diff.new_ui_type}")
    print(f"  Tables added   : {len(diff.added_tables)} ({', '.join(diff.added_tables) or 'none'})")
    print(f"  Tables removed : {len(diff.removed_tables)} ({', '.join(diff.removed_tables[:3]) or 'none'}{'...' if len(diff.removed_tables) > 3 else ''})")
    print(f"  Tables modified: {len(diff.modified_tables)}")
    print()

    # Write the diff report
    diff_path = out / "schema_diff.md"
    diff_path.write_text(diff.to_markdown())
    print(f"  Diff report written to {diff_path.name} ({diff_path.stat().st_size} bytes)")
    print()
    print("  Summary:")
    for line in diff.summary().splitlines():
        print(f"    {line}")

print()
print("Pipeline complete.")
