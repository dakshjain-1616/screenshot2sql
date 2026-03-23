```markdown
# Screenshot2SQL: Turn Any UI Screenshot into SQL Schema Magic 🪄

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Built by NEO](https://img.shields.io/badge/Built%20autonomously%20by-NEO-blueviolet?style=flat-square&logo=robot)](https://heyneo.so)

**Reverse-engineer SaaS UIs into SQL schemas with a single screenshot.**  
Drop a Notion, Shopify, or GitHub screenshot and get a fully normalized relational model, SQLAlchemy ORM classes, and ER diagrams — instantly. Powered by MiMo-V2-Pro.

---

## Why This is Cool

Ever found yourself staring at a SaaS UI, wishing you could extract its underlying data model without digging through APIs or docs? Screenshot2SQL solves this exact pain point. It automates the tedious process of reverse-engineering UIs, turning screenshots into production-ready SQL schemas with sample queries, foreign keys, and even Mermaid ER diagrams. The wow moment? Watching a Notion screenshot transform into a relational model with just a drag-and-drop.

---

## Installation

Install via pip:

```bash
pip install screenshot2sql
```

Or build from source:

```bash
git clone https://github.com/NeoResearchAI/screenshot2sql
cd screenshot2sql
pip install -e .
```

---

## Quick Example

Run the demo (no API key needed):

```bash
python demo.py
```

Or use the included sample screenshot with the CLI:

```bash
# No API key — mock mode (instant, no cost)
screenshot2sql samples/shopify_products.png --format sql

# With a real API key — actual vision analysis
OPENROUTER_API_KEY=your_key screenshot2sql samples/shopify_products.png --format mermaid
```

Or launch the Streamlit web app:

```bash
screenshot2sql --demo
```

1. Open `http://localhost:8501`.
2. Drag & drop any UI screenshot (or use `samples/shopify_products.png`).
3. Watch it generate a SQL schema, sample queries, and a Mermaid ER diagram.

---

## Key Features

- 🖼️ **UI to SQL Magic**: Convert SaaS/mobile UI screenshots into SQL schemas instantly.  
- 🔍 **Full SQL DDL**: `CREATE TABLE` statements with types, constraints, and foreign keys.  
- 🧪 **SQLite Validated**: Every schema is tested against a real SQLite engine.  
- 📊 **Sample Queries**: Practical `SELECT` queries for common use cases.  
- 📉 **Mermaid ER Diagrams**: Visualize relationships with one-click diagrams.  
- 🐍 **SQLAlchemy ORM**: Python model classes ready for your project.  
- 🔄 **Schema Diff**: Compare two screenshots to track changes.  
- 📂 **Batch Mode**: Process directories of screenshots in one command.  
- 🎮 **Demo Mode**: Try it out without an API key.  

---

## Contributing

We welcome contributions! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for details.  

---

License: [MIT](LICENSE)  

```