#!/usr/bin/env python3
"""
Lucid XML Parser
================

Parses Lucidchart XML files to extract flowchart information
for use as input reference documents in code generation.

Converts flowcharts back to:
- Requirements lists
- Code patterns (service methods, repositories)
- SQL operations
- Process flow specifications

Usage:
    from services.reference_generator import LucidXMLParser
    
    parser = LucidXMLParser()
    flowchart = parser.parse("flowchart.xml")
    patterns = parser.extract_patterns(flowchart)
    requirements = parser.extract_requirements(flowchart)
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .lucid_flowchart_generator import (
    ConnectionType,
    Flowchart,
    FlowchartConnection,
    FlowchartNode,
    NodeType,
)
from .models import CodePattern, FileType, PatternType, ReferenceFile


# =============================================================================
# DATA MODELS FOR PARSED CONTENT
# =============================================================================


@dataclass
class ParsedRequirement:
    """A requirement extracted from a flowchart."""
    
    id: str
    title: str
    description: str = ""
    requirement_type: str = "functional"  # functional, non-functional
    priority: str = "medium"  # high, medium, low
    related_nodes: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "requirement_type": self.requirement_type,
            "priority": self.priority,
            "related_nodes": self.related_nodes,
            "acceptance_criteria": self.acceptance_criteria,
        }


@dataclass
class ParsedProcess:
    """A process/operation extracted from a flowchart."""
    
    id: str
    name: str
    process_type: str  # action, decision, data_operation, subprocess
    description: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "process_type": self.process_type,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "conditions": self.conditions,
        }


@dataclass
class ParsedDataFlow:
    """A data flow/table operation extracted from a flowchart."""
    
    id: str
    table_name: str
    operation: str  # read, write, update, delete
    columns: list[str] = field(default_factory=list)
    conditions: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "table_name": self.table_name,
            "operation": self.operation,
            "columns": self.columns,
            "conditions": self.conditions,
        }


@dataclass
class FlowchartParseResult:
    """Result of parsing a Lucid XML flowchart."""
    
    success: bool = False
    flowchart: Flowchart | None = None
    requirements: list[ParsedRequirement] = field(default_factory=list)
    processes: list[ParsedProcess] = field(default_factory=list)
    data_flows: list[ParsedDataFlow] = field(default_factory=list)
    generated_patterns: list[CodePattern] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "flowchart_name": self.flowchart.name if self.flowchart else None,
            "requirements": [r.to_dict() for r in self.requirements],
            "processes": [p.to_dict() for p in self.processes],
            "data_flows": [d.to_dict() for d in self.data_flows],
            "pattern_count": len(self.generated_patterns),
            "errors": self.errors,
            "warnings": self.warnings,
        }


# =============================================================================
# LUCID XML PARSER
# =============================================================================


class LucidXMLParser:
    """
    Parses Lucidchart XML files to extract structured information.
    
    Supports:
    - Standard Lucidchart XML export format
    - Custom DevFlow flowchart XML format
    - Mermaid-style text definitions (as fallback)
    """
    
    def __init__(self) -> None:
        """Initialize the parser."""
        # Shape type to node type mapping
        self._shape_to_node_type = {
            "ellipse": NodeType.START,
            "rectangle": NodeType.PROCESS,
            "diamond": NodeType.DECISION,
            "parallelogram": NodeType.DATA,
            "cylinder": NodeType.DATABASE,
            "document": NodeType.DOCUMENT,
            "predefinedprocess": NodeType.SUBPROCESS,
            "circle": NodeType.CONNECTOR,
            "offpagereference": NodeType.COMMENT,
        }
        
        # Keywords for classification
        self._requirement_keywords = [
            "shall", "must", "should", "will", "requirement",
            "feature", "user story", "acceptance", "criteria",
        ]
        self._data_keywords = [
            "read", "write", "select", "insert", "update", "delete",
            "fetch", "save", "load", "store", "query", "table",
        ]
    
    def parse(self, xml_path: str | Path) -> FlowchartParseResult:
        """
        Parse a Lucid XML file.
        
        Args:
            xml_path: Path to the XML file
            
        Returns:
            FlowchartParseResult with extracted information
        """
        result = FlowchartParseResult()
        
        try:
            path = Path(xml_path)
            if not path.exists():
                result.errors.append(f"File not found: {xml_path}")
                return result
            
            content = path.read_text(encoding="utf-8")
            return self.parse_content(content, path.stem)
            
        except Exception as e:
            result.errors.append(f"Parse error: {str(e)}")
            return result
    
    def parse_content(self, xml_content: str, name: str = "Flowchart") -> FlowchartParseResult:
        """
        Parse XML content string.
        
        Args:
            xml_content: XML content
            name: Name for the flowchart
            
        Returns:
            FlowchartParseResult
        """
        result = FlowchartParseResult()
        
        try:
            # Try to parse as XML
            root = ET.fromstring(xml_content)
            
            # Create flowchart
            flowchart = Flowchart(name=name)
            
            # Detect format and parse accordingly
            if root.tag == "lucidchart":
                self._parse_lucidchart_format(root, flowchart, result)
            elif root.tag == "mxGraphModel":
                self._parse_drawio_format(root, flowchart, result)
            else:
                # Try generic parsing
                self._parse_generic_xml(root, flowchart, result)
            
            result.flowchart = flowchart
            
            # Extract semantic information
            result.requirements = self._extract_requirements(flowchart)
            result.processes = self._extract_processes(flowchart)
            result.data_flows = self._extract_data_flows(flowchart)
            
            # Generate code patterns
            result.generated_patterns = self._generate_patterns(
                flowchart, result.requirements, result.processes, result.data_flows
            )
            
            result.success = True
            
        except ET.ParseError as e:
            result.errors.append(f"XML parse error: {str(e)}")
        except Exception as e:
            result.errors.append(f"Parse error: {str(e)}")
        
        return result
    
    def _parse_lucidchart_format(
        self,
        root: ET.Element,
        flowchart: Flowchart,
        result: FlowchartParseResult,
    ) -> None:
        """Parse Lucidchart/DevFlow XML format."""
        # Extract metadata
        meta = root.find("metadata")
        if meta is not None:
            name_elem = meta.find("name")
            if name_elem is not None and name_elem.text:
                flowchart.name = name_elem.text
            desc_elem = meta.find("description")
            if desc_elem is not None and desc_elem.text:
                flowchart.description = desc_elem.text
        
        # Find diagram and page
        diagram = root.find("diagram")
        if diagram is None:
            result.warnings.append("No diagram element found")
            return
        
        page = diagram.find("page")
        if page is None:
            page = diagram  # Use diagram as page
        
        # Parse shapes
        shapes = page.find("shapes")
        if shapes is not None:
            for shape in shapes.findall("shape"):
                node = self._parse_shape(shape)
                if node:
                    flowchart.add_node(node)
        
        # Parse lines/connections
        lines = page.find("lines")
        if lines is not None:
            for line in lines.findall("line"):
                conn = self._parse_line(line)
                if conn:
                    flowchart.add_connection(conn)
    
    def _parse_drawio_format(
        self,
        root: ET.Element,
        flowchart: Flowchart,
        result: FlowchartParseResult,
    ) -> None:
        """Parse draw.io/diagrams.net XML format."""
        # Find root cell
        root_elem = root.find(".//root")
        if root_elem is None:
            result.warnings.append("No root element in draw.io format")
            return
        
        # Parse all mxCell elements
        for cell in root_elem.findall("mxCell"):
            cell_id = cell.get("id", "")
            value = cell.get("value", "")
            style = cell.get("style", "")
            
            # Skip root and layer cells
            if cell_id in ("0", "1"):
                continue
            
            # Check if it's an edge (connection)
            if cell.get("edge") == "1":
                source = cell.get("source", "")
                target = cell.get("target", "")
                if source and target:
                    conn = FlowchartConnection(
                        id=cell_id,
                        source_id=source,
                        target_id=target,
                        label=value,
                    )
                    flowchart.add_connection(conn)
            else:
                # It's a vertex (node)
                geometry = cell.find("mxGeometry")
                x, y, width, height = 0, 0, 100, 60
                if geometry is not None:
                    x = int(float(geometry.get("x", 0)))
                    y = int(float(geometry.get("y", 0)))
                    width = int(float(geometry.get("width", 100)))
                    height = int(float(geometry.get("height", 60)))
                
                node_type = self._detect_node_type_from_style(style)
                
                if value:  # Only add nodes with labels
                    node = FlowchartNode(
                        id=cell_id,
                        label=self._clean_html(value),
                        node_type=node_type,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                    )
                    flowchart.add_node(node)
    
    def _parse_generic_xml(
        self,
        root: ET.Element,
        flowchart: Flowchart,
        result: FlowchartParseResult,
    ) -> None:
        """Parse generic XML format by searching for common patterns."""
        result.warnings.append(f"Unknown XML format: {root.tag}, attempting generic parse")
        
        # Look for any elements that might be shapes/nodes
        for elem in root.iter():
            # Check for shape-like elements
            if any(kw in elem.tag.lower() for kw in ["shape", "node", "box", "cell"]):
                node_id = elem.get("id", elem.get("Id", str(id(elem))))
                label = elem.get("label", elem.get("value", elem.get("text", "")))
                
                if not label:
                    # Try to find text content
                    text_elem = elem.find(".//text") or elem.find(".//content")
                    if text_elem is not None and text_elem.text:
                        label = text_elem.text
                
                if label:
                    node = FlowchartNode(
                        id=node_id,
                        label=self._clean_html(label),
                        node_type=self._detect_node_type_from_label(label),
                    )
                    flowchart.add_node(node)
            
            # Check for connection-like elements
            if any(kw in elem.tag.lower() for kw in ["line", "edge", "connector", "arrow"]):
                conn_id = elem.get("id", str(id(elem)))
                source = elem.get("source", elem.get("from", ""))
                target = elem.get("target", elem.get("to", ""))
                
                if source and target:
                    conn = FlowchartConnection(
                        id=conn_id,
                        source_id=source,
                        target_id=target,
                    )
                    flowchart.add_connection(conn)
    
    def _parse_shape(self, shape: ET.Element) -> FlowchartNode | None:
        """Parse a shape element into a FlowchartNode."""
        node_id = shape.get("id", "")
        shape_type = shape.get("type", "Rectangle").lower()
        
        # Get bounds
        bounds = shape.find("bounds")
        x, y, width, height = 0, 0, 100, 60
        if bounds is not None:
            x = int(float(bounds.get("x", 0)))
            y = int(float(bounds.get("y", 0)))
            width = int(float(bounds.get("width", 100)))
            height = int(float(bounds.get("height", 60)))
        
        # Get text content
        text_elem = shape.find("text/content")
        label = text_elem.text if text_elem is not None and text_elem.text else ""
        
        # Get tooltip/description
        tooltip = shape.find("tooltip")
        description = tooltip.text if tooltip is not None and tooltip.text else ""
        
        # Determine node type
        node_type = self._shape_to_node_type.get(shape_type, NodeType.PROCESS)
        
        # Override based on label content
        node_type = self._refine_node_type(node_type, label)
        
        return FlowchartNode(
            id=node_id,
            label=label,
            node_type=node_type,
            x=x,
            y=y,
            width=width,
            height=height,
            description=description,
        )
    
    def _parse_line(self, line: ET.Element) -> FlowchartConnection | None:
        """Parse a line element into a FlowchartConnection."""
        line_id = line.get("id", "")
        conn_type = line.get("type", "flow")
        
        # Get endpoints
        endpoints = line.find("endpoints")
        if endpoints is None:
            return None
        
        source = endpoints.find("source")
        target = endpoints.find("target")
        
        if source is None or target is None:
            return None
        
        source_id = source.get("shapeId", "")
        target_id = target.get("shapeId", "")
        
        if not source_id or not target_id:
            return None
        
        # Get label
        label_elem = line.find("label/content")
        label = label_elem.text if label_elem is not None and label_elem.text else ""
        
        # Determine connection type
        connection_type = ConnectionType.FLOW
        try:
            connection_type = ConnectionType(conn_type)
        except ValueError:
            if "yes" in conn_type.lower():
                connection_type = ConnectionType.YES
            elif "no" in conn_type.lower():
                connection_type = ConnectionType.NO
            elif "data" in conn_type.lower():
                connection_type = ConnectionType.DATA_FLOW
        
        return FlowchartConnection(
            id=line_id,
            source_id=source_id,
            target_id=target_id,
            connection_type=connection_type,
            label=label,
        )
    
    def _detect_node_type_from_style(self, style: str) -> NodeType:
        """Detect node type from draw.io style string."""
        style_lower = style.lower()
        
        if "ellipse" in style_lower:
            return NodeType.START
        if "rhombus" in style_lower or "diamond" in style_lower:
            return NodeType.DECISION
        if "cylinder" in style_lower:
            return NodeType.DATABASE
        if "parallelogram" in style_lower:
            return NodeType.DATA
        if "document" in style_lower:
            return NodeType.DOCUMENT
        if "process" in style_lower and "sub" in style_lower:
            return NodeType.SUBPROCESS
        
        return NodeType.PROCESS
    
    def _detect_node_type_from_label(self, label: str) -> NodeType:
        """Detect node type from label content."""
        label_lower = label.lower()
        
        if label_lower.startswith("start") or label_lower.startswith("begin"):
            return NodeType.START
        if label_lower.startswith("end") or label_lower.startswith("stop"):
            return NodeType.END
        if label_lower.startswith("if ") or "?" in label or label_lower.startswith("check"):
            return NodeType.DECISION
        if any(kw in label_lower for kw in ["read", "write", "table", "db", "database"]):
            return NodeType.DATABASE
        if any(kw in label_lower for kw in self._requirement_keywords):
            return NodeType.REQUIREMENT
        
        return NodeType.PROCESS
    
    def _refine_node_type(self, node_type: NodeType, label: str) -> NodeType:
        """Refine node type based on label content."""
        label_lower = label.lower()
        
        # Check for start/end
        if node_type == NodeType.START:
            if "end" in label_lower or "stop" in label_lower:
                return NodeType.END
        
        # Check for data operations
        if any(kw in label_lower for kw in self._data_keywords):
            return NodeType.DATABASE
        
        # Check for requirements
        if any(kw in label_lower for kw in self._requirement_keywords):
            return NodeType.REQUIREMENT
        
        return node_type
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        # Remove HTML tags
        clean = re.sub(r"<[^>]+>", "", text)
        # Decode HTML entities
        clean = clean.replace("&lt;", "<").replace("&gt;", ">")
        clean = clean.replace("&amp;", "&").replace("&quot;", '"')
        clean = clean.replace("&#xa;", "\n").replace("&#10;", "\n")
        return clean.strip()
    
    # =========================================================================
    # SEMANTIC EXTRACTION
    # =========================================================================
    
    def _extract_requirements(self, flowchart: Flowchart) -> list[ParsedRequirement]:
        """Extract requirements from flowchart nodes."""
        requirements: list[ParsedRequirement] = []
        
        for node in flowchart.nodes:
            # Check if node represents a requirement
            if node.node_type in (NodeType.REQUIREMENT, NodeType.DOCUMENT):
                req = ParsedRequirement(
                    id=node.id,
                    title=node.label,
                    description=node.description,
                    requirement_type="functional",
                )
                requirements.append(req)
            
            # Also check process nodes with requirement keywords
            elif any(kw in node.label.lower() for kw in self._requirement_keywords):
                req = ParsedRequirement(
                    id=node.id,
                    title=node.label,
                    description=node.description,
                    requirement_type="functional",
                )
                requirements.append(req)
        
        # Find related nodes through connections
        for req in requirements:
            for conn in flowchart.connections:
                if conn.source_id == req.id:
                    req.related_nodes.append(conn.target_id)
                elif conn.target_id == req.id:
                    req.related_nodes.append(conn.source_id)
        
        return requirements
    
    def _extract_processes(self, flowchart: Flowchart) -> list[ParsedProcess]:
        """Extract processes from flowchart nodes."""
        processes: list[ParsedProcess] = []
        
        for node in flowchart.nodes:
            if node.node_type in (NodeType.START, NodeType.END, NodeType.CONNECTOR):
                continue
            
            process_type = "action"
            if node.node_type == NodeType.DECISION:
                process_type = "decision"
            elif node.node_type == NodeType.DATABASE:
                process_type = "data_operation"
            elif node.node_type == NodeType.SUBPROCESS:
                process_type = "subprocess"
            
            process = ParsedProcess(
                id=node.id,
                name=node.label,
                process_type=process_type,
                description=node.description,
            )
            
            # Find inputs and outputs from connections
            for conn in flowchart.connections:
                if conn.target_id == node.id:
                    source_node = next(
                        (n for n in flowchart.nodes if n.id == conn.source_id),
                        None
                    )
                    if source_node:
                        process.inputs.append(source_node.label)
                elif conn.source_id == node.id:
                    target_node = next(
                        (n for n in flowchart.nodes if n.id == conn.target_id),
                        None
                    )
                    if target_node:
                        process.outputs.append(target_node.label)
                    if conn.label:
                        process.conditions.append(conn.label)
            
            processes.append(process)
        
        return processes
    
    def _extract_data_flows(self, flowchart: Flowchart) -> list[ParsedDataFlow]:
        """Extract data flows from flowchart."""
        data_flows: list[ParsedDataFlow] = []
        
        for node in flowchart.nodes:
            if node.node_type == NodeType.DATABASE:
                label_lower = node.label.lower()
                
                # Determine operation type
                operation = "read"
                if any(kw in label_lower for kw in ["write", "insert", "save", "create"]):
                    operation = "write"
                elif any(kw in label_lower for kw in ["update", "modify"]):
                    operation = "update"
                elif any(kw in label_lower for kw in ["delete", "remove"]):
                    operation = "delete"
                
                # Extract table name
                table_name = node.label
                # Try to extract from patterns like "Read: orders" or "Write to users"
                match = re.search(r"(?:from|to|:)\s*(\w+)", label_lower)
                if match:
                    table_name = match.group(1)
                
                data_flow = ParsedDataFlow(
                    id=node.id,
                    table_name=table_name,
                    operation=operation,
                )
                data_flows.append(data_flow)
        
        return data_flows
    
    # =========================================================================
    # PATTERN GENERATION
    # =========================================================================
    
    def _generate_patterns(
        self,
        flowchart: Flowchart,
        requirements: list[ParsedRequirement],
        processes: list[ParsedProcess],
        data_flows: list[ParsedDataFlow],
    ) -> list[CodePattern]:
        """Generate code patterns from parsed flowchart."""
        patterns: list[CodePattern] = []
        
        # Generate service method patterns from processes
        for process in processes:
            if process.process_type == "data_operation":
                continue  # Skip, handled by data flows
            
            # Create a service method pattern
            method_name = self._to_method_name(process.name)
            
            # Generate method signature
            params = ", ".join(f"{self._to_param_name(inp)}: Any" for inp in process.inputs[:3])
            
            code = f'''async def {method_name}(self, {params}) -> Any:
    """
    {process.name}
    
    {process.description if process.description else 'Auto-generated from flowchart.'}
    """
    # TODO: Implement {process.name}
    pass
'''
            
            pattern = CodePattern(
                name=method_name,
                pattern_type=PatternType.SERVICE_CLASS,
                source_file=f"flowchart:{flowchart.name}",
                code_snippet=code,
                entity_name=self._extract_entity_name(process.name),
                description=process.description or f"Generated from flowchart node: {process.name}",
                confidence=0.7,
                metadata={
                    "source_node_id": process.id,
                    "process_type": process.process_type,
                    "inputs": process.inputs,
                    "outputs": process.outputs,
                },
            )
            patterns.append(pattern)
        
        # Generate repository patterns from data flows
        tables_seen: set[str] = set()
        for df in data_flows:
            if df.table_name in tables_seen:
                continue
            tables_seen.add(df.table_name)
            
            entity_name = self._to_pascal_case(df.table_name)
            
            code = f'''class {entity_name}Repository:
    """Repository for {entity_name} entity."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_id(self, id: int) -> {entity_name} | None:
        """Get {entity_name} by ID."""
        stmt = select({entity_name}).where({entity_name}.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, entity: {entity_name}) -> {entity_name}:
        """Create new {entity_name}."""
        self.session.add(entity)
        await self.session.flush()
        return entity
'''
            
            pattern = CodePattern(
                name=f"{entity_name}Repository",
                pattern_type=PatternType.REPOSITORY,
                source_file=f"flowchart:{flowchart.name}",
                code_snippet=code,
                entity_name=entity_name,
                description=f"Repository for {entity_name} entity from flowchart",
                confidence=0.75,
                metadata={
                    "table_name": df.table_name,
                    "operations": [df.operation],
                },
            )
            patterns.append(pattern)
        
        return patterns
    
    def _to_method_name(self, label: str) -> str:
        """Convert label to method name."""
        # Remove special characters
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", label)
        # Convert to snake_case
        words = clean.lower().split()
        return "_".join(words[:5])  # Limit length
    
    def _to_param_name(self, label: str) -> str:
        """Convert label to parameter name."""
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", label)
        words = clean.lower().split()
        return "_".join(words[:3])
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        words = re.sub(r"[^a-zA-Z0-9]", " ", name).split()
        return "".join(w.title() for w in words)
    
    def _extract_entity_name(self, label: str) -> str:
        """Extract entity name from process label."""
        # Common patterns: "Create Order", "Update User", "Process Payment"
        words = label.split()
        
        # Skip action verbs
        action_verbs = ["create", "update", "delete", "get", "find", "process", "handle", "validate"]
        
        for word in words:
            if word.lower() not in action_verbs:
                return word.title()
        
        return words[-1].title() if words else "Entity"
    
    def to_reference_file(self, result: FlowchartParseResult) -> ReferenceFile | None:
        """
        Convert parse result to a ReferenceFile for use in code generation.
        
        Args:
            result: FlowchartParseResult
            
        Returns:
            ReferenceFile representing the flowchart
        """
        if not result.success or not result.flowchart:
            return None
        
        # Generate a markdown representation
        content_lines = [
            f"# {result.flowchart.name}",
            "",
            result.flowchart.description or "Flowchart-based requirements document.",
            "",
        ]
        
        # Add requirements section
        if result.requirements:
            content_lines.append("## Requirements")
            content_lines.append("")
            for req in result.requirements:
                content_lines.append(f"- **{req.title}**: {req.description}")
            content_lines.append("")
        
        # Add process section
        if result.processes:
            content_lines.append("## Processes")
            content_lines.append("")
            for proc in result.processes:
                content_lines.append(f"### {proc.name}")
                content_lines.append(f"Type: {proc.process_type}")
                if proc.inputs:
                    content_lines.append(f"Inputs: {', '.join(proc.inputs)}")
                if proc.outputs:
                    content_lines.append(f"Outputs: {', '.join(proc.outputs)}")
                content_lines.append("")
        
        # Add data flows section
        if result.data_flows:
            content_lines.append("## Data Operations")
            content_lines.append("")
            for df in result.data_flows:
                content_lines.append(f"- {df.operation.upper()} on `{df.table_name}`")
            content_lines.append("")
        
        return ReferenceFile(
            path=f"flowcharts/{result.flowchart.name}.md",
            content="\n".join(content_lines),
            file_type=FileType.REQUIREMENTS,
            language="markdown",
            patterns_found=[p.name for p in result.generated_patterns],
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def parse_lucid_xml(xml_path: str) -> FlowchartParseResult:
    """
    Convenience function to parse a Lucid XML file.
    
    Args:
        xml_path: Path to XML file
        
    Returns:
        FlowchartParseResult
    """
    parser = LucidXMLParser()
    return parser.parse(xml_path)


def extract_patterns_from_flowchart(xml_path: str) -> list[CodePattern]:
    """
    Extract code patterns from a Lucid XML flowchart.
    
    Args:
        xml_path: Path to XML file
        
    Returns:
        List of CodePattern objects
    """
    parser = LucidXMLParser()
    result = parser.parse(xml_path)
    return result.generated_patterns if result.success else []
