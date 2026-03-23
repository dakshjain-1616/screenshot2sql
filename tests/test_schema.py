"""Tests for the SchemaGenerator component."""

import sqlite3
import tempfile
import os
import pytest

from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.schema import SchemaGenerator
from screenshot2sql_conve.mock_data import MOCK_RESPONSES


@pytest.fixture
def generator():
    return SchemaGenerator()


@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


@pytest.fixture
def shopify_analysis(analyzer):
    return analyzer.analyze(hint="shopify")


@pytest.fixture
def twitter_analysis(analyzer):
    return analyzer.analyze(hint="twitter")


@pytest.fixture
def no_ui_analysis(analyzer):
    return analyzer.analyze(hint="nature")


# ── DDL generation ────────────────────────────────────────────────────────────

class TestCreateTable:
    def test_generates_create_table_statement(self, generator):
        entity = {
            "name": "users",
            "fields": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
            ],
        }
        ddl = generator.generate_create_table(entity)
        assert "CREATE TABLE IF NOT EXISTS users" in ddl
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in ddl
        assert "email VARCHAR(255) UNIQUE NOT NULL" in ddl

    def test_handles_empty_constraints(self, generator):
        entity = {
            "name": "items",
            "fields": [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
                {"name": "name", "type": "TEXT", "constraints": ""},
            ],
        }
        ddl = generator.generate_create_table(entity)
        assert "name TEXT" in ddl


class TestGenerateSchema:
    def test_shopify_schema_contains_create_tables(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        assert "CREATE TABLE IF NOT EXISTS" in schema

    def test_shopify_schema_has_products(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        assert "products" in schema

    def test_shopify_schema_has_orders(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        assert "orders" in schema

    def test_shopify_schema_has_customers(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        assert "customers" in schema

    def test_twitter_schema_has_users(self, generator, twitter_analysis):
        schema = generator.generate_schema(twitter_analysis)
        assert "users" in schema

    def test_twitter_schema_has_tweets(self, generator, twitter_analysis):
        schema = generator.generate_schema(twitter_analysis)
        assert "tweets" in schema

    def test_schema_raises_for_no_ui(self, generator, no_ui_analysis):
        with pytest.raises(ValueError, match="No UI detected"):
            generator.generate_schema(no_ui_analysis)

    def test_schema_has_comment_header(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        assert "-- Schema for:" in schema


class TestValidateSchema:
    def test_shopify_schema_is_valid_sqlite(self, generator, shopify_analysis):
        schema = generator.generate_schema(shopify_analysis)
        is_valid, error = generator.validate_schema(schema)
        assert is_valid is True, f"Schema validation failed: {error}"

    def test_twitter_schema_is_valid_sqlite(self, generator, twitter_analysis):
        schema = generator.generate_schema(twitter_analysis)
        is_valid, error = generator.validate_schema(schema)
        assert is_valid is True, f"Schema validation failed: {error}"

    def test_invalid_sql_returns_false(self, generator):
        bad_sql = "CREATE TABLE oops (id INVALID_TYPE PRIMARY KEY);"
        is_valid, error = generator.validate_schema(bad_sql)
        # SQLite is lenient about types; test with truly broken SQL
        really_bad = "NOT SQL AT ALL %%##"
        is_valid2, error2 = generator.validate_schema(really_bad)
        assert is_valid2 is False
        assert error2 is not None


class TestSampleQueries:
    def test_shopify_has_sample_queries(self, generator, shopify_analysis):
        queries = generator.generate_sample_queries(shopify_analysis)
        assert len(queries) >= 2

    def test_queries_have_description_and_sql(self, generator, shopify_analysis):
        queries = generator.generate_sample_queries(shopify_analysis)
        for q in queries:
            assert "description" in q
            assert "sql" in q
            assert len(q["sql"]) > 10

    def test_no_ui_has_no_queries(self, generator, no_ui_analysis):
        queries = generator.generate_sample_queries(no_ui_analysis)
        assert queries == []


class TestSQLiteDbCreation:
    def test_creates_db_file(self, generator, shopify_analysis, tmp_path):
        db_path = str(tmp_path / "test.db")
        result_path = generator.generate_sqlite_db(shopify_analysis, db_path=db_path)
        assert os.path.exists(result_path)
        assert result_path == db_path

    def test_db_contains_tables(self, generator, shopify_analysis, tmp_path):
        db_path = str(tmp_path / "shopify.db")
        generator.generate_sqlite_db(shopify_analysis, db_path=db_path)
        conn = sqlite3.connect(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = [t[0] for t in tables]
        assert "products" in table_names
        assert "orders" in table_names
        assert "customers" in table_names

    def test_auto_temp_path_when_none(self, generator, shopify_analysis):
        path = generator.generate_sqlite_db(shopify_analysis, db_path=None)
        assert os.path.exists(path)
        os.unlink(path)  # cleanup


class TestFullOutput:
    def test_full_output_contains_schema_and_queries(self, generator, shopify_analysis):
        output = generator.format_full_output(shopify_analysis)
        assert "CREATE TABLE" in output
        assert "SELECT" in output
        assert "SAMPLE QUERIES" in output

    def test_full_output_is_string(self, generator, shopify_analysis):
        output = generator.format_full_output(shopify_analysis)
        assert isinstance(output, str)
        assert len(output) > 100
