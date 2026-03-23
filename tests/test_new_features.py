"""
Tests for the three new features added in v0.3.0:
  1. IndexAdvisor — CREATE INDEX recommendations
  2. DataDictExporter — Markdown & CSV data dictionaries
  3. PrismaExporter — Prisma schema & TypeScript interfaces

Also covers:
  - New mock platforms (Jira, Figma, Airtable, HubSpot)
  - CLI --confidence and --indexes flags (unit-level)
  - Version bump to 0.3.0
"""

import csv
import io
import json
import pytest

from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.schema import SchemaGenerator
from screenshot2sql_conve.index_advisor import IndexAdvisor, IndexRecommendation
from screenshot2sql_conve.data_dict import DataDictExporter
from screenshot2sql_conve.prisma_exporter import PrismaExporter
from screenshot2sql_conve import __version__


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


@pytest.fixture
def generator():
    return SchemaGenerator()


@pytest.fixture
def shopify(analyzer):
    return analyzer.analyze(hint="shopify")


@pytest.fixture
def stripe(analyzer):
    return analyzer.analyze(hint="stripe")


@pytest.fixture
def hubspot(analyzer):
    return analyzer.analyze(hint="hubspot")


@pytest.fixture
def jira(analyzer):
    return analyzer.analyze(hint="jira")


@pytest.fixture
def figma(analyzer):
    return analyzer.analyze(hint="figma")


@pytest.fixture
def airtable(analyzer):
    return analyzer.analyze(hint="airtable")


# ── Version ───────────────────────────────────────────────────────────────────

class TestVersion:
    def test_version_is_030(self):
        assert __version__ == "0.3.0"

    def test_version_importable_from_shim(self):
        from screenshot2sql import __version__ as sv
        assert sv == "0.3.0"


# ── IndexAdvisor ─────────────────────────────────────────────────────────────

class TestIndexAdvisor:
    @pytest.fixture
    def advisor(self):
        return IndexAdvisor()

    def test_recommend_returns_list(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        assert isinstance(recs, list)

    def test_recommend_not_empty_for_shopify(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        assert len(recs) > 0

    def test_all_items_are_index_recommendations(self, advisor, shopify):
        for r in advisor.recommend(shopify):
            assert isinstance(r, IndexRecommendation)

    def test_recommendations_have_required_fields(self, advisor, shopify):
        for r in advisor.recommend(shopify):
            assert r.table
            assert r.column
            assert r.reason
            assert r.index_sql
            assert r.priority in ("high", "medium", "low")

    def test_fk_columns_are_high_priority(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        high = [r for r in recs if r.priority == "high"]
        assert len(high) > 0

    def test_pk_columns_not_recommended(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        for r in recs:
            assert r.column != "id" or r.table != "products"

    def test_unique_columns_not_recommended(self, advisor, shopify):
        # 'handle' in products is UNIQUE NOT NULL — skip since it has implicit index
        recs = advisor.recommend(shopify)
        # handle should not appear (UNIQUE skips)
        handle_recs = [r for r in recs if r.table == "products" and r.column == "handle"]
        assert handle_recs == []

    def test_sorted_high_before_medium(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        priorities = [priority_order[r.priority] for r in recs]
        assert priorities == sorted(priorities)

    def test_no_duplicate_table_column_pairs(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        seen = set()
        for r in recs:
            key = (r.table, r.column)
            assert key not in seen, f"Duplicate recommendation: {key}"
            seen.add(key)

    def test_index_sql_contains_create_index(self, advisor, shopify):
        for r in advisor.recommend(shopify):
            assert "CREATE INDEX" in r.index_sql.upper()

    def test_index_sql_contains_table_name(self, advisor, shopify):
        for r in advisor.recommend(shopify):
            assert r.table in r.index_sql

    def test_format_sql_returns_string(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        output = advisor.format_sql(recs)
        assert isinstance(output, str)

    def test_format_sql_contains_index_statements(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        output = advisor.format_sql(recs)
        assert "CREATE INDEX" in output

    def test_format_sql_empty_returns_no_recommendations(self, advisor):
        output = advisor.format_sql([])
        assert "No index recommendations" in output

    def test_format_markdown_returns_string(self, advisor, shopify):
        recs = advisor.recommend(shopify)
        md = advisor.format_markdown(recs)
        assert isinstance(md, str)
        assert "## Index Recommendations" in md

    def test_format_markdown_empty_list(self, advisor):
        md = advisor.format_markdown([])
        assert "No index recommendations" in md

    def test_describe_method(self, advisor, shopify):
        for r in advisor.recommend(shopify):
            desc = r.describe()
            assert isinstance(desc, str)
            assert r.priority.upper() in desc

    def test_stripe_has_stripe_id_recommendation(self, advisor, stripe):
        recs = advisor.recommend(stripe)
        stripe_id_recs = [
            r for r in recs
            if r.column == "stripe_id"
        ]
        assert len(stripe_id_recs) > 0

    def test_status_column_medium_priority(self, advisor, stripe):
        recs = advisor.recommend(stripe)
        status_recs = [r for r in recs if r.column == "status"]
        for r in status_recs:
            assert r.priority == "medium"


# ── DataDictExporter ─────────────────────────────────────────────────────────

class TestDataDictMarkdown:
    @pytest.fixture
    def exp(self):
        return DataDictExporter()

    def test_generate_markdown_returns_string(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert isinstance(md, str)

    def test_markdown_starts_with_h1(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert md.startswith("# Data Dictionary:")

    def test_markdown_contains_ui_type(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "Shopify" in md

    def test_markdown_contains_all_table_names(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        for entity in shopify["entities"]:
            assert entity["name"] in md

    def test_markdown_contains_column_names(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "email" in md  # customers.email

    def test_markdown_has_overview_section(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "## Overview" in md

    def test_markdown_has_tables_toc(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "## Tables" in md

    def test_markdown_has_sample_queries(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "## Sample Queries" in md
        assert "```sql" in md

    def test_markdown_shows_pk_emoji(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "🔑" in md

    def test_markdown_shows_fk_emoji(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "🔗" in md

    def test_markdown_shows_confidence(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "Confidence" in md

    def test_markdown_shows_analyzed_at(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "Analyzed At" in md

    def test_markdown_mock_note_present(self, exp, shopify):
        md = exp.generate_markdown(shopify)
        assert "demo/mock" in md.lower() or "mock" in md.lower()

    def test_hubspot_markdown_valid(self, exp, hubspot):
        md = exp.generate_markdown(hubspot)
        assert "HubSpot" in md
        assert "deals" in md


class TestDataDictCSV:
    @pytest.fixture
    def exp(self):
        return DataDictExporter()

    def test_generate_csv_returns_string(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        assert isinstance(csv_out, str)

    def test_csv_has_header_row(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        reader = csv.DictReader(io.StringIO(csv_out))
        headers = reader.fieldnames
        assert headers is not None
        assert "table" in headers
        assert "column" in headers
        assert "type" in headers

    def test_csv_row_count_matches_columns(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        reader = csv.DictReader(io.StringIO(csv_out))
        rows = list(reader)
        expected = sum(len(e["fields"]) for e in shopify["entities"])
        assert len(rows) == expected

    def test_csv_pk_columns_marked(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        reader = csv.DictReader(io.StringIO(csv_out))
        pk_rows = [r for r in reader if r["is_pk"] == "yes"]
        assert len(pk_rows) > 0

    def test_csv_fk_ref_populated(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        reader = csv.DictReader(io.StringIO(csv_out))
        fk_rows = [r for r in reader if r["is_fk"] == "yes"]
        assert len(fk_rows) > 0
        for row in fk_rows:
            assert "." in row["fk_ref"], f"fk_ref should be table.col, got: {row['fk_ref']}"

    def test_csv_unique_flag(self, exp, shopify):
        csv_out = exp.generate_csv(shopify)
        reader = csv.DictReader(io.StringIO(csv_out))
        unique_rows = [r for r in reader if r["is_unique"] == "yes"]
        assert len(unique_rows) > 0


# ── PrismaExporter ────────────────────────────────────────────────────────────

class TestPrismaExporter:
    @pytest.fixture
    def exp(self):
        return PrismaExporter()

    def test_generate_prisma_returns_string(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert isinstance(schema, str)

    def test_prisma_has_generator_block(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "generator client" in schema
        assert "prisma-client-js" in schema

    def test_prisma_has_datasource_block(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "datasource db" in schema
        assert "sqlite" in schema

    def test_prisma_has_model_for_each_entity(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        for entity in shopify["entities"]:
            model_name = "".join(w.capitalize() for w in entity["name"].split("_"))
            assert f"model {model_name}" in schema

    def test_prisma_has_id_decorator(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "@id" in schema

    def test_prisma_has_map_annotations(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "@@map" in schema

    def test_prisma_default_autoincrement(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "@default(autoincrement())" in schema

    def test_prisma_unique_annotation(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "@unique" in schema

    def test_prisma_relation_fields(self, exp, shopify):
        schema = exp.generate_prisma(shopify)
        assert "@relation(" in schema

    def test_generate_typescript_returns_string(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        assert isinstance(ts, str)

    def test_typescript_has_export_interface(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        assert "export interface" in ts

    def test_typescript_has_interface_for_each_entity(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        for entity in shopify["entities"]:
            model_name = "".join(w.capitalize() for w in entity["name"].split("_"))
            assert f"interface {model_name}" in ts

    def test_typescript_has_any_entity_union(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        assert "export type AnyEntity" in ts

    def test_typescript_uses_correct_types(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        assert "number" in ts  # INTEGER → number
        assert "string" in ts  # VARCHAR → string

    def test_typescript_optional_fields(self, exp, shopify):
        ts = exp.generate_typescript(shopify)
        assert "?" in ts  # nullable fields should be optional

    def test_jira_prisma_valid(self, exp, jira):
        schema = exp.generate_prisma(jira)
        assert "model Projects" in schema or "model Project" in schema
        assert "model Issues" in schema or "model Issue" in schema

    def test_figma_typescript_valid(self, exp, figma):
        ts = exp.generate_typescript(figma)
        assert "interface Files" in ts or "interface File" in ts or "Files" in ts


# ── New mock platforms ────────────────────────────────────────────────────────

class TestNewMockPlatforms:
    @pytest.mark.parametrize("hint,expected_ui_fragment", [
        ("jira", "Jira"),
        ("figma", "Figma"),
        ("airtable", "Airtable"),
        ("hubspot", "HubSpot"),
    ])
    def test_platform_detected(self, analyzer, hint, expected_ui_fragment):
        analysis = analyzer.analyze(hint=hint)
        assert analysis["is_ui"] is True
        assert expected_ui_fragment in analysis["ui_type"]

    @pytest.mark.parametrize("hint", ["jira", "figma", "airtable", "hubspot"])
    def test_platform_schema_valid_sqlite(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        g = SchemaGenerator()
        analysis = a.analyze(hint=hint)
        ddl = g.generate_schema(analysis)
        is_valid, error = g.validate_schema(ddl)
        assert is_valid, f"Invalid schema for {hint}: {error}"

    @pytest.mark.parametrize("hint", ["jira", "figma", "airtable", "hubspot"])
    def test_platform_has_sample_queries(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        analysis = a.analyze(hint=hint)
        assert len(analysis.get("sample_queries", [])) >= 1

    @pytest.mark.parametrize("hint", ["jira", "figma", "airtable", "hubspot"])
    def test_platform_full_output_has_select(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        g = SchemaGenerator()
        analysis = a.analyze(hint=hint)
        output = g.format_full_output(analysis)
        assert "SELECT" in output

    def test_jira_keyword_mapping(self, analyzer):
        result = analyzer.analyze(hint="atlassian jira board")
        assert "Jira" in result["ui_type"]

    def test_figma_keyword_mapping(self, analyzer):
        result = analyzer.analyze(hint="figma design tool")
        assert "Figma" in result["ui_type"]

    def test_hubspot_crm_keyword(self, analyzer):
        result = analyzer.analyze(hint="crm pipeline sales")
        assert "HubSpot" in result["ui_type"]

    def test_jira_has_issues_table(self, jira):
        names = [e["name"] for e in jira["entities"]]
        assert "issues" in names

    def test_jira_has_sprints_table(self, jira):
        names = [e["name"] for e in jira["entities"]]
        assert "sprints" in names

    def test_hubspot_has_deals_table(self, hubspot):
        names = [e["name"] for e in hubspot["entities"]]
        assert "deals" in names

    def test_hubspot_has_contacts_table(self, hubspot):
        names = [e["name"] for e in hubspot["entities"]]
        assert "contacts" in names

    def test_figma_has_files_table(self, figma):
        names = [e["name"] for e in figma["entities"]]
        assert "files" in names

    def test_figma_has_components_table(self, figma):
        names = [e["name"] for e in figma["entities"]]
        assert "components" in names

    def test_airtable_has_bases_table(self, airtable):
        names = [e["name"] for e in airtable["entities"]]
        assert "bases" in names

    @pytest.mark.parametrize("hint", ["jira", "figma", "airtable", "hubspot"])
    def test_platform_confidence_high(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        analysis = a.analyze(hint=hint)
        assert analysis["confidence"] >= 0.9


# ── IndexAdvisor + new platform cross-tests ───────────────────────────────────

class TestIndexAdvisorNewPlatforms:
    @pytest.fixture
    def advisor(self):
        return IndexAdvisor()

    @pytest.mark.parametrize("hint", ["jira", "hubspot", "figma", "airtable"])
    def test_recommendations_not_empty(self, advisor, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        analysis = a.analyze(hint=hint)
        recs = advisor.recommend(analysis)
        assert len(recs) > 0

    @pytest.mark.parametrize("hint", ["jira", "hubspot", "figma", "airtable"])
    def test_sql_output_valid(self, advisor, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        g = SchemaGenerator()
        analysis = a.analyze(hint=hint)
        recs = advisor.recommend(analysis)
        sql = advisor.format_sql(recs)
        # Full schema + index SQL should be valid SQLite
        schema = g.generate_schema(analysis)
        combined = schema + "\n" + "\n".join(
            r.index_sql for r in recs
        )
        is_valid, err = g.validate_schema(combined)
        assert is_valid, f"Combined schema+indexes invalid for {hint}: {err}"


# ── DataDictExporter + PrismaExporter on all platforms ────────────────────────

class TestExportersAllPlatforms:
    @pytest.mark.parametrize("hint", [
        "shopify", "twitter", "github", "slack", "stripe", "linear",
        "jira", "figma", "airtable", "hubspot",
    ])
    def test_markdown_generated(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        exp = DataDictExporter()
        analysis = a.analyze(hint=hint)
        md = exp.generate_markdown(analysis)
        assert "# Data Dictionary:" in md
        assert len(md) > 100

    @pytest.mark.parametrize("hint", [
        "shopify", "twitter", "github", "slack", "stripe", "linear",
        "jira", "figma", "airtable", "hubspot",
    ])
    def test_csv_generated(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        exp = DataDictExporter()
        analysis = a.analyze(hint=hint)
        csv_out = exp.generate_csv(analysis)
        reader = csv.DictReader(io.StringIO(csv_out))
        rows = list(reader)
        expected = sum(len(e["fields"]) for e in analysis["entities"])
        assert len(rows) == expected

    @pytest.mark.parametrize("hint", [
        "shopify", "twitter", "github", "slack", "stripe", "linear",
        "jira", "figma", "airtable", "hubspot",
    ])
    def test_prisma_schema_generated(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        exp = PrismaExporter()
        analysis = a.analyze(hint=hint)
        schema = exp.generate_prisma(analysis)
        assert "generator client" in schema
        assert "datasource db" in schema

    @pytest.mark.parametrize("hint", [
        "shopify", "twitter", "github", "slack", "stripe", "linear",
        "jira", "figma", "airtable", "hubspot",
    ])
    def test_typescript_interfaces_generated(self, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        exp = PrismaExporter()
        analysis = a.analyze(hint=hint)
        ts = exp.generate_typescript(analysis)
        assert "export interface" in ts
        assert "export type AnyEntity" in ts
