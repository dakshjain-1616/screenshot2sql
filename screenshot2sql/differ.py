"""Compatibility shim — real implementation is in screenshot2sql_conve.differ."""

from screenshot2sql_conve.differ import (  # noqa: F401
    FieldChange,
    TableChange,
    SchemaDiff,
    SchemaDiffer,
)

__all__ = ["FieldChange", "TableChange", "SchemaDiff", "SchemaDiffer"]
