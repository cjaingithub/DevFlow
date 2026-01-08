#!/usr/bin/env python3
"""
Reference Manager
=================

Manages reference projects: loading, storing, indexing, and retrieval.

Responsibilities:
- Load reference folders and parse all files
- Extract and index patterns from files
- Store references for later use
- Search and retrieve patterns by criteria
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .lucid_xml_parser import LucidXMLParser
from .models import (
    CodePattern,
    FileType,
    PatternType,
    ReferenceFile,
    ReferenceProject,
    SQLTable,
    TechStack,
)
from .pattern_extractor import PatternExtractor
from .sql_converter import SQLConverter


# =============================================================================
# CONSTANTS
# =============================================================================


# File extensions to include when loading references
INCLUDED_EXTENSIONS = {
    ".py", ".pyi",  # Python
    ".ts", ".tsx", ".js", ".jsx",  # TypeScript/JavaScript
    ".sql",  # SQL
    ".tf", ".tfvars",  # Terraform
    ".json", ".yaml", ".yml",  # Config files
    ".md", ".txt",  # Markdown and text (requirements/documentation)
    ".java", ".go", ".rs",  # Other languages
    ".xml",  # Lucid flowchart XML files
}

# Files/directories to skip
SKIP_PATTERNS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".terraform",
    "*.pyc",
    "*.pyo",
}

# Default storage location for reference metadata
DEFAULT_STORAGE_DIR = ".devflow/references"


# =============================================================================
# REFERENCE MANAGER
# =============================================================================


class ReferenceManager:
    """
    Manages reference projects for code generation.

    Usage:
        manager = ReferenceManager(project_dir)
        reference = await manager.load_reference("examples/user-auth", "user-auth")
        patterns = manager.search_patterns(pattern_type=PatternType.SERVICE_CLASS)
    """

    def __init__(self, project_dir: Path | str) -> None:
        """
        Initialize the reference manager.

        Args:
            project_dir: Path to the current project directory
        """
        self.project_dir = Path(project_dir)
        self.storage_dir = self.project_dir / DEFAULT_STORAGE_DIR
        self._references: dict[str, ReferenceProject] = {}
        self._pattern_extractor = PatternExtractor()
        self._sql_converter = SQLConverter()
        self._xml_parser = LucidXMLParser()

        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Load existing references
        self._load_stored_references()

    def _load_stored_references(self) -> None:
        """Load previously stored reference metadata."""
        index_file = self.storage_dir / "index.json"
        if not index_file.exists():
            return

        try:
            with open(index_file, encoding="utf-8") as f:
                data = json.load(f)

            for ref_data in data.get("references", []):
                ref = ReferenceProject.from_dict(ref_data)
                self._references[ref.name] = ref

        except (json.JSONDecodeError, OSError):
            # Ignore corrupt or unreadable index
            pass

    def _save_reference_index(self) -> None:
        """Save reference index to disk."""
        index_file = self.storage_dir / "index.json"

        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "references": [ref.to_dict() for ref in self._references.values()],
        }

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    async def load_reference(
        self,
        reference_path: str | Path,
        name: str,
        description: str = "",
    ) -> ReferenceProject:
        """
        Load a reference folder and extract patterns.

        Args:
            reference_path: Path to the reference folder
            name: Name to identify this reference
            description: Optional description

        Returns:
            ReferenceProject with extracted patterns
        """
        ref_path = Path(reference_path)
        if not ref_path.is_absolute():
            ref_path = self.project_dir / ref_path

        if not ref_path.exists():
            raise FileNotFoundError(f"Reference path not found: {ref_path}")

        # Create reference project
        reference = ReferenceProject(
            name=name,
            path=str(ref_path),
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Load all files
        reference.files = self._load_files(ref_path)

        # Extract patterns from each file
        for file in reference.files:
            # Check if it's an XML flowchart file
            if file.extension == ".xml":
                xml_patterns = self._process_flowchart_xml(file)
                reference.patterns.extend(xml_patterns)
                file.patterns_found = [p.name for p in xml_patterns]
            else:
                patterns = self._pattern_extractor.extract_patterns(file)
                reference.patterns.extend(patterns)
                file.patterns_found = [p.name for p in patterns]

        # Detect tech stack
        reference.tech_stack = self._pattern_extractor.detect_tech_stack(
            reference.files
        )

        # Parse SQL tables
        for file in reference.files:
            if file.file_type in (FileType.SQL_SCHEMA, FileType.SQL_MIGRATION):
                tables = self._sql_converter.parse_create_table(file.content)
                reference.sql_tables.extend(tables)

        # Extract requirements from markdown files
        for file in reference.files:
            if file.file_type == FileType.REQUIREMENTS:
                reference.requirements.extend(
                    self._extract_requirements(file.content)
                )

        # Store reference
        self._references[name] = reference
        self._save_reference_index()

        # Save detailed reference data
        self._save_reference_detail(reference)

        return reference

    def _load_files(self, root_path: Path) -> list[ReferenceFile]:
        """Load all relevant files from a directory."""
        files: list[ReferenceFile] = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter out skip patterns
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_PATTERNS and not d.startswith(".")
            ]

            for filename in filenames:
                filepath = Path(dirpath) / filename
                ext = filepath.suffix.lower()

                # Skip files not in included extensions
                if ext not in INCLUDED_EXTENSIONS:
                    continue

                # Skip hidden files
                if filename.startswith("."):
                    continue

                try:
                    content = filepath.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

                relative_path = filepath.relative_to(root_path).as_posix()

                # Detect file type
                file_type = self._pattern_extractor.detect_file_type(
                    relative_path, content
                )

                files.append(
                    ReferenceFile(
                        path=relative_path,
                        content=content,
                        file_type=file_type,
                        language=self._detect_language(ext),
                    )
                )

        return files

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        ext_to_lang = {
            ".py": "python",
            ".pyi": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".sql": "sql",
            ".tf": "terraform",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
        }
        return ext_to_lang.get(extension.lower(), "")

    def _extract_requirements(self, content: str) -> list[str]:
        """Extract requirement items from markdown."""
        requirements: list[str] = []

        # Find bullet points
        import re
        bullet_matches = re.findall(r"^[-*]\s+(.+)$", content, re.MULTILINE)
        requirements.extend(bullet_matches)

        # Find numbered lists
        numbered_matches = re.findall(r"^\d+\.\s+(.+)$", content, re.MULTILINE)
        requirements.extend(numbered_matches)

        return requirements

    def _process_flowchart_xml(self, file: ReferenceFile) -> list[CodePattern]:
        """
        Process an XML flowchart file and extract patterns.
        
        Args:
            file: ReferenceFile containing XML content
            
        Returns:
            List of extracted CodePattern objects
        """
        result = self._xml_parser.parse_content(file.content, file.name)
        
        if not result.success:
            return []
        
        # Update file type
        file.file_type = FileType.REQUIREMENTS
        
        # Add metadata about the flowchart
        file.metadata["flowchart_name"] = result.flowchart.name if result.flowchart else ""
        file.metadata["node_count"] = len(result.flowchart.nodes) if result.flowchart else 0
        file.metadata["requirement_count"] = len(result.requirements)
        file.metadata["process_count"] = len(result.processes)
        file.metadata["data_flow_count"] = len(result.data_flows)
        
        return result.generated_patterns

    async def load_flowchart_xml(
        self,
        xml_path: str | Path,
        name: str,
        description: str = "",
    ) -> ReferenceProject:
        """
        Load a Lucid XML flowchart as a reference project.
        
        This is a convenience method for loading a single XML flowchart file
        as a reference, extracting requirements and patterns from it.
        
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
        
        if not path.exists():
            raise FileNotFoundError(f"XML file not found: {path}")
        
        # Parse the XML
        result = self._xml_parser.parse(path)
        
        if not result.success:
            raise ValueError(f"Failed to parse XML: {result.errors}")
        
        # Create reference project
        reference = ReferenceProject(
            name=name,
            path=str(path),
            description=description or result.flowchart.description if result.flowchart else "",
        )
        
        # Add the XML file
        content = path.read_text(encoding="utf-8")
        xml_file = ReferenceFile(
            path=path.name,
            content=content,
            file_type=FileType.REQUIREMENTS,
            language="xml",
            patterns_found=[p.name for p in result.generated_patterns],
            metadata={
                "flowchart_name": result.flowchart.name if result.flowchart else "",
                "is_flowchart_xml": True,
            },
        )
        reference.files.append(xml_file)
        
        # Add the markdown representation as well
        ref_file = self._xml_parser.to_reference_file(result)
        if ref_file:
            reference.files.append(ref_file)
        
        # Add extracted patterns
        reference.patterns.extend(result.generated_patterns)
        
        # Extract requirements as strings
        for req in result.requirements:
            reference.requirements.append(req.title)
        
        # Store reference
        self._references[name] = reference
        self._save_reference_index()
        self._save_reference_detail(reference)
        
        return reference

    def _save_reference_detail(self, reference: ReferenceProject) -> None:
        """Save detailed reference data to disk."""
        ref_dir = self.storage_dir / reference.name
        ref_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        meta_file = ref_dir / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(reference.to_dict(), f, indent=2)

        # Save patterns
        patterns_file = ref_dir / "patterns.json"
        with open(patterns_file, "w", encoding="utf-8") as f:
            json.dump(
                [p.to_dict() for p in reference.patterns],
                f,
                indent=2,
            )

        # Save SQL tables
        if reference.sql_tables:
            tables_file = ref_dir / "sql_tables.json"
            with open(tables_file, "w", encoding="utf-8") as f:
                json.dump(
                    [t.to_dict() for t in reference.sql_tables],
                    f,
                    indent=2,
                )

    def get_reference(self, name: str) -> ReferenceProject | None:
        """
        Get a reference by name.

        Args:
            name: Reference name

        Returns:
            ReferenceProject if found, None otherwise
        """
        return self._references.get(name)

    def list_references(self) -> list[ReferenceProject]:
        """
        List all loaded references.

        Returns:
            List of ReferenceProject objects
        """
        return list(self._references.values())

    def delete_reference(self, name: str) -> bool:
        """
        Delete a reference.

        Args:
            name: Reference name to delete

        Returns:
            True if deleted, False if not found
        """
        if name not in self._references:
            return False

        del self._references[name]

        # Remove storage
        ref_dir = self.storage_dir / name
        if ref_dir.exists():
            import shutil
            shutil.rmtree(ref_dir)

        self._save_reference_index()
        return True

    def search_patterns(
        self,
        reference_name: str | None = None,
        pattern_type: PatternType | None = None,
        entity_name: str | None = None,
        file_type: FileType | None = None,
    ) -> list[CodePattern]:
        """
        Search for patterns across references.

        Args:
            reference_name: Filter by reference name
            pattern_type: Filter by pattern type
            entity_name: Filter by entity name (partial match)
            file_type: Filter by source file type

        Returns:
            List of matching patterns
        """
        results: list[CodePattern] = []

        # Determine which references to search
        if reference_name:
            refs = [self._references[reference_name]] if reference_name in self._references else []
        else:
            refs = list(self._references.values())

        for ref in refs:
            for pattern in ref.patterns:
                # Apply filters
                if pattern_type and pattern.pattern_type != pattern_type:
                    continue

                if entity_name:
                    if entity_name.lower() not in pattern.entity_name.lower():
                        continue

                if file_type:
                    # Check if source file matches file type
                    source_file = next(
                        (f for f in ref.files if f.path == pattern.source_file),
                        None,
                    )
                    if source_file and source_file.file_type != file_type:
                        continue

                results.append(pattern)

        return results

    def get_patterns_by_type(
        self,
        reference_name: str,
        pattern_types: list[PatternType],
    ) -> dict[PatternType, list[CodePattern]]:
        """
        Get patterns grouped by type.

        Args:
            reference_name: Reference to search
            pattern_types: Types to include

        Returns:
            Dict mapping pattern types to patterns
        """
        result: dict[PatternType, list[CodePattern]] = {
            pt: [] for pt in pattern_types
        }

        ref = self._references.get(reference_name)
        if not ref:
            return result

        for pattern in ref.patterns:
            if pattern.pattern_type in pattern_types:
                result[pattern.pattern_type].append(pattern)

        return result

    def get_sql_tables(self, reference_name: str) -> list[SQLTable]:
        """
        Get SQL tables from a reference.

        Args:
            reference_name: Reference name

        Returns:
            List of SQLTable objects
        """
        ref = self._references.get(reference_name)
        return ref.sql_tables if ref else []

    def update_usage(self, reference_name: str) -> None:
        """
        Update usage statistics for a reference.

        Args:
            reference_name: Reference name
        """
        ref = self._references.get(reference_name)
        if ref:
            ref.usage_count += 1
            ref.last_used = datetime.now()
            self._save_reference_index()

    def get_reference_stats(self, reference_name: str) -> dict[str, Any]:
        """
        Get statistics about a reference.

        Args:
            reference_name: Reference name

        Returns:
            Dict with statistics
        """
        ref = self._references.get(reference_name)
        if not ref:
            return {}

        # Count patterns by type
        pattern_counts: dict[str, int] = {}
        for pattern in ref.patterns:
            pt = pattern.pattern_type.value
            pattern_counts[pt] = pattern_counts.get(pt, 0) + 1

        # Count files by type
        file_counts: dict[str, int] = {}
        for file in ref.files:
            ft = file.file_type.value
            file_counts[ft] = file_counts.get(ft, 0) + 1

        return {
            "name": ref.name,
            "description": ref.description,
            "path": ref.path,
            "total_files": len(ref.files),
            "total_patterns": len(ref.patterns),
            "total_sql_tables": len(ref.sql_tables),
            "tech_stack": [t.value for t in ref.tech_stack],
            "pattern_counts": pattern_counts,
            "file_counts": file_counts,
            "usage_count": ref.usage_count,
            "last_used": ref.last_used.isoformat() if ref.last_used else None,
            "created_at": ref.created_at.isoformat(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert manager state to dictionary."""
        return {
            "project_dir": str(self.project_dir),
            "storage_dir": str(self.storage_dir),
            "reference_count": len(self._references),
            "references": [
                {
                    "name": ref.name,
                    "path": ref.path,
                    "patterns": len(ref.patterns),
                    "files": len(ref.files),
                    "tech_stack": [t.value for t in ref.tech_stack],
                }
                for ref in self._references.values()
            ],
        }


# =============================================================================
# ASYNC HELPER
# =============================================================================


async def load_reference_project(
    project_dir: Path,
    reference_path: str,
    name: str,
    description: str = "",
) -> ReferenceProject:
    """
    Helper function to load a reference project.

    Args:
        project_dir: Current project directory
        reference_path: Path to reference folder
        name: Name for the reference
        description: Optional description

    Returns:
        Loaded ReferenceProject
    """
    manager = ReferenceManager(project_dir)
    return await manager.load_reference(reference_path, name, description)
