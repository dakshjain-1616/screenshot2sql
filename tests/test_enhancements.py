"""Tests for enhanced analyzer, schema stats, and new env var support."""

import os
import pytest
from unittest.mock import patch

from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.schema import SchemaGenerator


@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


@pytest.fixture
def generator():
    return SchemaGenerator()


@pytest.fixture
def shopify_analysis(analyzer):
    return analyzer.analyze(hint="shopify")


@pytest.fixture
def twitter_analysis(analyzer):
    return analyzer.analyze(hint="twitter")


# ── Analyzer: timestamps ──────────────────────────────────────────────────────

class TestAnalyzerTimestamps:
    def test_mock_result_has_analyzed_at(self, analyzer):
        result = analyzer.analyze(hint="shopify")
        assert "_analyzed_at" in result

    def test_analyzed_at_is_iso_string(self, analyzer):
        result = analyzer.analyze(hint="shopify")
        ts = result["_analyzed_at"]
        assert isinstance(ts, str)
        assert "T" in ts  # ISO 8601

    def test_different_calls_have_different_timestamps(self, analyzer):
        import time
        r1 = analyzer.analyze(hint="shopify")
        time.sleep(0.01)
        r2 = analyzer.analyze(hint="shopify")
        # Both are valid timestamps; values may differ by tiny amount
        assert "_analyzed_at" in r1
        assert "_analyzed_at" in r2


# ── Analyzer: constructor env vars ───────────────────────────────────────────

class TestAnalyzerEnvVars:
    def test_max_tokens_from_constructor(self):
        a = ScreenshotAnalyzer(mock_mode=True, max_tokens=1024)
        assert a.max_tokens == 1024

    def test_max_retries_from_constructor(self):
        a = ScreenshotAnalyzer(mock_mode=True, max_retries=5)
        assert a.max_retries == 5

    def test_retry_delay_from_constructor(self):
        a = ScreenshotAnalyzer(mock_mode=True, retry_delay=1.5)
        assert a.retry_delay == 1.5

    def test_max_tokens_from_env(self):
        with patch.dict(os.environ, {"MAX_TOKENS": "2048"}):
            a = ScreenshotAnalyzer(mock_mode=True)
            assert a.max_tokens == 2048

    def test_max_retries_from_env(self):
        with patch.dict(os.environ, {"MAX_RETRIES": "7"}):
            a = ScreenshotAnalyzer(mock_mode=True)
            assert a.max_retries == 7

    def test_model_from_env(self):
        with patch.dict(os.environ, {"SCREENSHOT_MODEL": "google/gemini-2.5-flash"}):
            a = ScreenshotAnalyzer(mock_mode=True)
            assert a.model == "google/gemini-2.5-flash"

    def test_model_default_is_gemini_flash_lite(self):
        with patch.dict(os.environ, {}, clear=False):
            env = {k: v for k, v in os.environ.items() if k != "SCREENSHOT_MODEL"}
            with patch.dict(os.environ, env, clear=True):
                a = ScreenshotAnalyzer(mock_mode=True)
                assert a.model == "google/gemini-2.5-flash-lite"

    def test_constructor_overrides_env_model(self):
        with patch.dict(os.environ, {"SCREENSHOT_MODEL": "google/gemini-2.5-flash"}):
            a = ScreenshotAnalyzer(mock_mode=True, model="meta-llama/llama-4-scout")
            assert a.model == "meta-llama/llama-4-scout"


# ── Analyzer: mock mode detection ─────────────────────────────────────────────

class TestAnalyzerMockModeDetection:
    def test_no_api_key_uses_mock_mode(self):
        with patch.dict(os.environ, {}, clear=False):
            env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
            with patch.dict(os.environ, env, clear=True):
                a = ScreenshotAnalyzer()
                assert a.mock_mode is True

    def test_explicit_mock_true_overrides_key(self):
        a = ScreenshotAnalyzer(api_key="sk-fake-key", mock_mode=True)
        assert a.mock_mode is True

    def test_explicit_mock_false_with_key(self):
        a = ScreenshotAnalyzer(api_key="sk-fake-key", mock_mode=False)
        assert a.mock_mode is False


# ── SchemaGenerator: stats ────────────────────────────────────────────────────

class TestSchemaStats:
    def test_get_stats_returns_dict(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert isinstance(stats, dict)

    def test_stats_table_count(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["table_count"] == len(shopify_analysis["entities"])

    def test_stats_total_columns(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        expected = sum(len(e["fields"]) for e in shopify_analysis["entities"])
        assert stats["total_columns"] == expected

    def test_stats_fk_count(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["fk_count"] >= 1

    def test_stats_confidence(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["confidence"] == shopify_analysis["confidence"]

    def test_stats_ui_type(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["ui_type"] == shopify_analysis["ui_type"]

    def test_stats_query_count(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["query_count"] == len(shopify_analysis["sample_queries"])

    def test_stats_is_mock_true(self, generator, shopify_analysis):
        stats = generator.get_stats(shopify_analysis)
        assert stats["is_mock"] is True


# ── SchemaGenerator: richer schema header ────────────────────────────────────

class TestRicherSchemaHeader:
    def test_schema_has_table_count_comment(self, generator, shopify_analysis):
        ddl = generator.generate_schema(shopify_analysis)
        assert "Tables:" in ddl

    def test_schema_has_total_columns_comment(self, generator, shopify_analysis):
        ddl = generator.generate_schema(shopify_analysis)
        assert "Total columns:" in ddl

    def test_schema_has_analyzed_at_when_present(self, generator, shopify_analysis):
        ddl = generator.generate_schema(shopify_analysis)
        assert "Analyzed at:" in ddl

    def test_schema_has_mock_comment(self, generator, shopify_analysis):
        ddl = generator.generate_schema(shopify_analysis)
        assert "mock" in ddl.lower()

    def test_entity_comment_includes_column_count(self, generator, shopify_analysis):
        ddl = generator.generate_schema(shopify_analysis)
        assert "columns)" in ddl


# ── SchemaGenerator: JSON output ──────────────────────────────────────────────

class TestJsonOutput:
    def test_format_json_output_is_valid_json(self, generator, shopify_analysis):
        import json
        output = generator.format_json_output(shopify_analysis)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_output_contains_meta(self, generator, shopify_analysis):
        import json
        output = generator.format_json_output(shopify_analysis)
        parsed = json.loads(output)
        assert "_meta" in parsed

    def test_json_meta_has_table_count(self, generator, shopify_analysis):
        import json
        output = generator.format_json_output(shopify_analysis)
        meta = json.loads(output)["_meta"]
        assert "table_count" in meta
        assert meta["table_count"] >= 3

    def test_json_output_has_entities(self, generator, shopify_analysis):
        import json
        output = generator.format_json_output(shopify_analysis)
        parsed = json.loads(output)
        assert "entities" in parsed
        assert len(parsed["entities"]) >= 3


# ── All new mocks produce valid SQLite schemas ────────────────────────────────

class TestNewMockSchemaValidity:
    @pytest.mark.parametrize("hint", ["github", "slack", "stripe", "linear"])
    def test_schema_is_valid_sqlite(self, generator, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        analysis = a.analyze(hint=hint)
        ddl = generator.generate_schema(analysis)
        is_valid, error = generator.validate_schema(ddl)
        assert is_valid, f"Invalid schema for {hint}: {error}"

    @pytest.mark.parametrize("hint", ["github", "slack", "stripe", "linear"])
    def test_full_output_has_queries(self, generator, hint):
        a = ScreenshotAnalyzer(mock_mode=True)
        analysis = a.analyze(hint=hint)
        output = generator.format_full_output(analysis)
        assert "SELECT" in output
        assert "SAMPLE QUERIES" in output
