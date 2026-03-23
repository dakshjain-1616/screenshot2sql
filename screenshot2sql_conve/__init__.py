"""Screenshot2SQL - Convert UI screenshots to database schemas."""

__version__ = "0.3.0"
__author__ = "NEO"

from .analyzer import ScreenshotAnalyzer
from .schema import SchemaGenerator
from .exporter import MermaidExporter, SQLAlchemyExporter
from .differ import SchemaDiffer, SchemaDiff
from .index_advisor import IndexAdvisor, IndexRecommendation
from .data_dict import DataDictExporter
from .prisma_exporter import PrismaExporter

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
