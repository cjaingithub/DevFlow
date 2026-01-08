/**
 * FlowchartPreviewStep - Preview parsed flowchart structure
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  ArrowRight,
  FileText,
  Workflow,
  Database,
  GitBranch,
  Code2,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Box,
  Diamond,
  Circle
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { cn } from '../../lib/utils';
import type { FlowchartParseResult, ParsedProcess, ParsedRequirement, ParsedDataFlow, CodePattern } from '../../../shared/types';

interface FlowchartPreviewStepProps {
  parseResult: FlowchartParseResult;
  onContinue: () => void;
  onBack: () => void;
}

function ProcessTypeIcon({ type }: { type: string }) {
  switch (type) {
    case 'decision':
      return <Diamond className="h-4 w-4 text-amber-400" />;
    case 'data_operation':
      return <Database className="h-4 w-4 text-blue-400" />;
    case 'subprocess':
      return <GitBranch className="h-4 w-4 text-purple-400" />;
    default:
      return <Box className="h-4 w-4 text-emerald-400" />;
  }
}

function PatternTypeIcon({ type }: { type: string }) {
  switch (type) {
    case 'repository':
      return <Database className="h-4 w-4 text-blue-400" />;
    case 'service_class':
      return <Workflow className="h-4 w-4 text-violet-400" />;
    case 'controller':
      return <GitBranch className="h-4 w-4 text-emerald-400" />;
    default:
      return <Code2 className="h-4 w-4 text-gray-400" />;
  }
}

export function FlowchartPreviewStep({
  parseResult,
  onContinue,
  onBack
}: FlowchartPreviewStepProps) {
  const { t } = useTranslation(['flowchart', 'common']);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedPatterns, setExpandedPatterns] = useState<Set<string>>(new Set());

  const flowchart = parseResult.flowchart;
  const { requirements, processes, dataFlows, generatedPatterns, warnings } = parseResult;

  const togglePattern = (patternName: string) => {
    setExpandedPatterns(prev => {
      const next = new Set(prev);
      if (next.has(patternName)) {
        next.delete(patternName);
      } else {
        next.add(patternName);
      }
      return next;
    });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Summary Header */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border-b border-emerald-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/20">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <CardTitle>{flowchart?.name || 'Flowchart'}</CardTitle>
                <CardDescription>
                  {flowchart?.description || 'Flowchart parsed successfully'}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-emerald-400">
                  {flowchart?.nodes.length || 0}
                </div>
                <div className="text-xs text-muted-foreground">Nodes</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-cyan-400">
                  {flowchart?.connections.length || 0}
                </div>
                <div className="text-xs text-muted-foreground">Connections</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-violet-400">
                  {generatedPatterns.length}
                </div>
                <div className="text-xs text-muted-foreground">Patterns</div>
              </div>
            </div>
          </div>
        </CardHeader>

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="px-6 py-3 bg-amber-500/10 border-b border-amber-500/20">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-amber-400">Warnings</h4>
                <ul className="mt-1 text-xs text-amber-300/80 space-y-0.5">
                  {warnings.map((warning, i) => (
                    <li key={i}>{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Tabs for Different Views */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="gap-2">
            <Workflow className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="requirements" className="gap-2">
            <FileText className="h-4 w-4" />
            Requirements ({requirements.length})
          </TabsTrigger>
          <TabsTrigger value="processes" className="gap-2">
            <GitBranch className="h-4 w-4" />
            Processes ({processes.length})
          </TabsTrigger>
          <TabsTrigger value="patterns" className="gap-2">
            <Code2 className="h-4 w-4" />
            Patterns ({generatedPatterns.length})
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Node Types */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Node Types</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(
                    flowchart?.nodes.reduce((acc, node) => {
                      acc[node.nodeType] = (acc[node.nodeType] || 0) + 1;
                      return acc;
                    }, {} as Record<string, number>) || {}
                  ).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ProcessTypeIcon type={type} />
                        <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                      </div>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Data Operations */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Data Operations</CardTitle>
              </CardHeader>
              <CardContent>
                {dataFlows.length > 0 ? (
                  <div className="space-y-2">
                    {dataFlows.map((df) => (
                      <div key={df.id} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                        <div className="flex items-center gap-2">
                          <Database className="h-4 w-4 text-blue-400" />
                          <span className="text-sm font-mono">{df.tableName}</span>
                        </div>
                        <Badge 
                          variant="outline"
                          className={cn(
                            df.operation === 'read' && 'text-emerald-400 border-emerald-500/30',
                            df.operation === 'write' && 'text-blue-400 border-blue-500/30',
                            df.operation === 'update' && 'text-amber-400 border-amber-500/30',
                            df.operation === 'delete' && 'text-red-400 border-red-500/30'
                          )}
                        >
                          {df.operation.toUpperCase()}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No data operations detected</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Requirements Tab */}
        <TabsContent value="requirements" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              {requirements.length > 0 ? (
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3 pr-4">
                    {requirements.map((req) => (
                      <div key={req.id} className="p-4 rounded-lg border border-border bg-card">
                        <div className="flex items-start justify-between">
                          <h4 className="font-medium">{req.title}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="capitalize">
                              {req.requirementType}
                            </Badge>
                            <Badge 
                              variant="outline"
                              className={cn(
                                req.priority === 'high' && 'text-red-400 border-red-500/30',
                                req.priority === 'medium' && 'text-amber-400 border-amber-500/30',
                                req.priority === 'low' && 'text-emerald-400 border-emerald-500/30'
                              )}
                            >
                              {req.priority}
                            </Badge>
                          </div>
                        </div>
                        {req.description && (
                          <p className="text-sm text-muted-foreground mt-2">{req.description}</p>
                        )}
                        {req.acceptanceCriteria.length > 0 && (
                          <div className="mt-3">
                            <h5 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                              Acceptance Criteria
                            </h5>
                            <ul className="text-sm space-y-1">
                              {req.acceptanceCriteria.map((ac, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <CheckCircle2 className="h-3 w-3 text-emerald-400 mt-1 flex-shrink-0" />
                                  <span>{ac}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No requirements extracted from flowchart</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Processes Tab */}
        <TabsContent value="processes" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              {processes.length > 0 ? (
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3 pr-4">
                    {processes.map((proc) => (
                      <div key={proc.id} className="p-4 rounded-lg border border-border bg-card">
                        <div className="flex items-center gap-3">
                          <ProcessTypeIcon type={proc.processType} />
                          <div className="flex-1">
                            <h4 className="font-medium">{proc.name}</h4>
                            <Badge variant="outline" className="mt-1 capitalize text-xs">
                              {proc.processType.replace('_', ' ')}
                            </Badge>
                          </div>
                        </div>
                        {proc.description && (
                          <p className="text-sm text-muted-foreground mt-2">{proc.description}</p>
                        )}
                        <div className="grid grid-cols-2 gap-4 mt-3">
                          {proc.inputs.length > 0 && (
                            <div>
                              <h5 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                                Inputs
                              </h5>
                              <div className="flex flex-wrap gap-1">
                                {proc.inputs.map((input, i) => (
                                  <Badge key={i} variant="secondary" className="text-xs">
                                    {input}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          {proc.outputs.length > 0 && (
                            <div>
                              <h5 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                                Outputs
                              </h5>
                              <div className="flex flex-wrap gap-1">
                                {proc.outputs.map((output, i) => (
                                  <Badge key={i} variant="secondary" className="text-xs">
                                    {output}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <GitBranch className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No processes extracted from flowchart</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              {generatedPatterns.length > 0 ? (
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2 pr-4">
                    {generatedPatterns.map((pattern) => (
                      <Collapsible
                        key={pattern.name}
                        open={expandedPatterns.has(pattern.name)}
                        onOpenChange={() => togglePattern(pattern.name)}
                      >
                        <CollapsibleTrigger className="w-full">
                          <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-card hover:bg-muted/50 transition-colors">
                            <div className="flex items-center gap-3">
                              <PatternTypeIcon type={pattern.patternType} />
                              <div className="text-left">
                                <h4 className="font-mono text-sm font-medium">{pattern.name}</h4>
                                <p className="text-xs text-muted-foreground capitalize">
                                  {pattern.patternType.replace('_', ' ')}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge variant="outline" className="text-xs">
                                {Math.round(pattern.confidence * 100)}% confidence
                              </Badge>
                              {expandedPatterns.has(pattern.name) ? (
                                <ChevronDown className="h-4 w-4" />
                              ) : (
                                <ChevronRight className="h-4 w-4" />
                              )}
                            </div>
                          </div>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                          <div className="mt-2 p-4 rounded-lg bg-muted/50 border border-border">
                            <p className="text-sm text-muted-foreground mb-3">
                              {pattern.description}
                            </p>
                            <pre className="text-xs font-mono p-3 rounded bg-black/30 overflow-x-auto">
                              <code>{pattern.codeSnippet}</code>
                            </pre>
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    ))}
                  </div>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Code2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No patterns generated from flowchart</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4">
        <Button variant="outline" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <Button onClick={onContinue} className="gap-2">
          Continue to Configuration
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
