/**
 * FlowchartUploadStep - File upload/selection step
 */

import { useState, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Upload,
  FileUp,
  FolderOpen,
  FileCode,
  CheckCircle2,
  XCircle,
  Loader2,
  Workflow
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { cn } from '../../lib/utils';
import type { FlowchartParseResult } from '../../../shared/types';

interface FlowchartUploadStepProps {
  projectId: string;
  onFileSelected: (file: File, parseResult: FlowchartParseResult) => void;
  isLoading: boolean;
}

export function FlowchartUploadStep({
  projectId,
  onFileSelected,
  isLoading
}: FlowchartUploadStepProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [isDragging, setIsDragging] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const parseFile = useCallback(async (file: File) => {
    setIsParsing(true);
    setParseError(null);
    setSelectedFile(file);

    try {
      const content = await file.text();
      
      // Call the IPC to parse the XML content
      const result = await window.electronAPI.parseFlowchartContent(
        projectId,
        content,
        file.name.replace(/\.xml$/i, '')
      );

      if (result.success && result.data) {
        onFileSelected(file, result.data);
      } else {
        setParseError(result.error || 'Failed to parse flowchart');
      }
    } catch (error) {
      setParseError(error instanceof Error ? error.message : 'Failed to read file');
    } finally {
      setIsParsing(false);
    }
  }, [projectId, onFileSelected]);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const xmlFile = files.find(f => f.name.toLowerCase().endsWith('.xml'));

    if (xmlFile) {
      await parseFile(xmlFile);
    } else {
      setParseError('Please drop an XML file');
    }
  }, [parseFile]);

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await parseFile(file);
    }
  }, [parseFile]);

  const handleBrowse = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleSelectFromProject = useCallback(async () => {
    try {
      const result = await window.electronAPI.selectFlowchartFile();
      if (result.success && result.data) {
        // Read the file content
        const fileResult = await window.electronAPI.parseFlowchartXml(projectId, result.data);
        if (fileResult.success && fileResult.data) {
          // Create a fake File object for consistency
          const fakeFile = new File([''], result.data.split('/').pop() || 'flowchart.xml');
          onFileSelected(fakeFile, fileResult.data);
        } else {
          setParseError(fileResult.error || 'Failed to parse flowchart');
        }
      }
    } catch (error) {
      setParseError(error instanceof Error ? error.message : 'Failed to select file');
    }
  }, [projectId, onFileSelected]);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Main Upload Card */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-violet-500/10 via-fuchsia-500/10 to-purple-500/10 border-b border-violet-500/20">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-violet-500/20">
              <Workflow className="h-5 w-5 text-violet-400" />
            </div>
            <div>
              <CardTitle>Import Lucid Flowchart</CardTitle>
              <CardDescription>
                Upload a Lucidchart XML export to extract requirements and generate code
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {/* Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              'relative border-2 border-dashed rounded-xl p-12 transition-all duration-200 text-center',
              isDragging && 'border-violet-500 bg-violet-500/10 scale-[1.02]',
              !isDragging && 'border-muted-foreground/25 hover:border-muted-foreground/50 hover:bg-muted/30',
              parseError && 'border-destructive/50 bg-destructive/5'
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".xml"
              onChange={handleFileChange}
              className="hidden"
            />

            {isParsing ? (
              <div className="flex flex-col items-center gap-4">
                <div className="p-4 rounded-full bg-violet-500/20 animate-pulse">
                  <Loader2 className="h-8 w-8 text-violet-400 animate-spin" />
                </div>
                <div>
                  <h3 className="text-lg font-medium">Parsing Flowchart...</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Extracting nodes, connections, and patterns
                  </p>
                </div>
              </div>
            ) : selectedFile && !parseError ? (
              <div className="flex flex-col items-center gap-4">
                <div className="p-4 rounded-full bg-green-500/20">
                  <CheckCircle2 className="h-8 w-8 text-green-400" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-green-400">File Ready</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {selectedFile.name}
                  </p>
                </div>
              </div>
            ) : parseError ? (
              <div className="flex flex-col items-center gap-4">
                <div className="p-4 rounded-full bg-destructive/20">
                  <XCircle className="h-8 w-8 text-destructive" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-destructive">Parse Error</h3>
                  <p className="text-sm text-destructive/80 mt-1">
                    {parseError}
                  </p>
                </div>
                <Button variant="outline" onClick={handleBrowse}>
                  Try Another File
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-4">
                <div className="p-4 rounded-full bg-muted">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="text-lg font-medium">Drop your XML file here</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    or click to browse
                  </p>
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <Button onClick={handleBrowse} className="gap-2">
                    <FileUp className="h-4 w-4" />
                    Browse Files
                  </Button>
                  <Button variant="outline" onClick={handleSelectFromProject} className="gap-2">
                    <FolderOpen className="h-4 w-4" />
                    From Project
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Supported Formats Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Supported Formats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              <FileCode className="h-5 w-5 text-violet-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-sm">Lucidchart XML</h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Native Lucidchart export
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              <FileCode className="h-5 w-5 text-blue-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-sm">draw.io / diagrams.net</h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  mxGraphModel format
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
              <FileCode className="h-5 w-5 text-emerald-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-sm">DevFlow XML</h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Custom flowchart format
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tips Card */}
      <Card className="border-violet-500/20 bg-violet-500/5">
        <CardContent className="pt-6">
          <h4 className="font-medium text-violet-400 mb-3">💡 Tips for Best Results</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-violet-400">•</span>
              Use clear, descriptive labels for your flowchart nodes
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">•</span>
              Use database shapes (cylinders) for data operations
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">•</span>
              Decision diamonds will generate conditional logic
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">•</span>
              Subprocess shapes create separate service methods
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
