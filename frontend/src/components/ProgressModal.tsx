'use client';

import { Progress } from '@/components/ui/progress';

interface ProgressModalProps {
  isOpen: boolean;
  progress: number;
  message: string;
  status: string | null;
}

export function ProgressModal({ isOpen, progress, message, status }: ProgressModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-in fade-in zoom-in duration-300">
        <div className="text-center">
          {/* Animated spinner */}
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full border-4 border-purple-100" />
            <div 
              className="absolute inset-0 rounded-full border-4 border-transparent border-t-[#8458B3] animate-spin"
              style={{ animationDuration: '1s' }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">🔍</span>
            </div>
          </div>

          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {status === 'running' ? 'Analyzing Reviews' : 'Initializing...'}
          </h3>
          
          <p className="text-gray-600 mb-6 min-h-[3rem]">
            {message || 'Please wait while we gather and analyze reviews...'}
          </p>

          {/* Progress bar */}
          <div className="space-y-2">
            <Progress value={progress} className="h-3" />
            <p className="text-sm text-gray-500">
              {progress}% complete
            </p>
          </div>

          <div className="mt-6 flex items-center justify-center gap-2 text-xs text-gray-400">
            <span className="animate-pulse">●</span>
            <span>This may take a few minutes depending on the number of reviews</span>
          </div>
        </div>
      </div>
    </div>
  );
}
