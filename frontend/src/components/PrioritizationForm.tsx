'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PrioritizationRequest, PRIORITIZATION_METHODS } from '@/types/api';

interface PrioritizationFormProps {
  taskId: string;
  onSubmit: (data: PrioritizationRequest) => void;
  onBack: () => void;
  isLoading: boolean;
}

export function PrioritizationForm({ taskId, onSubmit, onBack, isLoading }: PrioritizationFormProps) {
  const [method, setMethod] = useState<'MoSCoW' | 'Lean'>('MoSCoW');
  const [duration, setDuration] = useState('14');
  const [budget, setBudget] = useState('160');
  const [businessGoal, setBusinessGoal] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!duration || parseInt(duration) < 1) {
      setError('Please enter a valid sprint duration');
      return;
    }
    if (!budget || parseInt(budget) < 1) {
      setError('Please enter a valid resource budget');
      return;
    }
    if (!businessGoal.trim()) {
      setError('Please enter a business goal');
      return;
    }

    onSubmit({
      task_id: taskId,
      method,
      duration: parseInt(duration),
      budget: parseInt(budget),
      business_goal: businessGoal.trim(),
    });
  };

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          🎯 Step 2: Prioritization Strategy
        </CardTitle>
        <CardDescription>
          Configure your prioritization framework to rank identified issues
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="method">
              Prioritization Technique <span className="text-red-500">*</span>
            </Label>
            <Select
              value={method}
              onValueChange={(v) => setMethod(v as 'MoSCoW' | 'Lean')}
              disabled={isLoading}
            >
              <SelectTrigger id="method">
                <SelectValue placeholder="Select technique" />
              </SelectTrigger>
              <SelectContent>
                {PRIORITIZATION_METHODS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {method === 'MoSCoW'
                ? 'Categorize items as Must-have, Should-have, Could-have, or Won\'t-have'
                : 'Prioritize based on Impact vs Effort matrix'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration">
                Sprint Timeframe (days) <span className="text-red-500">*</span>
              </Label>
              <Input
                id="duration"
                type="number"
                min="1"
                placeholder="e.g., 14"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Number of days in sprint
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">
                Resource Budget (hours) <span className="text-red-500">*</span>
              </Label>
              <Input
                id="budget"
                type="number"
                min="1"
                placeholder="e.g., 160"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Total available hours for sprint
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="goal">
              Business Goal <span className="text-red-500">*</span>
            </Label>
            <Input
              id="goal"
              placeholder="e.g., Increase user retention by 20%"
              value={businessGoal}
              onChange={(e) => setBusinessGoal(e.target.value)}
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">
              The primary business objective guiding prioritization
            </p>
          </div>

          <div className="flex flex-col sm:flex-row justify-between gap-4 pt-4 border-t">
            <Button type="button" variant="secondary" onClick={onBack} disabled={isLoading}>
              ← Back to Results
            </Button>
            <Button
              type="submit"
              className="bg-gradient-to-r from-[#8458B3] to-[#9b6fc4] hover:from-[#9b6fc4] hover:to-[#8458B3] text-white"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Prioritizing...
                </>
              ) : (
                <>
                  🎯 Generate Prioritization
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
