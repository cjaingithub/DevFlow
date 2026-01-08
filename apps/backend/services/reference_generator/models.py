#!/usr/bin/env python3
"""
Reference Generator Models
==========================

Data models for the Reference-Based Code Generation feature.

These models represent:
- Reference projects (complete implementations to learn from)
- Code patterns (extracted reusable patterns)
- SQL transformations
- Generation results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


# =============================================================================
# ENUMS
# =============================================================================


class PatternType(str, Enum):
    """Types of code patterns that can be extracted."""

    SERVICE_CLASS = "service_class"
    REPOSITORY = "repository"
    CONTROLLER = "controller"
    DATABASE_MODEL = "database_model"
    API_ENDPOINT = "api_endpoint"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AUTHENTICATION = "authentication"
    ERROR_HANDLING = "error_handling"
    UTILITY = "utility"
    # Infrastructure patterns
    LAMBDA_FUNCTION = "lambda_function"
    GLUE_JOB = "glue_job"
    STEP_FUNCTION = "step_function"
    TERRAFORM_RESOURCE = "terraform_resource"
    # Caching patterns
    LRU_CACHE = "lru_cache"
    TTL_CACHE = "ttl_cache"
    REDIS_CACHE = "redis_cache"
    CACHE_ASIDE = "cache_aside"
    # Context patterns
    CONTEXT_MANAGER = "context_manager"
    CONTEXT_VAR = "context_var"
    TRANSACTION_CONTEXT = "transaction_context"


class FileType(str, Enum):
    """Types of files in a reference project."""

    REQUIREMENTS = "requirements"
    SQL_SCHEMA = "sql_schema"
    SQL_MIGRATION = "sql_migration"
    SQL_PROCEDURE = "sql_procedure"
    PYTHON_SERVICE = "python_service"
    PYTHON_REPOSITORY = "python_repository"
    PYTHON_MODEL = "python_model"
    PYTHON_CONTROLLER = "python_controller"
    PYTHON_TEST = "python_test"
    TERRAFORM = "terraform"
    GLUE_SCRIPT = "glue_script"
    LAMBDA_HANDLER = "lambda_handler"
    STEP_FUNCTION_DEF = "step_function_def"
    CONFIG = "config"
    OTHER = "other"


class TechStack(str, Enum):
    """Technology stack identifiers."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    TERRAFORM = "terraform"
    AWS_CDK = "aws_cdk"
    SERVERLESS = "serverless"
    DOCKER = "docker"
    REDIS = "redis"
    DYNAMODB = "dynamodb"


# =============================================================================
# REFERENCE FILE MODELS
# =============================================================================


@dataclass
class ReferenceFile:
    """A single file in a reference project."""

    path: str
    content: str
    file_type: FileType = FileType.OTHER
    language: str = ""
    patterns_found: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def extension(self) -> str:
        """Get file extension."""
        return Path(self.path).suffix.lower()

    @property
    def name(self) -> str:
        """Get file name without path."""
        return Path(self.path).name


# =============================================================================
# CODE PATTERN MODELS
# =============================================================================


@dataclass
class CodePattern:
    """
    An extracted code pattern from a reference file.

    Patterns are reusable code structures that can be adapted
    for new entities/features.
    """

    name: str
    pattern_type: PatternType
    source_file: str
    code_snippet: str
    entity_name: str  # The entity this pattern is for (e.g., "User", "Order")
    replaceable_tokens: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    description: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "pattern_type": self.pattern_type.value,
            "source_file": self.source_file,
            "code_snippet": self.code_snippet,
            "entity_name": self.entity_name,
            "replaceable_tokens": self.replaceable_tokens,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "description": self.description,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


# =============================================================================
# SQL MODELS
# =============================================================================


@dataclass
class SQLTable:
    """Represents a SQL table definition."""

    name: str
    columns: list[dict[str, Any]] = field(default_factory=list)
    primary_key: str = ""
    foreign_keys: list[dict[str, str]] = field(default_factory=list)
    indexes: list[str] = field(default_factory=list)
    original_sql: str = ""
    dialect: str = "postgresql"  # postgresql, mysql, oracle

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "columns": self.columns,
            "primary_key": self.primary_key,
            "foreign_keys": self.foreign_keys,
            "indexes": self.indexes,
            "dialect": self.dialect,
        }


@dataclass
class SQLTransformation:
    """Describes a SQL transformation from reference to target."""

    original_table: str
    new_table: str
    column_mappings: dict[str, str] = field(default_factory=dict)
    type_conversions: dict[str, str] = field(default_factory=dict)
    dialect_conversion: str = ""  # e.g., "oracle_to_postgresql"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_table": self.original_table,
            "new_table": self.new_table,
            "column_mappings": self.column_mappings,
            "type_conversions": self.type_conversions,
            "dialect_conversion": self.dialect_conversion,
        }


# =============================================================================
# ENTITY MAPPING MODELS
# =============================================================================


@dataclass
class EntityMapping:
    """Maps reference entities to new entities."""

    reference_name: str
    new_name: str
    additional_mappings: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reference_name": self.reference_name,
            "new_name": self.new_name,
            "additional_mappings": self.additional_mappings,
        }


@dataclass
class InfraEntityMapping(EntityMapping):
    """Extended mapping for infrastructure transformations."""

    resource_prefix: str = ""
    environment: str = "dev"
    region: str = "us-east-1"
    cache_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update(
            {
                "resource_prefix": self.resource_prefix,
                "environment": self.environment,
                "region": self.region,
                "cache_config": self.cache_config,
            }
        )
        return base


# =============================================================================
# REFERENCE PROJECT MODEL
# =============================================================================


@dataclass
class ReferenceProject:
    """
    A complete reference project that serves as a template.

    Contains:
    - Source files (requirements, SQL, code, tests)
    - Extracted patterns
    - Technology stack information
    - Usage metadata
    """

    name: str
    path: str
    description: str = ""
    files: list[ReferenceFile] = field(default_factory=list)
    patterns: list[CodePattern] = field(default_factory=list)
    sql_tables: list[SQLTable] = field(default_factory=list)
    tech_stack: list[TechStack] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    last_used: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "file_count": len(self.files),
            "pattern_count": len(self.patterns),
            "sql_table_count": len(self.sql_tables),
            "tech_stack": [t.value for t in self.tech_stack],
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "patterns": [p.to_dict() for p in self.patterns],
            "sql_tables": [t.to_dict() for t in self.sql_tables],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReferenceProject":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            path=data["path"],
            description=data.get("description", ""),
            tech_stack=[TechStack(t) for t in data.get("tech_stack", [])],
            requirements=data.get("requirements", []),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(),
            usage_count=data.get("usage_count", 0),
            last_used=datetime.fromisoformat(data["last_used"])
            if data.get("last_used")
            else None,
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# GENERATION RESULT MODELS
# =============================================================================


@dataclass
class GeneratedFile:
    """A file generated from patterns."""

    path: str
    content: str
    source_pattern: str
    file_type: FileType = FileType.OTHER
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "content": self.content,
            "source_pattern": self.source_pattern,
            "file_type": self.file_type.value,
            "confidence": self.confidence,
            "warnings": self.warnings,
        }


@dataclass
class GenerationResult:
    """Result of code generation from reference."""

    success: bool = False
    generated_files: list[GeneratedFile] = field(default_factory=list)
    sql_transformations: list[SQLTransformation] = field(default_factory=list)
    patterns_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "generated_files": [f.to_dict() for f in self.generated_files],
            "sql_transformations": [t.to_dict() for t in self.sql_transformations],
            "patterns_applied": self.patterns_applied,
            "warnings": self.warnings,
            "errors": self.errors,
            "execution_time_ms": self.execution_time_ms,
        }
