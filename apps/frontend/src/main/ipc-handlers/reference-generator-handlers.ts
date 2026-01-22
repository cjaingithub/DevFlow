/**
 * IPC Handlers for Reference Generator Operations
 * 
 * These handlers bridge the frontend UI with the Python backend's
 * Reference Generator service for pattern-based code generation.
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
 * Execute a Python reference generator command
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
 * Register all reference generator IPC handlers
 */
export function registerReferenceGeneratorHandlers(
  envManager: PythonEnvManager,
  getMainWindow: () => BrowserWindow | null
): void {
  pythonEnvManager = envManager;

  // Load a reference project
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_LOAD,
    async (_event, projectId: string, referencePath: string, name: string, description?: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      const result = await executePythonCommand(project.path, 'load', {
        reference: referencePath,
        name,
        description: description || ''
      });

      // Send progress event
      const mainWindow = getMainWindow();
      if (mainWindow && result.success) {
        mainWindow.webContents.send(IPC_CHANNELS.REFERENCE_LOAD_PROGRESS, {
          current: 100,
          total: 100,
          phase: 'complete'
        });
      }

      return result;
    }
  );

  // List all reference projects
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_LIST,
    async (_event, projectId: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return [];
      }

      const result = await executePythonCommand(project.path, 'list');
      return result.success ? result.data : [];
    }
  );

  // Get a specific reference project
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_GET,
    async (_event, projectId: string, referenceName: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return null;
      }

      const result = await executePythonCommand(project.path, 'info', {
        name: referenceName
      });
      return result.success ? result.data : null;
    }
  );

  // Delete a reference project
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_DELETE,
    async (_event, projectId: string, referenceName: string) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      return executePythonCommand(project.path, 'delete', {
        name: referenceName
      });
    }
  );

  // Generate code from a reference
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_GENERATE,
    async (
      _event,
      projectId: string,
      referenceName: string,
      requirementsContent: string,
      config: {
        entityMappings: Array<{ reference: string; new: string }>;
        outputDir: string;
      }
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, error: 'Project not found' };
      }

      // Write requirements to a temp file
      const tempReqPath = path.join(project.path, '.devflow', 'temp-requirements.md');
      await fs.mkdir(path.dirname(tempReqPath), { recursive: true });
      await fs.writeFile(tempReqPath, requirementsContent, 'utf-8');

      const mainWindow = getMainWindow();
      
      // Send progress events
      if (mainWindow) {
        mainWindow.webContents.send(IPC_CHANNELS.REFERENCE_GENERATION_PROGRESS, {
          current: 0,
          total: 100,
          phase: 'starting'
        });
      }

      try {
        const result = await executePythonCommand(project.path, 'generate', {
          name: referenceName,
          requirements: tempReqPath,
          output: config.outputDir,
          'entity-mapping': JSON.stringify(config.entityMappings[0] || {})
        });

        // Clean up temp file
        await fs.unlink(tempReqPath).catch(() => {});

        if (mainWindow) {
          if (result.success) {
            mainWindow.webContents.send(IPC_CHANNELS.REFERENCE_GENERATION_COMPLETE, result.data);
          } else {
            mainWindow.webContents.send(IPC_CHANNELS.REFERENCE_GENERATION_ERROR, {
              message: result.error || 'Generation failed'
            });
          }
        }

        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        if (mainWindow) {
          mainWindow.webContents.send(IPC_CHANNELS.REFERENCE_GENERATION_ERROR, {
            message: errorMessage
          });
        }
        return { success: false, error: errorMessage };
      }
    }
  );

  // Select directory dialog
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_SELECT_DIR,
    async (_event, projectId: string) => {
      const project = projectStore.getProject(projectId);
      
      const result = await dialog.showOpenDialog({
        properties: ['openDirectory'],
        title: 'Select Reference Directory',
        defaultPath: project?.path
      });

      return {
        path: result.canceled ? null : result.filePaths[0],
        canceled: result.canceled
      };
    }
  );

  // Select requirements file dialog
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_SELECT_FILE,
    async (_event, projectId: string) => {
      const project = projectStore.getProject(projectId);
      
      const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        title: 'Select Requirements File',
        defaultPath: project?.path,
        filters: [
          { name: 'Markdown', extensions: ['md', 'markdown'] },
          { name: 'Text', extensions: ['txt'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (result.canceled || !result.filePaths[0]) {
        return { path: null, content: null, canceled: true };
      }

      const filePath = result.filePaths[0];
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        return { path: filePath, content, canceled: false };
      } catch {
        return { path: filePath, content: null, canceled: false };
      }
    }
  );

  // Save generated files
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_SAVE_FILES,
    async (
      _event,
      projectId: string,
      files: Array<{ path: string; content: string }>,
      outputDir: string
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, savedCount: 0, error: 'Project not found' };
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

  // Apply generated files to project
  ipcMain.handle(
    IPC_CHANNELS.REFERENCE_APPLY_TO_PROJECT,
    async (
      _event,
      projectId: string,
      files: Array<{ path: string; content: string }>
    ) => {
      const project = projectStore.getProject(projectId);
      if (!project) {
        return { success: false, appliedCount: 0, error: 'Project not found' };
      }

      let appliedCount = 0;
      const errors: string[] = [];

      for (const file of files) {
        const fullPath = path.join(project.path, file.path);
        try {
          await fs.mkdir(path.dirname(fullPath), { recursive: true });
          await fs.writeFile(fullPath, file.content, 'utf-8');
          appliedCount++;
        } catch (error) {
          errors.push(`Failed to apply ${file.path}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }

      return {
        success: errors.length === 0,
        appliedCount,
        error: errors.length > 0 ? errors.join('\n') : undefined
      };
    }
  );

  console.log('[IPC] Reference Generator handlers registered');
}
