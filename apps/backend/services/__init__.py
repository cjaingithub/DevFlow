"""
Services Module
===============

Background services and orchestration for DevFlow.

Includes:
- ServiceOrchestrator: Multi-service environment management
- ServiceContext: Context manager for service lifecycle
- RecoveryManager: Error recovery and retry logic
- ReferenceGeneratorService: Reference-based code generation
"""

from .context import ServiceContext
from .orchestrator import ServiceOrchestrator
from .recovery import RecoveryManager
from .reference_generator import (
    CodeGenerator,
    CodePattern,
    ConnectionType,
    EntityMapping,
    FileType,
    Flowchart,
    FlowchartConnection,
    FlowchartGenerationResult,
    FlowchartNode,
    GeneratedFile,
    GenerationResult,
    InfraEntityMapping,
    LucidFlowchartGenerator,
    NodeType,
    PatternExtractor,
    PatternType,
    ReferenceGeneratorService,
    ReferenceManager,
    ReferenceProject,
    SQLConverter,
    SQLTable,
    TechStack,
)

__all__ = [
    # Core services
    "ServiceContext",
    "ServiceOrchestrator",
    "RecoveryManager",
    # Reference generator
    "ReferenceGeneratorService",
    "ReferenceManager",
    "PatternExtractor",
    "CodeGenerator",
    "SQLConverter",
    # Flowchart generator
    "LucidFlowchartGenerator",
    "Flowchart",
    "FlowchartNode",
    "FlowchartConnection",
    "FlowchartGenerationResult",
    # Models
    "ReferenceProject",
    "CodePattern",
    "SQLTable",
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
]
