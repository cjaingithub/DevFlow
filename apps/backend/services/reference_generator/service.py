#!/usr/bin/env python3
"""
Reference Generator Service
===========================

Main orchestrator for the Reference-Based Code Generation feature.

Provides a unified interface for:
- Loading reference projects
- Extracting patterns
- Generating code for new requirements
- Managing stored references

CLI Usage:
    # Load a reference project
    python -m services.reference_generator.service \\
        --action load \\
        --reference examples/user-auth \\
        --name user-authentication

    # List saved references
    python -m services.reference_generator.service --action list

    # Generate code for new requirements
    python -m services.reference_generator.service \\
        --action generate \\
        --name user-authentication \\
        --requirements specs/product-catalog.md \\
        --output generated/product-catalog

    # Get info about a reference
    python -m services.reference_generator.service \\
        --action info \\
        --name user-authentication \\
        --json
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .code_generator import CodeGenerator
from .lucid_flowchart_generator import (
    FlowchartGenerationResult,
    LucidFlowchartGenerator,
)
from .lucid_xml_parser import FlowchartParseResult, LucidXMLParser
from .models import (
    EntityMapping,
    GenerationResult,
    InfraEntityMapping,
    PatternType,
    ReferenceProject,
)
from .reference_manager import ReferenceManager


# =============================================================================
# SERVICE CLASS
# =============================================================================


@dataclass
class ServiceConfig:
    """Configuration for the reference generator service."""

    project_dir: Path
    generate_tests: bool = True
    generate_migrations: bool = True
    include_comments: bool = True
    verbose: bool = False


class ReferenceGeneratorService:
    """
    Main service for reference-based code generation.

    This is the primary entry point for the reference generator feature.

    Usage:
        service = ReferenceGeneratorService(project_dir="/my/project")

        # Load a reference
        reference = await service.load_reference(
            reference_path="examples/user-auth",
            name="user-auth-feature",
        )

        # Generate code
        result = await service.generate_from_reference(
            reference_name="user-auth-feature",
            new_requirements_path="specs/product-catalog.md",
            entity_mappings=[
                {"reference": "User", "new": "Product"},
            ],
            output_dir="generated/product-catalog",
        )
    """

    def __init__(
        self,
        project_dir: str | Path,
        config: ServiceConfig | None = None,
    ) -> None:
        """
        Initialize the reference generator service.

        Args:
            project_dir: Path to the project directory
            config: Optional service configuration
        """
        self.project_dir = Path(project_dir)
        self.config = config or ServiceConfig(project_dir=self.project_dir)
        self._manager = ReferenceManager(self.project_dir)
        self._generator = CodeGenerator()
        self._flowchart_generator = LucidFlowchartGenerator()
        self._xml_parser = LucidXMLParser()

    async def load_reference(
        self,
        reference_path: str | Path,
        name: str,
        description: str = "",
    ) -> ReferenceProject:
        """
        Load a reference project from a folder.

        Args:
            reference_path: Path to the reference folder
            name: Name to identify this reference
            description: Optional description

        Returns:
            Loaded ReferenceProject with extracted patterns
        """
        return await self._manager.load_reference(
            reference_path=reference_path,
            name=name,
            description=description,
        )

    async def generate_from_reference(
        self,
        reference_name: str,
        new_requirements_path: str | Path,
        entity_mappings: list[dict[str, str]],
        output_dir: str | Path,
    ) -> GenerationResult:
        """
        Generate code from a reference for new requirements.

        Args:
            reference_name: Name of the loaded reference
            new_requirements_path: Path to new requirements document
            entity_mappings: List of {"reference": "old", "new": "new"} dicts
            output_dir: Directory to write generated files

        Returns:
            GenerationResult with all generated files

        Raises:
            ValueError: If reference not found
        """
        # Get the reference
        reference = self._manager.get_reference(reference_name)
        if not reference:
            raise ValueError(f"Reference not found: {reference_name}")

        # Convert entity mappings
        mappings = [
            EntityMapping(
                reference_name=m.get("reference", ""),
                new_name=m.get("new", ""),
                additional_mappings=m.get("additional", {}),
            )
            for m in entity_mappings
        ]

        # Update usage stats
        self._manager.update_usage(reference_name)

        # Generate code
        result = await self._generator.generate(
            reference=reference,
            new_requirements_path=new_requirements_path,
            entity_mappings=mappings,
            output_dir=output_dir,
        )

        return result

    async def generate_infrastructure(
        self,
        reference_name: str,
        entity_mapping: dict[str, Any],
        output_dir: str | Path,
    ) -> GenerationResult:
        """
        Generate infrastructure code (Terraform, Lambda, Glue).

        Args:
            reference_name: Name of the loaded reference
            entity_mapping: Infrastructure entity mapping config
            output_dir: Directory to write generated files

        Returns:
            GenerationResult with infrastructure files
        """
        reference = self._manager.get_reference(reference_name)
        if not reference:
            raise ValueError(f"Reference not found: {reference_name}")

        # Create infrastructure mapping
        infra_mapping = InfraEntityMapping(
            reference_name=entity_mapping.get("reference", ""),
            new_name=entity_mapping.get("new", ""),
            resource_prefix=entity_mapping.get("resource_prefix", ""),
            environment=entity_mapping.get("environment", "dev"),
            region=entity_mapping.get("region", "us-east-1"),
            cache_config=entity_mapping.get("cache_config", {}),
        )

        result = GenerationResult()
        output_path = Path(output_dir)

        # Get infrastructure patterns
        infra_types = [
            PatternType.TERRAFORM_RESOURCE,
            PatternType.LAMBDA_FUNCTION,
            PatternType.GLUE_JOB,
            PatternType.STEP_FUNCTION,
        ]

        patterns_by_type = self._manager.get_patterns_by_type(
            reference_name, infra_types
        )

        # Generate Terraform resources
        for pattern in patterns_by_type.get(PatternType.TERRAFORM_RESOURCE, []):
            generated = self._generator.generate_terraform(
                pattern, infra_mapping, output_path
            )
            result.generated_files.append(generated)
            result.patterns_applied.append(pattern.name)

        # Generate Lambda handlers
        for pattern in patterns_by_type.get(PatternType.LAMBDA_FUNCTION, []):
            mapping = EntityMapping(
                reference_name=infra_mapping.reference_name,
                new_name=infra_mapping.new_name,
            )
            generated = self._generator.generate_lambda_handler(
                pattern, mapping, output_path
            )
            result.generated_files.append(generated)
            result.patterns_applied.append(pattern.name)

        result.success = True
        self._manager.update_usage(reference_name)

        return result

    def list_references(self) -> list[dict[str, Any]]:
        """
        List all loaded references.

        Returns:
            List of reference summaries
        """
        references = self._manager.list_references()
        return [
            {
                "name": ref.name,
                "description": ref.description,
                "path": ref.path,
                "patterns": len(ref.patterns),
                "files": len(ref.files),
                "tech_stack": [t.value for t in ref.tech_stack],
                "usage_count": ref.usage_count,
                "last_used": ref.last_used.isoformat() if ref.last_used else None,
            }
            for ref in references
        ]

    def get_reference_info(self, name: str) -> dict[str, Any]:
        """
        Get detailed information about a reference.

        Args:
            name: Reference name

        Returns:
            Dict with reference statistics and patterns
        """
        return self._manager.get_reference_stats(name)

    def delete_reference(self, name: str) -> bool:
        """
        Delete a reference.

        Args:
            name: Reference name

        Returns:
            True if deleted, False if not found
        """
        return self._manager.delete_reference(name)

    def search_patterns(
        self,
        reference_name: str | None = None,
        pattern_type: str | None = None,
        entity_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for patterns across references.

        Args:
            reference_name: Filter by reference
            pattern_type: Filter by pattern type
            entity_name: Filter by entity name

        Returns:
            List of matching patterns
        """
        pt = PatternType(pattern_type) if pattern_type else None

        patterns = self._manager.search_patterns(
            reference_name=reference_name,
            pattern_type=pt,
            entity_name=entity_name,
        )

        return [p.to_dict() for p in patterns]

    def to_dict(self) -> dict[str, Any]:
        """Convert service state to dictionary."""
        return {
            "project_dir": str(self.project_dir),
            "config": {
                "generate_tests": self.config.generate_tests,
                "generate_migrations": self.config.generate_migrations,
                "include_comments": self.config.include_comments,
            },
            "manager": self._manager.to_dict(),
        }

    # =========================================================================
    # FLOWCHART GENERATION METHODS
    # =========================================================================

    def generate_flowchart_from_sql(
        self,
        sql_path: str | Path,
        output_path: str | Path | None = None,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate Lucid flowchart from Oracle SQL file.

        Args:
            sql_path: Path to SQL file
            output_path: Optional path to save output
            output_format: "xml" or "mermaid"

        Returns:
            FlowchartGenerationResult with XML content
        """
        # Resolve path relative to project
        path = Path(sql_path)
        if not path.is_absolute():
            path = self.project_dir / path

        result = self._flowchart_generator.generate_from_sql(path, output_format)

        if output_path and result.success:
            out_path = Path(output_path)
            if not out_path.is_absolute():
                out_path = self.project_dir / out_path
            self._flowchart_generator.save_to_file(result, out_path)

        return result

    def generate_flowchart_from_docs(
        self,
        doc_path: str | Path,
        output_path: str | Path | None = None,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate Lucid requirements flowchart from documentation.

        Args:
            doc_path: Path to documentation file
            output_path: Optional path to save output
            output_format: "xml" or "mermaid"

        Returns:
            FlowchartGenerationResult with XML content
        """
        path = Path(doc_path)
        if not path.is_absolute():
            path = self.project_dir / path

        result = self._flowchart_generator.generate_from_docs(path, output_format)

        if output_path and result.success:
            out_path = Path(output_path)
            if not out_path.is_absolute():
                out_path = self.project_dir / out_path
            self._flowchart_generator.save_to_file(result, out_path)

        return result

    def generate_combined_flowchart(
        self,
        sql_files: list[str | Path] | None = None,
        doc_files: list[str | Path] | None = None,
        output_path: str | Path | None = None,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate combined flowchart from multiple SQL and doc files.

        Args:
            sql_files: List of SQL file paths
            doc_files: List of documentation file paths
            output_path: Optional path to save output
            output_format: "xml" or "mermaid"

        Returns:
            FlowchartGenerationResult with combined flowchart
        """
        # Resolve all paths
        resolved_sql = []
        if sql_files:
            for f in sql_files:
                path = Path(f)
                if not path.is_absolute():
                    path = self.project_dir / path
                resolved_sql.append(path)

        resolved_docs = []
        if doc_files:
            for f in doc_files:
                path = Path(f)
                if not path.is_absolute():
                    path = self.project_dir / path
                resolved_docs.append(path)

        result = self._flowchart_generator.generate_combined(
            sql_files=resolved_sql,
            doc_files=resolved_docs,
            output_format=output_format,
        )

        if output_path and result.success:
            out_path = Path(output_path)
            if not out_path.is_absolute():
                out_path = self.project_dir / out_path
            self._flowchart_generator.save_to_file(result, out_path)

        return result

    def generate_flowchart_from_sql_content(
        self,
        sql_content: str,
        name: str = "SQL_Procedure",
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate flowchart from SQL content string.

        Args:
            sql_content: Oracle SQL content
            name: Name for the flowchart
            output_format: "xml" or "mermaid"

        Returns:
            FlowchartGenerationResult
        """
        return self._flowchart_generator.generate_from_sql_content(
            sql_content, name, output_format
        )

    def generate_flowchart_from_doc_content(
        self,
        doc_content: str,
        name: str = "Requirements",
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate flowchart from documentation content string.

        Args:
            doc_content: Documentation content
            name: Name for the flowchart
            output_format: "xml" or "mermaid"

        Returns:
            FlowchartGenerationResult
        """
        return self._flowchart_generator.generate_from_doc_content(
            doc_content, name, output_format
        )

    # =========================================================================
    # FLOWCHART XML AS INPUT REFERENCE
    # =========================================================================

    async def load_flowchart_as_reference(
        self,
        xml_path: str | Path,
        name: str,
        description: str = "",
    ) -> ReferenceProject:
        """
        Load a Lucid XML flowchart as a reference for code generation.

        This allows users to provide flowchart XML files as input documents
        that will be parsed to extract requirements and generate code patterns.

        Args:
            xml_path: Path to the XML flowchart file
            name: Name to identify this reference
            description: Optional description

        Returns:
            ReferenceProject with patterns extracted from the flowchart
        """
        path = Path(xml_path)
        if not path.is_absolute():
            path = self.project_dir / path

        return await self._manager.load_flowchart_xml(path, name, description)

    def parse_flowchart_xml(
        self,
        xml_path: str | Path,
    ) -> FlowchartParseResult:
        """
        Parse a Lucid XML flowchart file and extract structured information.

        This is useful for inspecting what will be extracted from a flowchart
        before using it as a reference.

        Args:
            xml_path: Path to the XML flowchart file

        Returns:
            FlowchartParseResult with extracted requirements, processes, etc.
        """
        path = Path(xml_path)
        if not path.is_absolute():
            path = self.project_dir / path

        return self._xml_parser.parse(path)

    def parse_flowchart_xml_content(
        self,
        xml_content: str,
        name: str = "Flowchart",
    ) -> FlowchartParseResult:
        """
        Parse Lucid XML content string.

        Args:
            xml_content: XML content string
            name: Name for the flowchart

        Returns:
            FlowchartParseResult
        """
        return self._xml_parser.parse_content(xml_content, name)

    async def generate_from_flowchart(
        self,
        xml_path: str | Path,
        entity_mappings: list[dict[str, str]],
        output_dir: str | Path,
    ) -> GenerationResult:
        """
        Generate code directly from a flowchart XML file.

        This is a convenience method that combines:
        1. Parsing the flowchart XML
        2. Loading it as a reference
        3. Generating code from the patterns

        Args:
            xml_path: Path to the flowchart XML
            entity_mappings: Entity name mappings
            output_dir: Output directory for generated code

        Returns:
            GenerationResult with generated files
        """
        # Parse and load the flowchart
        path = Path(xml_path)
        if not path.is_absolute():
            path = self.project_dir / path

        temp_name = f"flowchart_{path.stem}"
        reference = await self._manager.load_flowchart_xml(path, temp_name)

        # Convert entity mappings
        from .models import EntityMapping
        mappings = [
            EntityMapping(
                reference_name=m.get("reference", ""),
                new_name=m.get("new", ""),
            )
            for m in entity_mappings
        ]

        # Generate code
        result = await self._generator.generate(
            reference=reference,
            new_requirements_path="",  # Not needed, using patterns from flowchart
            entity_mappings=mappings,
            output_dir=output_dir,
        )

        return result


# =============================================================================
# CLI IMPLEMENTATION
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Reference-Based Code Generation Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Load a reference
    python -m services.reference_generator.service \\
        --action load --reference examples/user-auth --name user-auth

    # Generate code
    python -m services.reference_generator.service \\
        --action generate --name user-auth \\
        --requirements product.md --output generated/product

    # List references
    python -m services.reference_generator.service --action list --json
        """,
    )

    parser.add_argument(
        "--action",
        choices=[
            "load", "generate", "list", "info", "delete", "search",
            "flowchart-sql", "flowchart-docs", "flowchart-combined",
            "load-flowchart", "parse-flowchart", "generate-from-flowchart",
        ],
        required=True,
        help="Action to perform",
    )

    parser.add_argument(
        "--reference",
        type=str,
        help="Path to reference folder (for load action)",
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Reference name",
    )

    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Reference description (for load action)",
    )

    parser.add_argument(
        "--requirements",
        type=str,
        help="Path to new requirements file (for generate action)",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output directory (for generate action)",
    )

    parser.add_argument(
        "--entity-mapping",
        type=str,
        help='Entity mapping as JSON: {"reference": "User", "new": "Product"}',
    )

    parser.add_argument(
        "--pattern-type",
        type=str,
        help="Filter by pattern type (for search action)",
    )

    parser.add_argument(
        "--entity",
        type=str,
        help="Filter by entity name (for search action)",
    )

    parser.add_argument(
        "--sql-files",
        type=str,
        nargs="+",
        help="SQL files for flowchart generation",
    )

    parser.add_argument(
        "--doc-files",
        type=str,
        nargs="+",
        help="Documentation files for flowchart generation",
    )

    parser.add_argument(
        "--xml-file",
        type=str,
        help="Lucid XML flowchart file to use as input reference",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["xml", "mermaid"],
        default="xml",
        help="Output format for flowcharts (default: xml)",
    )

    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project directory (default: current directory)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    return parser.parse_args()


async def run_cli(args: argparse.Namespace) -> int:
    """Run CLI command."""
    project_dir = Path(args.project_dir).resolve()
    service = ReferenceGeneratorService(project_dir)

    try:
        if args.action == "load":
            if not args.reference or not args.name:
                print("Error: --reference and --name required for load action")
                return 1

            reference = await service.load_reference(
                reference_path=args.reference,
                name=args.name,
                description=args.description,
            )

            if args.json:
                print(json.dumps(reference.to_dict(), indent=2))
            else:
                print(f"✅ Loaded reference: {reference.name}")
                print(f"   Path: {reference.path}")
                print(f"   Files: {len(reference.files)}")
                print(f"   Patterns: {len(reference.patterns)}")
                print(f"   SQL Tables: {len(reference.sql_tables)}")
                print(f"   Tech Stack: {', '.join(t.value for t in reference.tech_stack)}")

        elif args.action == "generate":
            if not args.name or not args.requirements or not args.output:
                print("Error: --name, --requirements, and --output required for generate action")
                return 1

            # Parse entity mapping
            entity_mappings = []
            if args.entity_mapping:
                mapping = json.loads(args.entity_mapping)
                entity_mappings.append(mapping)

            result = await service.generate_from_reference(
                reference_name=args.name,
                new_requirements_path=args.requirements,
                entity_mappings=entity_mappings,
                output_dir=args.output,
            )

            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                if result.success:
                    print(f"✅ Generated {len(result.generated_files)} files")
                    for f in result.generated_files:
                        print(f"   - {f.path}")
                else:
                    print(f"❌ Generation failed: {result.errors}")

        elif args.action == "list":
            references = service.list_references()

            if args.json:
                print(json.dumps(references, indent=2))
            else:
                if references:
                    print("Loaded References:")
                    for ref in references:
                        print(f"\n  📁 {ref['name']}")
                        print(f"     Path: {ref['path']}")
                        print(f"     Patterns: {ref['patterns']}")
                        print(f"     Files: {ref['files']}")
                        print(f"     Tech: {', '.join(ref['tech_stack'])}")
                        if ref['usage_count']:
                            print(f"     Used: {ref['usage_count']} times")
                else:
                    print("No references loaded. Use --action load to add one.")

        elif args.action == "info":
            if not args.name:
                print("Error: --name required for info action")
                return 1

            info = service.get_reference_info(args.name)

            if args.json:
                print(json.dumps(info, indent=2))
            else:
                if info:
                    print(f"Reference: {info['name']}")
                    print(f"Description: {info.get('description', 'N/A')}")
                    print(f"Path: {info['path']}")
                    print(f"\nFiles ({info['total_files']}):")
                    for ft, count in info.get("file_counts", {}).items():
                        print(f"  - {ft}: {count}")
                    print(f"\nPatterns ({info['total_patterns']}):")
                    for pt, count in info.get("pattern_counts", {}).items():
                        print(f"  - {pt}: {count}")
                else:
                    print(f"Reference not found: {args.name}")

        elif args.action == "delete":
            if not args.name:
                print("Error: --name required for delete action")
                return 1

            if service.delete_reference(args.name):
                print(f"✅ Deleted reference: {args.name}")
            else:
                print(f"Reference not found: {args.name}")
                return 1

        elif args.action == "search":
            patterns = service.search_patterns(
                reference_name=args.name,
                pattern_type=args.pattern_type,
                entity_name=args.entity,
            )

            if args.json:
                print(json.dumps(patterns, indent=2))
            else:
                if patterns:
                    print(f"Found {len(patterns)} patterns:")
                    for p in patterns:
                        print(f"\n  📋 {p['name']}")
                        print(f"     Type: {p['pattern_type']}")
                        print(f"     Entity: {p['entity_name']}")
                        print(f"     Source: {p['source_file']}")
                else:
                    print("No patterns found matching criteria.")

        elif args.action == "flowchart-sql":
            if not args.sql_files:
                print("Error: --sql-files required for flowchart-sql action")
                return 1

            sql_file = args.sql_files[0]  # Use first file for single SQL
            result = service.generate_flowchart_from_sql(
                sql_path=sql_file,
                output_path=args.output,
                output_format=args.format,
            )

            if args.json:
                print(json.dumps({
                    "success": result.success,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "xml_content": result.xml_content if not args.output else f"Saved to {args.output}",
                }, indent=2))
            else:
                if result.success:
                    if args.output:
                        print(f"✅ Flowchart saved to: {args.output}")
                    else:
                        print(result.xml_content)
                else:
                    print(f"❌ Generation failed: {result.errors}")

        elif args.action == "flowchart-docs":
            if not args.doc_files:
                print("Error: --doc-files required for flowchart-docs action")
                return 1

            doc_file = args.doc_files[0]  # Use first file for single doc
            result = service.generate_flowchart_from_docs(
                doc_path=doc_file,
                output_path=args.output,
                output_format=args.format,
            )

            if args.json:
                print(json.dumps({
                    "success": result.success,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "xml_content": result.xml_content if not args.output else f"Saved to {args.output}",
                }, indent=2))
            else:
                if result.success:
                    if args.output:
                        print(f"✅ Flowchart saved to: {args.output}")
                    else:
                        print(result.xml_content)
                else:
                    print(f"❌ Generation failed: {result.errors}")

        elif args.action == "flowchart-combined":
            if not args.sql_files and not args.doc_files:
                print("Error: --sql-files and/or --doc-files required for flowchart-combined action")
                return 1

            result = service.generate_combined_flowchart(
                sql_files=args.sql_files,
                doc_files=args.doc_files,
                output_path=args.output,
                output_format=args.format,
            )

            if args.json:
                print(json.dumps({
                    "success": result.success,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "node_count": len(result.flowchart.nodes) if result.flowchart else 0,
                    "xml_content": result.xml_content if not args.output else f"Saved to {args.output}",
                }, indent=2))
            else:
                if result.success:
                    fc = result.flowchart
                    print(f"✅ Generated combined flowchart")
                    print(f"   Nodes: {len(fc.nodes) if fc else 0}")
                    print(f"   Connections: {len(fc.connections) if fc else 0}")
                    if args.output:
                        print(f"   Saved to: {args.output}")
                    else:
                        print(result.xml_content)
                    if result.warnings:
                        print(f"   Warnings: {result.warnings}")
                else:
                    print(f"❌ Generation failed: {result.errors}")

        elif args.action == "load-flowchart":
            if not args.xml_file or not args.name:
                print("Error: --xml-file and --name required for load-flowchart action")
                return 1

            reference = await service.load_flowchart_as_reference(
                xml_path=args.xml_file,
                name=args.name,
                description=args.description,
            )

            if args.json:
                print(json.dumps(reference.to_dict(), indent=2))
            else:
                print(f"✅ Loaded flowchart as reference: {reference.name}")
                print(f"   Path: {reference.path}")
                print(f"   Patterns extracted: {len(reference.patterns)}")
                print(f"   Requirements: {len(reference.requirements)}")
                if reference.patterns:
                    print("   Pattern types:")
                    type_counts: dict[str, int] = {}
                    for p in reference.patterns:
                        t = p.pattern_type.value
                        type_counts[t] = type_counts.get(t, 0) + 1
                    for t, c in type_counts.items():
                        print(f"     - {t}: {c}")

        elif args.action == "parse-flowchart":
            if not args.xml_file:
                print("Error: --xml-file required for parse-flowchart action")
                return 1

            result = service.parse_flowchart_xml(args.xml_file)

            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                if result.success:
                    print(f"✅ Parsed flowchart: {result.flowchart.name if result.flowchart else 'Unknown'}")
                    print(f"   Nodes: {len(result.flowchart.nodes) if result.flowchart else 0}")
                    print(f"   Connections: {len(result.flowchart.connections) if result.flowchart else 0}")
                    print(f"\n   Requirements extracted: {len(result.requirements)}")
                    for req in result.requirements[:5]:
                        print(f"     - {req.title}")
                    if len(result.requirements) > 5:
                        print(f"     ... and {len(result.requirements) - 5} more")
                    print(f"\n   Processes extracted: {len(result.processes)}")
                    for proc in result.processes[:5]:
                        print(f"     - {proc.name} ({proc.process_type})")
                    if len(result.processes) > 5:
                        print(f"     ... and {len(result.processes) - 5} more")
                    print(f"\n   Data flows extracted: {len(result.data_flows)}")
                    for df in result.data_flows[:5]:
                        print(f"     - {df.operation.upper()} on {df.table_name}")
                    print(f"\n   Patterns generated: {len(result.generated_patterns)}")
                else:
                    print(f"❌ Parse failed: {result.errors}")

        elif args.action == "generate-from-flowchart":
            if not args.xml_file or not args.output:
                print("Error: --xml-file and --output required for generate-from-flowchart action")
                return 1

            entity_mappings = []
            if args.entity_mapping:
                mapping = json.loads(args.entity_mapping)
                entity_mappings.append(mapping)

            result = await service.generate_from_flowchart(
                xml_path=args.xml_file,
                entity_mappings=entity_mappings,
                output_dir=args.output,
            )

            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                if result.success:
                    print(f"✅ Generated {len(result.generated_files)} files from flowchart")
                    for f in result.generated_files:
                        print(f"   - {f.path}")
                else:
                    print(f"❌ Generation failed: {result.errors}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    exit_code = asyncio.run(run_cli(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
