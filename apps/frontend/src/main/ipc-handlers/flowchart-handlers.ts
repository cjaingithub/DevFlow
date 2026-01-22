/**
 * IPC Handlers for Flowchart Import Operations
 * 
 * These handlers bridge the frontend UI with the Python backend's
 * Lucid Flowchart XML parser and code generation service.
 */

import { ipcMain, dialog, BrowserWindow } from 'electron';
import { IPC_CHANNELS } from '../../shared/constants';
import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs/promises';
import { projectStore } from '../project-store';
import { PythonEnvManager } from '../python-env-manager';

// Store reference for the Python environment manager
let pythonEnvManager: PythonEnvManager | null = null;

/**
 * Execute a Python flowchart command
 */
async function executePythonCommand(
  projectPath: string,
  action: string,
  args: Record<string, unknown> = {}
): Promise<{ success: boolean; data?: unknown; error?: string }> {
  return new Promise((resolve) => {
    // Get Python executable path
    const pythonPath = pythonEnvManager?.getPythonPath() || 'python';
    const backendPath = path.join(__dirname, '../../..', 'backend');
    
    // Build command arguments
    const cmdArgs = [
      '-m', 'services.reference_generator.service',
      '--action', action,
      '--project-dir', projectPath,
      '--json'
    ];

    // Add additional arguments
    for (const [key, value] of Object.entries(args)) {
      if (value !== undefined && value !== null) {
        cmdArgs.push(`--${key}`, String(value));
      }
    }

    const process = spawn(pythonPath, cmdArgs, {
      cwd: backendPath,
      env: { ...process.env, PYTHONPATH: backendPath }
    });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve({ success: true, data: result });
        } catch {
          resolve({ success: true, data: stdout });
        }
      } else {
        resolve({ 
          success: false, 
          error: stderr || `Process exited with code ${code}` 
        });
      }
    });

    process.on('error', (err) => {
      resolve({ success: false, error: err.message });
    });
  });
}

/**
 * Register all flowchart IPC handlers
 */
export function registerFlowchartHandlers(
  envManager: PythonEnvManager,
  getMainWindow: () => BrowserWindow | null
): void {
  pythonEnvManager = envManager;

  // Parse flowchart XML from file path
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_PARSE_XML,
    async (_event, projectId: string, xmlPath: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      const mainWindow = getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_PARSE_PROGRESS, 
          projectId, 0, 'Starting XML parsing...');
      }

      const result = await executePythonCommand(project.path, 'parse-flowchart', {
        'xml-file': xmlPath
      });

      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_PARSE_PROGRESS,
          projectId, 100, 'Parsing complete');
      }

      return result;
    }
  );

  // Parse flowchart XML from content string
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_PARSE_CONTENT,
    async (_event, projectId: string, xmlContent: string, name: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      // Write content to temp file
      const tempPath = path.join(project.path, '.devflow', `temp-flowchart-${Date.now()}.xml`);
      await fs.mkdir(path.dirname(tempPath), { recursive: true });
      await fs.writeFile(tempPath, xmlContent, 'utf-8');

      try {
        const result = await executePythonCommand(project.path, 'parse-flowchart', {
          'xml-file': tempPath
        });

        // Clean up temp file
        await fs.unlink(tempPath).catch(() => {});

        return result;
      } catch (error) {
        await fs.unlink(tempPath).catch(() => {});
        return { 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        };
      }
    }
  );

  // Load flowchart as reference
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_LOAD_REFERENCE,
    async (_event, projectId: string, xmlPath: string, name: string, description?: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      return executePythonCommand(project.path, 'load-flowchart', {
        'xml-file': xmlPath,
        name,
        description: description || ''
      });
    }
  );

  // List flowchart references
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_LIST_REFERENCES,
    async (_event, projectId: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, data: [] };
      }

      const result = await executePythonCommand(project.path, 'list');
      
      // Filter to only include flowchart-based references
      if (result.success && Array.isArray(result.data)) {
        const flowchartRefs = (result.data as Array<{ metadata?: { is_flowchart_xml?: boolean } }>)
          .filter(ref => ref.metadata?.is_flowchart_xml);
        return { success: true, data: flowchartRefs };
      }

      return result;
    }
  );

  // Get flowchart reference
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_GET_REFERENCE,
    async (_event, projectId: string, referenceId: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, data: null };
      }

      return executePythonCommand(project.path, 'info', {
        name: referenceId
      });
    }
  );

  // Delete flowchart reference
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_DELETE_REFERENCE,
    async (_event, projectId: string, referenceId: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      return executePythonCommand(project.path, 'delete', {
        name: referenceId
      });
    }
  );

  // Generate code from flowchart XML
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_GENERATE,
    async (
      _event,
      projectId: string,
      xmlPath: string,
      config: {
        entityMappings: Array<{ reference: string; new: string }>;
        outputDir: string;
      }
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      const mainWindow = getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_GENERATION_PROGRESS,
          projectId, 0, 'Starting code generation...');
      }

      const result = await executePythonCommand(project.path, 'generate-from-flowchart', {
        'xml-file': xmlPath,
        output: config.outputDir,
        'entity-mapping': JSON.stringify(config.entityMappings[0] || {})
      });

      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_GENERATION_PROGRESS,
          projectId, 100, 'Generation complete');
      }

      return result;
    }
  );

  // Generate code from flowchart reference
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_GENERATE_FROM_REF,
    async (
      _event,
      projectId: string,
      referenceId: string,
      config: {
        entityMappings: Array<{ reference: string; new: string }>;
        outputDir: string;
        requirementsContent?: string;
      }
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      const mainWindow = getMainWindow();
      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_GENERATION_PROGRESS,
          projectId, 0, 'Starting code generation...');
      }

      // Write requirements to temp file if provided
      let tempReqPath: string | undefined;
      if (config.requirementsContent) {
        tempReqPath = path.join(project.path, '.devflow', 'temp-requirements.md');
        await fs.mkdir(path.dirname(tempReqPath), { recursive: true });
        await fs.writeFile(tempReqPath, config.requirementsContent, 'utf-8');
      }

      try {
        const result = await executePythonCommand(project.path, 'generate', {
          name: referenceId,
          output: config.outputDir,
          'entity-mapping': JSON.stringify(config.entityMappings[0] || {}),
          requirements: tempReqPath
        });

        // Clean up temp file
        if (tempReqPath) {
          await fs.unlink(tempReqPath).catch(() => {});
        }

        if (mainWindow) {
          mainWindow.webContents.send(IPC_CHANNELS.FLOWCHART_GENERATION_PROGRESS,
            projectId, 100, 'Generation complete');
        }

        return result;
      } catch (error) {
        if (tempReqPath) {
          await fs.unlink(tempReqPath).catch(() => {});
        }
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    }
  );

  // Select flowchart XML file
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_SELECT_FILE,
    async () => {
      const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        title: 'Select Flowchart XML File',
        filters: [
          { name: 'XML Files', extensions: ['xml'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      return {
        success: true,
        data: result.canceled ? null : result.filePaths[0]
      };
    }
  );

  // Save generated files
  ipcMain.handle(
    IPC_CHANNELS.FLOWCHART_SAVE_FILES,
    async (
      _event,
      projectId: string,
      outputDir: string,
      files: Array<{ path: string; content: string }>
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      let savedCount = 0;
      const errors: string[] = [];

      for (const file of files) {
        const fullPath = path.join(outputDir, file.path);
        try {
          await fs.mkdir(path.dirname(fullPath), { recursive: true });
          await fs.writeFile(fullPath, file.content, 'utf-8');
          savedCount++;
        } catch (error) {
          errors.push(`Failed to save ${file.path}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }

      return {
        success: errors.length === 0,
        savedCount,
        error: errors.length > 0 ? errors.join('\n') : undefined
      };
    }
  );

  console.log('[IPC] Flowchart handlers registered');
}
