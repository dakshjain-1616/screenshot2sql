"""Compatibility shim — real implementation is in screenshot2sql_conve.analyzer."""

from screenshot2sql_conve.analyzer import ScreenshotAnalyzer, ANALYZE_PROMPT  # noqa: F401

__all__ = ["ScreenshotAnalyzer", "ANALYZE_PROMPT"]
