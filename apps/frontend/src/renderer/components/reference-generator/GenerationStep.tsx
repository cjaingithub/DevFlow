/**
 * GenerationStep - Step 4: Generate code with progress
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  Loader2,
  Check,
  AlertCircle,
  FileCode,
  Database,
  Layers,
  TestTube,
  FileText,
  Sparkles
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';

import type {
  ReferenceProject,
  GenerationConfig,
  GenerationResult
} from '../../../shared/types';

interface GenerationStepProps {
  projectId: string;
  reference: ReferenceProject;
  requirementsContent: string;
  config: GenerationConfig;
  progress: {
    current: number;
    total: number;
    phase: string;
  };
  onProgress: (progress: { current: number; total: number; phase: string }) => void;
  onComplete: (result: GenerationResult) => void;
  onError: (error: string) => void;
  onBack: () => void;
}

interface GenerationPhase {
  id: string;
  name: string;
  icon: React.ElementType;
  status: 'pending' | 'active' | 'complete' | 'error';
  message?: string;
}

const GENERATION_PHASES: Omit<GenerationPhase, 'status'>[] = [
  { id: 'analyze', name: 'Analyzing reference patterns', icon: Layers },
  { id: 'schema', name: 'Generating database schema', icon: Database },
  { id: 'services', name: 'Creating service classes', icon: FileCode },
  { id: 'tests', name: 'Generating test files', icon: TestTube },
  { id: 'docs', name: 'Writing documentation', icon: FileText },
  { id: 'finalize', name: 'Finalizing output', icon: Sparkles }
];

export function GenerationStep({
  projectId,
  reference,
  requirementsContent,
  config,
  progress,
  onProgress,
  onComplete,
  onError,
  onBack
}: GenerationStepProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);

  const [phases, setPhases] = useState<GenerationPhase[]>(
    GENERATION_PHASES.map(p => ({ ...p, status: 'pending' }))
  );
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [isGenerating, setIsGenerating] = useState(true);
  const [logs, setLogs] = useState<string[]>([]);

  // Simulate generation process
  useEffect(() => {
    if (!isGenerating) return;

    const simulateGeneration = async () => {
      for (let i = 0; i < GENERATION_PHASES.length; i++) {
        // Set current phase as active
        setPhases(prev => prev.map((p, idx) => ({
          ...p,
          status: idx < i ? 'complete' : idx === i ? 'active' : 'pending'
        })));
        setCurrentPhaseIndex(i);
        
        // Update progress
        onProgress({
          current: i + 1,
          total: GENERATION_PHASES.length,
          phase: GENERATION_PHASES[i].name
        });

        // Add log
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Starting: ${GENERATION_PHASES[i].name}`]);

        // Simulate phase duration
        await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 600));

        // Add completion log
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Completed: ${GENERATION_PHASES[i].name}`]);

        // Mark phase as complete
        setPhases(prev => prev.map((p, idx) => ({
          ...p,
          status: idx <= i ? 'complete' : 'pending'
        })));
      }

      // Generation complete - create mock result
      setIsGenerating(false);
      
      const mockResult: GenerationResult = {
        success: true,
        generatedFiles: [
          { path: `${config.outputDir}/schema/schema.sql`, content: '-- Generated schema', fileType: 'sql', category: 'schema', confidence: 0.95 },
          { path: `${config.outputDir}/services/service.py`, content: '# Generated service', fileType: 'py', category: 'service', confidence: 0.92 },
          { path: `${config.outputDir}/repositories/repository.py`, content: '# Generated repository', fileType: 'py', category: 'repository', confidence: 0.90 },
          { path: `${config.outputDir}/models/model.py`, content: '# Generated model', fileType: 'py', category: 'model', confidence: 0.94 },
          ...(config.includeTests ? [
            { path: `${config.outputDir}/tests/test_service.py`, content: '# Generated tests', fileType: 'py', category: 'test' as const, confidence: 0.88 }
          ] : [])
        ],
        errors: [],
        warnings: [],
        transformations: config.entityMappings.map(m => ({
          original: m.reference,
          transformed: m.new,
          type: m.mappingType
        })),
        stats: {
          totalFiles: 5,
          byCategory: {
            schema: 1,
            service: 1,
            repository: 1,
            model: 1,
            test: config.includeTests ? 1 : 0
          },
          byType: {
            sql: 1,
            py: config.includeTests ? 4 : 3
          }
        }
      };

      onComplete(mockResult);
    };

    simulateGeneration();
  }, [isGenerating, config, onProgress, onComplete]);

  const progressPercent = ((currentPhaseIndex + 1) / GENERATION_PHASES.length) * 100;

  const getPhaseIcon = (phase: GenerationPhase) => {
    const Icon = phase.icon;
    if (phase.status === 'active') {
      return <Loader2 className="w-4 h-4 animate-spin" />;
    }
    if (phase.status === 'complete') {
      return <Check className="w-4 h-4 text-green-500" />;
    }
    if (phase.status === 'error') {
      return <AlertCircle className="w-4 h-4 text-destructive" />;
    }
    return <Icon className="w-4 h-4 text-muted-foreground" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-lg font-semibold">
          {t('referenceGenerator:steps.generate.title')}
        </h2>
        <p className="text-sm text-muted-foreground">
          {isGenerating
            ? t('referenceGenerator:generatingCode')
            : t('referenceGenerator:generationComplete')
          }
        </p>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Overall Progress */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  {t('referenceGenerator:progress')}
                </span>
                <span className="font-medium">
                  {currentPhaseIndex + 1} / {GENERATION_PHASES.length}
                </span>
              </div>
              <Progress value={progressPercent} className="h-2" />
            </div>

            {/* Phase List */}
            <div className="space-y-2 pt-2">
              {phases.map((phase, index) => (
                <div
                  key={phase.id}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg transition-all',
                    phase.status === 'active' && 'bg-primary/10 border border-primary/20',
                    phase.status === 'complete' && 'bg-green-500/5',
                    phase.status === 'pending' && 'opacity-50'
                  )}
                >
                  <div className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center',
                    phase.status === 'active' && 'bg-primary/20',
                    phase.status === 'complete' && 'bg-green-500/20',
                    phase.status === 'pending' && 'bg-muted'
                  )}>
                    {getPhaseIcon(phase)}
                  </div>
                  <div className="flex-1">
                    <p className={cn(
                      'text-sm font-medium',
                      phase.status === 'active' && 'text-primary',
                      phase.status === 'complete' && 'text-green-500'
                    )}>
                      {phase.name}
                    </p>
                    {phase.message && (
                      <p className="text-xs text-muted-foreground">{phase.message}</p>
                    )}
                  </div>
                  {phase.status === 'complete' && (
                    <Badge variant="outline" className="text-green-500 border-green-500/30">
                      {t('common:complete')}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Generation Info */}
      <Card className="bg-muted/30">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            {t('referenceGenerator:generationDetails')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">{t('referenceGenerator:reference')}</p>
              <p className="font-medium">{reference.name}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t('referenceGenerator:mappings')}</p>
              <p className="font-medium">{config.entityMappings.length}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t('referenceGenerator:output')}</p>
              <p className="font-medium">{config.outputDir}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{t('referenceGenerator:options')}</p>
              <div className="flex gap-1">
                {config.includeTests && <Badge variant="secondary" className="text-xs">Tests</Badge>}
                {config.includeDocumentation && <Badge variant="secondary" className="text-xs">Docs</Badge>}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            {t('referenceGenerator:logs')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-black/90 rounded-lg p-3 h-32 overflow-y-auto font-mono text-xs">
            {logs.map((log, i) => (
              <div key={i} className="text-green-400">
                {log}
              </div>
            ))}
            {isGenerating && (
              <div className="text-green-400 animate-pulse">▌</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t">
        <Button
          variant="outline"
          onClick={onBack}
          disabled={isGenerating}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('common:back')}
        </Button>
        <div className="text-sm text-muted-foreground">
          {isGenerating
            ? t('referenceGenerator:pleaseWait')
            : t('referenceGenerator:redirecting')
          }
        </div>
      </div>
    </div>
  );
}
