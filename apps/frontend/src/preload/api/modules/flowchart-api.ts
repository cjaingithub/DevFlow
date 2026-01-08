import { IPC_CHANNELS } from '../../../shared/constants';
import type {
  FlowchartParseResult,
  FlowchartReference,
  FlowchartGenerationConfig,
  GenerationResult,
  IPCResult
} from '../../../shared/types';
import { invokeIpc, IpcListenerCleanup, createIpcListener } from './ipc-utils';

/**
 * Flowchart API operations for Lucid XML import and code generation
 */
export interface FlowchartAPI {
  // Parsing operations
  parseFlowchartXml: (projectId: string, xmlPath: string) => Promise<IPCResult<FlowchartParseResult>>;
  parseFlowchartContent: (projectId: string, xmlContent: string, name: string) => Promise<IPCResult<FlowchartParseResult>>;
  
  // Reference management
  loadFlowchartAsReference: (
    projectId: string,
    xmlPath: string,
    name: string,
    description?: string
  ) => Promise<IPCResult<FlowchartReference>>;
  listFlowchartReferences: (projectId: string) => Promise<IPCResult<FlowchartReference[]>>;
  getFlowchartReference: (projectId: string, referenceId: string) => Promise<IPCResult<FlowchartReference | null>>;
  deleteFlowchartReference: (projectId: string, referenceId: string) => Promise<IPCResult>;
  
  // Code generation
  generateFromFlowchart: (
    projectId: string,
    xmlPath: string,
    config: FlowchartGenerationConfig
  ) => Promise<IPCResult<GenerationResult>>;
  generateFromReference: (
    projectId: string,
    referenceId: string,
    config: FlowchartGenerationConfig
  ) => Promise<IPCResult<GenerationResult>>;
  
  // File operations
  selectFlowchartFile: () => Promise<IPCResult<string | null>>;
  saveGeneratedFiles: (projectId: string, outputDir: string, files: { path: string; content: string }[]) => Promise<IPCResult>;
  
  // Event listeners
  onFlowchartParseProgress: (callback: (projectId: string, progress: number, message: string) => void) => IpcListenerCleanup;
  onFlowchartGenerationProgress: (callback: (projectId: string, progress: number, currentFile: string) => void) => IpcListenerCleanup;
}

/**
 * Creates the Flowchart API implementation
 */
export const createFlowchartAPI = (): FlowchartAPI => ({
  // Parsing operations
  parseFlowchartXml: (projectId: string, xmlPath: string): Promise<IPCResult<FlowchartParseResult>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_PARSE_XML, projectId, xmlPath),

  parseFlowchartContent: (projectId: string, xmlContent: string, name: string): Promise<IPCResult<FlowchartParseResult>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_PARSE_CONTENT, projectId, xmlContent, name),

  // Reference management
  loadFlowchartAsReference: (
    projectId: string,
    xmlPath: string,
    name: string,
    description?: string
  ): Promise<IPCResult<FlowchartReference>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_LOAD_REFERENCE, projectId, xmlPath, name, description),

  listFlowchartReferences: (projectId: string): Promise<IPCResult<FlowchartReference[]>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_LIST_REFERENCES, projectId),

  getFlowchartReference: (projectId: string, referenceId: string): Promise<IPCResult<FlowchartReference | null>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_GET_REFERENCE, projectId, referenceId),

  deleteFlowchartReference: (projectId: string, referenceId: string): Promise<IPCResult> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_DELETE_REFERENCE, projectId, referenceId),

  // Code generation
  generateFromFlowchart: (
    projectId: string,
    xmlPath: string,
    config: FlowchartGenerationConfig
  ): Promise<IPCResult<GenerationResult>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_GENERATE, projectId, xmlPath, config),

  generateFromReference: (
    projectId: string,
    referenceId: string,
    config: FlowchartGenerationConfig
  ): Promise<IPCResult<GenerationResult>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_GENERATE_FROM_REF, projectId, referenceId, config),

  // File operations
  selectFlowchartFile: (): Promise<IPCResult<string | null>> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_SELECT_FILE),

  saveGeneratedFiles: (
    projectId: string,
    outputDir: string,
    files: { path: string; content: string }[]
  ): Promise<IPCResult> =>
    invokeIpc(IPC_CHANNELS.FLOWCHART_SAVE_FILES, projectId, outputDir, files),

  // Event listeners
  onFlowchartParseProgress: (
    callback: (projectId: string, progress: number, message: string) => void
  ): IpcListenerCleanup =>
    createIpcListener(IPC_CHANNELS.FLOWCHART_PARSE_PROGRESS, callback),

  onFlowchartGenerationProgress: (
    callback: (projectId: string, progress: number, currentFile: string) => void
  ): IpcListenerCleanup =>
    createIpcListener(IPC_CHANNELS.FLOWCHART_GENERATION_PROGRESS, callback)
});
