"""
02_advanced_usage.py — More features and output formats.

Demonstrates:
- Multiple UI analyses
- Mermaid ER diagram export
- SQLAlchemy ORM model generation
- SQLite database creation
- Schema stats

Run:
    python examples/02_advanced_usage.py
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile

from screenshot2sql_conve import ScreenshotAnalyzer, SchemaGenerator, MermaidExporter, SQLAlchemyExporter

analyzer = ScreenshotAnalyzer(mock_mode=True)
generator = SchemaGenerator()
mermaid_exp = MermaidExporter()
sqlalchemy_exp = SQLAlchemyExporter()

# --- Analyze a GitHub UI ---
analysis = analyzer.analyze(hint="github repository pull requests issues")

stats = generator.get_stats(analysis)
print(f"Detected: {stats['ui_type']} ({stats['confidence']:.0%} confidence)")
print(f"Tables: {stats['table_count']}  |  Columns: {stats['total_columns']}  |  FKs: {stats['fk_count']}")
print()

# --- SQL DDL ---
print("=== SQL Schema ===")
schema = generator.generate_schema(analysis)
print(schema[:600], "...\n")

# --- Sample queries ---
print("=== Sample Queries ===")
for q in generator.generate_sample_queries(analysis):
    print(f"-- {q['description']}")
    print(q['sql'])
    print()

# --- Mermaid ER diagram ---
print("=== Mermaid ER Diagram (first 10 lines) ===")
diagram = mermaid_exp.generate(analysis)
for line in diagram.splitlines()[:10]:
    print(line)
print("... (paste full output into https://mermaid.live)\n")

# --- SQLAlchemy ORM models ---
print("=== SQLAlchemy ORM Models (first 20 lines) ===")
models = sqlalchemy_exp.generate(analysis)
for line in models.splitlines()[:20]:
    print(line)
print("...\n")

# --- Export to SQLite ---
with tempfile.NamedTemporaryFile(suffix=".db", delete=False, prefix="s2sql_") as f:
    db_path = f.name

try:
    path = generator.generate_sqlite_db(analysis, db_path=db_path)
    size = os.path.getsize(path)
    print(f"SQLite DB created: {path} ({size} bytes)")
finally:
    if os.path.exists(db_path):
        os.unlink(db_path)
