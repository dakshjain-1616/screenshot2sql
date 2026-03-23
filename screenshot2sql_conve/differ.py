"""
Schema differ: compare two UI analysis results to highlight structural changes.

Useful for product managers tracking how a SaaS data model evolves
across different versions or screenshots.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class FieldChange:
    name: str
    change_type: str  # "added" | "removed" | "type_changed" | "constraints_changed"
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None

    def describe(self) -> str:
        """Return a human-readable one-line description of this field change."""
        if self.change_type == "added":
            f = self.new_value or {}
            return f"+ {f.get('name', self.name)} {f.get('type', '')} {f.get('constraints', '')}".rstrip()
        if self.change_type == "removed":
            f = self.old_value or {}
            return f"- {f.get('name', self.name)} {f.get('type', '')}".rstrip()
        if self.change_type == "type_changed":
            return (
                f"~ {self.name}: type "
                f"{(self.old_value or {}).get('type', '?')} → "
                f"{(self.new_value or {}).get('type', '?')}"
            )
        if self.change_type == "constraints_changed":
            return (
                f"~ {self.name}: constraints "
                f'"{(self.old_value or {}).get("constraints", "")}" → '
                f'"{(self.new_value or {}).get("constraints", "")}"'
            )
        return f"? {self.name} ({self.change_type})"


@dataclass
class TableChange:
    name: str
    change_type: str  # "added" | "removed" | "modified"
    field_changes: list = field(default_factory=list)

    def describe(self) -> str:
        """Return a human-readable description of this table-level change."""
        if self.change_type == "added":
            return f"+ table {self.name} (new)"
        if self.change_type == "removed":
            return f"- table {self.name} (removed)"
        lines = [f"~ table {self.name}:"]
        for fc in self.field_changes:
            lines.append(f"    {fc.describe()}")
        return "\n".join(lines)


@dataclass
class SchemaDiff:
    old_ui_type: str
    new_ui_type: str
    compared_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    table_changes: list = field(default_factory=list)

    @property
    def added_tables(self) -> list:
        return [t.name for t in self.table_changes if t.change_type == "added"]

    @property
    def removed_tables(self) -> list:
        return [t.name for t in self.table_changes if t.change_type == "removed"]

    @property
    def modified_tables(self) -> list:
        return [t for t in self.table_changes if t.change_type == "modified"]

    @property
    def has_changes(self) -> bool:
        return bool(self.table_changes)

    def summary(self) -> str:
        """Return a plain-text summary of all schema changes."""
        parts = [
            f"Schema diff: {self.old_ui_type} → {self.new_ui_type}",
            f"Compared at: {self.compared_at}",
            "",
        ]
        if not self.has_changes:
            parts.append("No structural changes detected.")
            return "\n".join(parts)

        if self.added_tables:
            parts.append(f"Tables added ({len(self.added_tables)}): {', '.join(self.added_tables)}")
        if self.removed_tables:
            parts.append(f"Tables removed ({len(self.removed_tables)}): {', '.join(self.removed_tables)}")
        if self.modified_tables:
            parts.append(f"Tables modified ({len(self.modified_tables)}): {', '.join(t.name for t in self.modified_tables)}")

        total_field_changes = sum(
            len(t.field_changes) for t in self.modified_tables
        )
        if total_field_changes:
            parts.append(f"Field-level changes: {total_field_changes}")
        return "\n".join(parts)

    def to_markdown(self) -> str:
        lines = [
            f"# Schema Diff Report",
            f"",
            f"| | Value |",
            f"|---|---|",
            f"| **Before** | {self.old_ui_type} |",
            f"| **After** | {self.new_ui_type} |",
            f"| **Compared at** | {self.compared_at} |",
            f"",
        ]

        if not self.has_changes:
            lines.append("_No structural changes detected between these schemas._")
            return "\n".join(lines)

        if self.added_tables:
            lines.append("## Tables Added")
            for name in self.added_tables:
                lines.append(f"- `{name}`")
            lines.append("")

        if self.removed_tables:
            lines.append("## Tables Removed")
            for name in self.removed_tables:
                lines.append(f"- `{name}`")
            lines.append("")

        if self.modified_tables:
            lines.append("## Tables Modified")
            for tc in self.modified_tables:
                lines.append(f"### `{tc.name}`")
                lines.append("")
                lines.append("| Change | Field | Old | New |")
                lines.append("|--------|-------|-----|-----|")
                for fc in tc.field_changes:
                    if fc.change_type == "added":
                        f = fc.new_value or {}
                        lines.append(
                            f"| ➕ Added | `{fc.name}` | — | `{f.get('type','')}` {f.get('constraints','')} |"
                        )
                    elif fc.change_type == "removed":
                        f = fc.old_value or {}
                        lines.append(
                            f"| ➖ Removed | `{fc.name}` | `{f.get('type','')}` | — |"
                        )
                    elif fc.change_type == "type_changed":
                        lines.append(
                            f"| 🔄 Type | `{fc.name}` | `{(fc.old_value or {}).get('type','')}` | `{(fc.new_value or {}).get('type','')}` |"
                        )
                    elif fc.change_type == "constraints_changed":
                        lines.append(
                            f"| ⚙️ Constraints | `{fc.name}` | `{(fc.old_value or {}).get('constraints','')}` | `{(fc.new_value or {}).get('constraints','')}` |"
                        )
                lines.append("")

        return "\n".join(lines)


class SchemaDiffer:
    """Compares two analysis results and returns a SchemaDiff."""

    def _index_entities(self, analysis: dict) -> dict:
        """Build a lookup of {table_name: {field_name: field_dict}} from an analysis result."""
        result = {}
        for entity in analysis.get("entities", []):
            fields = {f["name"]: f for f in entity.get("fields", [])}
            result[entity["name"]] = fields
        return result

    def compare(self, old_analysis: dict, new_analysis: dict) -> SchemaDiff:
        """Compare two analysis results. Returns a SchemaDiff."""
        old_entities = self._index_entities(old_analysis)
        new_entities = self._index_entities(new_analysis)

        old_names = set(old_entities)
        new_names = set(new_entities)

        table_changes = []

        # Removed tables
        for name in sorted(old_names - new_names):
            table_changes.append(TableChange(name=name, change_type="removed"))

        # Added tables
        for name in sorted(new_names - old_names):
            table_changes.append(TableChange(name=name, change_type="added"))

        # Modified tables (in both, check field-level diffs)
        for name in sorted(old_names & new_names):
            old_fields = old_entities[name]
            new_fields = new_entities[name]
            field_changes = []

            # Removed fields
            for fname in sorted(set(old_fields) - set(new_fields)):
                field_changes.append(
                    FieldChange(
                        name=fname,
                        change_type="removed",
                        old_value=old_fields[fname],
                    )
                )

            # Added fields
            for fname in sorted(set(new_fields) - set(old_fields)):
                field_changes.append(
                    FieldChange(
                        name=fname,
                        change_type="added",
                        new_value=new_fields[fname],
                    )
                )

            # Changed fields
            for fname in sorted(set(old_fields) & set(new_fields)):
                of = old_fields[fname]
                nf = new_fields[fname]
                if of.get("type", "") != nf.get("type", ""):
                    field_changes.append(
                        FieldChange(
                            name=fname,
                            change_type="type_changed",
                            old_value=of,
                            new_value=nf,
                        )
                    )
                elif of.get("constraints", "") != nf.get("constraints", ""):
                    field_changes.append(
                        FieldChange(
                            name=fname,
                            change_type="constraints_changed",
                            old_value=of,
                            new_value=nf,
                        )
                    )

            if field_changes:
                table_changes.append(
                    TableChange(
                        name=name,
                        change_type="modified",
                        field_changes=field_changes,
                    )
                )

        return SchemaDiff(
            old_ui_type=old_analysis.get("ui_type", "Unknown"),
            new_ui_type=new_analysis.get("ui_type", "Unknown"),
            table_changes=table_changes,
        )
