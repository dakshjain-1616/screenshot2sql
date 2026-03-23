"""Tests for MermaidExporter and SQLAlchemyExporter."""

import pytest
from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.exporter import MermaidExporter, SQLAlchemyExporter


@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


@pytest.fixture
def mermaid():
    return MermaidExporter()


@pytest.fixture
def sqlalchemy():
    return SQLAlchemyExporter()


@pytest.fixture
def shopify_analysis(analyzer):
    return analyzer.analyze(hint="shopify")


@pytest.fixture
def twitter_analysis(analyzer):
    return analyzer.analyze(hint="twitter")


@pytest.fixture
def github_analysis(analyzer):
    return analyzer.analyze(hint="github")


@pytest.fixture
def stripe_analysis(analyzer):
    return analyzer.analyze(hint="stripe")


# ── MermaidExporter ───────────────────────────────────────────────────────────

class TestMermaidExporter:
    def test_produces_erdiagram_header(self, mermaid, shopify_analysis):
        result = mermaid.generate(shopify_analysis)
        assert "erDiagram" in result

    def test_contains_table_names(self, mermaid, shopify_analysis):
        result = mermaid.generate(shopify_analysis)
        assert "products" in result
        assert "orders" in result
        assert "customers" in result

    def test_has_frontmatter_title(self, mermaid, shopify_analysis):
        result = mermaid.generate(shopify_analysis)
        assert "---" in result
        assert "title:" in result

    def test_pk_annotation(self, mermaid, shopify_analysis):
        result = mermaid.generate(shopify_analysis)
        assert "PK" in result

    def test_fk_annotation(self, mermaid, twitter_analysis):
        result = mermaid.generate(twitter_analysis)
        assert "FK" in result

    def test_fk_relationships_generated(self, mermaid, shopify_analysis):
        result = mermaid.generate(shopify_analysis)
        # At least one ||--o{ relationship line
        assert "||--o{" in result

    def test_mermaid_type_integer(self, mermaid):
        assert mermaid._mermaid_type("INTEGER") == "int"

    def test_mermaid_type_varchar(self, mermaid):
        assert mermaid._mermaid_type("VARCHAR(255)") == "string"

    def test_mermaid_type_boolean(self, mermaid):
        assert mermaid._mermaid_type("BOOLEAN") == "boolean"

    def test_mermaid_type_timestamp(self, mermaid):
        assert mermaid._mermaid_type("TIMESTAMP") == "datetime"

    def test_mermaid_type_decimal(self, mermaid):
        assert mermaid._mermaid_type("DECIMAL(10,2)") == "float"

    def test_mermaid_type_unknown_defaults_to_string(self, mermaid):
        assert mermaid._mermaid_type("WEIRD_TYPE") == "string"

    def test_extract_fk_pairs_finds_relationships(self, mermaid, shopify_analysis):
        entities = shopify_analysis["entities"]
        pairs = mermaid._extract_fk_pairs(entities)
        assert len(pairs) > 0
        from_tables = [p[0] for p in pairs]
        assert any("order" in t for t in from_tables)

    def test_twitter_schema_mermaid(self, mermaid, twitter_analysis):
        result = mermaid.generate(twitter_analysis)
        assert "users" in result
        assert "tweets" in result

    def test_github_schema_mermaid(self, mermaid, github_analysis):
        result = mermaid.generate(github_analysis)
        assert "repositories" in result
        assert "pull_requests" in result

    def test_stripe_schema_mermaid(self, mermaid, stripe_analysis):
        result = mermaid.generate(stripe_analysis)
        assert "subscriptions" in result
        assert "customers" in result


# ── SQLAlchemyExporter ────────────────────────────────────────────────────────

class TestSQLAlchemyExporter:
    def test_produces_declarative_base(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "DeclarativeBase" in result
        assert "class Base" in result

    def test_produces_model_classes(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "class Products(Base):" in result
        assert "class Orders(Base):" in result
        assert "class Customers(Base):" in result

    def test_has_tablename_attr(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert '__tablename__ = "products"' in result

    def test_primary_key_column(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "primary_key=True" in result

    def test_foreign_key_column(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "ForeignKey(" in result

    def test_has_column_imports(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "from sqlalchemy import" in result
        assert "Column" in result
        assert "Integer" in result

    def test_varchar_gets_string_type(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "String" in result

    def test_repr_method_generated(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "__repr__" in result

    def test_has_generation_timestamp_comment(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "Generated by Screenshot2SQL" in result

    def test_sa_type_integer(self, sqlalchemy):
        assert sqlalchemy._sa_type("INTEGER") == "Integer"

    def test_sa_type_varchar_with_length(self, sqlalchemy):
        assert sqlalchemy._sa_type("VARCHAR(255)") == "String(255)"

    def test_sa_type_decimal_with_precision(self, sqlalchemy):
        assert sqlalchemy._sa_type("DECIMAL(10,2)") == "Numeric(10,2)"

    def test_sa_type_timestamp(self, sqlalchemy):
        assert sqlalchemy._sa_type("TIMESTAMP") == "DateTime"

    def test_sa_type_boolean(self, sqlalchemy):
        assert sqlalchemy._sa_type("BOOLEAN") == "Boolean"

    def test_class_name_single_word(self, sqlalchemy):
        assert sqlalchemy._class_name("users") == "Users"

    def test_class_name_snake_case(self, sqlalchemy):
        assert sqlalchemy._class_name("order_line_items") == "OrderLineItems"

    def test_twitter_models(self, sqlalchemy, twitter_analysis):
        result = sqlalchemy.generate(twitter_analysis)
        assert "class Tweets(Base):" in result
        assert "class Users(Base):" in result

    def test_not_null_becomes_nullable_false(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "nullable=False" in result

    def test_unique_constraint(self, sqlalchemy, shopify_analysis):
        result = sqlalchemy.generate(shopify_analysis)
        assert "unique=True" in result
