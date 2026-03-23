"""Compatibility shim — real implementation is in screenshot2sql_conve.index_advisor."""

from screenshot2sql_conve.index_advisor import IndexAdvisor, IndexRecommendation  # noqa: F401

__all__ = ["IndexAdvisor", "IndexRecommendation"]
