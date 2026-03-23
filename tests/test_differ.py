"""Tests for SchemaDiffer and SchemaDiff."""

import pytest
from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.differ import SchemaDiffer, SchemaDiff, TableChange, FieldChange


@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


@pytest.fixture
def differ():
    return SchemaDiffer()


@pytest.fixture
def shopify_analysis(analyzer):
    return analyzer.analyze(hint="shopify")


@pytest.fixture
def twitter_analysis(analyzer):
    return analyzer.analyze(hint="twitter")


@pytest.fixture
def github_analysis(analyzer):
    return analyzer.analyze(hint="github")


def _make_analysis(tables: list, ui_type: str = "Test UI") -> dict:
    """Helper: build a minimal analysis dict with given table specs."""
    entities = []
    for name, fields in tables:
        entities.append({
            "name": name,
            "description": f"Table {name}",
            "fields": [
                {"name": f["name"], "type": f.get("type", "TEXT"), "constraints": f.get("constraints", "")}
                for f in fields
            ],
        })
    return {
        "is_ui": True,
        "ui_type": ui_type,
        "confidence": 0.9,
        "entities": entities,
        "sample_queries": [],
    }


# ── SchemaDiffer.compare ──────────────────────────────────────────────────────

class TestSchemaDifferNoChanges:
    def test_same_schema_no_changes(self, differ, shopify_analysis):
        diff = differ.compare(shopify_analysis, shopify_analysis)
        assert not diff.has_changes

    def test_same_schema_summary_says_no_changes(self, differ, shopify_analysis):
        diff = differ.compare(shopify_analysis, shopify_analysis)
        assert "No structural changes" in diff.summary()


class TestSchemaDifferAddedTable:
    @pytest.fixture
    def diff_added(self, differ):
        old = _make_analysis([("users", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}])])
        new = _make_analysis([
            ("users", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}]),
            ("posts", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}]),
        ])
        return differ.compare(old, new)

    def test_detects_added_table(self, diff_added):
        assert "posts" in diff_added.added_tables

    def test_no_removed_tables(self, diff_added):
        assert diff_added.removed_tables == []

    def test_has_changes(self, diff_added):
        assert diff_added.has_changes

    def test_summary_mentions_added(self, diff_added):
        assert "added" in diff_added.summary().lower()


class TestSchemaDifferRemovedTable:
    @pytest.fixture
    def diff_removed(self, differ):
        old = _make_analysis([
            ("users", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}]),
            ("posts", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}]),
        ])
        new = _make_analysis([("users", [{"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"}])])
        return differ.compare(old, new)

    def test_detects_removed_table(self, diff_removed):
        assert "posts" in diff_removed.removed_tables

    def test_summary_mentions_removed(self, diff_removed):
        assert "removed" in diff_removed.summary().lower()


class TestSchemaDifferModifiedTable:
    @pytest.fixture
    def diff_modified(self, differ):
        old = _make_analysis([
            ("users", [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
                {"name": "name", "type": "TEXT", "constraints": ""},
            ])
        ])
        new = _make_analysis([
            ("users", [
                {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
                {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE"},
            ])
        ])
        return differ.compare(old, new)

    def test_detects_modified_table(self, diff_modified):
        assert len(diff_modified.modified_tables) == 1
        assert diff_modified.modified_tables[0].name == "users"

    def test_detects_added_field(self, diff_modified):
        tc = diff_modified.modified_tables[0]
        added = [fc for fc in tc.field_changes if fc.change_type == "added"]
        assert any(fc.name == "email" for fc in added)

    def test_detects_type_change(self, diff_modified):
        tc = diff_modified.modified_tables[0]
        type_changes = [fc for fc in tc.field_changes if fc.change_type == "type_changed"]
        assert any(fc.name == "name" for fc in type_changes)


class TestSchemaDifferCrossUI:
    def test_shopify_vs_twitter_has_changes(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        assert diff.has_changes

    def test_cross_ui_has_added_and_removed(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        assert len(diff.removed_tables) > 0
        assert len(diff.added_tables) > 0

    def test_ui_types_recorded(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        assert "Shopify" in diff.old_ui_type
        assert "Twitter" in diff.new_ui_type


# ── SchemaDiff output ─────────────────────────────────────────────────────────

class TestSchemaDiffOutput:
    def test_to_markdown_returns_string(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        md = diff.to_markdown()
        assert isinstance(md, str)
        assert len(md) > 50

    def test_to_markdown_contains_header(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        md = diff.to_markdown()
        assert "# Schema Diff Report" in md

    def test_to_markdown_lists_removed_tables(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        md = diff.to_markdown()
        assert "## Tables Removed" in md

    def test_to_markdown_lists_added_tables(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        md = diff.to_markdown()
        assert "## Tables Added" in md

    def test_summary_contains_ui_types(self, differ, shopify_analysis, twitter_analysis):
        diff = differ.compare(shopify_analysis, twitter_analysis)
        summary = diff.summary()
        assert "Shopify" in summary
        assert "Twitter" in summary

    def test_summary_has_timestamp(self, differ, shopify_analysis):
        diff = differ.compare(shopify_analysis, shopify_analysis)
        assert "Compared at:" in diff.summary()

    def test_compared_at_is_iso_format(self, differ, shopify_analysis):
        diff = differ.compare(shopify_analysis, shopify_analysis)
        assert "T" in diff.compared_at  # ISO 8601 format

    def test_no_changes_markdown(self, differ, shopify_analysis):
        diff = differ.compare(shopify_analysis, shopify_analysis)
        md = diff.to_markdown()
        assert "No structural changes" in md


# ── FieldChange.describe ──────────────────────────────────────────────────────

class TestFieldChangeDescribe:
    def test_added_field_describe(self):
        fc = FieldChange(
            name="email",
            change_type="added",
            new_value={"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE"},
        )
        desc = fc.describe()
        assert "+" in desc
        assert "email" in desc

    def test_removed_field_describe(self):
        fc = FieldChange(
            name="phone",
            change_type="removed",
            old_value={"name": "phone", "type": "VARCHAR(20)", "constraints": ""},
        )
        desc = fc.describe()
        assert "-" in desc
        assert "phone" in desc

    def test_type_changed_describe(self):
        fc = FieldChange(
            name="amount",
            change_type="type_changed",
            old_value={"type": "INTEGER"},
            new_value={"type": "DECIMAL(10,2)"},
        )
        desc = fc.describe()
        assert "→" in desc
        assert "INTEGER" in desc
        assert "DECIMAL" in desc


# ── New mock data coverage ────────────────────────────────────────────────────

class TestNewMockData:
    def test_github_mock_routes(self, analyzer):
        result = analyzer.analyze(hint="github repository pull request")
        assert result["is_ui"] is True
        assert "GitHub" in result["ui_type"]

    def test_slack_mock_routes(self, analyzer):
        result = analyzer.analyze(hint="slack workspace channel")
        assert result["is_ui"] is True
        assert "Slack" in result["ui_type"]

    def test_stripe_mock_routes(self, analyzer):
        result = analyzer.analyze(hint="stripe payment billing")
        assert result["is_ui"] is True
        assert "Stripe" in result["ui_type"]

    def test_linear_mock_routes(self, analyzer):
        result = analyzer.analyze(hint="linear issue tracker backlog")
        assert result["is_ui"] is True
        assert "Linear" in result["ui_type"]

    def test_github_has_repositories_table(self, analyzer):
        result = analyzer.analyze(hint="github")
        names = [e["name"] for e in result["entities"]]
        assert "repositories" in names

    def test_slack_has_messages_table(self, analyzer):
        result = analyzer.analyze(hint="slack")
        names = [e["name"] for e in result["entities"]]
        assert "messages" in names

    def test_stripe_has_subscriptions_table(self, analyzer):
        result = analyzer.analyze(hint="stripe")
        names = [e["name"] for e in result["entities"]]
        assert "subscriptions" in names

    def test_linear_has_issues_table(self, analyzer):
        result = analyzer.analyze(hint="linear")
        names = [e["name"] for e in result["entities"]]
        assert "issues" in names

    def test_all_new_mocks_have_sample_queries(self, analyzer):
        for hint in ("github", "slack", "stripe", "linear"):
            result = analyzer.analyze(hint=hint)
            assert len(result.get("sample_queries", [])) >= 2, f"Missing queries for {hint}"

    def test_all_new_mocks_have_confidence_above_90(self, analyzer):
        for hint in ("github", "slack", "stripe", "linear"):
            result = analyzer.analyze(hint=hint)
            assert result["confidence"] >= 0.9, f"Low confidence for {hint}"
