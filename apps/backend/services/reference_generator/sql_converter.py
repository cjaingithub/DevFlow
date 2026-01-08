#!/usr/bin/env python3
"""
SQL Converter
=============

Transforms SQL schemas between dialects and performs entity substitution.

Supports:
- Oracle to PostgreSQL conversion
- MySQL to PostgreSQL conversion
- Table/column renaming
- Foreign key updates
- Migration script generation
"""

import re
from dataclasses import dataclass, field
from typing import Any

from .models import SQLTable, SQLTransformation


# =============================================================================
# TYPE MAPPINGS
# =============================================================================


# Oracle to PostgreSQL type mappings
ORACLE_TO_POSTGRES: dict[str, str] = {
    # Numeric types
    "NUMBER": "NUMERIC",
    "NUMBER(10)": "INTEGER",
    "NUMBER(19)": "BIGINT",
    "NUMBER(10,2)": "DECIMAL(10,2)",
    "NUMBER(19,2)": "DECIMAL(19,2)",
    "NUMBER(38)": "NUMERIC",
    "BINARY_FLOAT": "REAL",
    "BINARY_DOUBLE": "DOUBLE PRECISION",
    # String types
    "VARCHAR2": "VARCHAR",
    "NVARCHAR2": "VARCHAR",
    "CHAR": "CHAR",
    "NCHAR": "CHAR",
    "CLOB": "TEXT",
    "NCLOB": "TEXT",
    "LONG": "TEXT",
    # Date/Time types
    "DATE": "TIMESTAMP",
    "TIMESTAMP": "TIMESTAMP",
    "TIMESTAMP WITH TIME ZONE": "TIMESTAMPTZ",
    "TIMESTAMP WITH LOCAL TIME ZONE": "TIMESTAMPTZ",
    "INTERVAL YEAR TO MONTH": "INTERVAL",
    "INTERVAL DAY TO SECOND": "INTERVAL",
    # Binary types
    "BLOB": "BYTEA",
    "RAW": "BYTEA",
    "LONG RAW": "BYTEA",
    # Boolean (Oracle doesn't have native boolean)
    "NUMBER(1)": "BOOLEAN",
    # Special
    "ROWID": "TEXT",
    "UROWID": "TEXT",
    "XMLTYPE": "XML",
}

# MySQL to PostgreSQL type mappings
MYSQL_TO_POSTGRES: dict[str, str] = {
    # Numeric types
    "TINYINT": "SMALLINT",
    "SMALLINT": "SMALLINT",
    "MEDIUMINT": "INTEGER",
    "INT": "INTEGER",
    "INTEGER": "INTEGER",
    "BIGINT": "BIGINT",
    "DECIMAL": "DECIMAL",
    "NUMERIC": "NUMERIC",
    "FLOAT": "REAL",
    "DOUBLE": "DOUBLE PRECISION",
    "DOUBLE PRECISION": "DOUBLE PRECISION",
    # String types
    "VARCHAR": "VARCHAR",
    "CHAR": "CHAR",
    "TINYTEXT": "TEXT",
    "TEXT": "TEXT",
    "MEDIUMTEXT": "TEXT",
    "LONGTEXT": "TEXT",
    "ENUM": "VARCHAR(255)",
    "SET": "VARCHAR(255)",
    # Date/Time types
    "DATE": "DATE",
    "DATETIME": "TIMESTAMP",
    "TIMESTAMP": "TIMESTAMP",
    "TIME": "TIME",
    "YEAR": "SMALLINT",
    # Binary types
    "TINYBLOB": "BYTEA",
    "BLOB": "BYTEA",
    "MEDIUMBLOB": "BYTEA",
    "LONGBLOB": "BYTEA",
    "BINARY": "BYTEA",
    "VARBINARY": "BYTEA",
    # Boolean
    "BOOL": "BOOLEAN",
    "BOOLEAN": "BOOLEAN",
    # JSON
    "JSON": "JSONB",
}

# Oracle to PostgreSQL function mappings
ORACLE_FUNCTION_TO_POSTGRES: dict[str, str] = {
    "SYSDATE": "CURRENT_DATE",
    "SYSTIMESTAMP": "CURRENT_TIMESTAMP",
    "NVL": "COALESCE",
    "NVL2": "CASE WHEN",  # Needs special handling
    "DECODE": "CASE",  # Needs special handling
    "TO_CHAR": "TO_CHAR",
    "TO_DATE": "TO_DATE",
    "TO_NUMBER": "CAST",
    "SUBSTR": "SUBSTRING",
    "INSTR": "POSITION",
    "LENGTH": "LENGTH",
    "LPAD": "LPAD",
    "RPAD": "RPAD",
    "TRIM": "TRIM",
    "UPPER": "UPPER",
    "LOWER": "LOWER",
    "INITCAP": "INITCAP",
    "CONCAT": "CONCAT",
    "ROUND": "ROUND",
    "TRUNC": "TRUNC",
    "MOD": "MOD",
    "ABS": "ABS",
    "CEIL": "CEIL",
    "FLOOR": "FLOOR",
    "ROWNUM": "ROW_NUMBER() OVER ()",
    "DUAL": "(SELECT 1)",
}


# =============================================================================
# SQL CONVERTER CLASS
# =============================================================================


@dataclass
class ConversionResult:
    """Result of a SQL conversion."""

    success: bool = False
    converted_sql: str = ""
    transformations: list[SQLTransformation] = field(default_factory=list)
    tables_converted: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SQLConverter:
    """
    Converts SQL schemas between dialects with entity substitution.

    Usage:
        converter = SQLConverter()
        result = converter.convert_schema(
            original_sql=oracle_sql,
            table_mappings={"users": "products"},
            source_dialect="oracle",
            target_dialect="postgresql",
        )
    """

    def __init__(self) -> None:
        """Initialize the SQL converter."""
        self._type_mappings: dict[str, dict[str, str]] = {
            "oracle_to_postgresql": ORACLE_TO_POSTGRES,
            "mysql_to_postgresql": MYSQL_TO_POSTGRES,
        }

    def convert_schema(
        self,
        original_sql: str,
        table_mappings: dict[str, str] | None = None,
        column_mappings: dict[str, dict[str, str]] | None = None,
        source_dialect: str = "oracle",
        target_dialect: str = "postgresql",
    ) -> ConversionResult:
        """
        Convert SQL schema from one dialect to another.

        Args:
            original_sql: The original SQL schema
            table_mappings: Dict mapping old table names to new names
            column_mappings: Dict of table -> {old_col: new_col}
            source_dialect: Source SQL dialect
            target_dialect: Target SQL dialect

        Returns:
            ConversionResult with converted SQL and metadata
        """
        result = ConversionResult()
        table_mappings = table_mappings or {}
        column_mappings = column_mappings or {}

        try:
            converted = original_sql

            # Step 1: Convert data types
            type_key = f"{source_dialect}_to_{target_dialect}"
            if type_key in self._type_mappings:
                converted = self._convert_types(
                    converted, self._type_mappings[type_key]
                )

            # Step 2: Convert Oracle-specific syntax
            if source_dialect == "oracle":
                converted = self._convert_oracle_syntax(converted)

            # Step 3: Apply table name mappings
            for old_table, new_table in table_mappings.items():
                converted = self._replace_table_name(converted, old_table, new_table)
                result.transformations.append(
                    SQLTransformation(
                        original_table=old_table,
                        new_table=new_table,
                        dialect_conversion=type_key,
                    )
                )
                result.tables_converted.append(f"{old_table} -> {new_table}")

            # Step 4: Apply column name mappings
            for table, cols in column_mappings.items():
                for old_col, new_col in cols.items():
                    converted = self._replace_column_name(
                        converted, table, old_col, new_col
                    )
                    # Update transformation
                    for t in result.transformations:
                        if t.original_table == table:
                            t.column_mappings[old_col] = new_col

            # Step 5: Convert sequence/identity syntax
            if source_dialect == "oracle" and target_dialect == "postgresql":
                converted = self._convert_sequences(converted)

            # Step 6: Clean up and format
            converted = self._clean_sql(converted)

            result.success = True
            result.converted_sql = converted

        except Exception as e:
            result.errors.append(f"Conversion failed: {str(e)}")

        return result

    def _convert_types(self, sql: str, type_map: dict[str, str]) -> str:
        """Convert data types using the provided mapping."""
        converted = sql

        # Sort by length descending to match longer types first
        sorted_types = sorted(type_map.keys(), key=len, reverse=True)

        for oracle_type, pg_type in [(t, type_map[t]) for t in sorted_types]:
            # Match type with optional size specification
            pattern = rf"\b{re.escape(oracle_type)}\b(\([^)]+\))?"
            converted = re.sub(
                pattern,
                lambda m: pg_type + (m.group(1) or ""),
                converted,
                flags=re.IGNORECASE,
            )

        return converted

    def _convert_oracle_syntax(self, sql: str) -> str:
        """Convert Oracle-specific syntax to PostgreSQL."""
        converted = sql

        # Convert SYSDATE/SYSTIMESTAMP
        converted = re.sub(
            r"\bSYSDATE\b", "CURRENT_DATE", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\bSYSTIMESTAMP\b", "CURRENT_TIMESTAMP", converted, flags=re.IGNORECASE
        )

        # Convert NVL to COALESCE
        converted = re.sub(
            r"\bNVL\s*\(", "COALESCE(", converted, flags=re.IGNORECASE
        )

        # Remove Oracle-specific storage clauses
        converted = re.sub(
            r"\s+TABLESPACE\s+\w+", "", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\s+STORAGE\s*\([^)]+\)", "", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\s+PCTFREE\s+\d+", "", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\s+PCTUSED\s+\d+", "", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\s+INITRANS\s+\d+", "", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\s+MAXTRANS\s+\d+", "", converted, flags=re.IGNORECASE
        )

        # Convert VARCHAR2 to VARCHAR
        converted = re.sub(
            r"\bVARCHAR2\b", "VARCHAR", converted, flags=re.IGNORECASE
        )

        # Convert NUMBER types
        converted = re.sub(
            r"\bNUMBER\(10\)\b", "INTEGER", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\bNUMBER\(19\)\b", "BIGINT", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\bNUMBER\(1\)\b", "BOOLEAN", converted, flags=re.IGNORECASE
        )
        converted = re.sub(
            r"\bNUMBER\((\d+),\s*(\d+)\)",
            r"DECIMAL(\1,\2)",
            converted,
            flags=re.IGNORECASE,
        )
        converted = re.sub(
            r"\bNUMBER\b", "NUMERIC", converted, flags=re.IGNORECASE
        )

        return converted

    def _convert_sequences(self, sql: str) -> str:
        """Convert Oracle sequences to PostgreSQL SERIAL/IDENTITY."""
        converted = sql

        # Pattern: column_name NUMBER DEFAULT seq_name.NEXTVAL
        # Replace with: column_name SERIAL
        converted = re.sub(
            r"(\w+)\s+(?:NUMBER|INTEGER)\s+DEFAULT\s+\w+\.NEXTVAL",
            r"\1 SERIAL",
            converted,
            flags=re.IGNORECASE,
        )

        # Remove standalone CREATE SEQUENCE statements if using SERIAL
        # (optional - sometimes you want to keep them)

        return converted

    def _replace_table_name(
        self, sql: str, old_name: str, new_name: str
    ) -> str:
        """Replace table name throughout SQL."""
        # Match table name as whole word
        pattern = rf"\b{re.escape(old_name)}\b"
        return re.sub(pattern, new_name, sql, flags=re.IGNORECASE)

    def _replace_column_name(
        self, sql: str, table: str, old_col: str, new_col: str
    ) -> str:
        """Replace column name for a specific table."""
        # Simple replacement - could be enhanced with context awareness
        pattern = rf"\b{re.escape(old_col)}\b"
        return re.sub(pattern, new_col, sql, flags=re.IGNORECASE)

    def _clean_sql(self, sql: str) -> str:
        """Clean up and format the converted SQL."""
        # Remove extra whitespace
        sql = re.sub(r"\n\s*\n\s*\n", "\n\n", sql)
        # Ensure statements end with semicolon and newline
        sql = re.sub(r";\s*$", ";\n", sql, flags=re.MULTILINE)
        return sql.strip()

    def parse_create_table(self, sql: str) -> list[SQLTable]:
        """
        Parse CREATE TABLE statements from SQL.

        Args:
            sql: SQL containing CREATE TABLE statements

        Returns:
            List of SQLTable objects
        """
        tables: list[SQLTable] = []

        # Find all CREATE TABLE statements
        pattern = r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^;]+)\)"
        matches = re.finditer(pattern, sql, re.IGNORECASE | re.DOTALL)

        for match in matches:
            table_name = match.group(1)
            columns_str = match.group(2)

            table = SQLTable(
                name=table_name,
                original_sql=match.group(0),
            )

            # Parse columns
            table.columns = self._parse_columns(columns_str)

            # Find primary key
            pk_match = re.search(
                r"PRIMARY\s+KEY\s*\((\w+)\)",
                columns_str,
                re.IGNORECASE,
            )
            if pk_match:
                table.primary_key = pk_match.group(1)
            else:
                # Check for inline PRIMARY KEY
                for col in table.columns:
                    if col.get("primary_key"):
                        table.primary_key = col["name"]
                        break

            # Find foreign keys
            fk_matches = re.finditer(
                r"FOREIGN\s+KEY\s*\((\w+)\)\s*REFERENCES\s+(\w+)\s*\((\w+)\)",
                columns_str,
                re.IGNORECASE,
            )
            for fk in fk_matches:
                table.foreign_keys.append({
                    "column": fk.group(1),
                    "references_table": fk.group(2),
                    "references_column": fk.group(3),
                })

            tables.append(table)

        return tables

    def _parse_columns(self, columns_str: str) -> list[dict[str, Any]]:
        """Parse column definitions from a CREATE TABLE body."""
        columns: list[dict[str, Any]] = []

        # Split by commas, but not commas inside parentheses
        parts = re.split(r",(?![^()]*\))", columns_str)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Skip constraints
            if re.match(
                r"^\s*(PRIMARY|FOREIGN|UNIQUE|CHECK|CONSTRAINT)",
                part,
                re.IGNORECASE,
            ):
                continue

            # Parse column definition
            col_match = re.match(
                r"(\w+)\s+(\w+(?:\([^)]+\))?)\s*(.*)",
                part,
                re.IGNORECASE,
            )
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                col_attrs = col_match.group(3)

                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "nullable": "NOT NULL" not in col_attrs.upper(),
                    "primary_key": "PRIMARY KEY" in col_attrs.upper(),
                    "unique": "UNIQUE" in col_attrs.upper(),
                    "default": self._extract_default(col_attrs),
                })

        return columns

    def _extract_default(self, attrs: str) -> str | None:
        """Extract DEFAULT value from column attributes."""
        match = re.search(
            r"DEFAULT\s+([^,\s]+(?:\([^)]*\))?)",
            attrs,
            re.IGNORECASE,
        )
        return match.group(1) if match else None

    def generate_migration(
        self,
        from_tables: list[SQLTable],
        to_tables: list[SQLTable],
    ) -> str:
        """
        Generate migration SQL between two table states.

        Args:
            from_tables: Original table definitions
            to_tables: Target table definitions

        Returns:
            SQL migration script
        """
        lines: list[str] = []
        lines.append("-- Migration Script")
        lines.append("-- Generated by ReferenceGenerator SQLConverter")
        lines.append("")

        from_dict = {t.name.lower(): t for t in from_tables}
        to_dict = {t.name.lower(): t for t in to_tables}

        # Find new tables
        for name, table in to_dict.items():
            if name not in from_dict:
                lines.append(f"-- Create new table: {table.name}")
                lines.append(table.original_sql)
                lines.append("")

        # Find dropped tables
        for name, table in from_dict.items():
            if name not in to_dict:
                lines.append(f"-- Drop table: {table.name}")
                lines.append(f"DROP TABLE IF EXISTS {table.name} CASCADE;")
                lines.append("")

        # Find renamed tables (tables that exist in both with mapped names)
        # This is handled by the conversion process

        return "\n".join(lines)


# =============================================================================
# STORED PROCEDURE CONVERTER
# =============================================================================


class StoredProcedureConverter:
    """
    Converts Oracle PL/SQL stored procedures to Python async methods.

    This is used for the Oracle-to-PostgreSQL migration pattern.
    """

    def __init__(self) -> None:
        """Initialize the converter."""
        pass

    def convert_to_python(
        self,
        procedure_sql: str,
        entity_mapping: dict[str, str] | None = None,
    ) -> str:
        """
        Convert a stored procedure to a Python async method.

        Args:
            procedure_sql: The PL/SQL procedure code
            entity_mapping: Mapping of old entity names to new ones

        Returns:
            Python async method code
        """
        entity_mapping = entity_mapping or {}

        # Extract procedure name and parameters
        proc_match = re.match(
            r"CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)\s*\(([^)]*)\)",
            procedure_sql,
            re.IGNORECASE,
        )
        if not proc_match:
            return "# Could not parse procedure"

        proc_name = proc_match.group(1)
        params_str = proc_match.group(2)

        # Convert procedure name
        method_name = self._convert_procedure_name(proc_name, entity_mapping)

        # Parse parameters
        params = self._parse_parameters(params_str, entity_mapping)
        in_params = [p for p in params if p["direction"] in ("IN", "INOUT")]
        out_params = [p for p in params if p["direction"] in ("OUT", "INOUT")]

        # Generate Python method signature
        param_str = ", ".join(
            f"{p['name']}: {p['python_type']}"
            for p in in_params
        )

        # Determine return type
        if len(out_params) == 0:
            return_type = "None"
        elif len(out_params) == 1:
            return_type = out_params[0]["python_type"]
        else:
            return_type = "dict[str, Any]"

        # Generate method
        lines: list[str] = []
        lines.append(f"    async def {method_name}(")
        lines.append(f"        self,")
        if param_str:
            lines.append(f"        {param_str},")
        lines.append(f"    ) -> {return_type}:")
        lines.append(f'        """')
        lines.append(f"        {self._generate_docstring(proc_name, in_params, out_params)}")
        lines.append(f"        Replaces Oracle {proc_name} procedure.")
        lines.append(f'        """')
        lines.append(f"        # TODO: Implement business logic")
        lines.append(f"        pass")

        return "\n".join(lines)

    def _convert_procedure_name(
        self, proc_name: str, entity_mapping: dict[str, str]
    ) -> str:
        """Convert procedure name to Python method name."""
        # Remove SP_ prefix
        name = proc_name
        if name.upper().startswith("SP_"):
            name = name[3:]

        # Convert to snake_case
        name = re.sub(r"([A-Z])", r"_\1", name).lower().lstrip("_")

        # Apply entity mapping
        for old, new in entity_mapping.items():
            name = name.replace(old.lower(), new.lower())

        return name

    def _parse_parameters(
        self,
        params_str: str,
        entity_mapping: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Parse procedure parameters."""
        params: list[dict[str, Any]] = []

        if not params_str.strip():
            return params

        # Split by comma (outside parentheses)
        parts = re.split(r",(?![^()]*\))", params_str)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Parse: p_name IN/OUT TYPE
            match = re.match(
                r"(\w+)\s+(IN(?:\s+OUT)?|OUT)?\s*(\w+(?:\([^)]+\))?)",
                part,
                re.IGNORECASE,
            )
            if match:
                param_name = match.group(1)
                direction = (match.group(2) or "IN").upper().replace(" ", "")
                oracle_type = match.group(3)

                # Convert parameter name
                py_name = param_name.lower()
                if py_name.startswith("p_"):
                    py_name = py_name[2:]

                # Apply entity mapping
                for old, new in entity_mapping.items():
                    py_name = py_name.replace(old.lower(), new.lower())

                params.append({
                    "name": py_name,
                    "direction": direction,
                    "oracle_type": oracle_type,
                    "python_type": self._oracle_type_to_python(oracle_type),
                })

        return params

    def _oracle_type_to_python(self, oracle_type: str) -> str:
        """Convert Oracle type to Python type hint."""
        type_upper = oracle_type.upper()

        if "NUMBER" in type_upper or "INT" in type_upper:
            return "int"
        if "VARCHAR" in type_upper or "CHAR" in type_upper:
            return "str"
        if "DATE" in type_upper or "TIMESTAMP" in type_upper:
            return "datetime"
        if "CLOB" in type_upper or "BLOB" in type_upper:
            return "bytes"
        if "CURSOR" in type_upper:
            return "list[dict[str, Any]]"
        if "BOOLEAN" in type_upper:
            return "bool"

        return "Any"

    def _generate_docstring(
        self,
        proc_name: str,
        in_params: list[dict[str, Any]],
        out_params: list[dict[str, Any]],
    ) -> str:
        """Generate docstring for the method."""
        parts: list[str] = []

        if in_params:
            parts.append("Args:")
            for p in in_params:
                parts.append(f"            {p['name']}: {p['python_type']}")

        if out_params:
            parts.append("        Returns:")
            if len(out_params) == 1:
                parts.append(f"            {out_params[0]['python_type']}")
            else:
                parts.append("            dict with: " + ", ".join(
                    p["name"] for p in out_params
                ))

        return "\n".join(parts) if parts else f"Converted from {proc_name}."


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def convert_oracle_to_postgres(
    sql: str,
    table_mappings: dict[str, str] | None = None,
    column_mappings: dict[str, dict[str, str]] | None = None,
) -> tuple[str, list[SQLTransformation]]:
    """
    Convenience function to convert Oracle SQL to PostgreSQL.

    Args:
        sql: Oracle SQL
        table_mappings: Table name mappings
        column_mappings: Column name mappings per table

    Returns:
        Tuple of (converted SQL, transformations applied)
    """
    converter = SQLConverter()
    result = converter.convert_schema(
        original_sql=sql,
        table_mappings=table_mappings,
        column_mappings=column_mappings,
        source_dialect="oracle",
        target_dialect="postgresql",
    )

    if not result.success:
        raise ValueError(f"Conversion failed: {result.errors}")

    return result.converted_sql, result.transformations
