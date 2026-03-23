"""
01_quick_start.py — Minimal working example.

Analyzes a UI hint (no real screenshot needed) and prints the SQL schema.
Works without an API key — uses built-in demo/mock mode automatically.

Run:
    python examples/01_quick_start.py
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from screenshot2sql_conve import ScreenshotAnalyzer, SchemaGenerator

# No API key required — mock mode activates automatically
analyzer = ScreenshotAnalyzer(mock_mode=True)
generator = SchemaGenerator()

# Option A: analyze via keyword hint (mock mode — no image needed)
analysis = analyzer.analyze(hint="shopify")

# Option B: analyze a real screenshot (requires OPENROUTER_API_KEY)
#   _SAMPLE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples", "shopify_products.png")
#   analyzer_real = ScreenshotAnalyzer()  # auto-uses OPENROUTER_API_KEY if set
#   analysis = analyzer_real.analyze(image_path=_SAMPLE)

# Generate and print the SQL schema
schema = generator.generate_schema(analysis)
print(schema)
