"""Compatibility shim — real implementation is in screenshot2sql_conve.prisma_exporter."""

from screenshot2sql_conve.prisma_exporter import PrismaExporter  # noqa: F401

__all__ = ["PrismaExporter"]
