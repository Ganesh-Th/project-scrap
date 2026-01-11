'use client';

import { useState, useCallback } from 'react';
import { Toaster, toast } from 'sonner';

import { Header } from '@/components/Header';
import { StepIndicator } from '@/components/StepIndicator';
import { AnalysisForm } from '@/components/AnalysisForm';
import { ProgressModal } from '@/components/ProgressModal';
import { ResultsView } from '@/components/ResultsView';
import { PrioritizationForm } from '@/components/PrioritizationForm';
import { PrioritizationResults } from '@/components/PrioritizationResults';

import { useTaskPolling } from '@/hooks/useTaskPolling';
import { startScrape, prioritize } from '@/lib/api';
import { ScrapeRequest, TaskResult, PrioritizationRequest, PrioritizationPlan } from '@/types/api';

type AppStep = 'form' | 'scraping' | 'results' | 'prioritizing' | 'prioritization-loading' | 'complete';

const STEPS = [
  { label: 'Data Collection', description: 'Gather & Analyze' },
  { label: 'Prioritization', description: 'Plan & Execute' },
];

export default function Home() {
  const [currentStep, setCurrentStep] = useState<AppStep>('form');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [scrapeResult, setScrapeResult] = useState<TaskResult | null>(null);
  const [prioritizationPlan, setPrioritizationPlan] = useState<PrioritizationPlan | null>(null);
  const [prioritizationConfig, setPrioritizationConfig] = useState<{
    method: string;
    duration: number;
    budget: number;
    businessGoal: string;
  } | null>(null);

  const getStepNumber = () => {
    switch (currentStep) {
      case 'form':
      case 'scraping':
        return 1;
      case 'results':
      case 'prioritizing':
      case 'prioritization-loading':
      case 'complete':
        return 2;
      default:
        return 1;
    }
  };

  const handleScrapeComplete = useCallback((result: TaskResult) => {
    setScrapeResult(result);
    setCurrentStep('results');
    toast.success('Analysis complete!', {
      description: `Analyzed ${result.sentiment_analysis.overall_sentiment.total_reviews_analyzed} reviews`,
    });
  }, []);

  const handleScrapeError = useCallback((error: string) => {
    setCurrentStep('form');
    toast.error('Analysis failed', {
      description: error,
    });
  }, []);

  const { progress, message, status, startPolling } = useTaskPolling({
    onComplete: handleScrapeComplete,
    onError: handleScrapeError,
  });

  const handleAnalyzeSubmit = async (data: ScrapeRequest) => {
    try {
      setCurrentStep('scraping');
      const response = await startScrape(data);
      setTaskId(response.task_id);
      startPolling(response.task_id);
    } catch (error) {
      setCurrentStep('form');
      toast.error('Failed to start analysis', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleContinueToPrioritization = () => {
    setCurrentStep('prioritizing');
  };

  const handleBackToForm = () => {
    setCurrentStep('form');
    setTaskId(null);
    setScrapeResult(null);
    setPrioritizationConfig(null);
  };

  const handleBackToResults = () => {
    setCurrentStep('results');
  };

  const handlePrioritizationSubmit = async (data: PrioritizationRequest) => {
    try {
      setCurrentStep('prioritization-loading');
      setPrioritizationConfig({
        method: data.method,
        duration: data.duration,
        budget: data.budget,
        businessGoal: data.business_goal,
      });

      const response = await prioritize(data);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      if (response.plan) {
        setPrioritizationPlan(response.plan);
        setCurrentStep('complete');
        toast.success('Prioritization complete!');
      } else {
        throw new Error('No prioritization plan returned');
      }
    } catch (error) {
      setCurrentStep('prioritizing');
      toast.error('Prioritization failed', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const handleStartOver = () => {
    setCurrentStep('form');
    setTaskId(null);
    setScrapeResult(null);
    setPrioritizationPlan(null);
    setPrioritizationConfig(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f5f2f9] via-[#ede7f5] to-[#faf8fc] p-4 md:p-8">
      <Toaster richColors position="top-right" />
      
      <div className="max-w-5xl mx-auto">
        <Header />
        
        <StepIndicator currentStep={getStepNumber()} steps={STEPS} />

        {/* Step 1: Analysis Form */}
        {currentStep === 'form' && (
          <AnalysisForm
            onSubmit={handleAnalyzeSubmit}
            isLoading={false}
          />
        )}

        {/* Scraping Progress */}
        <ProgressModal
          isOpen={currentStep === 'scraping'}
          progress={progress}
          message={message}
          status={status}
        />

        {/* Results View */}
        {currentStep === 'results' && scrapeResult && (
          <ResultsView
            result={scrapeResult}
            onContinue={handleContinueToPrioritization}
            onBack={handleBackToForm}
          />
        )}

        {/* Step 2: Prioritization Form */}
        {currentStep === 'prioritizing' && taskId && (
          <PrioritizationForm
            taskId={taskId}
            onSubmit={handlePrioritizationSubmit}
            onBack={handleBackToResults}
            isLoading={false}
          />
        )}

        {/* Prioritization Loading */}
        <ProgressModal
          isOpen={currentStep === 'prioritization-loading'}
          progress={50}
          message="Generating prioritization recommendations..."
          status="running"
        />

        {/* Prioritization Results */}
        {currentStep === 'complete' && prioritizationPlan && prioritizationConfig && (
          <PrioritizationResults
            plan={prioritizationPlan}
            method={prioritizationConfig.method}
            duration={prioritizationConfig.duration}
            budget={prioritizationConfig.budget}
            businessGoal={prioritizationConfig.businessGoal}
            onStartOver={handleStartOver}
          />
        )}
      </div>
    </div>
  );
}

