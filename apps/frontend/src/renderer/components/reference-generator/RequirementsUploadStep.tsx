/**
 * RequirementsUploadStep - Step 2: Upload new requirements
 */

import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileUp,
  FileText,
  ArrowLeft,
  ArrowRight,
  X,
  Upload,
  Loader2
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { cn } from '../../lib/utils';

interface RequirementsUploadStepProps {
  projectId: string;
  requirementsContent: string;
  onUpload: (content: string, file?: File) => void;
  onBack: () => void;
}

export function RequirementsUploadStep({
  projectId,
  requirementsContent,
  onUpload,
  onBack
}: RequirementsUploadStepProps) {
  const { t } = useTranslation(['referenceGenerator', 'common']);
  
  const [content, setContent] = useState(requirementsContent);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'write' | 'upload'>(
    requirementsContent ? 'write' : 'upload'
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const mdFile = files.find(f => 
      f.name.endsWith('.md') || 
      f.name.endsWith('.txt') || 
      f.name.endsWith('.json')
    );
    
    if (mdFile) {
      setIsLoading(true);
      const text = await mdFile.text();
      setContent(text);
      setUploadedFile(mdFile);
      setIsLoading(false);
      setActiveTab('write');
    }
  }, []);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsLoading(true);
      const text = await file.text();
      setContent(text);
      setUploadedFile(file);
      setIsLoading(false);
      setActiveTab('write');
    }
  }, []);

  const handleClearFile = useCallback(() => {
    setUploadedFile(null);
    setContent('');
  }, []);

  const handleContinue = useCallback(() => {
    if (content.trim()) {
      onUpload(content, uploadedFile || undefined);
    }
  }, [content, uploadedFile, onUpload]);

  const canContinue = content.trim().length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold">
          {t('referenceGenerator:steps.requirements.title')}
        </h2>
        <p className="text-sm text-muted-foreground">
          {t('referenceGenerator:steps.requirements.subtitle')}
        </p>
      </div>

      {/* Content */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'write' | 'upload')}>
        <TabsList className="mb-4">
          <TabsTrigger value="upload">
            <Upload className="w-4 h-4 mr-2" />
            {t('referenceGenerator:uploadFile')}
          </TabsTrigger>
          <TabsTrigger value="write">
            <FileText className="w-4 h-4 mr-2" />
            {t('referenceGenerator:writeRequirements')}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="mt-0">
          <Card
            className={cn(
              'border-2 border-dashed transition-all',
              isDragging && 'border-primary bg-primary/5',
              !isDragging && 'border-muted-foreground/20'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <CardContent className="flex flex-col items-center justify-center py-12">
              {isLoading ? (
                <div className="flex flex-col items-center gap-2">
                  <Loader2 className="w-12 h-12 text-muted-foreground animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    {t('referenceGenerator:loadingFile')}
                  </span>
                </div>
              ) : uploadedFile ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="flex items-center gap-3 bg-muted/50 px-4 py-2 rounded-lg">
                    <FileText className="w-6 h-6 text-primary" />
                    <div>
                      <p className="text-sm font-medium">{uploadedFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(uploadedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={handleClearFile}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-sm text-green-500">
                    {t('referenceGenerator:fileLoaded')}
                  </p>
                </div>
              ) : (
                <>
                  <FileUp className="w-12 h-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium mb-1">
                    {t('referenceGenerator:dropFileHere')}
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('referenceGenerator:orClickToBrowse')}
                  </p>
                  <label>
                    <input
                      type="file"
                      accept=".md,.txt,.json"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Button variant="outline" asChild>
                      <span>
                        <Upload className="w-4 h-4 mr-2" />
                        {t('referenceGenerator:selectFile')}
                      </span>
                    </Button>
                  </label>
                  <p className="text-xs text-muted-foreground mt-4">
                    {t('referenceGenerator:supportedFormats')}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="write" className="mt-0">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="requirements-content">
                {t('referenceGenerator:requirementsContent')}
              </Label>
              {uploadedFile && (
                <span className="text-xs text-muted-foreground">
                  {t('referenceGenerator:loadedFrom')}: {uploadedFile.name}
                </span>
              )}
            </div>
            <Textarea
              id="requirements-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={t('referenceGenerator:requirementsPlaceholder')}
              className="min-h-[400px] font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground">
              {t('referenceGenerator:markdownSupported')}
            </p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Example Requirements */}
      <Card className="bg-muted/30">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            {t('referenceGenerator:exampleRequirements')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-xs text-muted-foreground overflow-x-auto">
{`# Product Catalog Feature

## Features
- List all products with pagination
- Filter products by category
- Search products by name
- View product details
- Create new products (admin only)

## Acceptance Criteria
- Products have: id, name, description, price, category, sku
- API responds within 200ms
- Pagination supports 20 items per page`}
          </pre>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('common:back')}
        </Button>
        <Button onClick={handleContinue} disabled={!canContinue}>
          {t('common:continue')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
