#!/usr/bin/env python3
"""
Lucid Flowchart Generator
=========================

Generates XML flowcharts from Oracle SQL files and documentation.

Produces Lucidchart-compatible XML for:
- Stored procedure logic flows
- Data flow diagrams
- Requirement relationship charts
- Entity relationship diagrams

Usage:
    from services.reference_generator import LucidFlowchartGenerator
    
    generator = LucidFlowchartGenerator()
    xml = generator.generate_from_sql("path/to/procedure.sql")
    xml = generator.generate_from_docs("path/to/requirements.md")
"""

import re
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from xml.dom import minidom


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================


class NodeType(str, Enum):
    """Types of flowchart nodes."""
    
    START = "start"
    END = "end"
    PROCESS = "process"
    DECISION = "decision"
    DATA = "data"
    DATABASE = "database"
    DOCUMENT = "document"
    SUBPROCESS = "subprocess"
    CONNECTOR = "connector"
    COMMENT = "comment"
    REQUIREMENT = "requirement"
    ACTOR = "actor"
    TABLE = "table"


class ConnectionType(str, Enum):
    """Types of connections between nodes."""
    
    FLOW = "flow"
    DATA_FLOW = "data_flow"
    DEPENDENCY = "dependency"
    IMPLEMENTS = "implements"
    REFERENCES = "references"
    YES = "yes"
    NO = "no"


# Lucidchart shape IDs mapping
LUCID_SHAPES = {
    NodeType.START: "Ellipse",
    NodeType.END: "Ellipse",
    NodeType.PROCESS: "Rectangle",
    NodeType.DECISION: "Diamond",
    NodeType.DATA: "Parallelogram",
    NodeType.DATABASE: "Cylinder",
    NodeType.DOCUMENT: "Document",
    NodeType.SUBPROCESS: "PredefinedProcess",
    NodeType.CONNECTOR: "Circle",
    NodeType.COMMENT: "OffPageReference",
    NodeType.REQUIREMENT: "Rectangle",
    NodeType.ACTOR: "Ellipse",
    NodeType.TABLE: "Rectangle",
}

# Colors for different node types
NODE_COLORS = {
    NodeType.START: "#22c55e",  # Green
    NodeType.END: "#ef4444",    # Red
    NodeType.PROCESS: "#3b82f6", # Blue
    NodeType.DECISION: "#f59e0b", # Amber
    NodeType.DATA: "#8b5cf6",    # Purple
    NodeType.DATABASE: "#06b6d4", # Cyan
    NodeType.DOCUMENT: "#64748b", # Slate
    NodeType.SUBPROCESS: "#6366f1", # Indigo
    NodeType.REQUIREMENT: "#10b981", # Emerald
    NodeType.TABLE: "#0ea5e9",   # Sky
}


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class FlowchartNode:
    """A node in the flowchart."""
    
    id: str
    label: str
    node_type: NodeType
    x: int = 0
    y: int = 0
    width: int = 120
    height: int = 60
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class FlowchartConnection:
    """A connection between nodes."""
    
    id: str
    source_id: str
    target_id: str
    connection_type: ConnectionType = ConnectionType.FLOW
    label: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "connection_type": self.connection_type.value,
            "label": self.label,
        }


@dataclass
class Flowchart:
    """A complete flowchart."""
    
    name: str
    description: str = ""
    nodes: list[FlowchartNode] = field(default_factory=list)
    connections: list[FlowchartConnection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, node: FlowchartNode) -> None:
        """Add a node to the flowchart."""
        self.nodes.append(node)
    
    def add_connection(self, connection: FlowchartConnection) -> None:
        """Add a connection to the flowchart."""
        self.connections.append(connection)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "connections": [c.to_dict() for c in self.connections],
            "metadata": self.metadata,
        }


@dataclass
class FlowchartGenerationResult:
    """Result of flowchart generation."""
    
    success: bool = False
    flowchart: Flowchart | None = None
    xml_content: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# SQL PARSER
# =============================================================================


class OracleSQLParser:
    """
    Parses Oracle SQL files to extract flow information.
    
    Extracts:
    - Stored procedure logic
    - Control flow (IF/ELSE, LOOP, CASE)
    - Data operations (SELECT, INSERT, UPDATE, DELETE)
    - Exception handling
    """
    
    def __init__(self) -> None:
        """Initialize the parser."""
        self._procedure_pattern = re.compile(
            r"CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)\s*\(([^)]*)\)",
            re.IGNORECASE | re.DOTALL,
        )
        self._if_pattern = re.compile(
            r"\bIF\s+(.+?)\s+THEN\b",
            re.IGNORECASE,
        )
        self._elsif_pattern = re.compile(
            r"\bELSIF\s+(.+?)\s+THEN\b",
            re.IGNORECASE,
        )
        self._else_pattern = re.compile(r"\bELSE\b", re.IGNORECASE)
        self._endif_pattern = re.compile(r"\bEND\s+IF\b", re.IGNORECASE)
        self._loop_pattern = re.compile(
            r"\b(FOR|WHILE|LOOP)\b",
            re.IGNORECASE,
        )
        self._case_pattern = re.compile(
            r"\bCASE\s+(\w+)\b",
            re.IGNORECASE,
        )
        self._when_pattern = re.compile(
            r"\bWHEN\s+(.+?)\s+THEN\b",
            re.IGNORECASE,
        )
        self._select_pattern = re.compile(
            r"\bSELECT\s+.+?\s+(?:INTO\s+.+?\s+)?FROM\s+(\w+)",
            re.IGNORECASE | re.DOTALL,
        )
        self._insert_pattern = re.compile(
            r"\bINSERT\s+INTO\s+(\w+)",
            re.IGNORECASE,
        )
        self._update_pattern = re.compile(
            r"\bUPDATE\s+(\w+)\s+SET\b",
            re.IGNORECASE,
        )
        self._delete_pattern = re.compile(
            r"\bDELETE\s+FROM\s+(\w+)",
            re.IGNORECASE,
        )
        self._exception_pattern = re.compile(
            r"\bEXCEPTION\b",
            re.IGNORECASE,
        )
        self._commit_pattern = re.compile(r"\bCOMMIT\b", re.IGNORECASE)
        self._rollback_pattern = re.compile(r"\bROLLBACK\b", re.IGNORECASE)
    
    def parse(self, sql_content: str) -> Flowchart:
        """
        Parse Oracle SQL and generate a flowchart.
        
        Args:
            sql_content: Oracle SQL content
            
        Returns:
            Flowchart representing the SQL logic
        """
        # Extract procedure name
        proc_match = self._procedure_pattern.search(sql_content)
        proc_name = proc_match.group(1) if proc_match else "SQL_Procedure"
        
        flowchart = Flowchart(
            name=f"{proc_name} Flow",
            description=f"Logic flow for {proc_name}",
        )
        
        # Add start node
        start_node = FlowchartNode(
            id=self._gen_id(),
            label=f"Start: {proc_name}",
            node_type=NodeType.START,
            x=300,
            y=50,
        )
        flowchart.add_node(start_node)
        
        # Parse the SQL body
        nodes, connections = self._parse_body(sql_content, start_node.id, 50)
        
        for node in nodes:
            flowchart.add_node(node)
        for conn in connections:
            flowchart.add_connection(conn)
        
        # Add end node if not present
        if not any(n.node_type == NodeType.END for n in flowchart.nodes):
            end_node = FlowchartNode(
                id=self._gen_id(),
                label="End",
                node_type=NodeType.END,
                x=300,
                y=max(n.y for n in flowchart.nodes) + 100,
            )
            flowchart.add_node(end_node)
            
            # Connect last process to end
            if nodes:
                flowchart.add_connection(FlowchartConnection(
                    id=self._gen_id(),
                    source_id=nodes[-1].id,
                    target_id=end_node.id,
                ))
        
        return flowchart
    
    def _parse_body(
        self,
        sql_content: str,
        prev_node_id: str,
        start_y: int,
    ) -> tuple[list[FlowchartNode], list[FlowchartConnection]]:
        """Parse SQL body and extract nodes/connections."""
        nodes: list[FlowchartNode] = []
        connections: list[FlowchartConnection] = []
        current_y = start_y + 80
        current_prev = prev_node_id
        
        # Find all data operations
        tables_read: set[str] = set()
        tables_written: set[str] = set()
        
        for match in self._select_pattern.finditer(sql_content):
            tables_read.add(match.group(1))
        
        for match in self._insert_pattern.finditer(sql_content):
            tables_written.add(match.group(1))
        
        for match in self._update_pattern.finditer(sql_content):
            tables_written.add(match.group(1))
        
        for match in self._delete_pattern.finditer(sql_content):
            tables_written.add(match.group(1))
        
        # Add data read nodes
        if tables_read:
            for table in tables_read:
                node = FlowchartNode(
                    id=self._gen_id(),
                    label=f"Read: {table}",
                    node_type=NodeType.DATABASE,
                    x=300,
                    y=current_y,
                    description=f"SELECT from {table}",
                )
                nodes.append(node)
                connections.append(FlowchartConnection(
                    id=self._gen_id(),
                    source_id=current_prev,
                    target_id=node.id,
                    connection_type=ConnectionType.DATA_FLOW,
                ))
                current_prev = node.id
                current_y += 80
        
        # Find IF statements and create decision nodes
        if_matches = list(self._if_pattern.finditer(sql_content))
        for match in if_matches:
            condition = match.group(1).strip()[:50]  # Truncate long conditions
            
            decision_node = FlowchartNode(
                id=self._gen_id(),
                label=f"If: {condition}",
                node_type=NodeType.DECISION,
                x=300,
                y=current_y,
                width=150,
                height=80,
            )
            nodes.append(decision_node)
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=current_prev,
                target_id=decision_node.id,
            ))
            
            # Add Yes branch placeholder
            yes_node = FlowchartNode(
                id=self._gen_id(),
                label="Process (Yes)",
                node_type=NodeType.PROCESS,
                x=150,
                y=current_y + 100,
            )
            nodes.append(yes_node)
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=decision_node.id,
                target_id=yes_node.id,
                connection_type=ConnectionType.YES,
                label="Yes",
            ))
            
            # Add No branch placeholder
            no_node = FlowchartNode(
                id=self._gen_id(),
                label="Process (No)",
                node_type=NodeType.PROCESS,
                x=450,
                y=current_y + 100,
            )
            nodes.append(no_node)
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=decision_node.id,
                target_id=no_node.id,
                connection_type=ConnectionType.NO,
                label="No",
            ))
            
            # Merge node
            merge_node = FlowchartNode(
                id=self._gen_id(),
                label="Continue",
                node_type=NodeType.CONNECTOR,
                x=300,
                y=current_y + 180,
                width=40,
                height=40,
            )
            nodes.append(merge_node)
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=yes_node.id,
                target_id=merge_node.id,
            ))
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=no_node.id,
                target_id=merge_node.id,
            ))
            
            current_prev = merge_node.id
            current_y += 260
        
        # Add data write nodes
        if tables_written:
            for table in tables_written:
                node = FlowchartNode(
                    id=self._gen_id(),
                    label=f"Write: {table}",
                    node_type=NodeType.DATABASE,
                    x=300,
                    y=current_y,
                    description=f"INSERT/UPDATE/DELETE on {table}",
                )
                nodes.append(node)
                connections.append(FlowchartConnection(
                    id=self._gen_id(),
                    source_id=current_prev,
                    target_id=node.id,
                    connection_type=ConnectionType.DATA_FLOW,
                ))
                current_prev = node.id
                current_y += 80
        
        # Check for exception handling
        if self._exception_pattern.search(sql_content):
            exception_node = FlowchartNode(
                id=self._gen_id(),
                label="Exception Handler",
                node_type=NodeType.SUBPROCESS,
                x=500,
                y=current_y - 40,
            )
            nodes.append(exception_node)
        
        # Check for COMMIT/ROLLBACK
        if self._commit_pattern.search(sql_content):
            commit_node = FlowchartNode(
                id=self._gen_id(),
                label="COMMIT",
                node_type=NodeType.PROCESS,
                x=300,
                y=current_y,
            )
            nodes.append(commit_node)
            connections.append(FlowchartConnection(
                id=self._gen_id(),
                source_id=current_prev,
                target_id=commit_node.id,
            ))
            current_prev = commit_node.id
            current_y += 80
        
        return nodes, connections
    
    def _gen_id(self) -> str:
        """Generate unique ID."""
        return str(uuid.uuid4())[:8]


# =============================================================================
# DOCUMENTATION PARSER
# =============================================================================


class DocumentationParser:
    """
    Parses documentation and text files to extract requirements.
    
    Extracts:
    - Requirements (bullet points, numbered lists)
    - Features and user stories
    - Acceptance criteria
    - Dependencies and relationships
    """
    
    def __init__(self) -> None:
        """Initialize the parser."""
        self._heading_pattern = re.compile(r"^#+\s+(.+)$", re.MULTILINE)
        self._bullet_pattern = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)
        self._numbered_pattern = re.compile(r"^\d+\.\s+(.+)$", re.MULTILINE)
        self._requirement_keywords = [
            "shall", "must", "should", "will", "can", "may",
            "requirement", "feature", "user story", "acceptance",
        ]
    
    def parse(self, doc_content: str, doc_name: str = "Requirements") -> Flowchart:
        """
        Parse documentation and generate a requirements flowchart.
        
        Args:
            doc_content: Documentation content
            doc_name: Name of the document
            
        Returns:
            Flowchart representing requirements
        """
        flowchart = Flowchart(
            name=f"{doc_name} Requirements Flow",
            description=f"Requirements diagram from {doc_name}",
        )
        
        # Extract headings as main categories
        headings = self._heading_pattern.findall(doc_content)
        
        # Extract requirements from bullets
        bullets = self._bullet_pattern.findall(doc_content)
        numbered = self._numbered_pattern.findall(doc_content)
        
        all_requirements = bullets + numbered
        
        # Create nodes
        current_y = 50
        current_x = 50
        
        # Add main title node
        title_node = FlowchartNode(
            id=self._gen_id(),
            label=doc_name,
            node_type=NodeType.DOCUMENT,
            x=300,
            y=current_y,
            width=200,
            height=60,
        )
        flowchart.add_node(title_node)
        current_y += 100
        
        # Add heading nodes
        heading_nodes: list[FlowchartNode] = []
        for i, heading in enumerate(headings[:5]):  # Limit to 5 main headings
            heading_text = heading[:40] if len(heading) > 40 else heading
            node = FlowchartNode(
                id=self._gen_id(),
                label=heading_text,
                node_type=NodeType.SUBPROCESS,
                x=50 + (i * 180),
                y=current_y,
                width=160,
                height=50,
            )
            heading_nodes.append(node)
            flowchart.add_node(node)
            flowchart.add_connection(FlowchartConnection(
                id=self._gen_id(),
                source_id=title_node.id,
                target_id=node.id,
                connection_type=ConnectionType.DEPENDENCY,
            ))
        
        current_y += 100
        
        # Add requirement nodes grouped by category
        for i, req in enumerate(all_requirements[:15]):  # Limit to 15 requirements
            req_text = req[:50] if len(req) > 50 else req
            
            # Determine if it's a functional requirement
            is_functional = any(kw in req.lower() for kw in self._requirement_keywords)
            
            node = FlowchartNode(
                id=self._gen_id(),
                label=req_text,
                node_type=NodeType.REQUIREMENT if is_functional else NodeType.PROCESS,
                x=50 + ((i % 4) * 200),
                y=current_y + ((i // 4) * 80),
                width=180,
                height=60,
                description=req,
            )
            flowchart.add_node(node)
            
            # Connect to nearest heading or title
            if heading_nodes and (i < len(heading_nodes)):
                flowchart.add_connection(FlowchartConnection(
                    id=self._gen_id(),
                    source_id=heading_nodes[i % len(heading_nodes)].id,
                    target_id=node.id,
                    connection_type=ConnectionType.IMPLEMENTS,
                ))
        
        return flowchart
    
    def _gen_id(self) -> str:
        """Generate unique ID."""
        return str(uuid.uuid4())[:8]


# =============================================================================
# XML GENERATOR
# =============================================================================


class LucidXMLGenerator:
    """
    Generates Lucidchart-compatible XML from flowcharts.
    
    Produces XML that can be imported into Lucidchart or
    other diagram tools that support the format.
    """
    
    def __init__(self) -> None:
        """Initialize the generator."""
        self._namespace = "http://www.lucidchart.com/diagram"
    
    def generate(self, flowchart: Flowchart) -> str:
        """
        Generate Lucidchart XML from a flowchart.
        
        Args:
            flowchart: The flowchart to convert
            
        Returns:
            XML string
        """
        # Create root element
        root = ET.Element("lucidchart")
        root.set("version", "1.0")
        root.set("generated", datetime.now().isoformat())
        
        # Add metadata
        meta = ET.SubElement(root, "metadata")
        ET.SubElement(meta, "name").text = flowchart.name
        ET.SubElement(meta, "description").text = flowchart.description
        ET.SubElement(meta, "created").text = datetime.now().isoformat()
        
        # Add diagram element
        diagram = ET.SubElement(root, "diagram")
        diagram.set("id", str(uuid.uuid4()))
        diagram.set("name", flowchart.name)
        
        # Add page
        page = ET.SubElement(diagram, "page")
        page.set("id", "page1")
        page.set("name", "Page 1")
        
        # Add shapes (nodes)
        shapes = ET.SubElement(page, "shapes")
        for node in flowchart.nodes:
            shape = self._create_shape_element(node)
            shapes.append(shape)
        
        # Add lines (connections)
        lines = ET.SubElement(page, "lines")
        for conn in flowchart.connections:
            line = self._create_line_element(conn)
            lines.append(line)
        
        # Convert to pretty-printed XML string
        xml_str = ET.tostring(root, encoding="unicode")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        return "\n".join(lines)
    
    def _create_shape_element(self, node: FlowchartNode) -> ET.Element:
        """Create XML element for a shape."""
        shape = ET.Element("shape")
        shape.set("id", node.id)
        shape.set("type", LUCID_SHAPES.get(node.node_type, "Rectangle"))
        
        # Position
        bounds = ET.SubElement(shape, "bounds")
        bounds.set("x", str(node.x))
        bounds.set("y", str(node.y))
        bounds.set("width", str(node.width))
        bounds.set("height", str(node.height))
        
        # Style
        style = ET.SubElement(shape, "style")
        ET.SubElement(style, "fillColor").text = NODE_COLORS.get(
            node.node_type, "#ffffff"
        )
        ET.SubElement(style, "strokeColor").text = "#000000"
        ET.SubElement(style, "strokeWidth").text = "2"
        
        # Text
        text = ET.SubElement(shape, "text")
        ET.SubElement(text, "content").text = node.label
        ET.SubElement(text, "fontSize").text = "12"
        ET.SubElement(text, "fontFamily").text = "Arial"
        ET.SubElement(text, "fontColor").text = "#ffffff" if node.node_type in [
            NodeType.START, NodeType.END, NodeType.PROCESS,
            NodeType.DECISION, NodeType.DATABASE
        ] else "#000000"
        
        # Description as tooltip
        if node.description:
            ET.SubElement(shape, "tooltip").text = node.description
        
        # Metadata
        if node.metadata:
            meta = ET.SubElement(shape, "metadata")
            for key, value in node.metadata.items():
                item = ET.SubElement(meta, "item")
                item.set("key", key)
                item.text = str(value)
        
        return shape
    
    def _create_line_element(self, conn: FlowchartConnection) -> ET.Element:
        """Create XML element for a line."""
        line = ET.Element("line")
        line.set("id", conn.id)
        line.set("type", conn.connection_type.value)
        
        # Endpoints
        endpoints = ET.SubElement(line, "endpoints")
        source = ET.SubElement(endpoints, "source")
        source.set("shapeId", conn.source_id)
        target = ET.SubElement(endpoints, "target")
        target.set("shapeId", conn.target_id)
        
        # Style
        style = ET.SubElement(line, "style")
        ET.SubElement(style, "strokeColor").text = "#000000"
        ET.SubElement(style, "strokeWidth").text = "2"
        ET.SubElement(style, "arrowEnd").text = "true"
        
        if conn.connection_type in [ConnectionType.YES, ConnectionType.NO]:
            ET.SubElement(style, "strokeStyle").text = "solid"
        elif conn.connection_type == ConnectionType.DATA_FLOW:
            ET.SubElement(style, "strokeStyle").text = "dashed"
        
        # Label
        if conn.label:
            label = ET.SubElement(line, "label")
            ET.SubElement(label, "content").text = conn.label
            ET.SubElement(label, "position").text = "middle"
        
        return line
    
    def generate_mermaid(self, flowchart: Flowchart) -> str:
        """
        Generate Mermaid.js flowchart syntax as alternative.
        
        Args:
            flowchart: The flowchart to convert
            
        Returns:
            Mermaid flowchart string
        """
        lines = ["```mermaid", "flowchart TD"]
        
        # Add nodes
        for node in flowchart.nodes:
            shape = self._mermaid_shape(node)
            lines.append(f"    {node.id}{shape}")
        
        lines.append("")
        
        # Add connections
        for conn in flowchart.connections:
            label = f"|{conn.label}|" if conn.label else ""
            if conn.connection_type == ConnectionType.DATA_FLOW:
                lines.append(f"    {conn.source_id} -.-> {label}{conn.target_id}")
            else:
                lines.append(f"    {conn.source_id} --> {label}{conn.target_id}")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _mermaid_shape(self, node: FlowchartNode) -> str:
        """Get Mermaid shape syntax for a node."""
        label = node.label.replace('"', "'")
        
        if node.node_type == NodeType.START:
            return f"(({label}))"
        elif node.node_type == NodeType.END:
            return f"(({label}))"
        elif node.node_type == NodeType.DECISION:
            return f"{{{label}}}"
        elif node.node_type == NodeType.DATABASE:
            return f"[({label})]"
        elif node.node_type == NodeType.DOCUMENT:
            return f">{label}]"
        elif node.node_type == NodeType.SUBPROCESS:
            return f"[[{label}]]"
        else:
            return f"[{label}]"


# =============================================================================
# MAIN GENERATOR CLASS
# =============================================================================


class LucidFlowchartGenerator:
    """
    Main class for generating Lucid flowcharts from SQL and documentation.
    
    Usage:
        generator = LucidFlowchartGenerator()
        
        # From SQL file
        result = generator.generate_from_sql("procedure.sql")
        
        # From documentation
        result = generator.generate_from_docs("requirements.md")
        
        # Combined
        result = generator.generate_combined(
            sql_files=["proc1.sql", "proc2.sql"],
            doc_files=["requirements.md", "design.txt"],
        )
    """
    
    def __init__(self) -> None:
        """Initialize the generator."""
        self._sql_parser = OracleSQLParser()
        self._doc_parser = DocumentationParser()
        self._xml_generator = LucidXMLGenerator()
    
    def generate_from_sql(
        self,
        sql_path: str | Path,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate flowchart from Oracle SQL file.
        
        Args:
            sql_path: Path to SQL file
            output_format: "xml" or "mermaid"
            
        Returns:
            FlowchartGenerationResult
        """
        result = FlowchartGenerationResult()
        
        try:
            path = Path(sql_path)
            if not path.exists():
                result.errors.append(f"File not found: {sql_path}")
                return result
            
            content = path.read_text(encoding="utf-8")
            flowchart = self._sql_parser.parse(content)
            
            if output_format == "mermaid":
                result.xml_content = self._xml_generator.generate_mermaid(flowchart)
            else:
                result.xml_content = self._xml_generator.generate(flowchart)
            
            result.flowchart = flowchart
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def generate_from_sql_content(
        self,
        sql_content: str,
        name: str = "SQL_Procedure",
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate flowchart from SQL content string.
        
        Args:
            sql_content: SQL content
            name: Name for the flowchart
            output_format: "xml" or "mermaid"
            
        Returns:
            FlowchartGenerationResult
        """
        result = FlowchartGenerationResult()
        
        try:
            flowchart = self._sql_parser.parse(sql_content)
            flowchart.name = name
            
            if output_format == "mermaid":
                result.xml_content = self._xml_generator.generate_mermaid(flowchart)
            else:
                result.xml_content = self._xml_generator.generate(flowchart)
            
            result.flowchart = flowchart
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def generate_from_docs(
        self,
        doc_path: str | Path,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate requirements flowchart from documentation.
        
        Args:
            doc_path: Path to documentation file
            output_format: "xml" or "mermaid"
            
        Returns:
            FlowchartGenerationResult
        """
        result = FlowchartGenerationResult()
        
        try:
            path = Path(doc_path)
            if not path.exists():
                result.errors.append(f"File not found: {doc_path}")
                return result
            
            content = path.read_text(encoding="utf-8")
            flowchart = self._doc_parser.parse(content, path.stem)
            
            if output_format == "mermaid":
                result.xml_content = self._xml_generator.generate_mermaid(flowchart)
            else:
                result.xml_content = self._xml_generator.generate(flowchart)
            
            result.flowchart = flowchart
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def generate_from_doc_content(
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
        result = FlowchartGenerationResult()
        
        try:
            flowchart = self._doc_parser.parse(doc_content, name)
            
            if output_format == "mermaid":
                result.xml_content = self._xml_generator.generate_mermaid(flowchart)
            else:
                result.xml_content = self._xml_generator.generate(flowchart)
            
            result.flowchart = flowchart
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def generate_combined(
        self,
        sql_files: list[str | Path] | None = None,
        doc_files: list[str | Path] | None = None,
        output_format: str = "xml",
    ) -> FlowchartGenerationResult:
        """
        Generate combined flowchart from multiple SQL and doc files.
        
        Args:
            sql_files: List of SQL file paths
            doc_files: List of documentation file paths
            output_format: "xml" or "mermaid"
            
        Returns:
            FlowchartGenerationResult with combined flowchart
        """
        result = FlowchartGenerationResult()
        sql_files = sql_files or []
        doc_files = doc_files or []
        
        combined = Flowchart(
            name="Combined Requirements & Logic Flow",
            description="Combined diagram from SQL and documentation",
        )
        
        current_y = 50
        
        try:
            # Process SQL files
            for sql_path in sql_files:
                path = Path(sql_path)
                if not path.exists():
                    result.warnings.append(f"SQL file not found: {sql_path}")
                    continue
                
                content = path.read_text(encoding="utf-8")
                sql_flow = self._sql_parser.parse(content)
                
                # Offset nodes
                for node in sql_flow.nodes:
                    node.y += current_y
                    combined.add_node(node)
                
                for conn in sql_flow.connections:
                    combined.add_connection(conn)
                
                current_y += max(n.y for n in sql_flow.nodes) + 150
            
            # Process doc files
            for doc_path in doc_files:
                path = Path(doc_path)
                if not path.exists():
                    result.warnings.append(f"Doc file not found: {doc_path}")
                    continue
                
                content = path.read_text(encoding="utf-8")
                doc_flow = self._doc_parser.parse(content, path.stem)
                
                # Offset nodes
                for node in doc_flow.nodes:
                    node.y += current_y
                    combined.add_node(node)
                
                for conn in doc_flow.connections:
                    combined.add_connection(conn)
                
                current_y += max(n.y for n in doc_flow.nodes) + 150
            
            if output_format == "mermaid":
                result.xml_content = self._xml_generator.generate_mermaid(combined)
            else:
                result.xml_content = self._xml_generator.generate(combined)
            
            result.flowchart = combined
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def save_to_file(
        self,
        result: FlowchartGenerationResult,
        output_path: str | Path,
    ) -> bool:
        """
        Save generated flowchart to file.
        
        Args:
            result: Generation result
            output_path: Output file path
            
        Returns:
            True if saved successfully
        """
        if not result.success or not result.xml_content:
            return False
        
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(result.xml_content, encoding="utf-8")
            return True
        except Exception:
            return False


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def generate_flowchart_from_sql(
    sql_path: str,
    output_path: str | None = None,
    output_format: str = "xml",
) -> str:
    """
    Convenience function to generate flowchart from SQL file.
    
    Args:
        sql_path: Path to SQL file
        output_path: Optional output file path
        output_format: "xml" or "mermaid"
        
    Returns:
        Generated flowchart content
    """
    generator = LucidFlowchartGenerator()
    result = generator.generate_from_sql(sql_path, output_format)
    
    if output_path and result.success:
        generator.save_to_file(result, output_path)
    
    return result.xml_content if result.success else ""


def generate_flowchart_from_docs(
    doc_path: str,
    output_path: str | None = None,
    output_format: str = "xml",
) -> str:
    """
    Convenience function to generate flowchart from documentation.
    
    Args:
        doc_path: Path to documentation file
        output_path: Optional output file path
        output_format: "xml" or "mermaid"
        
    Returns:
        Generated flowchart content
    """
    generator = LucidFlowchartGenerator()
    result = generator.generate_from_docs(doc_path, output_format)
    
    if output_path and result.success:
        generator.save_to_file(result, output_path)
    
    return result.xml_content if result.success else ""
