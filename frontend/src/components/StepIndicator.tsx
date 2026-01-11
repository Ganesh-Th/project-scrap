'use client';

import { cn } from '@/lib/utils';

interface StepIndicatorProps {
  currentStep: number;
  steps: { label: string; description: string }[];
}

export function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  return (
    <div className="bg-white rounded-full shadow-lg p-6 mb-8">
      <div className="relative flex items-center justify-center gap-20">
        {/* Connection line */}
        <div className="absolute top-1/2 left-[18%] right-[18%] h-1 -translate-y-1/2 bg-gradient-to-r from-gray-200 via-purple-300 to-gray-200 rounded-full hidden md:block" />

        {steps.map((step, index) => {
          const stepNumber = index + 1;
          const isActive = currentStep === stepNumber;
          const isCompleted = currentStep > stepNumber;

          return (
            <div key={stepNumber} className="relative z-10 text-center">
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center font-semibold text-lg mx-auto mb-2 transition-all duration-300',
                  isActive && 'bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-lg shadow-purple-400/50',
                  isCompleted && 'bg-green-50 border-2 border-green-500 text-green-600',
                  !isActive && !isCompleted && 'bg-gray-100 text-gray-500'
                )}
              >
                {isCompleted ? '✓' : stepNumber}
              </div>
              <div
                className={cn(
                  'text-sm font-semibold',
                  isActive ? 'text-indigo-600' : 'text-gray-900'
                )}
              >
                {step.label}
              </div>
              <div className="text-xs text-gray-500">{step.description}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
