"""Tests for the ScreenshotAnalyzer component."""

import pytest
from screenshot2sql_conve.analyzer import ScreenshotAnalyzer


@pytest.fixture
def analyzer():
    return ScreenshotAnalyzer(mock_mode=True)


# ── Mock mode routing ─────────────────────────────────────────────────────────

class TestMockRouting:
    def test_shopify_keyword_routes_correctly(self, analyzer):
        result = analyzer.analyze(hint="shopify")
        assert result["ui_type"] == "Shopify Admin"

    def test_twitter_keyword_routes_correctly(self, analyzer):
        result = analyzer.analyze(hint="twitter")
        assert result["ui_type"] == "Twitter / X Mobile App"

    def test_notion_keyword_routes_correctly(self, analyzer):
        result = analyzer.analyze(hint="notion")
        assert result["ui_type"] == "Notion Workspace"

    def test_nature_keyword_returns_no_ui(self, analyzer):
        result = analyzer.analyze(hint="nature landscape photo")
        assert result["is_ui"] is False

    def test_forest_returns_no_ui(self, analyzer):
        result = analyzer.analyze(hint="forest")
        assert result["is_ui"] is False

    def test_mock_flag_is_set(self, analyzer):
        result = analyzer.analyze(hint="shopify")
        assert result.get("_mock") is True

    def test_default_fallback_returns_ui(self, analyzer):
        result = analyzer.analyze(hint="random unknown app screenshot")
        assert result["is_ui"] is True


# ── Shopify analysis ──────────────────────────────────────────────────────────

class TestShopifyAnalysis:
    @pytest.fixture
    def shopify_result(self, analyzer):
        return analyzer.analyze(hint="shopify admin dashboard")

    def test_is_ui_true(self, shopify_result):
        assert shopify_result["is_ui"] is True

    def test_ui_type(self, shopify_result):
        assert "Shopify" in shopify_result["ui_type"]

    def test_confidence_high(self, shopify_result):
        assert shopify_result["confidence"] >= 0.9

    def test_has_entities(self, shopify_result):
        assert len(shopify_result["entities"]) >= 3

    def test_has_products_table(self, shopify_result):
        names = [e["name"] for e in shopify_result["entities"]]
        assert "products" in names

    def test_has_orders_table(self, shopify_result):
        names = [e["name"] for e in shopify_result["entities"]]
        assert "orders" in names

    def test_has_customers_table(self, shopify_result):
        names = [e["name"] for e in shopify_result["entities"]]
        assert "customers" in names

    def test_products_has_id_field(self, shopify_result):
        products = next(e for e in shopify_result["entities"] if e["name"] == "products")
        field_names = [f["name"] for f in products["fields"]]
        assert "id" in field_names

    def test_products_has_title_field(self, shopify_result):
        products = next(e for e in shopify_result["entities"] if e["name"] == "products")
        field_names = [f["name"] for f in products["fields"]]
        assert "title" in field_names

    def test_orders_references_customers(self, shopify_result):
        orders = next(e for e in shopify_result["entities"] if e["name"] == "orders")
        customer_fk = next(
            (f for f in orders["fields"] if "customer_id" in f["name"]),
            None,
        )
        assert customer_fk is not None

    def test_has_sample_queries(self, shopify_result):
        assert len(shopify_result["sample_queries"]) >= 2

    def test_sample_queries_have_sql(self, shopify_result):
        for q in shopify_result["sample_queries"]:
            assert "sql" in q
            assert "SELECT" in q["sql"].upper()


# ── Twitter analysis ──────────────────────────────────────────────────────────

class TestTwitterAnalysis:
    @pytest.fixture
    def twitter_result(self, analyzer):
        return analyzer.analyze(hint="twitter mobile app tweet")

    def test_is_ui_true(self, twitter_result):
        assert twitter_result["is_ui"] is True

    def test_ui_type_contains_twitter(self, twitter_result):
        assert "Twitter" in twitter_result["ui_type"] or "X" in twitter_result["ui_type"]

    def test_has_users_table(self, twitter_result):
        names = [e["name"] for e in twitter_result["entities"]]
        assert "users" in names

    def test_has_tweets_table(self, twitter_result):
        names = [e["name"] for e in twitter_result["entities"]]
        assert "tweets" in names

    def test_tweets_references_users(self, twitter_result):
        tweets = next(e for e in twitter_result["entities"] if e["name"] == "tweets")
        user_fk = next(
            (f for f in tweets["fields"] if "user_id" in f["name"]),
            None,
        )
        assert user_fk is not None

    def test_users_has_username_field(self, twitter_result):
        users = next(e for e in twitter_result["entities"] if e["name"] == "users")
        field_names = [f["name"] for f in users["fields"]]
        assert "username" in field_names

    def test_tweets_has_content_field(self, twitter_result):
        tweets = next(e for e in twitter_result["entities"] if e["name"] == "tweets")
        field_names = [f["name"] for f in tweets["fields"]]
        assert "content" in field_names


# ── Nature/no-UI edge case ────────────────────────────────────────────────────

class TestNoUIEdgeCase:
    @pytest.fixture
    def nature_result(self, analyzer):
        return analyzer.analyze(hint="nature photo of mountains")

    def test_is_ui_false(self, nature_result):
        assert nature_result["is_ui"] is False

    def test_has_error_message(self, nature_result):
        assert "error" in nature_result
        assert len(nature_result["error"]) > 0

    def test_error_mentions_no_ui(self, nature_result):
        assert "No UI detected" in nature_result["error"]

    def test_no_entities(self, nature_result):
        assert nature_result.get("entities", []) == []

    def test_no_sample_queries(self, nature_result):
        assert nature_result.get("sample_queries", []) == []

    def test_confidence_very_low(self, nature_result):
        assert nature_result["confidence"] < 0.1

    def test_landscape_also_no_ui(self, analyzer):
        result = analyzer.analyze(hint="landscape beach")
        assert result["is_ui"] is False

    def test_animal_photo_no_ui(self, analyzer):
        result = analyzer.analyze(hint="animal photo")
        assert result["is_ui"] is False


# ── Filename-based routing ────────────────────────────────────────────────────

class TestFilenameRouting:
    def test_filename_with_shopify_routes_correctly(self, analyzer):
        result = analyzer.analyze(image_path="/tmp/shopify_screenshot.png")
        assert result["is_ui"] is True
        assert "Shopify" in result["ui_type"]

    def test_filename_with_twitter_routes_correctly(self, analyzer):
        result = analyzer.analyze(image_path="/tmp/twitter_feed.png")
        assert result["is_ui"] is True
        assert "Twitter" in result["ui_type"]
