/**
 * ResultsStep - Step 5: Preview and download/apply generated files
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Download,
  FolderOpen,
  Check,
  Copy,
  FileCode,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  ExternalLink,
  Database,
  Layers,
  TestTube,
  FileText,
  Settings
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Separator } from '../ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { cn } from '../../lib/utils';

import type { GenerationResult, GeneratedFile } from '../../../shared/types';

interface ResultsStepProps {
  projectId: string;
  result: GenerationResult;
  onReset: () => void;
  onApply: () => void;
}

interface FileTreeNode {
  name: string;
  path: string;
  isDirectory: boolean;
  children?: FileTreeNode[];
  file?: GeneratedFile;
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'schema': return Database;
    case 'service': return FileCode;
    case 'repository': return Layers;
    case 'model': return FileCode;
    case 'test': return TestTube;
    case 'infrastructure': return Settings;
    default: return FileText;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'schema': return 'text-blue-500';
    case 'service': return 'text-purple-500';
    case 'repository': return 'text-green-500';
    case 'model': return 'text-amber-500';
    case 'test': return 'text-cyan-500';
    case 'infrastructure': return 'text-orange-500';
    default: return 'text-muted-foreground';
  }
};

function buildFileTree(files: GeneratedFile[]): FileTreeNode[] {
  const root: FileTreeNode[] = [];
  
  files.forEach(file => {
    const parts = file.path.split('/');
    let current = root;
    
    parts.forEach((part, index) => {
      const isLast = index === parts.length - 1;
      let existing = current.find(n => n.name === part);
      
      if (!existing) {
        existing = {
          name: part,
          path: parts.slice(0, index + 1).join('/'),
          isDirectory: !isLast,
          children: isLast ? undefined : [],
          file: isLast ? file : undefined
        };
        current.push(existing);
      }
      
      if (!isLast && existing.children) {
        current = existing.children;
      }
    });
  });
  
  return root;
}

function FileTreeItem({
  node,
  level = 0,
  selectedPath,
  onSelect
}: {
  node: FileTreeNode;
  level?: number;
  selectedPath: string | null;
  onSelect: (file: GeneratedFile) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  
  const Icon = node.isDirectory 
    ? (isExpanded ? ChevronDown : ChevronRight)
    : getCategoryIcon(node.file?.category || 'other');
  
  const handleClick = () => {
    if (node.isDirectory) {
      setIsExpanded(!isExpanded);
    } else if (node.file) {
      onSelect(node.file);
    }
  };
  
  return (
    <div>
      <button
        onClick={handleClick}
        className={cn(
          'w-full flex items-center gap-2 px-2 py-1.5 text-sm rounded-md transition-colors text-left',
          selectedPath === node.path && 'bg-primary/10 text-primary',
          selectedPath !== node.path && 'hover:bg-muted/50'
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        <Icon className={cn(
          'w-4 h-4 flex-shrink-0',
          node.isDirectory ? 'text-muted-foreground' : getCategoryColor(node.file?.category || 'other')
        )} />
        <span className="truncate">{node.name}</span>
        {node.file && (
          <Badge variant="outline" className="ml-auto text-xs">
            {Math.round(node.file.confidence * 100)}%
          </Badge>
        )}
      </button>
      {node.isDirectory && isExpanded && node.children && (
        <div>
          {node.children.map(child => (
            <FileTreeItem
              key={child.path}
              node={child}
              level={level + 1}
              selectedPath={selectedPath}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function ResultsStep({
  projectId,
  result,
  onReset,
  onApply
}: ResultsStepProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);
  
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(
    result.generatedFiles[0] || null
  );
  const [copied, setCopied] = useState(false);

  const fileTree = buildFileTree(result.generatedFiles);

  const handleCopyContent = useCallback(async () => {
    if (selectedFile) {
      await navigator.clipboard.writeText(selectedFile.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [selectedFile]);

  const handleDownloadZip = useCallback(async () => {
    try {
      const files = result.generatedFiles.map(f => ({ path: f.path, content: f.content }));
      const outputDir = result.generatedFiles[0]?.path.split('/')[0] || 'generated';
      
      const saveResult = await window.electronAPI.referenceGenerator.saveGeneratedFiles(
        projectId,
        files,
        outputDir
      );
      
      if (!saveResult.success) {
        console.error('Failed to save files:', saveResult.error);
      }
    } catch (error) {
      console.error('Failed to download files:', error);
    }
  }, [projectId, result.generatedFiles]);

  const handleApplyToProject = useCallback(async () => {
    try {
      const files = result.generatedFiles.map(f => ({ path: f.path, content: f.content }));
      
      const applyResult = await window.electronAPI.referenceGenerator.applyToProject(
        projectId,
        files
      );
      
      if (applyResult.success) {
        onApply();
      } else {
        console.error('Failed to apply files:', applyResult.error);
      }
    } catch (error) {
      console.error('Failed to apply to project:', error);
    }
  }, [projectId, result.generatedFiles, onApply]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Check className="w-5 h-5 text-green-500" />
            {t('referenceGenerator:generationComplete')}
          </h2>
          <p className="text-sm text-muted-foreground">
            {t('referenceGenerator:generatedFilesCount', { count: result.generatedFiles.length })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleDownloadZip}>
            <Download className="w-4 h-4 mr-2" />
            {t('referenceGenerator:downloadZip')}
          </Button>
          <Button onClick={handleApplyToProject}>
            <FolderOpen className="w-4 h-4 mr-2" />
            {t('referenceGenerator:applyToProject')}
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-muted/30">
          <CardContent className="pt-4 pb-4">
            <div className="text-2xl font-bold">{result.stats.totalFiles}</div>
            <div className="text-xs text-muted-foreground">{t('referenceGenerator:totalFiles')}</div>
          </CardContent>
        </Card>
        {Object.entries(result.stats.byCategory).map(([category, count]) => {
          const Icon = getCategoryIcon(category);
          return (
            <Card key={category} className="bg-muted/30">
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center gap-2">
                  <Icon className={cn('w-4 h-4', getCategoryColor(category))} />
                  <div className="text-2xl font-bold">{count}</div>
                </div>
                <div className="text-xs text-muted-foreground capitalize">{category}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* File Browser */}
      <Card className="overflow-hidden">
        <div className="flex h-[500px]">
          {/* File Tree */}
          <div className="w-64 border-r bg-muted/20">
            <div className="p-3 border-b">
              <h3 className="text-sm font-medium">{t('referenceGenerator:files')}</h3>
            </div>
            <ScrollArea className="h-[calc(100%-49px)]">
              <div className="p-2">
                {fileTree.map(node => (
                  <FileTreeItem
                    key={node.path}
                    node={node}
                    selectedPath={selectedFile?.path || null}
                    onSelect={setSelectedFile}
                  />
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* File Preview */}
          <div className="flex-1 flex flex-col">
            {selectedFile ? (
              <>
                <div className="p-3 border-b flex items-center justify-between bg-muted/10">
                  <div className="flex items-center gap-2">
                    <FileCode className={cn('w-4 h-4', getCategoryColor(selectedFile.category))} />
                    <span className="text-sm font-medium">{selectedFile.path}</span>
                    <Badge variant="outline" className="text-xs">
                      {selectedFile.fileType}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCopyContent}
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4 mr-2 text-green-500" />
                        {t('common:copied')}
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-2" />
                        {t('common:copy')}
                      </>
                    )}
                  </Button>
                </div>
                <ScrollArea className="flex-1">
                  <pre className="p-4 text-sm font-mono whitespace-pre-wrap">
                    {selectedFile.content}
                  </pre>
                </ScrollArea>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                {t('referenceGenerator:selectFileToPreview')}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Transformations */}
      {result.transformations.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">{t('referenceGenerator:transformations')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {result.transformations.map((t, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 bg-muted/30 px-3 py-1.5 rounded-full text-sm"
                >
                  <span className="text-muted-foreground">{t.original}</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  <span className="font-medium">{t.transformed}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <Card className="border-amber-500/30 bg-amber-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-amber-500">{t('referenceGenerator:warnings')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside text-sm text-muted-foreground">
              {result.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t">
        <Button variant="outline" onClick={onReset}>
          <RefreshCw className="w-4 h-4 mr-2" />
          {t('referenceGenerator:startOver')}
        </Button>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleDownloadZip}>
            <Download className="w-4 h-4 mr-2" />
            {t('referenceGenerator:downloadZip')}
          </Button>
          <Button onClick={handleApplyToProject}>
            <Check className="w-4 h-4 mr-2" />
            {t('referenceGenerator:applyToProject')}
          </Button>
        </div>
      </div>
    </div>
  );
}
