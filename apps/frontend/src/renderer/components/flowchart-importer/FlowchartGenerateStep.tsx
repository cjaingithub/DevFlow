/**
 * FlowchartGenerateStep - Code generation progress
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Loader2,
  Sparkles,
  FileCode2,
  CheckCircle2,
  AlertCircle,
  ArrowLeft
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import type { FlowchartParseResult, FlowchartGenerationConfig, GenerationResult } from '../../../shared/types';

interface FlowchartGenerateStepProps {
  projectId: string;
  xmlContent?: string;
  config: FlowchartGenerationConfig;
  parseResult: FlowchartParseResult | null;
  onComplete: (result: GenerationResult) => void;
  onBack: () => void;
}

interface GenerationLog {
  timestamp: Date;
  message: string;
  type: 'info' | 'success' | 'error';
}

export function FlowchartGenerateStep({
  projectId,
  xmlContent,
  config,
  parseResult,
  onComplete,
  onBack
}: FlowchartGenerateStepProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [logs, setLogs] = useState<GenerationLog[]>([]);
  const [isGenerating, setIsGenerating] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const addLog = useCallback((message: string, type: 'info' | 'success' | 'error' = 'info') => {
    setLogs(prev => [...prev, { timestamp: new Date(), message, type }]);
  }, []);

  useEffect(() => {
    // Subscribe to progress events
    const unsubscribeProgress = window.electronAPI.flowchart.onFlowchartGenerationProgress(
      (projId, prog, file) => {
        if (projId === projectId) {
          setProgress(prog);
          setCurrentFile(file);
          addLog(`Processing ${file}...`, 'info');
        }
      }
    );

    const generate = async () => {
      try {
        addLog('Starting code generation...');
        setProgress(10);

        // Call the IPC API to generate code from flowchart
        if (!parseResult || !parseResult.flowchart) {
          throw new Error('No flowchart data available');
        }

        addLog('Analyzing flowchart patterns...', 'info');
        setProgress(20);

        // Generate from the flowchart
        const result = await window.electronAPI.flowchart.generateFromFlowchart(
          projectId,
          '', // empty xmlPath since we're generating from parsed result
          config
        );

        if (result.success && result.data) {
          setProgress(100);
          addLog(`Successfully generated ${result.data.generatedFiles.length} files!`, 'success');
          setIsGenerating(false);

          // Wait a moment before transitioning
          await new Promise(r => setTimeout(r, 500));
          onComplete(result.data);
        } else {
          throw new Error(result.error || 'Generation failed');
        }

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Generation failed';
        setError(errorMessage);
        addLog(errorMessage, 'error');
        setIsGenerating(false);
      }
    };

    generate();

    return () => {
      unsubscribeProgress();
    };
  }, [projectId, config, parseResult, addLog, onComplete]);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Progress Card */}
      <Card className="overflow-hidden">
        <CardHeader className={cn(
          'border-b transition-colors duration-500',
          isGenerating && 'bg-gradient-to-r from-violet-500/10 via-fuchsia-500/10 to-purple-500/10 border-violet-500/20',
          !isGenerating && !error && 'bg-gradient-to-r from-emerald-500/10 via-green-500/10 to-teal-500/10 border-emerald-500/20',
          error && 'bg-gradient-to-r from-red-500/10 via-rose-500/10 to-pink-500/10 border-red-500/20'
        )}>
          <div className="flex items-center gap-4">
            <div className={cn(
              'p-3 rounded-xl',
              isGenerating && 'bg-violet-500/20',
              !isGenerating && !error && 'bg-emerald-500/20',
              error && 'bg-red-500/20'
            )}>
              {isGenerating ? (
                <Loader2 className="h-6 w-6 text-violet-400 animate-spin" />
              ) : error ? (
                <AlertCircle className="h-6 w-6 text-red-400" />
              ) : (
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              )}
            </div>
            <div className="flex-1">
              <CardTitle className={cn(
                isGenerating && 'text-violet-400',
                !isGenerating && !error && 'text-emerald-400',
                error && 'text-red-400'
              )}>
                {isGenerating ? 'Generating Code...' : error ? 'Generation Failed' : 'Generation Complete!'}
              </CardTitle>
              <CardDescription>
                {isGenerating 
                  ? currentFile 
                    ? `Processing ${currentFile}` 
                    : 'Preparing generation...'
                  : error
                    ? error
                    : 'All files have been generated successfully'
                }
              </CardDescription>
            </div>
            <div className="text-right">
              <div className={cn(
                'text-3xl font-bold',
                isGenerating && 'text-violet-400',
                !isGenerating && !error && 'text-emerald-400',
                error && 'text-red-400'
              )}>
                {progress}%
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <Progress 
            value={progress} 
            className={cn(
              'h-2',
              isGenerating && '[&>div]:bg-gradient-to-r [&>div]:from-violet-500 [&>div]:to-fuchsia-500',
              !isGenerating && !error && '[&>div]:bg-gradient-to-r [&>div]:from-emerald-500 [&>div]:to-green-500',
              error && '[&>div]:bg-red-500'
            )}
          />
        </CardContent>
      </Card>

      {/* Generation Logs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generation Log</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-[300px] overflow-y-auto font-mono text-sm">
            {logs.map((log, index) => (
              <div 
                key={index}
                className={cn(
                  'flex items-start gap-2 p-2 rounded',
                  log.type === 'success' && 'bg-emerald-500/10 text-emerald-400',
                  log.type === 'error' && 'bg-red-500/10 text-red-400',
                  log.type === 'info' && 'bg-muted/50 text-muted-foreground'
                )}
              >
                <span className="text-xs opacity-50 flex-shrink-0">
                  {log.timestamp.toLocaleTimeString()}
                </span>
                <span>{log.message}</span>
              </div>
            ))}
            {isGenerating && (
              <div className="flex items-center gap-2 p-2 text-muted-foreground animate-pulse">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>Processing...</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Preview */}
      {parseResult && (
        <Card className="border-violet-500/20">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileCode2 className="h-5 w-5 text-violet-400" />
                <div>
                  <h4 className="font-medium">Files to Generate</h4>
                  <p className="text-sm text-muted-foreground">
                    Based on {parseResult.generatedPatterns.length} patterns
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {Object.entries(
                  parseResult.generatedPatterns.reduce((acc, p) => {
                    acc[p.patternType] = (acc[p.patternType] || 0) + 1;
                    return acc;
                  }, {} as Record<string, number>)
                ).map(([type, count]) => (
                  <Badge key={type} variant="outline" className="capitalize">
                    {type.replace('_', ' ')}: {count}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Back Button (only if error) */}
      {error && (
        <div className="flex items-center justify-start pt-4">
          <Button variant="outline" onClick={onBack} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Configuration
          </Button>
        </div>
      )}
    </div>
  );
}
