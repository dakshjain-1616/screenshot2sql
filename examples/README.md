# Examples

All scripts work without an API key — they use built-in mock/demo mode automatically.
To use real Claude vision analysis, set `ANTHROPIC_API_KEY` in your environment.

Run any script from the project root:

```bash
python examples/01_quick_start.py
```

## Scripts

| Script | What it demonstrates |
|--------|----------------------|
| [`01_quick_start.py`](01_quick_start.py) | Minimal working example — analyze a UI hint and print the SQL schema (10-20 lines) |
| [`02_advanced_usage.py`](02_advanced_usage.py) | Multiple output formats: SQL DDL, sample queries, Mermaid ER diagram, SQLAlchemy ORM models, SQLite DB export |
| [`03_custom_config.py`](03_custom_config.py) | Configure via env vars (`ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `MAX_TOKENS`, etc.) or constructor arguments; JSON output |
| [`04_full_pipeline.py`](04_full_pipeline.py) | End-to-end workflow: analyze two UIs, validate schemas, write all formats to disk, compare schemas with diff report |

## Quick reference

```python
from screenshot2sql_conve import ScreenshotAnalyzer, SchemaGenerator

analyzer = ScreenshotAnalyzer()          # reads ANTHROPIC_API_KEY from env; mock mode if absent
generator = SchemaGenerator()

# From a real screenshot file
analysis = analyzer.analyze(image_path="screen.png")

# From a keyword hint (mock mode only)
analysis = analyzer.analyze(hint="shopify")

schema = generator.generate_schema(analysis)   # CREATE TABLE DDL
queries = generator.generate_sample_queries(analysis)
is_valid, err = generator.validate_schema(schema)
db_path = generator.generate_sqlite_db(analysis, db_path="myapp.db")
```
