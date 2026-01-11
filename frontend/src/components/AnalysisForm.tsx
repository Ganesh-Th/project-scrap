'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrapeRequest, COUNTRIES, PLATFORMS } from '@/types/api';

interface AnalysisFormProps {
  onSubmit: (data: ScrapeRequest) => void;
  isLoading: boolean;
}

export function AnalysisForm({ onSubmit, isLoading }: AnalysisFormProps) {
  const [productName, setProductName] = useState('');
  const [appStoreId, setAppStoreId] = useState('');
  const [playStoreId, setPlayStoreId] = useState('');
  const [country, setCountry] = useState('us');
  const [platform, setPlatform] = useState<'phone' | 'tablet' | 'chromebook'>('phone');
  const [includeReddit, setIncludeReddit] = useState(true);
  const [redditKeyword, setRedditKeyword] = useState('');
  const [includeGoogleSearch, setIncludeGoogleSearch] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }
    if (!appStoreId.trim() && !playStoreId.trim()) {
      setError('Please enter at least one App Store ID or Play Store ID');
      return;
    }

    const data: ScrapeRequest = {
      product_name: productName.trim(),
      include_reddit: includeReddit,
      include_google_search: includeGoogleSearch,
    };

    if (playStoreId.trim()) {
      data.google_play = {
        product_id: playStoreId.trim(),
        platform,
      };
    }

    if (appStoreId.trim()) {
      data.apple_store = {
        product_id: appStoreId.trim(),
        country,
        target_reviews: 199,
      };
    }

    if (includeReddit) {
      data.reddit = {
        keyword: redditKeyword.trim() || productName.trim(),
        limit_pages: 2,
      };
    }

    if (includeGoogleSearch) {
      data.google_search = {
        product_name: productName.trim(),
      };
    }

    onSubmit(data);
  };

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          📊 Step 1: Analyze Reviews
        </CardTitle>
        <CardDescription>
          Enter your app details to fetch and analyze reviews from multiple sources
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="product-name">
                Product Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="product-name"
                placeholder="e.g., Instagram"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">
                Country <span className="text-red-500">*</span>
              </Label>
              <Select value={country} onValueChange={setCountry} disabled={isLoading}>
                <SelectTrigger id="country">
                  <SelectValue placeholder="Select country" />
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES.map((c) => (
                    <SelectItem key={c.code} value={c.code}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="app-store-id">App Store ID</Label>
              <Input
                id="app-store-id"
                placeholder="e.g., 389801252"
                value={appStoreId}
                onChange={(e) => setAppStoreId(e.target.value)}
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Numeric ID from App Store URL
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="play-store-id">Play Store ID</Label>
              <Input
                id="play-store-id"
                placeholder="e.g., com.instagram.android"
                value={playStoreId}
                onChange={(e) => setPlayStoreId(e.target.value)}
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Package name from Play Store URL
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="platform">Platform</Label>
            <Select
              value={platform}
              onValueChange={(v) => setPlatform(v as 'phone' | 'tablet' | 'chromebook')}
              disabled={isLoading}
            >
              <SelectTrigger id="platform">
                <SelectValue placeholder="Select platform" />
              </SelectTrigger>
              <SelectContent>
                {PLATFORMS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Additional Sources */}
          <div className="space-y-4 pt-4 border-t">
            <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
              Additional Sources
            </h3>
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="include-reddit" className="cursor-pointer">
                  Include Reddit
                </Label>
                <p className="text-xs text-muted-foreground">
                  Scrape discussions from Reddit
                </p>
              </div>
              <Switch
                id="include-reddit"
                checked={includeReddit}
                onCheckedChange={setIncludeReddit}
                disabled={isLoading}
              />
            </div>

            {includeReddit && (
              <div className="space-y-2 pl-4 border-l-2 border-purple-200">
                <Label htmlFor="reddit-keyword">Reddit Search Keyword</Label>
                <Input
                  id="reddit-keyword"
                  placeholder="Leave empty to use product name"
                  value={redditKeyword}
                  onChange={(e) => setRedditKeyword(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="include-google" className="cursor-pointer">
                  Include Google Search
                </Label>
                <p className="text-xs text-muted-foreground">
                  Find review articles and discussions
                </p>
              </div>
              <Switch
                id="include-google"
                checked={includeGoogleSearch}
                onCheckedChange={setIncludeGoogleSearch}
                disabled={isLoading}
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-[#8458B3] to-[#9b6fc4] hover:from-[#9b6fc4] hover:to-[#8458B3] text-white shadow-lg"
            size="lg"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Analyzing...
              </>
            ) : (
              <>
                🚀 Analyze Reviews
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
