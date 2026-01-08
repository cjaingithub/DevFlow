/**
 * Preload API module for Reference Generator operations
 * Exposes backend reference-based code generation functionality to the renderer process
 */

import { ipcRenderer } from 'electron';
import { IPC_CHANNELS } from '../../../shared/constants';
import type {
  ReferenceProject,
  ReferenceProjectSummary,
  GenerationConfig,
  GenerationResult,
  LoadReferenceResult
} from '../../../shared/types';

export interface ReferenceGeneratorAPI {
  /**
   * Load a reference project from a directory path
   */
  loadReference: (
    projectId: string,
    referencePath: string,
    name: string,
    description?: string
  ) => Promise<LoadReferenceResult>;

  /**
   * List all loaded reference projects
   */
  listReferences: (projectId: string) => Promise<ReferenceProjectSummary[]>;

  /**
   * Get full details of a specific reference project
   */
  getReference: (projectId: string, referenceId: string) => Promise<ReferenceProject | null>;

  /**
   * Delete a reference project
   */
  deleteReference: (projectId: string, referenceId: string) => Promise<{ success: boolean; error?: string }>;

  /**
   * Generate code from a reference project
   */
  generateFromReference: (
    projectId: string,
    referenceId: string,
    requirementsContent: string,
    config: GenerationConfig
  ) => Promise<GenerationResult>;

  /**
   * Open directory selection dialog
   */
  selectDirectory: (projectId: string) => Promise<{ path: string | null; canceled: boolean }>;

  /**
   * Open file selection dialog for requirements file
   */
  selectRequirementsFile: (projectId: string) => Promise<{ path: string | null; content: string | null; canceled: boolean }>;

  /**
   * Save generated files to disk
   */
  saveGeneratedFiles: (
    projectId: string,
    files: { path: string; content: string }[],
    outputDir: string
  ) => Promise<{ success: boolean; savedCount: number; error?: string }>;

  /**
   * Apply generated files directly to the project
   */
  applyToProject: (
    projectId: string,
    files: { path: string; content: string }[]
  ) => Promise<{ success: boolean; appliedCount: number; error?: string }>;

  /**
   * Subscribe to load progress events
   */
  onLoadProgress: (callback: (progress: { current: number; total: number; phase: string }) => void) => () => void;

  /**
   * Subscribe to generation progress events
   */
  onGenerationProgress: (callback: (progress: { current: number; total: number; phase: string; currentFile?: string }) => void) => () => void;

  /**
   * Subscribe to generation complete events
   */
  onGenerationComplete: (callback: (result: GenerationResult) => void) => () => void;

  /**
   * Subscribe to generation error events
   */
  onGenerationError: (callback: (error: { message: string; details?: string }) => void) => () => void;
}

export function createReferenceGeneratorAPI(): ReferenceGeneratorAPI {
  return {
    loadReference: async (projectId, referencePath, name, description) => {
      return ipcRenderer.invoke(
        IPC_CHANNELS.REFERENCE_LOAD,
        projectId,
        referencePath,
        name,
        description
      );
    },

    listReferences: async (projectId) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_LIST, projectId);
    },

    getReference: async (projectId, referenceId) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_GET, projectId, referenceId);
    },

    deleteReference: async (projectId, referenceId) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_DELETE, projectId, referenceId);
    },

    generateFromReference: async (projectId, referenceId, requirementsContent, config) => {
      return ipcRenderer.invoke(
        IPC_CHANNELS.REFERENCE_GENERATE,
        projectId,
        referenceId,
        requirementsContent,
        config
      );
    },

    selectDirectory: async (projectId) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_SELECT_DIR, projectId);
    },

    selectRequirementsFile: async (projectId) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_SELECT_FILE, projectId);
    },

    saveGeneratedFiles: async (projectId, files, outputDir) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_SAVE_FILES, projectId, files, outputDir);
    },

    applyToProject: async (projectId, files) => {
      return ipcRenderer.invoke(IPC_CHANNELS.REFERENCE_APPLY_TO_PROJECT, projectId, files);
    },

    onLoadProgress: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, progress: { current: number; total: number; phase: string }) => {
        callback(progress);
      };
      ipcRenderer.on(IPC_CHANNELS.REFERENCE_LOAD_PROGRESS, handler);
      return () => {
        ipcRenderer.removeListener(IPC_CHANNELS.REFERENCE_LOAD_PROGRESS, handler);
      };
    },

    onGenerationProgress: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, progress: { current: number; total: number; phase: string; currentFile?: string }) => {
        callback(progress);
      };
      ipcRenderer.on(IPC_CHANNELS.REFERENCE_GENERATION_PROGRESS, handler);
      return () => {
        ipcRenderer.removeListener(IPC_CHANNELS.REFERENCE_GENERATION_PROGRESS, handler);
      };
    },

    onGenerationComplete: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, result: GenerationResult) => {
        callback(result);
      };
      ipcRenderer.on(IPC_CHANNELS.REFERENCE_GENERATION_COMPLETE, handler);
      return () => {
        ipcRenderer.removeListener(IPC_CHANNELS.REFERENCE_GENERATION_COMPLETE, handler);
      };
    },

    onGenerationError: (callback) => {
      const handler = (_event: Electron.IpcRendererEvent, error: { message: string; details?: string }) => {
        callback(error);
      };
      ipcRenderer.on(IPC_CHANNELS.REFERENCE_GENERATION_ERROR, handler);
      return () => {
        ipcRenderer.removeListener(IPC_CHANNELS.REFERENCE_GENERATION_ERROR, handler);
      };
    }
  };
}
