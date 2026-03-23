"""
03_custom_config.py — Customising behaviour via env vars and constructor args.

Demonstrates:
- Setting model, token limits, and retries via environment variables
- Overriding config per-instance via constructor arguments
- Using a real API key when available (falls back to mock mode automatically)
- JSON output format

Run:
    python examples/03_custom_config.py

    # With a real API key:
    ANTHROPIC_API_KEY=sk-... python examples/03_custom_config.py
"""

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json

from screenshot2sql_conve import ScreenshotAnalyzer, SchemaGenerator

# --- Option A: configure via environment variables ---
# These env vars are read automatically if constructor args are not provided:
#
#   ANTHROPIC_API_KEY   — enables real Claude vision analysis
#   CLAUDE_MODEL        — model ID, default "claude-sonnet-4-6"
#   MAX_TOKENS          — default 4096
#   MAX_RETRIES         — default 3
#   RETRY_DELAY         — base delay between retries, default 2.0 s

# --- Option B: configure via constructor args (overrides env vars) ---
analyzer = ScreenshotAnalyzer(
    # api_key="sk-ant-...",   # uncomment to use a real key
    model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
    max_tokens=4096,
    max_retries=3,
    retry_delay=2.0,
    mock_mode=True,            # force mock mode regardless of API key
)

generator = SchemaGenerator()

print(f"Analyzer config:")
print(f"  model       = {analyzer.model}")
print(f"  max_tokens  = {analyzer.max_tokens}")
print(f"  max_retries = {analyzer.max_retries}")
print(f"  retry_delay = {analyzer.retry_delay}s")
print(f"  mock_mode   = {analyzer.mock_mode}")
print()

# Analyze using keyword hint (mock mode) or image_path (real mode)
analysis = analyzer.analyze(hint="stripe payment billing subscription")

# --- JSON output ---
json_output = generator.format_json_output(analysis)
parsed = json.loads(json_output)

print(f"UI type   : {parsed.get('ui_type')}")
print(f"Confidence: {parsed.get('confidence', 0):.0%}")
print(f"Tables    : {parsed['_meta']['table_count']}")
print(f"Columns   : {parsed['_meta']['total_columns']}")
print(f"FK count  : {parsed['_meta']['fk_count']}")
print()
print("Full JSON output (first 500 chars):")
print(json_output[:500])
print("...")
