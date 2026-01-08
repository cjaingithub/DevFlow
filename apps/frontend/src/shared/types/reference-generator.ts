/**
 * TypeScript types for Reference-Based Code Generation feature
 */

// =============================================================================
// TECH STACK TYPES
// =============================================================================

export type TechStackLanguage = 
  | 'python'
  | 'typescript'
  | 'javascript'
  | 'java'
  | 'go'
  | 'rust'
  | 'sql';

export type TechStackFramework = 
  | 'django'
  | 'fastapi'
  | 'flask'
  | 'express'
  | 'nestjs'
  | 'react'
  | 'vue'
  | 'spring'
  | 'none';

export type TechStackDatabase = 
  | 'postgresql'
  | 'mysql'
  | 'oracle'
  | 'mongodb'
  | 'dynamodb'
  | 'sqlite'
  | 'redis'
  | 'none';

export type TechStackInfra = 
  | 'terraform'
  | 'cloudformation'
  | 'cdk'
  | 'serverless'
  | 'kubernetes'
  | 'docker'
  | 'none';

export interface TechStack {
  languages: TechStackLanguage[];
  frameworks: TechStackFramework[];
  databases: TechStackDatabase[];
  infrastructure: TechStackInfra[];
}

// =============================================================================
// PATTERN TYPES
// =============================================================================

export type ReferencePatternType =
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
  | 'cloudformation_resource'
  | 'test_case';

export interface ReferencePattern {
  name: string;
  patternType: ReferencePatternType;
  sourceFile: string;
  codeSnippet: string;
  entityName: string;
  description: string;
  confidence: number;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// SQL TABLE TYPES
// =============================================================================

export interface SQLColumn {
  name: string;
  dataType: string;
  nullable: boolean;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  defaultValue?: string;
  references?: {
    table: string;
    column: string;
  };
}

export interface SQLTable {
  name: string;
  schema?: string;
  columns: SQLColumn[];
  primaryKey: string[];
  foreignKeys: {
    columns: string[];
    referencedTable: string;
    referencedColumns: string[];
  }[];
  indexes: {
    name: string;
    columns: string[];
    unique: boolean;
  }[];
}

// =============================================================================
// REFERENCE PROJECT
// =============================================================================

export interface ReferenceProject {
  id: string;
  name: string;
  description: string;
  path: string;
  createdAt: string;
  updatedAt: string;
  fileCount: number;
  patternCount: number;
  tableCount: number;
  techStack: TechStack;
  patterns: ReferencePattern[];
  sqlTables: SQLTable[];
  files: string[];
  status: 'ready' | 'loading' | 'error' | 'indexing';
  errorMessage?: string;
  usageCount: number;
  lastUsed?: string;
}

export interface ReferenceProjectSummary {
  id: string;
  name: string;
  description: string;
  patternCount: number;
  tableCount: number;
  techStack: TechStack;
  status: 'ready' | 'loading' | 'error' | 'indexing';
  usageCount: number;
}

// =============================================================================
// ENTITY MAPPING
// =============================================================================

export interface EntityMapping {
  reference: string;
  new: string;
  mappingType: 'table' | 'class' | 'function' | 'variable' | 'auto';
}

export interface InfraEntityMapping extends EntityMapping {
  resourcePrefix?: string;
  environment?: string;
  region?: string;
}

export interface CacheMapping {
  keyPrefix: string;
  ttl: number;
  redisHost?: string;
  redisPort?: number;
}

// =============================================================================
// GENERATION CONFIG
// =============================================================================

export interface GenerationConfig {
  entityMappings: EntityMapping[];
  infraMappings?: InfraEntityMapping[];
  cacheMapping?: CacheMapping;
  outputDir: string;
  includeTests: boolean;
  includeDocumentation: boolean;
  includeMigrations: boolean;
  targetDatabase?: TechStackDatabase;
  targetLanguage?: TechStackLanguage;
}

// =============================================================================
// GENERATED OUTPUT
// =============================================================================

export interface GeneratedFile {
  path: string;
  content: string;
  fileType: string;
  sourcePattern?: string;
  confidence: number;
  category: 'schema' | 'service' | 'repository' | 'controller' | 'model' | 'test' | 'infrastructure' | 'migration' | 'other';
}

export interface GenerationResult {
  success: boolean;
  generatedFiles: GeneratedFile[];
  errors: string[];
  warnings: string[];
  transformations: {
    original: string;
    transformed: string;
    type: string;
  }[];
  stats: {
    totalFiles: number;
    byCategory: Record<string, number>;
    byType: Record<string, number>;
  };
}

// =============================================================================
// LOAD REFERENCE RESULT
// =============================================================================

export interface LoadReferenceResult {
  success: boolean;
  project: ReferenceProject | null;
  errors: string[];
  warnings: string[];
}

// =============================================================================
// UI STATE
// =============================================================================

export type ReferenceGeneratorStep = 
  | 'select'
  | 'requirements'
  | 'mapping'
  | 'generate'
  | 'result';

export interface ReferenceGeneratorState {
  step: ReferenceGeneratorStep;
  selectedReference: ReferenceProject | null;
  requirementsFile: File | null;
  requirementsContent: string;
  config: GenerationConfig;
  generationResult: GenerationResult | null;
  isLoading: boolean;
  error: string | null;
  progress: {
    current: number;
    total: number;
    phase: string;
  };
}

// =============================================================================
// WIZARD STEP
// =============================================================================

export interface ReferenceWizardStep {
  id: ReferenceGeneratorStep;
  titleKey: string;
  descriptionKey: string;
  icon: string;
}
