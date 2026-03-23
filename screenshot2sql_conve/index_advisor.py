"""
Index advisor: recommends CREATE INDEX statements based on schema analysis.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class IndexRecommendation:
    """Recommended index details."""
    table: str
    column: str
    priority: str  # "high" | "medium"
    reason: str
    index_sql: str = ""

    def describe(self) -> str:
        """Human-readable description of the recommendation."""
        return f"{self.priority.upper()} priority: {self.table}.{self.column} ({self.reason})"


class IndexAdvisor:
    """Analyzes a schema and recommends indexes."""

    def recommend(self, analysis: dict) -> List[IndexRecommendation]:
        """Generate index recommendations based on schema analysis."""
        recommendations = []
        
        # Add foreign key indexes (high priority)
        for entity in analysis.get("entities", []):
            for field in entity.get("fields", []):
                if "references" in field.get("constraints", "").lower():
                    sql = f"CREATE INDEX idx_{entity['name']}_{field['name']} ON {entity['name']}({field['name']});"
                    recommendations.append(
                        IndexRecommendation(
                            table=entity["name"],
                            column=field["name"],
                            priority="high",
                            reason="foreign key",
                            index_sql=sql
                        )
                    )

        # Add indexes for external reference ID columns (high priority)
        for entity in analysis.get("entities", []):
            for field in entity.get("fields", []):
                name = field["name"].lower()
                constraints = field.get("constraints", "").lower()
                # Skip primary keys and FK columns (already handled above)
                if name == "id" or "references" in constraints:
                    continue
                # Columns ending in _id are external lookup keys
                if name.endswith("_id"):
                    sql = f"CREATE INDEX idx_{entity['name']}_{field['name']} ON {entity['name']}({field['name']});"
                    recommendations.append(
                        IndexRecommendation(
                            table=entity["name"],
                            column=field["name"],
                            priority="high",
                            reason="external reference key",
                            index_sql=sql
                        )
                    )

        # Add indexes for columns frequently used in queries (medium priority)
        for query in analysis.get("sample_queries", []):
            sql = query["sql"].lower()
            for entity in analysis.get("entities", []):
                for field in entity.get("fields", []):
                    if field["name"].lower() in sql and f"where {field['name']}" in sql:
                        sql = f"CREATE INDEX idx_{entity['name']}_{field['name']} ON {entity['name']}({field['name']});"
                        recommendations.append(
                            IndexRecommendation(
                                table=entity["name"],
                                column=field["name"],
                                priority="medium",
                                reason="frequently queried",
                                index_sql=sql
                            )
                        )

        # Deduplicate recommendations
        unique_recs = {}
        for rec in recommendations:
            key = (rec.table, rec.column)
            if key not in unique_recs or rec.priority == "high":
                unique_recs[key] = rec
        
        return list(unique_recs.values())

    def format_sql(self, recommendations: List[IndexRecommendation]) -> str:
        """Format recommendations as SQL CREATE INDEX statements."""
        if not recommendations:
            return "No index recommendations"
        return "\n".join(r.index_sql for r in recommendations)

    def format_markdown(self, recommendations: List[IndexRecommendation]) -> str:
        """Format recommendations as a Markdown table."""
        if not recommendations:
            return "No index recommendations"

        md = "## Index Recommendations\n\n"
        md += "| Priority | Table | Column | Reason |\n"
        md += "|----------|-------|--------|--------|\n"
        for r in sorted(recommendations, key=lambda x: (-len(x.priority), x.table, x.column)):
            md += f"| {r.priority} | `{r.table}` | `{r.column}` | {r.reason} |\n"
        return md


