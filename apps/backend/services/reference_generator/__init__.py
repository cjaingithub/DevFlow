"""
Reference Generator Package
===========================

Reference-Based Code Generation for DevFlow.

This package provides the ability to:
- Load reference implementations as templates
- Extract code patterns from reference files
- Transform SQL schemas between dialects
- Generate new code by applying patterns with entity substitution

Usage:
    from services.reference_generator import ReferenceGeneratorService

    service = ReferenceGeneratorService(project_dir="/my/project")
    
    # Load a reference
    reference = await service.load_reference(
        reference_path="examples/user-auth",
        name="user-auth-feature",
    )
    
    # Generate code for new requirements
    result = await service.generate_from_reference(
        reference_name="user-auth-feature",
        new_requirements_path="specs/product-catalog.md",
        entity_mappings=[
            {"reference": "User", "new": "Product"},
        ],
        output_dir="generated/product-catalog",
    )

CLI Usage:
    # Load a reference
    python -m services.reference_generator.service \\
        --action load --reference examples/user-auth --name user-auth

    # Generate code
    python -m services.reference_generator.service \\
        --action generate --name user-auth \\
        --requirements product.md --output generated/product
"""

from .code_generator import CodeGenerator, generate_from_reference
from .lucid_flowchart_generator import (
    ConnectionType,
    Flowchart,
    FlowchartConnection,
    FlowchartGenerationResult,
    FlowchartNode,
    LucidFlowchartGenerator,
    LucidXMLGenerator,
    NodeType,
    generate_flowchart_from_docs,
    generate_flowchart_from_sql,
)
from .lucid_xml_parser import (
    FlowchartParseResult,
    LucidXMLParser,
    ParsedDataFlow,
    ParsedProcess,
    ParsedRequirement,
    extract_patterns_from_flowchart,
    parse_lucid_xml,
)
from .models import (
    CodePattern,
    EntityMapping,
    FileType,
    GeneratedFile,
    GenerationResult,
    InfraEntityMapping,
    PatternType,
    ReferenceFile,
    ReferenceProject,
    SQLTable,
    SQLTransformation,
    TechStack,
)
from .pattern_extractor import PatternExtractor, extract_patterns_from_file
from .reference_manager import ReferenceManager, load_reference_project
from .service import ReferenceGeneratorService
from .sql_converter import (
    SQLConverter,
    StoredProcedureConverter,
    convert_oracle_to_postgres,
)

__all__ = [
    # Main service
    "ReferenceGeneratorService",
    # Core classes
    "ReferenceManager",
    "PatternExtractor",
    "CodeGenerator",
    "SQLConverter",
    "StoredProcedureConverter",
    # Flowchart generation classes
    "LucidFlowchartGenerator",
    "LucidXMLGenerator",
    "Flowchart",
    "FlowchartNode",
    "FlowchartConnection",
    "FlowchartGenerationResult",
    # Flowchart parsing classes
    "LucidXMLParser",
    "FlowchartParseResult",
    "ParsedRequirement",
    "ParsedProcess",
    "ParsedDataFlow",
    # Models
    "ReferenceProject",
    "ReferenceFile",
    "CodePattern",
    "SQLTable",
    "SQLTransformation",
    "EntityMapping",
    "InfraEntityMapping",
    "GeneratedFile",
    "GenerationResult",
    # Enums
    "PatternType",
    "FileType",
    "TechStack",
    "NodeType",
    "ConnectionType",
    # Convenience functions
    "extract_patterns_from_file",
    "load_reference_project",
    "generate_from_reference",
    "convert_oracle_to_postgres",
    "generate_flowchart_from_sql",
    "generate_flowchart_from_docs",
    "parse_lucid_xml",
    "extract_patterns_from_flowchart",
]
