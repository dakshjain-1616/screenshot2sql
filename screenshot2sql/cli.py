"""Compatibility shim — real implementation is in screenshot2sql_conve.cli."""

from screenshot2sql_conve.cli import main, VALID_FORMATS  # noqa: F401

__all__ = ["main", "VALID_FORMATS"]

if __name__ == "__main__":
    main()
