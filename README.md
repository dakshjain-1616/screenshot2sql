[![Try NEO in VS Code](https://img.shields.io/badge/VS%20Code-Try%20NEO-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=NeoResearchInc.heyneo)
[![Built autonomously using NEO](https://img.shields.io/badge/Built%20with-NEO%20Autonomous%20AI-blueviolet?style=flat-square)](https://heyneo.so)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-302%20passing-brightgreen?style=flat-square)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

# Screenshot2SQL

**Reverse-engineer any SaaS UI screenshot into a production-ready SQL schema.**

Drop a Shopify, Notion, GitHub, or Stripe screenshot and get fully normalized `CREATE TABLE` statements, SQLAlchemy ORM models, Mermaid ER diagrams, Prisma schemas, and TypeScript interfaces — instantly. Powered by [Google Gemini 2.5 Flash Lite](https://openrouter.ai/google/gemini-2.5-flash-lite) via OpenRouter.

---

## Quick Start

No API key needed — runs in demo/mock mode out of the box:

```bash
git clone https://github.com/dakshjain-1616/screenshot2sql
cd screenshot2sql
pip install -r requirements.txt
python demo.py
```

**With a real API key** (actual vision analysis):

```bash
OPENROUTER_API_KEY=your_key python demo.py
```

---

## CLI Usage

A sample screenshot is included — clone and run immediately:

```bash
# Mock mode (no API key, instant)
screenshot2sql samples/shopify_products.png --format sql

# All formats at once
screenshot2sql samples/shopify_products.png --format all --output-dir ./out

# Real vision analysis
OPENROUTER_API_KEY=your_key screenshot2sql samples/shopify_products.png --format mermaid

# Compare two screenshots
screenshot2sql before.png --compare after.png

# Batch process a folder
screenshot2sql --batch ./screenshots/ --output-dir ./schemas/

# Launch Streamlit web app
screenshot2sql --demo
```

---

## Example Output

**Input:** `samples/shopify_products.png` (included in repo)

**Output — SQL DDL:**

```sql
-- Schema for: Shopify Admin
-- Confidence: 97% | Tables: 5 | Columns: 51 | FKs: 4

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    vendor VARCHAR(255),
    product_type VARCHAR(100),
    handle VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id),
    title VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    inventory_quantity INTEGER DEFAULT 0,
    ...
);
```

**Output — Mermaid ER Diagram:**

```
erDiagram
    products {
        int id PK
        string title
        string vendor
        string status
        datetime created_at
    }
    product_variants {
        int id PK
        int product_id FK
        string sku
        decimal price
    }
    products ||--o{ product_variants : "has"
    orders ||--o{ order_line_items : "contains"
```

> Paste into [mermaid.live](https://mermaid.live) to visualize instantly.

---

## Supported Vision Models

Set any model via `SCREENSHOT_MODEL` env var. All accessed through a single [OpenRouter](https://openrouter.ai) API key.

| Model | Input $/M | Context | Notes |
|---|---|---|---|
| `google/gemini-2.5-flash-lite` | $0.10 | 1M | **Default** — best balance of cost, speed, and quality |
| `google/gemini-2.5-flash` | $0.30 | 1M | Higher accuracy for complex UIs |
| `xiaomi/mimo-v2-omni` | $0.40 | 262K | Highest visual reasoning score (MMMU-Pro 76.8) — Xiaomi's latest omni model |
| `meta-llama/llama-4-scout` | $0.08 | Large | Open-weight, cheapest with vision |
| `qwen/qwen2.5-vl-72b-instruct` | free tier | 32K | Specialized for UI/OCR/charts |

> **MiMo-V2 note:** `xiaomi/mimo-v2-pro` is **text-only** and cannot process images. For vision tasks, use `xiaomi/mimo-v2-omni` instead.

---

## Features

| Feature | Description |
|---|---|
| **SQL DDL** | `CREATE TABLE` with types, constraints, foreign keys — SQLite validated |
| **Mermaid ER Diagram** | Paste into mermaid.live to visualize |
| **SQLAlchemy ORM** | Python model classes ready for your project |
| **Prisma Schema** | TypeScript/Node.js ready |
| **TypeScript Interfaces** | Frontend-ready type definitions |
| **Markdown Data Dict** | Human-readable column documentation |
| **Schema Diff** | Compare two UIs to track structural changes |
| **Index Advisor** | `CREATE INDEX` recommendations based on field types |
| **Batch Mode** | Process entire folders of screenshots |
| **Mock Mode** | Full demo without any API key |

---

## Supported UI Types

Works with any SaaS UI. Built-in mock responses for:

`Shopify` · `Stripe` · `Twitter/X` · `GitHub` · `Notion` · `Linear` · `HubSpot` · `Jira` · `Figma` · `Airtable`

---

## Examples

Runnable scripts in [`examples/`](examples/):

| Script | What it shows |
|---|---|
| [`01_quick_start.py`](examples/01_quick_start.py) | Analyze a hint, print SQL schema |
| [`02_advanced_usage.py`](examples/02_advanced_usage.py) | All export formats, SQLite DB export |
| [`03_custom_config.py`](examples/03_custom_config.py) | Configure model, tokens, retries via env vars |
| [`04_full_pipeline.py`](examples/04_full_pipeline.py) | End-to-end: analyze → export → diff → SQLite |

```bash
python examples/01_quick_start.py
python examples/04_full_pipeline.py
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in your values:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | API key from [openrouter.ai](https://openrouter.ai/keys). If unset, runs in mock mode. |
| `SCREENSHOT_MODEL` | `google/gemini-2.5-flash-lite` | Vision model to use. See alternatives below. |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | Override for custom proxies. |
| `MAX_TOKENS` | `4096` | Max tokens in model response. |
| `MAX_RETRIES` | `3` | Retries on rate limit / 503 errors. |
| `RETRY_DELAY` | `2.0` | Base delay (seconds) between retries. |
| `OUTPUT_FORMAT` | `sql` | Default CLI output format. |
| `CONFIDENCE_THRESHOLD` | `0.0` | Min confidence to produce output (0.0 = always). |

**Recommended vision models (via OpenRouter):**

```
google/gemini-2.5-flash-lite    # default — $0.10/M, 1M context, fast
google/gemini-2.5-flash         # $0.30/M — higher accuracy
xiaomi/mimo-v2-omni             # $0.40/M, 262K ctx — best visual reasoning (MMMU-Pro 76.8)
meta-llama/llama-4-scout        # $0.08/M — open-weight, good value
qwen/qwen2.5-vl-72b-instruct   # free tier available — strong on UI/OCR/charts
```

> **Note on MiMo-V2:** `xiaomi/mimo-v2-pro` is text-only (no vision). Use `xiaomi/mimo-v2-omni` for vision tasks. It scores highest on visual reasoning benchmarks but costs 4× more than the default.

---

## Testing

```bash
python -m pytest tests/ -v
# 302 passed in 0.5s
```

---

## Project Structure

```
screenshot2sql/
├── samples/
│   └── shopify_products.png   # sample UI screenshot — run examples immediately
├── examples/
│   ├── 01_quick_start.py
│   ├── 02_advanced_usage.py
│   ├── 03_custom_config.py
│   └── 04_full_pipeline.py
├── screenshot2sql_conve/
│   ├── analyzer.py            # vision LLM integration (OpenRouter)
│   ├── schema.py              # SQL DDL generator + SQLite validator
│   ├── exporter.py            # Mermaid + SQLAlchemy exporters
│   ├── prisma_exporter.py     # Prisma schema + TypeScript interfaces
│   ├── differ.py              # schema diff engine
│   ├── index_advisor.py       # CREATE INDEX recommendations
│   └── data_dict.py           # Markdown + CSV data dictionary
├── tests/                     # 302 tests
├── demo.py                    # full demo, no API key needed
└── .env.example
```

---

_Built autonomously using [NEO](https://heyneo.so) — your autonomous AI Agent_
