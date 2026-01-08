/**
 * FlowchartImporter - Main component for importing Lucid flowchart XML
 * 
 * This component provides a step-by-step wizard for:
 * 1. Uploading/selecting a Lucid XML flowchart file
 * 2. Previewing the parsed flowchart structure
 * 3. Configuring entity mappings for code generation
 * 4. Generating and reviewing the output code
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileUp,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Check,
  AlertCircle,
  FileCode2,
  GitBranch,
  Database,
  Workflow
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';

import { FlowchartUploadStep } from './FlowchartUploadStep';
import { FlowchartPreviewStep } from './FlowchartPreviewStep';
import { FlowchartConfigStep } from './FlowchartConfigStep';
import { FlowchartGenerateStep } from './FlowchartGenerateStep';
import { FlowchartResultStep } from './FlowchartResultStep';
import type {
  FlowchartImporterState,
  FlowchartParseResult,
  FlowchartGenerationConfig,
  GenerationResult,
  WizardStep
} from '../../../shared/types';

interface FlowchartImporterProps {
  projectId: string;
  onComplete?: (result: GenerationResult) => void;
  onCancel?: () => void;
}

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 'upload',
    title: 'Upload Flowchart',
    description: 'Select a Lucid XML flowchart file',
    isComplete: false,
    isActive: true
  },
  {
    id: 'preview',
    title: 'Preview & Analyze',
    description: 'Review extracted requirements and patterns',
    isComplete: false,
    isActive: false
  },
  {
    id: 'configure',
    title: 'Configure Generation',
    description: 'Set entity mappings and options',
    isComplete: false,
    isActive: false
  },
  {
    id: 'generate',
    title: 'Generate Code',
    description: 'Generate code from flowchart patterns',
    isComplete: false,
    isActive: false
  },
  {
    id: 'result',
    title: 'Review Results',
    description: 'Review and save generated files',
    isComplete: false,
    isActive: false
  }
];

const DEFAULT_CONFIG: FlowchartGenerationConfig = {
  entityMappings: [],
  outputDir: 'generated',
  includeTests: true,
  includeDocumentation: true,
  targetLanguage: 'python'
};

export function FlowchartImporter({ projectId, onComplete, onCancel }: FlowchartImporterProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  
  const [state, setState] = useState<FlowchartImporterState>({
    step: 'upload',
    uploadedFile: null,
    parseResult: null,
    config: DEFAULT_CONFIG,
    generationResult: null,
    isLoading: false,
    error: null
  });

  const [steps, setSteps] = useState<WizardStep[]>(WIZARD_STEPS);

  const currentStepIndex = steps.findIndex(s => s.id === state.step);

  const updateStep = useCallback((stepId: string, updates: Partial<WizardStep>) => {
    setSteps(prev => prev.map(s => 
      s.id === stepId ? { ...s, ...updates } : s
    ));
  }, []);

  const goToStep = useCallback((stepId: FlowchartImporterState['step']) => {
    // Mark previous steps as complete
    const stepIndex = steps.findIndex(s => s.id === stepId);
    setSteps(prev => prev.map((s, i) => ({
      ...s,
      isComplete: i < stepIndex,
      isActive: s.id === stepId
    })));
    setState(prev => ({ ...prev, step: stepId, error: null }));
  }, [steps]);

  const handleFileSelected = useCallback(async (file: File, parseResult: FlowchartParseResult) => {
    setState(prev => ({
      ...prev,
      uploadedFile: file,
      parseResult,
      error: parseResult.success ? null : parseResult.errors.join(', ')
    }));
    
    if (parseResult.success) {
      goToStep('preview');
    }
  }, [goToStep]);

  const handleConfigUpdate = useCallback((config: FlowchartGenerationConfig) => {
    setState(prev => ({ ...prev, config }));
  }, []);

  const handleGenerationStart = useCallback(() => {
    setState(prev => ({ ...prev, isLoading: true }));
    goToStep('generate');
  }, [goToStep]);

  const handleGenerationComplete = useCallback((result: GenerationResult) => {
    setState(prev => ({
      ...prev,
      generationResult: result,
      isLoading: false,
      error: result.success ? null : result.errors.join(', ')
    }));
    
    if (result.success) {
      goToStep('result');
    }
  }, [goToStep]);

  const handleComplete = useCallback(() => {
    if (state.generationResult) {
      onComplete?.(state.generationResult);
    }
  }, [state.generationResult, onComplete]);

  const handleBack = useCallback(() => {
    const prevStepIndex = currentStepIndex - 1;
    if (prevStepIndex >= 0) {
      const prevStep = steps[prevStepIndex];
      goToStep(prevStep.id as FlowchartImporterState['step']);
    }
  }, [currentStepIndex, steps, goToStep]);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-background">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-border bg-gradient-to-r from-violet-950/20 via-fuchsia-950/10 to-background">
        <div className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/30">
              <Workflow className="h-6 w-6 text-violet-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                Flowchart to Code
              </h1>
              <p className="text-sm text-muted-foreground">
                Import Lucid XML flowcharts and generate code patterns
              </p>
            </div>
          </div>
        </div>

        {/* Step Progress */}
        <div className="px-6 pb-4">
          <div className="flex items-center gap-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={cn(
                    'flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all duration-200',
                    step.isActive && 'bg-violet-500/20 border border-violet-500/30',
                    step.isComplete && !step.isActive && 'bg-green-500/10',
                    !step.isActive && !step.isComplete && 'opacity-50'
                  )}
                >
                  <div
                    className={cn(
                      'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                      step.isActive && 'bg-violet-500 text-white',
                      step.isComplete && !step.isActive && 'bg-green-500 text-white',
                      !step.isActive && !step.isComplete && 'bg-muted text-muted-foreground'
                    )}
                  >
                    {step.isComplete && !step.isActive ? (
                      <Check className="h-3 w-3" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  <span
                    className={cn(
                      'text-sm font-medium hidden md:block',
                      step.isActive && 'text-violet-400',
                      step.isComplete && !step.isActive && 'text-green-400',
                      !step.isActive && !step.isComplete && 'text-muted-foreground'
                    )}
                  >
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <ArrowRight className="h-4 w-4 mx-2 text-muted-foreground/50" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Error Banner */}
        {state.error && (
          <div className="mb-4 p-4 rounded-lg border border-destructive/50 bg-destructive/10 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-destructive">Error</h4>
              <p className="text-sm text-destructive/80">{state.error}</p>
            </div>
          </div>
        )}

        {/* Step Content */}
        {state.step === 'upload' && (
          <FlowchartUploadStep
            projectId={projectId}
            onFileSelected={handleFileSelected}
            isLoading={state.isLoading}
          />
        )}

        {state.step === 'preview' && state.parseResult && (
          <FlowchartPreviewStep
            parseResult={state.parseResult}
            onContinue={() => goToStep('configure')}
            onBack={handleBack}
          />
        )}

        {state.step === 'configure' && state.parseResult && (
          <FlowchartConfigStep
            parseResult={state.parseResult}
            config={state.config}
            onConfigUpdate={handleConfigUpdate}
            onGenerate={handleGenerationStart}
            onBack={handleBack}
          />
        )}

        {state.step === 'generate' && (
          <FlowchartGenerateStep
            projectId={projectId}
            xmlContent={state.uploadedFile ? undefined : undefined}
            config={state.config}
            parseResult={state.parseResult}
            onComplete={handleGenerationComplete}
            onBack={handleBack}
          />
        )}

        {state.step === 'result' && state.generationResult && (
          <FlowchartResultStep
            result={state.generationResult}
            onComplete={handleComplete}
            onBack={handleBack}
          />
        )}
      </div>

      {/* Footer with Cancel */}
      <div className="flex-shrink-0 border-t border-border px-6 py-4 bg-muted/30">
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <FileCode2 className="h-4 w-4" />
            <span>Lucid XML → Code Generator</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FlowchartImporter;
