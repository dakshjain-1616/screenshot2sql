"""Compatibility shim — real implementation is in screenshot2sql_conve.schema."""

from screenshot2sql_conve.schema import SchemaGenerator  # noqa: F401

__all__ = ["SchemaGenerator"]
