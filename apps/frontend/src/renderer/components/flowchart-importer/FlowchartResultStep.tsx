/**
 * FlowchartResultStep - Review and save generated files
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FolderOpen,
  FileCode2,
  Copy,
  ChevronRight,
  ChevronDown,
  ExternalLink,
  Sparkles,
  Database,
  GitBranch,
  Workflow
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Tooltip, TooltipContent, TooltipTrigger } from '../ui/tooltip';
import { cn } from '../../lib/utils';
import type { GenerationResult, GeneratedFile } from '../../../shared/types';

interface FlowchartResultStepProps {
  projectId: string;
  result: GenerationResult;
  onComplete: () => void;
  onBack: () => void;
}

function FileTypeIcon({ type }: { type: string }) {
  switch (type) {
    case 'repository':
      return <Database className="h-4 w-4 text-blue-400" />;
    case 'service_class':
      return <Workflow className="h-4 w-4 text-violet-400" />;
    case 'controller':
      return <GitBranch className="h-4 w-4 text-emerald-400" />;
    default:
      return <FileCode2 className="h-4 w-4 text-gray-400" />;
  }
}

function FileTree({ files }: { files: GeneratedFile[] }) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(null);

  // Group files by directory
  const fileTree = files.reduce((acc, file) => {
    const parts = file.path.split('/');
    const dir = parts.slice(0, -1).join('/');
    if (!acc[dir]) acc[dir] = [];
    acc[dir].push(file);
    return acc;
  }, {} as Record<string, GeneratedFile[]>);

  const toggleDir = (dir: string) => {
    setExpandedDirs(prev => {
      const next = new Set(prev);
      if (next.has(dir)) {
        next.delete(dir);
      } else {
        next.add(dir);
      }
      return next;
    });
  };

  const copyToClipboard = async (content: string) => {
    await navigator.clipboard.writeText(content);
  };

  return (
    <div className="grid grid-cols-5 gap-4 h-[400px]">
      {/* File Tree */}
      <div className="col-span-2 border border-border rounded-lg overflow-hidden">
        <div className="bg-muted/50 px-3 py-2 border-b border-border">
          <h4 className="text-sm font-medium">Generated Files</h4>
        </div>
        <ScrollArea className="h-[360px]">
          <div className="p-2 space-y-1">
            {Object.entries(fileTree).map(([dir, dirFiles]) => (
              <div key={dir}>
                <button
                  onClick={() => toggleDir(dir)}
                  className="flex items-center gap-2 w-full px-2 py-1.5 rounded hover:bg-muted/50 text-left"
                >
                  {expandedDirs.has(dir) ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  )}
                  <span className="text-sm font-medium">{dir || 'root'}/</span>
                  <Badge variant="secondary" className="text-xs ml-auto">
                    {dirFiles.length}
                  </Badge>
                </button>
                {expandedDirs.has(dir) && (
                  <div className="ml-6 space-y-0.5">
                    {dirFiles.map((file) => {
                      const fileName = file.path.split('/').pop();
                      return (
                        <button
                          key={file.path}
                          onClick={() => setSelectedFile(file)}
                          className={cn(
                            'flex items-center gap-2 w-full px-2 py-1.5 rounded text-left transition-colors',
                            selectedFile?.path === file.path
                              ? 'bg-primary/20 text-primary'
                              : 'hover:bg-muted/50'
                          )}
                        >
                          <FileTypeIcon type={file.fileType} />
                          <span className="text-sm font-mono truncate">{fileName}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* File Preview */}
      <div className="col-span-3 border border-border rounded-lg overflow-hidden">
        {selectedFile ? (
          <>
            <div className="bg-muted/50 px-3 py-2 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileTypeIcon type={selectedFile.fileType} />
                <span className="text-sm font-mono">{selectedFile.path}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {Math.round(selectedFile.confidence * 100)}% confidence
                </Badge>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => copyToClipboard(selectedFile.content)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Copy to clipboard</TooltipContent>
                </Tooltip>
              </div>
            </div>
            <ScrollArea className="h-[360px]">
              <pre className="p-4 text-xs font-mono">
                <code>{selectedFile.content}</code>
              </pre>
            </ScrollArea>
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <FileCode2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Select a file to preview</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function FlowchartResultStep({
  projectId,
  result,
  onComplete,
  onBack
}: FlowchartResultStepProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  const [activeTab, setActiveTab] = useState('files');
  
  const handleDownloadZip = useCallback(async () => {
    try {
      const files = result.generatedFiles.map(f => ({ path: f.path, content: f.content }));
      const outputDir = result.generatedFiles[0]?.path.split('/')[0] || 'generated';
      
      await window.electronAPI.flowchart.saveGeneratedFiles(projectId, outputDir, files);
    } catch (error) {
      console.error('Failed to save files:', error);
    }
  }, [projectId, result.generatedFiles]);

  const handleApplyToProject = useCallback(async () => {
    try {
      const files = result.generatedFiles.map(f => ({ path: f.path, content: f.content }));
      const outputDir = result.generatedFiles[0]?.path.split('/')[0] || 'generated';
      
      const saveResult = await window.electronAPI.flowchart.saveGeneratedFiles(projectId, outputDir, files);
      
      if (saveResult.success) {
        onComplete();
      }
    } catch (error) {
      console.error('Failed to apply files:', error);
    }
  }, [projectId, result.generatedFiles, onComplete]);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Success Header */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-emerald-500/10 via-green-500/10 to-teal-500/10 border-b border-emerald-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-emerald-500/20">
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <CardTitle className="text-emerald-400">Generation Complete!</CardTitle>
                <CardDescription>
                  {result.generatedFiles.length} files generated successfully
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-6">
              {Object.entries(result.stats.byType).map(([type, count]) => (
                <div key={type} className="text-center">
                  <div className="text-2xl font-bold text-emerald-400">{count}</div>
                  <div className="text-xs text-muted-foreground capitalize">
                    {type.replace('_', ' ')}s
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="files" className="gap-2">
            <FileCode2 className="h-4 w-4" />
            Generated Files
          </TabsTrigger>
          <TabsTrigger value="summary" className="gap-2">
            <Sparkles className="h-4 w-4" />
            Summary
          </TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <FileTree files={result.generatedFiles} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Files by Type */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Files by Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(result.stats.byType).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileTypeIcon type={type} />
                        <span className="capitalize">{type.replace('_', ' ')}</span>
                      </div>
                      <Badge variant="secondary">{count} files</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Confidence Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Confidence Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['high', 'medium', 'low'].map(level => {
                    const files = result.generatedFiles.filter(f => {
                      if (level === 'high') return f.confidence >= 0.8;
                      if (level === 'medium') return f.confidence >= 0.5 && f.confidence < 0.8;
                      return f.confidence < 0.5;
                    });
                    return (
                      <div key={level} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={cn(
                            'w-2 h-2 rounded-full',
                            level === 'high' && 'bg-emerald-500',
                            level === 'medium' && 'bg-amber-500',
                            level === 'low' && 'bg-red-500'
                          )} />
                          <span className="capitalize">{level} Confidence</span>
                        </div>
                        <Badge 
                          variant="outline"
                          className={cn(
                            level === 'high' && 'text-emerald-400 border-emerald-500/30',
                            level === 'medium' && 'text-amber-400 border-amber-500/30',
                            level === 'low' && 'text-red-400 border-red-500/30'
                          )}
                        >
                          {files.length} files
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Next Steps */}
      <Card className="border-violet-500/20 bg-violet-500/5">
        <CardContent className="pt-6">
          <h4 className="font-medium text-violet-400 mb-3">💡 Next Steps</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-violet-400">1.</span>
              Review the generated code and make any necessary adjustments
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">2.</span>
              Copy files to your project or use "Apply to Project" to save them
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">3.</span>
              Run tests to verify the generated code works correctly
            </li>
            <li className="flex items-start gap-2">
              <span className="text-violet-400">4.</span>
              Integrate with your existing codebase as needed
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4">
        <Button variant="outline" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Start Over
        </Button>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2" onClick={handleDownloadZip}>
            <Download className="h-4 w-4" />
            Download ZIP
          </Button>
          <Button 
            onClick={handleApplyToProject} 
            className="gap-2 bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600"
          >
            <FolderOpen className="h-4 w-4" />
            Apply to Project
          </Button>
        </div>
      </div>
    </div>
  );
}
