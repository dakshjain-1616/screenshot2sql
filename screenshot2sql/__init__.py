"""Screenshot2SQL - compatibility shim; core implementation is in screenshot2sql_conve."""

__version__ = "0.3.0"
__author__ = "NEO"

from screenshot2sql_conve.analyzer import ScreenshotAnalyzer
from screenshot2sql_conve.schema import SchemaGenerator
from screenshot2sql_conve.exporter import MermaidExporter, SQLAlchemyExporter
from screenshot2sql_conve.differ import SchemaDiffer, SchemaDiff
from screenshot2sql_conve.index_advisor import IndexAdvisor, IndexRecommendation
from screenshot2sql_conve.data_dict import DataDictExporter
from screenshot2sql_conve.prisma_exporter import PrismaExporter

__all__ = [
    "ScreenshotAnalyzer",
    "SchemaGenerator",
    "MermaidExporter",
    "SQLAlchemyExporter",
    "SchemaDiffer",
    "SchemaDiff",
    "IndexAdvisor",
    "IndexRecommendation",
    "DataDictExporter",
    "PrismaExporter",
]
