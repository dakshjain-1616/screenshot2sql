"""
SQL schema generator: converts analyzer output to DDL + sample queries.
"""

import json
import sqlite3
import tempfile
import os
from datetime import datetime, timezone
from typing import Optional


class SchemaGenerator:
    """Generates SQL DDL from entity definitions and validates it against SQLite."""

    def generate_create_table(self, entity: dict) -> str:
        """Generate a CREATE TABLE statement for one entity."""
        name = entity["name"]
        fields = entity.get("fields", [])

        lines = []
        for field in fields:
            field_name = field["name"]
            field_type = field["type"]
            constraints = field.get("constraints", "")
            col_def = f"    {field_name} {field_type}"
            if constraints:
                col_def += f" {constraints}"
            lines.append(col_def)

        col_block = ",\n".join(lines)
        ddl = f"CREATE TABLE IF NOT EXISTS {name} (\n{col_block}\n);"
        return ddl

    def generate_schema(self, analysis: dict) -> str:
        """
        Generate full SQL schema DDL from analysis result.

        Returns a string of CREATE TABLE statements.
        Raises ValueError if no UI was detected.
        """
        if not analysis.get("is_ui", False):
            error = analysis.get(
                "error",
                "No UI detected. Please upload a screenshot of a software application.",
            )
            raise ValueError(error)

        entities = analysis.get("entities", [])
        if not entities:
            raise ValueError("No entities found in analysis result.")

        analyzed_at = analysis.get("_analyzed_at", "")
        is_mock = analysis.get("_mock", False)
        model = analysis.get("_model", "")

        total_columns = sum(len(e.get("fields", [])) for e in entities)

        parts = [
            f"-- Schema for: {analysis.get('ui_type', 'Unknown UI')}",
            f"-- Confidence: {analysis.get('confidence', 0):.0%}",
            f"-- {analysis.get('description', '')}",
            f"-- Tables: {len(entities)}  |  Total columns: {total_columns}",
        ]
        if analyzed_at:
            parts.append(f"-- Analyzed at: {analyzed_at}")
        if model:
            parts.append(f"-- Model: {model}")
        if is_mock:
            parts.append("-- Mode: demo/mock")
        parts.append("")

        for entity in entities:
            comment = entity.get("description", "")
            field_count = len(entity.get("fields", []))
            if comment:
                parts.append(f"-- {comment} ({field_count} columns)")
            parts.append(self.generate_create_table(entity))
            parts.append("")

        return "\n".join(parts).rstrip() + "\n"

    def generate_sample_queries(self, analysis: dict) -> list:
        """Return list of {description, sql} dicts from analysis."""
        return analysis.get("sample_queries", [])

    def validate_schema(self, ddl: str) -> tuple:
        """
        Validate DDL by executing it against an in-memory SQLite database.

        Returns (is_valid, error_message).
        """
        try:
            conn = sqlite3.connect(":memory:")
            conn.executescript(ddl)
            conn.close()
            return True, None
        except sqlite3.Error as exc:
            return False, str(exc)

    def generate_sqlite_db(self, analysis: dict, db_path: Optional[str] = None) -> str:
        """
        Create a SQLite .db file with the schema.

        Returns path to the created file.
        """
        ddl = self.generate_schema(analysis)
        if db_path is None:
            fd, db_path = tempfile.mkstemp(suffix=".db", prefix="screenshot2sql_")
            os.close(fd)

        conn = sqlite3.connect(db_path)
        conn.executescript(ddl)
        conn.close()
        return db_path

    def get_stats(self, analysis: dict) -> dict:
        """
        Return a statistics dict summarising the analysis result.

        Keys: table_count, total_columns, fk_count, query_count,
              confidence, ui_type, analyzed_at, is_mock.
        """
        entities = analysis.get("entities", [])
        total_columns = sum(len(e.get("fields", [])) for e in entities)
        fk_count = sum(
            1
            for e in entities
            for f in e.get("fields", [])
            if "REFERENCES" in f.get("constraints", "").upper()
        )
        return {
            "ui_type": analysis.get("ui_type", "Unknown"),
            "confidence": analysis.get("confidence", 0.0),
            "table_count": len(entities),
            "total_columns": total_columns,
            "fk_count": fk_count,
            "query_count": len(analysis.get("sample_queries", [])),
            "analyzed_at": analysis.get("_analyzed_at", ""),
            "is_mock": analysis.get("_mock", False),
            "model": analysis.get("_model", ""),
        }

    def format_full_output(self, analysis: dict) -> str:
        """
        Format the complete output: schema + queries as a single SQL file string.
        """
        ddl = self.generate_schema(analysis)
        queries = self.generate_sample_queries(analysis)

        parts = [ddl]

        if queries:
            parts.append("\n-- ============================================================")
            parts.append("-- SAMPLE QUERIES")
            parts.append("-- ============================================================\n")
            for q in queries:
                parts.append(f"-- {q.get('description', 'Query')}")
                parts.append(q.get("sql", "").strip())
                parts.append("")

        return "\n".join(parts)

    def format_json_output(self, analysis: dict) -> str:
        """Return the raw analysis result as formatted JSON."""
        # Exclude internal _mock/_analyzed_at/_model for clean output but keep stats
        output = {k: v for k, v in analysis.items() if not k.startswith("_")}
        output["_meta"] = self.get_stats(analysis)
        return json.dumps(output, indent=2)
