/**
 * ReferenceGenerator - Main component for Reference-Based Code Generation
 * 
 * This component provides a step-by-step wizard for:
 * 1. Selecting or loading a reference project
 * 2. Uploading new requirements
 * 3. Configuring entity mappings
 * 4. Generating and reviewing the output code
 */

import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FolderOpen,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Check,
  AlertCircle,
  FileCode2,
  Database,
  Layers,
  Settings2,
  Download
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';

import { ReferenceSelectStep } from './ReferenceSelectStep';
import { RequirementsUploadStep } from './RequirementsUploadStep';
import { EntityMappingStep } from './EntityMappingStep';
import { GenerationStep } from './GenerationStep';
import { ResultsStep } from './ResultsStep';

import type {
  ReferenceProject,
  ReferenceGeneratorState,
  ReferenceGeneratorStep,
  GenerationConfig,
  GenerationResult,
  ReferenceWizardStep
} from '../../../shared/types';

interface ReferenceGeneratorProps {
  projectId: string;
  onComplete?: (result: GenerationResult) => void;
  onCancel?: () => void;
}

const WIZARD_STEPS: ReferenceWizardStep[] = [
  {
    id: 'select',
    titleKey: 'referenceGenerator:steps.select.title',
    descriptionKey: 'referenceGenerator:steps.select.description',
    icon: 'FolderOpen'
  },
  {
    id: 'requirements',
    titleKey: 'referenceGenerator:steps.requirements.title',
    descriptionKey: 'referenceGenerator:steps.requirements.description',
    icon: 'FileCode2'
  },
  {
    id: 'mapping',
    titleKey: 'referenceGenerator:steps.mapping.title',
    descriptionKey: 'referenceGenerator:steps.mapping.description',
    icon: 'Settings2'
  },
  {
    id: 'generate',
    titleKey: 'referenceGenerator:steps.generate.title',
    descriptionKey: 'referenceGenerator:steps.generate.description',
    icon: 'Sparkles'
  },
  {
    id: 'result',
    titleKey: 'referenceGenerator:steps.result.title',
    descriptionKey: 'referenceGenerator:steps.result.description',
    icon: 'Check'
  }
];

const STEP_ORDER: ReferenceGeneratorStep[] = ['select', 'requirements', 'mapping', 'generate', 'result'];

export function ReferenceGenerator({ projectId, onComplete, onCancel }: ReferenceGeneratorProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);

  const [state, setState] = useState<ReferenceGeneratorState>({
    step: 'select',
    selectedReference: null,
    requirementsFile: null,
    requirementsContent: '',
    config: {
      entityMappings: [],
      outputDir: 'generated',
      includeTests: true,
      includeDocumentation: true,
      includeMigrations: true
    },
    generationResult: null,
    isLoading: false,
    error: null,
    progress: {
      current: 0,
      total: 0,
      phase: ''
    }
  });

  const currentStepIndex = STEP_ORDER.indexOf(state.step);
  const progressPercent = ((currentStepIndex + 1) / WIZARD_STEPS.length) * 100;

  // Navigation handlers
  const goToStep = useCallback((step: ReferenceGeneratorStep) => {
    setState(prev => ({ ...prev, step, error: null }));
  }, []);

  const goNext = useCallback(() => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEP_ORDER.length) {
      goToStep(STEP_ORDER[nextIndex]);
    }
  }, [currentStepIndex, goToStep]);

  const goBack = useCallback(() => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      goToStep(STEP_ORDER[prevIndex]);
    }
  }, [currentStepIndex, goToStep]);

  // Handler: Reference selected
  const handleReferenceSelect = useCallback((reference: ReferenceProject) => {
    setState(prev => ({
      ...prev,
      selectedReference: reference,
      error: null
    }));
    goNext();
  }, [goNext]);

  // Handler: Requirements uploaded
  const handleRequirementsUpload = useCallback((content: string, file?: File) => {
    setState(prev => ({
      ...prev,
      requirementsContent: content,
      requirementsFile: file || null,
      error: null
    }));
    goNext();
  }, [goNext]);

  // Handler: Config updated
  const handleConfigUpdate = useCallback((config: GenerationConfig) => {
    setState(prev => ({
      ...prev,
      config,
      error: null
    }));
  }, []);

  // Handler: Start generation
  const handleStartGeneration = useCallback(() => {
    goNext(); // Move to generate step - the GenerationStep will handle the actual generation
  }, [goNext]);

  // Handler: Generation complete
  const handleGenerationComplete = useCallback((result: GenerationResult) => {
    setState(prev => ({
      ...prev,
      generationResult: result,
      isLoading: false
    }));
    goNext();
    onComplete?.(result);
  }, [goNext, onComplete]);

  // Handler: Generation error
  const handleGenerationError = useCallback((error: string) => {
    setState(prev => ({
      ...prev,
      error,
      isLoading: false
    }));
  }, []);

  // Handler: Update progress
  const handleProgressUpdate = useCallback((progress: { current: number; total: number; phase: string }) => {
    setState(prev => ({
      ...prev,
      progress
    }));
  }, []);

  // Handler: Reset wizard
  const handleReset = useCallback(() => {
    setState({
      step: 'select',
      selectedReference: null,
      requirementsFile: null,
      requirementsContent: '',
      config: {
        entityMappings: [],
        outputDir: 'generated',
        includeTests: true,
        includeDocumentation: true,
        includeMigrations: true
      },
      generationResult: null,
      isLoading: false,
      error: null,
      progress: {
        current: 0,
        total: 0,
        phase: ''
      }
    });
  }, []);

  // Can proceed to next step?
  const canProceed = useCallback(() => {
    switch (state.step) {
      case 'select':
        return state.selectedReference !== null;
      case 'requirements':
        return state.requirementsContent.trim().length > 0;
      case 'mapping':
        return state.config.entityMappings.length > 0;
      case 'generate':
        return false; // Generation step handles its own navigation
      case 'result':
        return true;
      default:
        return false;
    }
  }, [state]);

  const getStepIcon = (iconName: string) => {
    const icons: Record<string, React.ElementType> = {
      FolderOpen,
      FileCode2,
      Settings2,
      Sparkles,
      Check
    };
    return icons[iconName] || FolderOpen;
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                {t('referenceGenerator:title')}
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {t('referenceGenerator:description')}
              </p>
            </div>
            {onCancel && (
              <Button variant="ghost" onClick={onCancel}>
                {t('common:cancel')}
              </Button>
            )}
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-2">
            {WIZARD_STEPS.map((step, index) => {
              const Icon = getStepIcon(step.icon);
              const isActive = state.step === step.id;
              const isComplete = STEP_ORDER.indexOf(step.id) < currentStepIndex;
              const isDisabled = STEP_ORDER.indexOf(step.id) > currentStepIndex;

              return (
                <div key={step.id} className="flex items-center">
                  <button
                    onClick={() => !isDisabled && goToStep(step.id)}
                    disabled={isDisabled}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg transition-all',
                      isActive && 'bg-primary text-primary-foreground',
                      isComplete && 'bg-green-500/10 text-green-500',
                      isDisabled && 'opacity-50 cursor-not-allowed',
                      !isActive && !isComplete && !isDisabled && 'hover:bg-accent'
                    )}
                  >
                    <div className={cn(
                      'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                      isActive && 'bg-primary-foreground/20',
                      isComplete && 'bg-green-500/20',
                      !isActive && !isComplete && 'bg-muted'
                    )}>
                      {isComplete ? <Check className="w-3 h-3" /> : index + 1}
                    </div>
                    <span className="text-sm font-medium hidden sm:inline">
                      {t(step.titleKey)}
                    </span>
                  </button>
                  {index < WIZARD_STEPS.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-muted-foreground mx-1" />
                  )}
                </div>
              );
            })}
          </div>

          {/* Progress Bar */}
          <Progress value={progressPercent} className="h-1 mt-4" />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Error Display */}
        {state.error && (
          <Card className="mb-4 border-destructive/50 bg-destructive/10">
            <CardContent className="py-3">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{state.error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step Content */}
        {state.step === 'select' && (
          <ReferenceSelectStep
            projectId={projectId}
            selectedReference={state.selectedReference}
            onSelect={handleReferenceSelect}
            isLoading={state.isLoading}
          />
        )}

        {state.step === 'requirements' && (
          <RequirementsUploadStep
            projectId={projectId}
            requirementsContent={state.requirementsContent}
            onUpload={handleRequirementsUpload}
            onBack={goBack}
          />
        )}

        {state.step === 'mapping' && state.selectedReference && (
          <EntityMappingStep
            projectId={projectId}
            reference={state.selectedReference}
            config={state.config}
            onConfigUpdate={handleConfigUpdate}
            onNext={handleStartGeneration}
            onBack={goBack}
          />
        )}

        {state.step === 'generate' && state.selectedReference && (
          <GenerationStep
            projectId={projectId}
            reference={state.selectedReference}
            requirementsContent={state.requirementsContent}
            config={state.config}
            progress={state.progress}
            onProgress={handleProgressUpdate}
            onComplete={handleGenerationComplete}
            onError={handleGenerationError}
            onBack={goBack}
          />
        )}

        {state.step === 'result' && state.generationResult && (
          <ResultsStep
            projectId={projectId}
            result={state.generationResult}
            onReset={handleReset}
            onApply={() => {}}
          />
        )}
      </div>
    </div>
  );
}

export default ReferenceGenerator;
