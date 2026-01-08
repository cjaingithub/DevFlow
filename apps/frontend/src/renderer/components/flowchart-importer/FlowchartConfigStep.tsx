/**
 * FlowchartConfigStep - Configure entity mappings and generation options
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Trash2,
  Sparkles,
  FolderOutput,
  Settings2,
  FileCode,
  TestTube,
  FileText,
  Wand2
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';
import type { FlowchartParseResult, FlowchartGenerationConfig, EntityMapping } from '../../../shared/types';

interface FlowchartConfigStepProps {
  parseResult: FlowchartParseResult;
  config: FlowchartGenerationConfig;
  onConfigUpdate: (config: FlowchartGenerationConfig) => void;
  onGenerate: () => void;
  onBack: () => void;
}

export function FlowchartConfigStep({
  parseResult,
  config,
  onConfigUpdate,
  onGenerate,
  onBack
}: FlowchartConfigStepProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  const [newMapping, setNewMapping] = useState<EntityMapping>({ reference: '', new: '' });

  // Extract entity names from patterns for suggestions
  const suggestedEntities = Array.from(new Set(
    parseResult.generatedPatterns
      .map(p => p.entityName)
      .filter(Boolean)
  ));

  const handleAddMapping = useCallback(() => {
    if (newMapping.reference && newMapping.new) {
      onConfigUpdate({
        ...config,
        entityMappings: [...config.entityMappings, newMapping]
      });
      setNewMapping({ reference: '', new: '' });
    }
  }, [config, newMapping, onConfigUpdate]);

  const handleRemoveMapping = useCallback((index: number) => {
    onConfigUpdate({
      ...config,
      entityMappings: config.entityMappings.filter((_, i) => i !== index)
    });
  }, [config, onConfigUpdate]);

  const handleAutoSuggest = useCallback(() => {
    // Auto-generate mappings based on entities found
    const autoMappings: EntityMapping[] = suggestedEntities.map(entity => ({
      reference: entity,
      new: entity // User can modify these
    }));
    onConfigUpdate({
      ...config,
      entityMappings: [...config.entityMappings, ...autoMappings]
    });
  }, [config, suggestedEntities, onConfigUpdate]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-red-500/10 border-b border-amber-500/20">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/20">
              <Settings2 className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <CardTitle>Configure Generation</CardTitle>
              <CardDescription>
                Set up entity mappings and generation options
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Entity Mappings */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Entity Mappings</CardTitle>
              <CardDescription>
                Map entities from the flowchart to your new implementation
              </CardDescription>
            </div>
            {suggestedEntities.length > 0 && config.entityMappings.length === 0 && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleAutoSuggest}
                className="gap-2"
              >
                <Wand2 className="h-4 w-4" />
                Auto-Suggest
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Existing Mappings */}
          {config.entityMappings.length > 0 && (
            <div className="space-y-2">
              {config.entityMappings.map((mapping, index) => (
                <div 
                  key={index} 
                  className="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/30"
                >
                  <div className="flex-1 grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-xs text-muted-foreground">From (Reference)</Label>
                      <div className="font-mono text-sm mt-1">{mapping.reference}</div>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">To (New)</Label>
                      <div className="font-mono text-sm mt-1">{mapping.new}</div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => handleRemoveMapping(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Add New Mapping */}
          <div className="flex items-end gap-3 p-4 rounded-lg border border-dashed border-border bg-muted/20">
            <div className="flex-1 grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ref-entity">Reference Entity</Label>
                <Input
                  id="ref-entity"
                  placeholder="e.g., Order"
                  value={newMapping.reference}
                  onChange={(e) => setNewMapping(prev => ({ ...prev, reference: e.target.value }))}
                  list="entity-suggestions"
                />
                <datalist id="entity-suggestions">
                  {suggestedEntities.map(entity => (
                    <option key={entity} value={entity} />
                  ))}
                </datalist>
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-entity">New Entity Name</Label>
                <Input
                  id="new-entity"
                  placeholder="e.g., Inventory"
                  value={newMapping.new}
                  onChange={(e) => setNewMapping(prev => ({ ...prev, new: e.target.value }))}
                />
              </div>
            </div>
            <Button
              onClick={handleAddMapping}
              disabled={!newMapping.reference || !newMapping.new}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Add
            </Button>
          </div>

          {/* Suggested Entities */}
          {suggestedEntities.length > 0 && (
            <div className="pt-2">
              <Label className="text-xs text-muted-foreground">Detected Entities</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {suggestedEntities.map(entity => (
                  <Badge 
                    key={entity} 
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary/20"
                    onClick={() => setNewMapping(prev => ({ ...prev, reference: entity }))}
                  >
                    {entity}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Output Options */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Output Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Output Directory */}
          <div className="space-y-2">
            <Label htmlFor="output-dir" className="flex items-center gap-2">
              <FolderOutput className="h-4 w-4" />
              Output Directory
            </Label>
            <Input
              id="output-dir"
              value={config.outputDir}
              onChange={(e) => onConfigUpdate({ ...config, outputDir: e.target.value })}
              placeholder="generated"
            />
            <p className="text-xs text-muted-foreground">
              Generated files will be placed in this directory relative to your project root
            </p>
          </div>

          <Separator />

          {/* Target Language */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <FileCode className="h-4 w-4" />
              Target Language
            </Label>
            <Select
              value={config.targetLanguage}
              onValueChange={(value: 'python' | 'typescript' | 'java') => 
                onConfigUpdate({ ...config, targetLanguage: value })
              }
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="python">Python</SelectItem>
                <SelectItem value="typescript">TypeScript</SelectItem>
                <SelectItem value="java">Java</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          {/* Generation Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TestTube className="h-4 w-4 text-emerald-400" />
                <div>
                  <Label htmlFor="include-tests">Include Tests</Label>
                  <p className="text-xs text-muted-foreground">Generate test templates for each service</p>
                </div>
              </div>
              <Switch
                id="include-tests"
                checked={config.includeTests}
                onCheckedChange={(checked) => onConfigUpdate({ ...config, includeTests: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-blue-400" />
                <div>
                  <Label htmlFor="include-docs">Include Documentation</Label>
                  <p className="text-xs text-muted-foreground">Generate README and API documentation</p>
                </div>
              </div>
              <Switch
                id="include-docs"
                checked={config.includeDocumentation}
                onCheckedChange={(checked) => onConfigUpdate({ ...config, includeDocumentation: checked })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <Card className="border-violet-500/20 bg-violet-500/5">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-violet-400">Generation Summary</h4>
              <p className="text-sm text-muted-foreground mt-1">
                {parseResult.generatedPatterns.length} patterns will be generated
                {config.entityMappings.length > 0 && ` with ${config.entityMappings.length} entity mappings`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="gap-1">
                <FolderOutput className="h-3 w-3" />
                {config.outputDir}
              </Badge>
              <Badge variant="outline" className="gap-1">
                <FileCode className="h-3 w-3" />
                {config.targetLanguage}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4">
        <Button variant="outline" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <Button 
          onClick={onGenerate} 
          className="gap-2 bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600"
        >
          <Sparkles className="h-4 w-4" />
          Generate Code
        </Button>
      </div>
    </div>
  );
}
