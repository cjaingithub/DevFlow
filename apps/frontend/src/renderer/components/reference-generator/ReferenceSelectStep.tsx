/**
 * ReferenceSelectStep - Step 1: Select or load a reference project
 */

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FolderOpen,
  Plus,
  RefreshCw,
  Trash2,
  Check,
  Loader2,
  Database,
  Code2,
  Layers,
  FileCode,
  Clock,
  Zap
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '../ui/dialog';
import { cn } from '../../lib/utils';

import type { ReferenceProject, ReferenceProjectSummary } from '../../../shared/types';

interface ReferenceSelectStepProps {
  projectId: string;
  selectedReference: ReferenceProject | null;
  onSelect: (reference: ReferenceProject) => void;
  isLoading?: boolean;
}

// Mock data for now - will be replaced with actual API calls
const MOCK_REFERENCES: ReferenceProjectSummary[] = [
  {
    id: 'ref-1',
    name: 'User Authentication',
    description: 'JWT-based auth with roles, sessions, and OAuth support',
    patternCount: 12,
    tableCount: 4,
    techStack: {
      languages: ['python', 'typescript'],
      frameworks: ['fastapi', 'react'],
      databases: ['postgresql'],
      infrastructure: ['terraform']
    },
    status: 'ready',
    usageCount: 8
  },
  {
    id: 'ref-2',
    name: 'Orders Pipeline',
    description: 'AWS Lambda, Glue ETL, Step Functions for order processing',
    patternCount: 18,
    tableCount: 6,
    techStack: {
      languages: ['python'],
      frameworks: ['none'],
      databases: ['dynamodb', 'postgresql'],
      infrastructure: ['terraform', 'serverless']
    },
    status: 'ready',
    usageCount: 5
  }
];

export function ReferenceSelectStep({
  projectId,
  selectedReference,
  onSelect,
  isLoading = false
}: ReferenceSelectStepProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);
  
  const [references, setReferences] = useState<ReferenceProjectSummary[]>(MOCK_REFERENCES);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newRefName, setNewRefName] = useState('');
  const [newRefDescription, setNewRefDescription] = useState('');
  const [newRefPath, setNewRefPath] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(selectedReference?.id || null);
  
  // Load references on mount
  useEffect(() => {
    const loadReferences = async () => {
      try {
        const refs = await window.electronAPI.referenceGenerator.listReferences(projectId);
        if (refs && refs.length > 0) {
          setReferences(refs);
        }
      } catch (error) {
        console.error('Failed to load references:', error);
        // Keep mock references as fallback
      }
    };
    
    loadReferences();
  }, [projectId]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const refs = await window.electronAPI.referenceGenerator.listReferences(projectId);
      setReferences(refs);
    } catch (error) {
      console.error('Failed to refresh references:', error);
    }
    setIsRefreshing(false);
  }, [projectId]);

  const handleSelectDirectory = useCallback(async () => {
    try {
      const result = await window.electronAPI.referenceGenerator.selectDirectory(projectId);
      
      if (result.path && !result.canceled) {
        setNewRefPath(result.path);
      }
    } catch (error) {
      console.error('Failed to select directory:', error);
    }
  }, [projectId]);

  const handleAddReference = useCallback(async () => {
    if (!newRefName.trim() || !newRefPath.trim()) return;
    
    setIsAdding(true);
    try {
      const result = await window.electronAPI.referenceGenerator.loadReference(
        projectId,
        newRefPath,
        newRefName,
        newRefDescription
      );
      
      if (result.success && result.project) {
        const newRef: ReferenceProjectSummary = {
          id: result.project.id,
          name: result.project.name,
          description: result.project.description,
          patternCount: result.project.patternCount,
          tableCount: result.project.tableCount,
          techStack: result.project.techStack,
          status: result.project.status,
          usageCount: result.project.usageCount
        };
        
        setReferences(prev => [newRef, ...prev]);
        setShowAddDialog(false);
        setNewRefName('');
        setNewRefDescription('');
        setNewRefPath('');
      } else {
        console.error('Failed to load reference:', result.errors);
      }
    } catch (error) {
      console.error('Failed to add reference:', error);
    }
    setIsAdding(false);
  }, [projectId, newRefName, newRefDescription, newRefPath]);

  const handleSelectReference = useCallback(async (ref: ReferenceProjectSummary) => {
    if (ref.status !== 'ready') return;
    
    setSelectedId(ref.id);
    
    try {
      const fullRef = await window.electronAPI.referenceGenerator.getReference(projectId, ref.id);
      
      if (fullRef) {
        onSelect(fullRef);
      } else {
        // Fallback if full reference can't be loaded
        const fallbackRef: ReferenceProject = {
          ...ref,
          path: '',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          fileCount: 0,
          patterns: [],
          sqlTables: [],
          files: [],
          lastUsed: new Date().toISOString()
        };
        onSelect(fallbackRef);
      }
    } catch (error) {
      console.error('Failed to get reference details:', error);
    }
  }, [projectId, onSelect]);

  const getTechStackBadges = (techStack: ReferenceProjectSummary['techStack']) => {
    const badges: { label: string; variant: 'default' | 'secondary' | 'outline' }[] = [];
    
    techStack.languages.forEach(lang => {
      badges.push({ label: lang, variant: 'default' });
    });
    techStack.frameworks.filter(f => f !== 'none').forEach(fw => {
      badges.push({ label: fw, variant: 'secondary' });
    });
    techStack.databases.filter(d => d !== 'none').forEach(db => {
      badges.push({ label: db, variant: 'outline' });
    });
    
    return badges.slice(0, 5);
  };

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">
            {t('referenceGenerator:steps.select.title')}
          </h2>
          <p className="text-sm text-muted-foreground">
            {t('referenceGenerator:steps.select.subtitle')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={cn('w-4 h-4 mr-2', isRefreshing && 'animate-spin')} />
            {t('common:refresh')}
          </Button>
          <Button
            size="sm"
            onClick={() => setShowAddDialog(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('referenceGenerator:addReference')}
          </Button>
        </div>
      </div>

      {/* Reference Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {references.map(ref => (
          <Card
            key={ref.id}
            className={cn(
              'cursor-pointer transition-all hover:border-primary/50',
              selectedId === ref.id && 'border-primary ring-2 ring-primary/20',
              ref.status !== 'ready' && 'opacity-60 cursor-not-allowed'
            )}
            onClick={() => handleSelectReference(ref)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-base flex items-center gap-2">
                    <FolderOpen className="w-4 h-4 text-primary" />
                    {ref.name}
                  </CardTitle>
                  <CardDescription className="text-xs mt-1 line-clamp-2">
                    {ref.description}
                  </CardDescription>
                </div>
                {selectedId === ref.id && (
                  <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                    <Check className="w-3 h-3 text-primary-foreground" />
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              {/* Tech Stack Badges */}
              <div className="flex flex-wrap gap-1 mb-3">
                {getTechStackBadges(ref.techStack).map((badge, i) => (
                  <Badge key={i} variant={badge.variant} className="text-xs">
                    {badge.label}
                  </Badge>
                ))}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Code2 className="w-3 h-3" />
                  <span>{ref.patternCount} patterns</span>
                </div>
                <div className="flex items-center gap-1">
                  <Database className="w-3 h-3" />
                  <span>{ref.tableCount} tables</span>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  <span>{ref.usageCount}x used</span>
                </div>
              </div>

              {/* Status */}
              {ref.status !== 'ready' && (
                <div className="mt-2 flex items-center gap-2 text-xs text-amber-500">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>{ref.status === 'indexing' ? 'Indexing...' : 'Loading...'}</span>
                </div>
              )}
            </CardContent>
          </Card>
        ))}

        {/* Empty Add Card */}
        <Card
          className="cursor-pointer border-dashed hover:border-primary/50 transition-all"
          onClick={() => setShowAddDialog(true)}
        >
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[160px] text-muted-foreground">
            <Plus className="w-8 h-8 mb-2" />
            <span className="text-sm font-medium">
              {t('referenceGenerator:addNewReference')}
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Add Reference Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('referenceGenerator:addReference')}</DialogTitle>
            <DialogDescription>
              {t('referenceGenerator:addReferenceDescription')}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="ref-name">{t('referenceGenerator:referenceName')}</Label>
              <Input
                id="ref-name"
                value={newRefName}
                onChange={(e) => setNewRefName(e.target.value)}
                placeholder={t('referenceGenerator:referenceNamePlaceholder')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ref-description">{t('referenceGenerator:referenceDescription')}</Label>
              <Textarea
                id="ref-description"
                value={newRefDescription}
                onChange={(e) => setNewRefDescription(e.target.value)}
                placeholder={t('referenceGenerator:referenceDescriptionPlaceholder')}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label>{t('referenceGenerator:referencePath')}</Label>
              <div className="flex gap-2">
                <Input
                  value={newRefPath}
                  onChange={(e) => setNewRefPath(e.target.value)}
                  placeholder={t('referenceGenerator:referencePathPlaceholder')}
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  onClick={handleSelectDirectory}
                >
                  <FolderOpen className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowAddDialog(false)}
              disabled={isAdding}
            >
              {t('common:cancel')}
            </Button>
            <Button
              onClick={handleAddReference}
              disabled={!newRefName.trim() || !newRefPath.trim() || isAdding}
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('referenceGenerator:loading')}
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  {t('referenceGenerator:addReference')}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
