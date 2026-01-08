/**
 * EntityMappingStep - Step 3: Configure entity mappings
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Trash2,
  Wand2,
  Settings2,
  RefreshCw,
  FolderOutput
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../ui/select';
import { cn } from '../../lib/utils';

import type {
  ReferenceProject,
  GenerationConfig,
  EntityMapping
} from '../../../shared/types';

interface EntityMappingStepProps {
  projectId: string;
  reference: ReferenceProject;
  config: GenerationConfig;
  onConfigUpdate: (config: GenerationConfig) => void;
  onNext: () => void;
  onBack: () => void;
}

export function EntityMappingStep({
  projectId,
  reference,
  config,
  onConfigUpdate,
  onNext,
  onBack
}: EntityMappingStepProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);

  const [mappings, setMappings] = useState<EntityMapping[]>(
    config.entityMappings.length > 0 
      ? config.entityMappings 
      : [{ reference: '', new: '', mappingType: 'auto' as const }]
  );
  const [outputDir, setOutputDir] = useState(config.outputDir);
  const [includeTests, setIncludeTests] = useState(config.includeTests);
  const [includeDocs, setIncludeDocs] = useState(config.includeDocumentation);
  const [includeMigrations, setIncludeMigrations] = useState(config.includeMigrations);

  // Get available entities from reference for suggestions
  const referenceEntities = [
    ...reference.sqlTables.map(t => t.name),
    ...reference.patterns.map(p => p.entityName).filter(Boolean)
  ].filter((v, i, a) => a.indexOf(v) === i);

  const handleAddMapping = useCallback(() => {
    setMappings(prev => [...prev, { reference: '', new: '', mappingType: 'auto' as const }]);
  }, []);

  const handleRemoveMapping = useCallback((index: number) => {
    setMappings(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleMappingChange = useCallback((
    index: number, 
    field: keyof EntityMapping, 
    value: string
  ) => {
    setMappings(prev => prev.map((m, i) => 
      i === index ? { ...m, [field]: value } : m
    ));
  }, []);

  const handleAutoSuggest = useCallback(() => {
    // Simple auto-suggest based on reference entities
    if (referenceEntities.length > 0 && mappings.length === 1 && !mappings[0].reference) {
      const mainEntity = referenceEntities[0];
      setMappings([{
        reference: mainEntity,
        new: 'New' + mainEntity,
        mappingType: 'auto' as const
      }]);
    }
  }, [referenceEntities, mappings]);

  const handleSelectOutputDir = useCallback(async () => {
    try {
      const selectedPath = await window.api.project.selectDirectory();
      if (selectedPath) {
        setOutputDir(selectedPath);
      }
    } catch (error) {
      console.error('Failed to select output directory:', error);
    }
  }, []);

  const handleContinue = useCallback(() => {
    const validMappings = mappings.filter(m => m.reference.trim() && m.new.trim());
    onConfigUpdate({
      ...config,
      entityMappings: validMappings,
      outputDir,
      includeTests,
      includeDocumentation: includeDocs,
      includeMigrations
    });
    onNext();
  }, [mappings, outputDir, includeTests, includeDocs, includeMigrations, config, onConfigUpdate, onNext]);

  const canContinue = mappings.some(m => m.reference.trim() && m.new.trim());

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold">
          {t('referenceGenerator:steps.mapping.title')}
        </h2>
        <p className="text-sm text-muted-foreground">
          {t('referenceGenerator:steps.mapping.subtitle')}
        </p>
      </div>

      {/* Entity Mappings */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">
                {t('referenceGenerator:entityMappings')}
              </CardTitle>
              <CardDescription>
                {t('referenceGenerator:entityMappingsDescription')}
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleAutoSuggest}
            >
              <Wand2 className="w-4 h-4 mr-2" />
              {t('referenceGenerator:autoSuggest')}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {mappings.map((mapping, index) => (
            <div key={index} className="flex items-end gap-3">
              <div className="flex-1 space-y-1.5">
                <Label className="text-xs">
                  {t('referenceGenerator:referenceEntity')}
                </Label>
                <Select
                  value={mapping.reference}
                  onValueChange={(v) => handleMappingChange(index, 'reference', v)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('referenceGenerator:selectEntity')} />
                  </SelectTrigger>
                  <SelectContent>
                    {referenceEntities.map(entity => (
                      <SelectItem key={entity} value={entity}>
                        {entity}
                      </SelectItem>
                    ))}
                    <SelectItem value="_custom">
                      {t('referenceGenerator:customEntity')}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center text-muted-foreground">
                <ArrowRight className="w-4 h-4" />
              </div>

              <div className="flex-1 space-y-1.5">
                <Label className="text-xs">
                  {t('referenceGenerator:newEntity')}
                </Label>
                <Input
                  value={mapping.new}
                  onChange={(e) => handleMappingChange(index, 'new', e.target.value)}
                  placeholder={t('referenceGenerator:newEntityPlaceholder')}
                />
              </div>

              <Button
                variant="ghost"
                size="icon"
                className="text-muted-foreground hover:text-destructive"
                onClick={() => handleRemoveMapping(index)}
                disabled={mappings.length === 1}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}

          <Button
            variant="outline"
            size="sm"
            onClick={handleAddMapping}
            className="w-full"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('referenceGenerator:addMapping')}
          </Button>
        </CardContent>
      </Card>

      {/* Output Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {t('referenceGenerator:outputConfiguration')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Output Directory */}
          <div className="space-y-1.5">
            <Label>{t('referenceGenerator:outputDirectory')}</Label>
            <div className="flex gap-2">
              <Input
                value={outputDir}
                onChange={(e) => setOutputDir(e.target.value)}
                placeholder="generated/"
                className="flex-1"
              />
              <Button
                variant="outline"
                onClick={handleSelectOutputDir}
              >
                <FolderOutput className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
              <div className="space-y-0.5">
                <Label className="text-sm font-medium">
                  {t('referenceGenerator:includeTests')}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {t('referenceGenerator:includeTestsDescription')}
                </p>
              </div>
              <Switch
                checked={includeTests}
                onCheckedChange={setIncludeTests}
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
              <div className="space-y-0.5">
                <Label className="text-sm font-medium">
                  {t('referenceGenerator:includeDocs')}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {t('referenceGenerator:includeDocsDescription')}
                </p>
              </div>
              <Switch
                checked={includeDocs}
                onCheckedChange={setIncludeDocs}
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
              <div className="space-y-0.5">
                <Label className="text-sm font-medium">
                  {t('referenceGenerator:includeMigrations')}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {t('referenceGenerator:includeMigrationsDescription')}
                </p>
              </div>
              <Switch
                checked={includeMigrations}
                onCheckedChange={setIncludeMigrations}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reference Info */}
      <Card className="bg-muted/30">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            {t('referenceGenerator:selectedReference')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm">
            <span className="font-medium">{reference.name}</span>
            <div className="flex gap-2">
              <Badge variant="secondary">{reference.patternCount} patterns</Badge>
              <Badge variant="outline">{reference.tableCount} tables</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('common:back')}
        </Button>
        <Button onClick={handleContinue} disabled={!canContinue}>
          {t('referenceGenerator:generate')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
