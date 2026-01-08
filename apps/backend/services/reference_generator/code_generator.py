#!/usr/bin/env python3
"""
Code Generator
==============

Generates code from reference patterns with entity substitution.

Supports:
- Python service/repository/model generation
- SQL schema transformation
- Terraform resource generation
- Lambda handler generation
- Glue script generation
- Cache pattern generation
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import (
    CodePattern,
    EntityMapping,
    FileType,
    GeneratedFile,
    GenerationResult,
    InfraEntityMapping,
    PatternType,
    ReferenceProject,
    SQLTransformation,
)
from .sql_converter import SQLConverter, StoredProcedureConverter


# =============================================================================
# TEMPLATE HELPERS
# =============================================================================


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    result = re.sub(r"([A-Z])", r"_\1", name)
    return result.lower().lstrip("_")


def to_camel_case(name: str) -> str:
    """Convert snake_case to CamelCase."""
    parts = name.split("_")
    return "".join(p.title() for p in parts if p)


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase (same as CamelCase)."""
    return to_camel_case(name)


def to_kebab_case(name: str) -> str:
    """Convert snake_case or CamelCase to kebab-case."""
    # First convert to snake_case if needed
    snake = to_snake_case(name)
    return snake.replace("_", "-")


# =============================================================================
# CODE GENERATOR
# =============================================================================


@dataclass
class GeneratorConfig:
    """Configuration for code generation."""

    output_dir: Path
    entity_mapping: EntityMapping
    generate_tests: bool = True
    generate_migrations: bool = True
    include_comments: bool = True
    target_language: str = "python"
    target_dialect: str = "postgresql"


class CodeGenerator:
    """
    Generates code from reference patterns.

    Usage:
        generator = CodeGenerator()
        result = await generator.generate(
            reference=reference_project,
            new_requirements="path/to/new-requirements.md",
            entity_mappings=[EntityMapping(...)],
            output_dir=Path("generated"),
        )
    """

    def __init__(self) -> None:
        """Initialize the code generator."""
        self._sql_converter = SQLConverter()
        self._proc_converter = StoredProcedureConverter()

    async def generate(
        self,
        reference: ReferenceProject,
        new_requirements_path: str | Path,
        entity_mappings: list[EntityMapping],
        output_dir: str | Path,
        config: GeneratorConfig | None = None,
    ) -> GenerationResult:
        """
        Generate code from reference patterns.

        Args:
            reference: The reference project to use as template
            new_requirements_path: Path to new requirements document
            entity_mappings: List of entity name mappings
            output_dir: Directory to write generated files
            config: Optional configuration

        Returns:
            GenerationResult with all generated files
        """
        import time
        start_time = time.time()

        result = GenerationResult()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Read new requirements
        requirements = self._read_requirements(new_requirements_path)

        # Create primary entity mapping
        primary_mapping = entity_mappings[0] if entity_mappings else EntityMapping(
            reference_name="Entity",
            new_name="Entity",
        )

        # Build replacement map for all entity variations
        replacement_map = self._build_replacement_map(entity_mappings)

        try:
            # Generate SQL schemas
            for table in reference.sql_tables:
                generated = self._generate_sql_table(
                    table, replacement_map, output_path
                )
                if generated:
                    result.generated_files.append(generated)
                    result.patterns_applied.append(f"sql_table:{table.name}")

            # Generate code from patterns
            for pattern in reference.patterns:
                generated = self._generate_from_pattern(
                    pattern, replacement_map, output_path, reference
                )
                if generated:
                    result.generated_files.append(generated)
                    result.patterns_applied.append(pattern.name)

            # Generate additional boilerplate
            boilerplate = self._generate_boilerplate(
                reference, replacement_map, output_path, primary_mapping
            )
            result.generated_files.extend(boilerplate)

            result.success = True

        except Exception as e:
            result.errors.append(str(e))

        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    def _read_requirements(self, path: str | Path) -> str:
        """Read requirements file."""
        req_path = Path(path)
        if req_path.exists():
            return req_path.read_text(encoding="utf-8")
        return ""

    def _build_replacement_map(
        self, mappings: list[EntityMapping]
    ) -> dict[str, str]:
        """
        Build a comprehensive replacement map for all entity variations.

        Args:
            mappings: List of entity mappings

        Returns:
            Dict mapping old names/variations to new names
        """
        replacements: dict[str, str] = {}

        for mapping in mappings:
            old = mapping.reference_name
            new = mapping.new_name

            # Add all case variations
            replacements[old] = new
            replacements[old.lower()] = new.lower()
            replacements[old.upper()] = new.upper()
            replacements[to_snake_case(old)] = to_snake_case(new)
            replacements[to_camel_case(old)] = to_camel_case(new)
            replacements[to_kebab_case(old)] = to_kebab_case(new)

            # Add plural forms
            replacements[old + "s"] = new + "s"
            replacements[old.lower() + "s"] = new.lower() + "s"

            # Add additional mappings
            for old_extra, new_extra in mapping.additional_mappings.items():
                replacements[old_extra] = new_extra

        return replacements

    def _apply_replacements(
        self, content: str, replacements: dict[str, str]
    ) -> str:
        """Apply all replacements to content."""
        result = content

        # Sort by length descending to replace longer strings first
        sorted_keys = sorted(replacements.keys(), key=len, reverse=True)

        for old in sorted_keys:
            new = replacements[old]
            # Use word boundary matching for precision
            pattern = rf"\b{re.escape(old)}\b"
            result = re.sub(pattern, new, result)

        return result

    def _generate_sql_table(
        self,
        table: "SQLTable",
        replacements: dict[str, str],
        output_path: Path,
    ) -> GeneratedFile | None:
        """Generate SQL table with entity substitution."""
        from .models import SQLTable

        if not table.original_sql:
            return None

        # Apply replacements to SQL
        converted_sql = self._apply_replacements(table.original_sql, replacements)

        # Determine new table name
        new_table_name = table.name
        for old, new in replacements.items():
            if old.lower() == table.name.lower():
                new_table_name = new
                break

        # Create file path
        file_path = output_path / "schema" / f"{to_snake_case(new_table_name)}.sql"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return GeneratedFile(
            path=str(file_path),
            content=converted_sql,
            source_pattern=f"sql_table:{table.name}",
            file_type=FileType.SQL_SCHEMA,
            confidence=0.95,
        )

    def _generate_from_pattern(
        self,
        pattern: CodePattern,
        replacements: dict[str, str],
        output_path: Path,
        reference: ReferenceProject,
    ) -> GeneratedFile | None:
        """Generate code from a single pattern."""

        # Apply replacements to code snippet
        generated_code = self._apply_replacements(
            pattern.code_snippet, replacements
        )

        # Apply replacements to imports
        new_imports = [
            self._apply_replacements(imp, replacements)
            for imp in pattern.imports
        ]

        # Determine output path based on pattern type
        file_path = self._determine_output_path(
            pattern, replacements, output_path
        )

        # Add imports to top of file if they exist
        if new_imports and pattern.pattern_type in (
            PatternType.SERVICE_CLASS,
            PatternType.REPOSITORY,
            PatternType.CONTROLLER,
            PatternType.DATABASE_MODEL,
        ):
            import_block = "\n".join(new_imports)
            generated_code = f"{import_block}\n\n\n{generated_code}"

        # Add file header
        generated_code = self._add_file_header(
            generated_code, pattern, replacements
        )

        return GeneratedFile(
            path=str(file_path),
            content=generated_code,
            source_pattern=pattern.name,
            file_type=self._pattern_type_to_file_type(pattern.pattern_type),
            confidence=pattern.confidence,
        )

    def _determine_output_path(
        self,
        pattern: CodePattern,
        replacements: dict[str, str],
        output_path: Path,
    ) -> Path:
        """Determine output file path for a pattern."""
        # Determine new entity name
        new_entity = pattern.entity_name
        for old, new in replacements.items():
            if old.lower() == pattern.entity_name.lower():
                new_entity = new
                break

        entity_snake = to_snake_case(new_entity)

        # Map pattern type to directory and file name
        type_to_path = {
            PatternType.SERVICE_CLASS: f"services/{entity_snake}_service.py",
            PatternType.REPOSITORY: f"repositories/{entity_snake}_repository.py",
            PatternType.CONTROLLER: f"controllers/{entity_snake}_controller.py",
            PatternType.DATABASE_MODEL: f"models/{entity_snake}.py",
            PatternType.VALIDATION: f"validators/{entity_snake}_validator.py",
            PatternType.LAMBDA_FUNCTION: f"lambda/{entity_snake}/handler.py",
            PatternType.GLUE_JOB: f"glue/{entity_snake}_etl.py",
            PatternType.STEP_FUNCTION: f"step_functions/{entity_snake}_workflow.json",
            PatternType.TERRAFORM_RESOURCE: f"terraform/{entity_snake}.tf",
            PatternType.LRU_CACHE: f"cache/{entity_snake}_cache.py",
            PatternType.TTL_CACHE: f"cache/{entity_snake}_cache.py",
            PatternType.REDIS_CACHE: f"cache/{entity_snake}_cache.py",
            PatternType.CACHE_ASIDE: f"cache/{entity_snake}_cache.py",
            PatternType.CONTEXT_MANAGER: f"context/{entity_snake}_context.py",
            PatternType.CONTEXT_VAR: f"context/{entity_snake}_context.py",
            PatternType.TRANSACTION_CONTEXT: f"context/{entity_snake}_transaction.py",
        }

        relative_path = type_to_path.get(
            pattern.pattern_type,
            f"utils/{entity_snake}.py",
        )

        full_path = output_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        return full_path

    def _pattern_type_to_file_type(self, pattern_type: PatternType) -> FileType:
        """Convert pattern type to file type."""
        mapping = {
            PatternType.SERVICE_CLASS: FileType.PYTHON_SERVICE,
            PatternType.REPOSITORY: FileType.PYTHON_REPOSITORY,
            PatternType.CONTROLLER: FileType.PYTHON_CONTROLLER,
            PatternType.DATABASE_MODEL: FileType.PYTHON_MODEL,
            PatternType.LAMBDA_FUNCTION: FileType.LAMBDA_HANDLER,
            PatternType.GLUE_JOB: FileType.GLUE_SCRIPT,
            PatternType.STEP_FUNCTION: FileType.STEP_FUNCTION_DEF,
            PatternType.TERRAFORM_RESOURCE: FileType.TERRAFORM,
        }
        return mapping.get(pattern_type, FileType.OTHER)

    def _add_file_header(
        self,
        content: str,
        pattern: CodePattern,
        replacements: dict[str, str],
    ) -> str:
        """Add a descriptive header to the generated file."""
        # Determine the new entity name
        new_entity = pattern.entity_name
        for old, new in replacements.items():
            if old.lower() == pattern.entity_name.lower():
                new_entity = new
                break

        header = f'''#!/usr/bin/env python3
"""
{to_pascal_case(new_entity)} {pattern.pattern_type.value.replace("_", " ").title()}
{"=" * (len(new_entity) + len(pattern.pattern_type.value) + 2)}

Generated from reference pattern: {pattern.name}
Source: {pattern.source_file}
Generated: {datetime.now().isoformat()}

{pattern.description if pattern.description else f"Auto-generated {pattern.pattern_type.value} for {new_entity}."}
"""

'''
        return header + content

    def _generate_boilerplate(
        self,
        reference: ReferenceProject,
        replacements: dict[str, str],
        output_path: Path,
        primary_mapping: EntityMapping,
    ) -> list[GeneratedFile]:
        """Generate boilerplate files (__init__.py, etc.)."""
        files: list[GeneratedFile] = []
        new_entity = primary_mapping.new_name
        entity_snake = to_snake_case(new_entity)

        # Create __init__.py files for each directory
        dirs_with_files: set[Path] = set()
        for subdir in output_path.rglob("*.py"):
            dirs_with_files.add(subdir.parent)

        for dir_path in dirs_with_files:
            init_path = dir_path / "__init__.py"
            if not init_path.exists():
                # Gather exports from this directory
                py_files = list(dir_path.glob("*.py"))
                exports: list[str] = []

                for py_file in py_files:
                    if py_file.name == "__init__.py":
                        continue
                    module_name = py_file.stem
                    # Extract class names from file
                    content = py_file.read_text(encoding="utf-8") if py_file.exists() else ""
                    class_names = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
                    for class_name in class_names:
                        exports.append(
                            f"from .{module_name} import {class_name}"
                        )

                init_content = '"""Package exports."""\n\n'
                if exports:
                    init_content += "\n".join(exports)
                    init_content += "\n\n__all__ = [\n"
                    for exp in exports:
                        class_name = exp.split("import ")[-1]
                        init_content += f'    "{class_name}",\n'
                    init_content += "]\n"

                files.append(
                    GeneratedFile(
                        path=str(init_path),
                        content=init_content,
                        source_pattern="boilerplate:__init__",
                        file_type=FileType.OTHER,
                        confidence=1.0,
                    )
                )

        # Create main __init__.py at output root
        root_init = output_path / "__init__.py"
        files.append(
            GeneratedFile(
                path=str(root_init),
                content=f'''"""
{to_pascal_case(new_entity)} Module
{"=" * (len(new_entity) + 8)}

Generated from reference: {reference.name}
"""
''',
                source_pattern="boilerplate:root_init",
                file_type=FileType.OTHER,
                confidence=1.0,
            )
        )

        return files

    def generate_terraform(
        self,
        pattern: CodePattern,
        mapping: InfraEntityMapping,
        output_path: Path,
    ) -> GeneratedFile:
        """
        Generate Terraform resources with infrastructure-specific mappings.

        Args:
            pattern: Terraform pattern to transform
            mapping: Infrastructure entity mapping
            output_path: Output directory

        Returns:
            GeneratedFile with transformed Terraform
        """
        content = pattern.code_snippet

        # Apply basic entity replacement
        content = content.replace(
            mapping.reference_name, mapping.new_name
        )
        content = content.replace(
            mapping.reference_name.lower(), mapping.new_name.lower()
        )

        # Apply infrastructure-specific replacements
        if mapping.resource_prefix:
            content = re.sub(
                r'\$\{var\.prefix\}',
                mapping.resource_prefix,
                content,
            )

        if mapping.environment:
            content = re.sub(
                r'\$\{var\.environment\}',
                mapping.environment,
                content,
            )

        if mapping.region:
            content = re.sub(
                r'\$\{var\.region\}',
                mapping.region,
                content,
            )

        # Generate file path
        file_path = output_path / "terraform" / f"{to_snake_case(mapping.new_name)}.tf"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return GeneratedFile(
            path=str(file_path),
            content=content,
            source_pattern=pattern.name,
            file_type=FileType.TERRAFORM,
            confidence=0.9,
        )

    def generate_lambda_handler(
        self,
        pattern: CodePattern,
        mapping: EntityMapping,
        output_path: Path,
        trigger_type: str = "s3",
    ) -> GeneratedFile:
        """
        Generate Lambda handler from pattern.

        Args:
            pattern: Lambda pattern
            mapping: Entity mapping
            output_path: Output directory
            trigger_type: Type of trigger (s3, sqs, api_gateway, etc.)

        Returns:
            GeneratedFile with Lambda handler
        """
        new_entity = mapping.new_name
        entity_snake = to_snake_case(new_entity)

        # Base handler template
        handler = f'''#!/usr/bin/env python3
"""
{to_pascal_case(new_entity)} Lambda Handler
{"=" * (len(new_entity) + 16)}

Trigger: {trigger_type}
Generated from: {pattern.source_file}
"""

import json
import logging
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Lambda handler for {entity_snake} processing.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Response dict
    """
    logger.info(f"Processing {entity_snake} event")
'''

        # Add trigger-specific handling
        if trigger_type == "s3":
            handler += '''
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        logger.info(f"Processing S3 object: s3://{bucket}/{key}")
        
        # TODO: Implement processing logic
'''
        elif trigger_type == "sqs":
            handler += '''
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        logger.info(f"Processing SQS message: {body}")
        
        # TODO: Implement processing logic
'''
        elif trigger_type == "api_gateway":
            handler += '''
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = event.get("body", "{}")
    
    logger.info(f"Processing {http_method} request to {path}")
    
    # TODO: Implement API logic
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Success"}),
    }
'''

        handler += '''
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "processed"}),
    }
'''

        file_path = output_path / "lambda" / f"process_{entity_snake}" / "handler.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return GeneratedFile(
            path=str(file_path),
            content=handler,
            source_pattern=pattern.name,
            file_type=FileType.LAMBDA_HANDLER,
            confidence=0.85,
        )

    def generate_cache_service(
        self,
        entity_name: str,
        cache_type: str,
        output_path: Path,
        ttl: int = 3600,
        prefix: str = "",
    ) -> GeneratedFile:
        """
        Generate a cache service for an entity.

        Args:
            entity_name: Entity name
            cache_type: Type of cache (redis, lru, ttl)
            output_path: Output directory
            ttl: Cache TTL in seconds
            prefix: Cache key prefix

        Returns:
            GeneratedFile with cache service
        """
        entity_snake = to_snake_case(entity_name)
        entity_pascal = to_pascal_case(entity_name)
        key_prefix = prefix or f"{entity_snake}:"

        content = f'''#!/usr/bin/env python3
"""
{entity_pascal} Cache Service
{"=" * (len(entity_name) + 15)}

Provides caching for {entity_name} entities.
Cache type: {cache_type}
Default TTL: {ttl}s
"""

from typing import Any
import json
'''

        if cache_type == "redis":
            content += '''
import redis.asyncio as aioredis


class {entity_pascal}CacheService:
    """Redis cache service for {entity_name}."""
    
    def __init__(self, redis_client: aioredis.Redis) -> None:
        """Initialize with Redis client."""
        self.redis = redis_client
        self.prefix = "{key_prefix}"
        self.ttl = {ttl}
    
    async def get(self, {entity_snake}_id: int) -> dict[str, Any] | None:
        """Get {entity_name} from cache."""
        cached = await self.redis.get(f"{{self.prefix}}{{{entity_snake}_id}}")
        if cached:
            return json.loads(cached)
        return None
    
    async def set(
        self,
        {entity_snake}_id: int,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Set {entity_name} in cache."""
        await self.redis.set(
            f"{{self.prefix}}{{{entity_snake}_id}}",
            json.dumps(data),
            ex=ttl or self.ttl,
        )
    
    async def delete(self, {entity_snake}_id: int) -> None:
        """Delete {entity_name} from cache."""
        await self.redis.delete(f"{{self.prefix}}{{{entity_snake}_id}}")
    
    async def get_or_fetch(
        self,
        {entity_snake}_id: int,
        fetch_func,
        ttl: int | None = None,
    ) -> dict[str, Any] | None:
        """Get from cache or fetch and cache."""
        cached = await self.get({entity_snake}_id)
        if cached is not None:
            return cached
        
        data = await fetch_func({entity_snake}_id)
        if data is not None:
            await self.set({entity_snake}_id, data, ttl)
        
        return data
'''.format(
                entity_pascal=entity_pascal,
                entity_name=entity_name,
                entity_snake=entity_snake,
                key_prefix=key_prefix,
                ttl=ttl,
            )

        elif cache_type == "lru":
            content += f'''
from functools import lru_cache


@lru_cache(maxsize=256)
def get_{entity_snake}_by_id({entity_snake}_id: int) -> dict[str, Any] | None:
    """Get {entity_name} by ID with LRU caching."""
    # TODO: Implement fetch logic
    return None


def clear_{entity_snake}_cache() -> None:
    """Clear the {entity_name} LRU cache."""
    get_{entity_snake}_by_id.cache_clear()
'''

        elif cache_type == "ttl":
            content += f'''
from cachetools import TTLCache, cached


{entity_snake}_cache = TTLCache(maxsize=100, ttl={ttl})


@cached(cache={entity_snake}_cache)
def get_{entity_snake}_by_id({entity_snake}_id: int) -> dict[str, Any] | None:
    """Get {entity_name} by ID with TTL caching."""
    # TODO: Implement fetch logic
    return None


def clear_{entity_snake}_cache() -> None:
    """Clear the {entity_name} TTL cache."""
    {entity_snake}_cache.clear()
'''

        file_path = output_path / "cache" / f"{entity_snake}_cache.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return GeneratedFile(
            path=str(file_path),
            content=content,
            source_pattern=f"cache:{cache_type}",
            file_type=FileType.OTHER,
            confidence=0.9,
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


async def generate_from_reference(
    reference: ReferenceProject,
    new_requirements_path: str,
    entity_mappings: list[dict[str, str]],
    output_dir: str,
) -> GenerationResult:
    """
    Convenience function to generate code from a reference.

    Args:
        reference: Reference project
        new_requirements_path: Path to new requirements
        entity_mappings: List of {"reference": "old", "new": "new"} dicts
        output_dir: Output directory

    Returns:
        GenerationResult
    """
    generator = CodeGenerator()
    mappings = [
        EntityMapping(
            reference_name=m["reference"],
            new_name=m["new"],
        )
        for m in entity_mappings
    ]

    return await generator.generate(
        reference=reference,
        new_requirements_path=new_requirements_path,
        entity_mappings=mappings,
        output_dir=output_dir,
    )
