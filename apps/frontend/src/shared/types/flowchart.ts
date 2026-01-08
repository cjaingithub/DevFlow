/**
 * TypeScript types for Lucid Flowchart XML input feature
 */

// =============================================================================
// FLOWCHART NODE TYPES
// =============================================================================

export type FlowchartNodeType = 
  | 'start'
  | 'end'
  | 'process'
  | 'decision'
  | 'data'
  | 'database'
  | 'document'
  | 'subprocess'
  | 'connector'
  | 'requirement'
  | 'comment';

export interface FlowchartNode {
  id: string;
  label: string;
  nodeType: FlowchartNodeType;
  x: number;
  y: number;
  width: number;
  height: number;
  description?: string;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// FLOWCHART CONNECTION TYPES
// =============================================================================

export type ConnectionType = 
  | 'flow'
  | 'yes'
  | 'no'
  | 'data_flow'
  | 'reference';

export interface FlowchartConnection {
  id: string;
  sourceId: string;
  targetId: string;
  connectionType: ConnectionType;
  label?: string;
}

// =============================================================================
// FLOWCHART STRUCTURE
// =============================================================================

export interface Flowchart {
  name: string;
  description?: string;
  nodes: FlowchartNode[];
  connections: FlowchartConnection[];
  metadata?: Record<string, unknown>;
}

// =============================================================================
// PARSED ELEMENTS FROM FLOWCHART
// =============================================================================

export interface ParsedRequirement {
  id: string;
  title: string;
  description: string;
  requirementType: 'functional' | 'non-functional';
  priority: 'high' | 'medium' | 'low';
  relatedNodes: string[];
  acceptanceCriteria: string[];
}

export interface ParsedProcess {
  id: string;
  name: string;
  processType: 'action' | 'decision' | 'data_operation' | 'subprocess';
  description: string;
  inputs: string[];
  outputs: string[];
  conditions: string[];
}

export interface ParsedDataFlow {
  id: string;
  tableName: string;
  operation: 'read' | 'write' | 'update' | 'delete';
  columns: string[];
  conditions: string;
}

// =============================================================================
// CODE PATTERN (Generated from flowchart)
// =============================================================================

export type PatternType =
  | 'service_class'
  | 'repository'
  | 'controller'
  | 'database_model'
  | 'api_endpoint'
  | 'validation'
  | 'transformation'
  | 'authentication'
  | 'error_handling'
  | 'utility'
  | 'lambda_function'
  | 'glue_job'
  | 'step_function'
  | 'caching'
  | 'context_manager'
  | 'terraform_resource'
  | 'infrastructure';

export interface CodePattern {
  name: string;
  patternType: PatternType;
  sourceFile: string;
  codeSnippet: string;
  entityName: string;
  description: string;
  confidence: number;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// PARSE RESULT
// =============================================================================

export interface FlowchartParseResult {
  success: boolean;
  flowchart: Flowchart | null;
  requirements: ParsedRequirement[];
  processes: ParsedProcess[];
  dataFlows: ParsedDataFlow[];
  generatedPatterns: CodePattern[];
  errors: string[];
  warnings: string[];
}

// =============================================================================
// REFERENCE PROJECT (loaded from flowchart)
// =============================================================================

export interface FlowchartReference {
  id: string;
  name: string;
  description: string;
  path: string;
  createdAt: string;
  updatedAt: string;
  nodeCount: number;
  connectionCount: number;
  requirementCount: number;
  processCount: number;
  patternCount: number;
  techStack: string[];
  status: 'ready' | 'loading' | 'error';
  errorMessage?: string;
}

// =============================================================================
// GENERATION CONFIG
// =============================================================================

export interface EntityMapping {
  reference: string;
  new: string;
}

export interface FlowchartGenerationConfig {
  entityMappings: EntityMapping[];
  outputDir: string;
  includeTests: boolean;
  includeDocumentation: boolean;
  targetLanguage: 'python' | 'typescript' | 'java';
}

// =============================================================================
// GENERATED FILE
// =============================================================================

export interface GeneratedFile {
  path: string;
  content: string;
  fileType: string;
  sourcePattern?: string;
  confidence: number;
}

export interface GenerationResult {
  success: boolean;
  generatedFiles: GeneratedFile[];
  errors: string[];
  warnings: string[];
  stats: {
    totalFiles: number;
    byType: Record<string, number>;
  };
}

// =============================================================================
// UI STATE
// =============================================================================

export interface FlowchartImporterState {
  step: 'upload' | 'preview' | 'configure' | 'generate' | 'result';
  uploadedFile: File | null;
  parseResult: FlowchartParseResult | null;
  config: FlowchartGenerationConfig;
  generationResult: GenerationResult | null;
  isLoading: boolean;
  error: string | null;
}

// =============================================================================
// WIZARD STEP DEFINITIONS
// =============================================================================

export interface WizardStep {
  id: string;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}
