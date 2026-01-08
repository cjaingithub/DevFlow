#!/usr/bin/env python3
"""
Pattern Extractor
=================

Extracts code patterns from reference files.

Identifies and extracts:
- Service classes
- Repository patterns
- Controller/handler patterns
- Database models
- API endpoints
- Validation logic
- Infrastructure patterns (Lambda, Glue, Terraform)
- Caching patterns
- Context managers
"""

import re
from pathlib import Path
from typing import Any

from .models import (
    CodePattern,
    FileType,
    PatternType,
    ReferenceFile,
    TechStack,
)


# =============================================================================
# PATTERN EXTRACTORS
# =============================================================================


class PatternExtractor:
    """
    Extracts reusable code patterns from reference files.

    Supports:
    - Python (services, repositories, models, tests)
    - SQL (schemas, procedures)
    - Terraform (resources, modules)
    - Glue scripts (PySpark ETL)
    - Lambda handlers
    """

    def __init__(self) -> None:
        """Initialize the pattern extractor."""
        self._entity_pattern = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b")
        self._class_pattern = re.compile(r"class\s+(\w+)")
        self._function_pattern = re.compile(r"def\s+(\w+)")
        self._terraform_resource_pattern = re.compile(
            r'resource\s+"(\w+)"\s+"(\w+)"'
        )
        self._decorator_pattern = re.compile(r"@(\w+)(?:\([^)]*\))?")

    def extract_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """
        Extract patterns from a reference file.

        Args:
            file: The reference file to extract patterns from

        Returns:
            List of extracted patterns
        """
        patterns: list[CodePattern] = []

        if file.extension in (".py", ".pyi"):
            patterns.extend(self._extract_python_patterns(file))
        elif file.extension in (".tf", ".tfvars"):
            patterns.extend(self._extract_terraform_patterns(file))
        elif file.extension in (".sql",):
            patterns.extend(self._extract_sql_patterns(file))
        elif file.extension in (".ts", ".tsx", ".js", ".jsx"):
            patterns.extend(self._extract_typescript_patterns(file))
        elif file.extension in (".json",):
            patterns.extend(self._extract_json_patterns(file))

        return patterns

    def detect_file_type(self, file_path: str, content: str) -> FileType:
        """
        Detect the type of file based on path and content.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Detected FileType
        """
        path = Path(file_path)
        name = path.name.lower()
        ext = path.suffix.lower()

        # Check by extension first
        if ext == ".tf":
            return FileType.TERRAFORM
        if ext == ".sql":
            if "CREATE TABLE" in content.upper():
                return FileType.SQL_SCHEMA
            if "CREATE OR REPLACE PROCEDURE" in content.upper():
                return FileType.SQL_PROCEDURE
            if "migration" in name or "migrate" in name:
                return FileType.SQL_MIGRATION
            return FileType.SQL_SCHEMA

        # Check Python files
        if ext == ".py":
            if "test_" in name or "_test" in name:
                return FileType.PYTHON_TEST
            if "service" in name:
                return FileType.PYTHON_SERVICE
            if "repository" in name or "repo" in name:
                return FileType.PYTHON_REPOSITORY
            if "model" in name or "models" in name:
                return FileType.PYTHON_MODEL
            if "controller" in name or "handler" in name:
                return FileType.PYTHON_CONTROLLER
            if "lambda" in name:
                return FileType.LAMBDA_HANDLER
            if "glue" in name or "etl" in name:
                return FileType.GLUE_SCRIPT
            # Check content for patterns
            if "GlueContext" in content:
                return FileType.GLUE_SCRIPT
            if "def handler(" in content or "def lambda_handler(" in content:
                return FileType.LAMBDA_HANDLER

        # Check for requirements/docs
        if name in ("requirements.md", "prd.md", "readme.md"):
            return FileType.REQUIREMENTS
        if name.endswith((".json", ".yaml", ".yml")) and "config" in name:
            return FileType.CONFIG

        return FileType.OTHER

    def detect_tech_stack(
        self, files: list[ReferenceFile]
    ) -> list[TechStack]:
        """
        Detect technology stack from files.

        Args:
            files: List of reference files

        Returns:
            List of detected TechStack values
        """
        stack: set[TechStack] = set()

        for file in files:
            content = file.content
            ext = file.extension

            # Language detection
            if ext in (".py", ".pyi"):
                stack.add(TechStack.PYTHON)
                if "sqlalchemy" in content.lower():
                    stack.add(TechStack.SQL)
                if "asyncpg" in content or "psycopg" in content:
                    stack.add(TechStack.POSTGRESQL)
                if "redis" in content.lower():
                    stack.add(TechStack.REDIS)
                if "boto3" in content:
                    if "dynamodb" in content.lower():
                        stack.add(TechStack.DYNAMODB)
                if "GlueContext" in content:
                    stack.add(TechStack.PYTHON)

            elif ext in (".ts", ".tsx"):
                stack.add(TechStack.TYPESCRIPT)

            elif ext in (".js", ".jsx"):
                stack.add(TechStack.JAVASCRIPT)

            elif ext == ".tf":
                stack.add(TechStack.TERRAFORM)
                if "aws_" in content:
                    # AWS resources
                    if "aws_dynamodb" in content:
                        stack.add(TechStack.DYNAMODB)
                    if "elasticache" in content.lower():
                        stack.add(TechStack.REDIS)

            elif ext == ".sql":
                stack.add(TechStack.SQL)
                if "VARCHAR2" in content or "NUMBER(" in content:
                    stack.add(TechStack.ORACLE)
                elif "SERIAL" in content or "BIGSERIAL" in content:
                    stack.add(TechStack.POSTGRESQL)

            elif file.name == "Dockerfile":
                stack.add(TechStack.DOCKER)

        return list(stack)

    # =========================================================================
    # PYTHON PATTERN EXTRACTION
    # =========================================================================

    def _extract_python_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract patterns from Python files."""
        patterns: list[CodePattern] = []
        content = file.content

        # Extract class-based patterns
        patterns.extend(self._extract_python_classes(file))

        # Extract decorator patterns (caching, context)
        patterns.extend(self._extract_decorator_patterns(file))

        # Extract context manager patterns
        patterns.extend(self._extract_context_patterns(file))

        return patterns

    def _extract_python_classes(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract class patterns from Python."""
        patterns: list[CodePattern] = []
        content = file.content

        # Find all class definitions
        class_matches = list(re.finditer(
            r"class\s+(\w+)(?:\([^)]*\))?:\s*\n((?:[ \t]+[^\n]*\n)*)",
            content,
            re.MULTILINE,
        ))

        for match in class_matches:
            class_name = match.group(1)
            class_body_start = match.start()

            # Find end of class (next class or end of file)
            class_end = len(content)
            for other_match in class_matches:
                if other_match.start() > class_body_start:
                    class_end = other_match.start()
                    break

            class_content = content[class_body_start:class_end].strip()

            # Determine pattern type from class name
            pattern_type = self._classify_class_pattern(class_name, class_content)

            # Extract entity name
            entity_name = self._extract_entity_from_class(class_name)

            # Find imports used by this class
            imports = self._extract_imports(content)

            # Find replaceable tokens
            tokens = self._find_replaceable_tokens(class_content, entity_name)

            patterns.append(
                CodePattern(
                    name=class_name,
                    pattern_type=pattern_type,
                    source_file=file.path,
                    code_snippet=class_content,
                    entity_name=entity_name,
                    replaceable_tokens=tokens,
                    imports=imports,
                    description=self._extract_docstring(class_content),
                    confidence=0.9,
                )
            )

        return patterns

    def _classify_class_pattern(
        self, class_name: str, content: str
    ) -> PatternType:
        """Classify a class into a pattern type."""
        name_lower = class_name.lower()

        if "service" in name_lower:
            return PatternType.SERVICE_CLASS
        if "repository" in name_lower or "repo" in name_lower:
            return PatternType.REPOSITORY
        if "controller" in name_lower or "handler" in name_lower:
            return PatternType.CONTROLLER
        if "model" in name_lower:
            return PatternType.DATABASE_MODEL
        if "validator" in name_lower or "validation" in name_lower:
            return PatternType.VALIDATION
        if "cache" in name_lower:
            return PatternType.REDIS_CACHE
        if "context" in name_lower:
            if "transaction" in name_lower:
                return PatternType.TRANSACTION_CONTEXT
            return PatternType.CONTEXT_MANAGER

        # Check content for patterns
        if "@lru_cache" in content:
            return PatternType.LRU_CACHE
        if "TTLCache" in content or "@cached" in content:
            return PatternType.TTL_CACHE
        if "redis" in content.lower() and "cache" in content.lower():
            return PatternType.CACHE_ASIDE
        if "__aenter__" in content or "__enter__" in content:
            return PatternType.CONTEXT_MANAGER

        return PatternType.UTILITY

    def _extract_entity_from_class(self, class_name: str) -> str:
        """Extract entity name from class name."""
        # Remove common suffixes
        suffixes = [
            "Service", "Repository", "Repo", "Controller",
            "Handler", "Model", "Validator", "Cache", "Context",
            "Manager", "Factory", "Builder", "Client",
        ]

        entity = class_name
        for suffix in suffixes:
            if entity.endswith(suffix):
                entity = entity[: -len(suffix)]
                break

        return entity if entity else class_name

    def _extract_decorator_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract decorator-based patterns (caching, etc.)."""
        patterns: list[CodePattern] = []
        content = file.content

        # Find lru_cache patterns
        lru_matches = re.finditer(
            r"(@lru_cache\([^)]*\)\s*\n\s*def\s+(\w+)[^:]*:.*?(?=\n(?:@|\s*def\s|\s*class\s|$)))",
            content,
            re.DOTALL,
        )

        for match in lru_matches:
            func_name = match.group(2)
            snippet = match.group(0).strip()

            patterns.append(
                CodePattern(
                    name=f"{func_name}_lru_cache",
                    pattern_type=PatternType.LRU_CACHE,
                    source_file=file.path,
                    code_snippet=snippet,
                    entity_name=self._extract_entity_from_function(func_name),
                    imports=["from functools import lru_cache"],
                    description=f"LRU cached function: {func_name}",
                    confidence=0.95,
                )
            )

        # Find TTL cache patterns
        ttl_matches = re.finditer(
            r"(@cached\(cache=TTLCache[^)]*\)\s*\n\s*def\s+(\w+)[^:]*:.*?(?=\n(?:@|\s*def\s|\s*class\s|$)))",
            content,
            re.DOTALL,
        )

        for match in ttl_matches:
            func_name = match.group(2)
            snippet = match.group(0).strip()

            patterns.append(
                CodePattern(
                    name=f"{func_name}_ttl_cache",
                    pattern_type=PatternType.TTL_CACHE,
                    source_file=file.path,
                    code_snippet=snippet,
                    entity_name=self._extract_entity_from_function(func_name),
                    imports=[
                        "from cachetools import TTLCache, cached",
                    ],
                    description=f"TTL cached function: {func_name}",
                    confidence=0.95,
                )
            )

        return patterns

    def _extract_context_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract context manager patterns."""
        patterns: list[CodePattern] = []
        content = file.content

        # Find ContextVar patterns
        contextvar_matches = re.finditer(
            r"(\w+_context)\s*:\s*ContextVar\[(\w+)\]\s*=\s*ContextVar\([^)]+\)",
            content,
        )

        for match in contextvar_matches:
            var_name = match.group(1)
            type_name = match.group(2)

            patterns.append(
                CodePattern(
                    name=var_name,
                    pattern_type=PatternType.CONTEXT_VAR,
                    source_file=file.path,
                    code_snippet=match.group(0),
                    entity_name=self._extract_entity_from_class(type_name),
                    imports=["from contextvars import ContextVar"],
                    description=f"Context variable for {type_name}",
                    confidence=0.9,
                )
            )

        # Find asynccontextmanager patterns
        async_ctx_matches = re.finditer(
            r"(@asynccontextmanager\s*\n\s*async\s+def\s+(\w+)[^:]*:.*?(?=\n(?:@|\s*(?:async\s+)?def\s|\s*class\s|$)))",
            content,
            re.DOTALL,
        )

        for match in async_ctx_matches:
            func_name = match.group(2)
            snippet = match.group(0).strip()

            patterns.append(
                CodePattern(
                    name=func_name,
                    pattern_type=PatternType.CONTEXT_MANAGER,
                    source_file=file.path,
                    code_snippet=snippet,
                    entity_name=self._extract_entity_from_function(func_name),
                    imports=["from contextlib import asynccontextmanager"],
                    description=f"Async context manager: {func_name}",
                    confidence=0.9,
                )
            )

        return patterns

    def _extract_entity_from_function(self, func_name: str) -> str:
        """Extract entity name from function name."""
        # Remove common prefixes
        prefixes = [
            "get_", "set_", "create_", "update_", "delete_",
            "fetch_", "save_", "load_", "process_", "handle_",
        ]

        entity = func_name
        for prefix in prefixes:
            if entity.startswith(prefix):
                entity = entity[len(prefix):]
                break

        # Remove common suffixes
        suffixes = ["_by_id", "_all", "_list", "_context", "_cache"]
        for suffix in suffixes:
            if entity.endswith(suffix):
                entity = entity[: -len(suffix)]
                break

        return entity.title().replace("_", "")

    # =========================================================================
    # TERRAFORM PATTERN EXTRACTION
    # =========================================================================

    def _extract_terraform_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract patterns from Terraform files."""
        patterns: list[CodePattern] = []
        content = file.content

        # Find resource blocks
        resource_matches = re.finditer(
            r'(resource\s+"(\w+)"\s+"(\w+)"\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\})',
            content,
            re.MULTILINE,
        )

        for match in resource_matches:
            full_block = match.group(1)
            resource_type = match.group(2)
            resource_name = match.group(3)

            pattern_type = self._classify_terraform_resource(resource_type)
            entity = self._extract_entity_from_terraform(resource_name)

            patterns.append(
                CodePattern(
                    name=f"{resource_type}.{resource_name}",
                    pattern_type=pattern_type,
                    source_file=file.path,
                    code_snippet=full_block,
                    entity_name=entity,
                    replaceable_tokens=self._find_terraform_tokens(full_block, entity),
                    description=f"Terraform {resource_type}: {resource_name}",
                    confidence=0.95,
                    metadata={"resource_type": resource_type},
                )
            )

        return patterns

    def _classify_terraform_resource(self, resource_type: str) -> PatternType:
        """Classify Terraform resource type."""
        if "aws_lambda" in resource_type:
            return PatternType.LAMBDA_FUNCTION
        if "aws_glue" in resource_type:
            return PatternType.GLUE_JOB
        if "aws_sfn" in resource_type:
            return PatternType.STEP_FUNCTION
        return PatternType.TERRAFORM_RESOURCE

    def _extract_entity_from_terraform(self, resource_name: str) -> str:
        """Extract entity name from Terraform resource name."""
        # Common patterns: process_orders, orders_etl, orders_lambda
        parts = resource_name.split("_")
        # Skip action words
        skip_words = {"process", "lambda", "etl", "job", "workflow", "function"}
        entity_parts = [p for p in parts if p.lower() not in skip_words]
        return "_".join(entity_parts) if entity_parts else resource_name

    def _find_terraform_tokens(
        self, content: str, entity: str
    ) -> list[str]:
        """Find replaceable tokens in Terraform content."""
        tokens: list[str] = []
        entity_lower = entity.lower()

        # Find string references to entity
        string_matches = re.findall(r'"[^"]*' + entity_lower + r'[^"]*"', content)
        tokens.extend(set(string_matches))

        # Find variable references
        var_matches = re.findall(r'\$\{[^}]*' + entity_lower + r'[^}]*\}', content)
        tokens.extend(set(var_matches))

        return tokens

    # =========================================================================
    # SQL PATTERN EXTRACTION
    # =========================================================================

    def _extract_sql_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract patterns from SQL files."""
        patterns: list[CodePattern] = []
        content = file.content

        # Extract stored procedures
        proc_matches = re.finditer(
            r"(CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)[^;]*;)",
            content,
            re.IGNORECASE | re.DOTALL,
        )

        for match in proc_matches:
            proc_content = match.group(1)
            proc_name = match.group(2)

            # Extract entity from procedure name (e.g., SP_CREATE_ORDER -> Order)
            entity = self._extract_entity_from_procedure(proc_name)

            patterns.append(
                CodePattern(
                    name=proc_name,
                    pattern_type=PatternType.UTILITY,  # SQL procedures
                    source_file=file.path,
                    code_snippet=proc_content,
                    entity_name=entity,
                    description=f"SQL Procedure: {proc_name}",
                    confidence=0.9,
                    metadata={"sql_type": "procedure"},
                )
            )

        return patterns

    def _extract_entity_from_procedure(self, proc_name: str) -> str:
        """Extract entity from procedure name."""
        # Remove SP_ prefix and action suffixes
        name = proc_name.upper()
        if name.startswith("SP_"):
            name = name[3:]

        # Remove action words
        actions = ["CREATE", "UPDATE", "DELETE", "GET", "FETCH", "INSERT"]
        for action in actions:
            if name.startswith(action + "_"):
                name = name[len(action) + 1:]
                break

        # Convert to title case
        return name.replace("_", " ").title().replace(" ", "")

    # =========================================================================
    # TYPESCRIPT/JAVASCRIPT PATTERN EXTRACTION
    # =========================================================================

    def _extract_typescript_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract patterns from TypeScript/JavaScript files."""
        patterns: list[CodePattern] = []
        content = file.content

        # Find class definitions
        class_matches = re.finditer(
            r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{",
            content,
        )

        for match in class_matches:
            class_name = match.group(1)
            class_start = match.start()

            # Find matching closing brace
            brace_count = 0
            class_end = class_start
            for i, char in enumerate(content[class_start:], class_start):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i + 1
                        break

            class_content = content[class_start:class_end]
            pattern_type = self._classify_class_pattern(class_name, class_content)
            entity = self._extract_entity_from_class(class_name)

            patterns.append(
                CodePattern(
                    name=class_name,
                    pattern_type=pattern_type,
                    source_file=file.path,
                    code_snippet=class_content,
                    entity_name=entity,
                    description=f"TypeScript class: {class_name}",
                    confidence=0.85,
                )
            )

        return patterns

    # =========================================================================
    # JSON PATTERN EXTRACTION
    # =========================================================================

    def _extract_json_patterns(
        self, file: ReferenceFile
    ) -> list[CodePattern]:
        """Extract patterns from JSON files (Step Functions, etc.)."""
        patterns: list[CodePattern] = []
        content = file.content

        # Check if it's a Step Functions definition
        if '"States"' in content and '"StartAt"' in content:
            patterns.append(
                CodePattern(
                    name=file.name.replace(".json", ""),
                    pattern_type=PatternType.STEP_FUNCTION,
                    source_file=file.path,
                    code_snippet=content,
                    entity_name=self._extract_entity_from_function(
                        file.name.replace(".json", "")
                    ),
                    description="Step Functions state machine definition",
                    confidence=0.9,
                    metadata={"type": "step_functions"},
                )
            )

        return patterns

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements from content."""
        imports: list[str] = []

        # Python imports
        import_matches = re.findall(
            r"^(?:from\s+[\w.]+\s+import\s+.+|import\s+.+)$",
            content,
            re.MULTILINE,
        )
        imports.extend(import_matches)

        return imports

    def _find_replaceable_tokens(
        self, content: str, entity: str
    ) -> list[str]:
        """Find tokens that should be replaced when adapting pattern."""
        tokens: list[str] = []

        if not entity:
            return tokens

        # Find variations of entity name
        entity_lower = entity.lower()
        entity_upper = entity.upper()
        entity_snake = self._to_snake_case(entity)

        # Find occurrences
        for variation in [entity, entity_lower, entity_upper, entity_snake]:
            if variation in content:
                tokens.append(variation)

        return list(set(tokens))

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        result = re.sub(r"([A-Z])", r"_\1", name)
        return result.lower().lstrip("_")

    def _extract_docstring(self, content: str) -> str:
        """Extract docstring from code."""
        match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if match:
            return match.group(1).strip().split("\n")[0]
        return ""


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def extract_patterns_from_file(file_path: str, content: str) -> list[CodePattern]:
    """
    Extract patterns from a file.

    Args:
        file_path: Path to the file
        content: File content

    Returns:
        List of extracted CodePattern objects
    """
    extractor = PatternExtractor()
    file_type = extractor.detect_file_type(file_path, content)

    ref_file = ReferenceFile(
        path=file_path,
        content=content,
        file_type=file_type,
    )

    return extractor.extract_patterns(ref_file)
