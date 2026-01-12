'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { getTaskStatus } from '@/lib/api';
import { TaskStatusResponse, TaskResult } from '@/types/api';

interface UseTaskPollingOptions {
  pollInterval?: number; // in milliseconds
  onComplete?: (result: TaskResult) => void;
  onError?: (error: string) => void;
}

interface UseTaskPollingReturn {
  status: TaskStatusResponse['status'] | null;
  progress: number;
  message: string;
  result: TaskResult | null;
  error: string | null;
  isPolling: boolean;
  startPolling: (taskId: string) => void;
  stopPolling: () => void;
}

export function useTaskPolling(options: UseTaskPollingOptions = {}): UseTaskPollingReturn {
  const { pollInterval = 2000, onComplete, onError } = options;

  const [status, setStatus] = useState<TaskStatusResponse['status'] | null>(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<TaskResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const taskIdRef = useRef<string | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const poll = useCallback(async () => {
    if (!taskIdRef.current) return;

    try {
      const response = await getTaskStatus(taskIdRef.current);
      
      setStatus(response.status);
      setProgress(response.progress);
      setMessage(response.message);

      if (response.status === 'completed' && response.result) {
        setResult(response.result);
        stopPolling();
        onComplete?.(response.result);
      } else if (response.status === 'failed') {
        const errorMsg = response.error || 'Task failed';
        setError(errorMsg);
        stopPolling();
        onError?.(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get task status';
      setError(errorMsg);
      stopPolling();
      onError?.(errorMsg);
    }
  }, [stopPolling, onComplete, onError]);

  const startPolling = useCallback((taskId: string) => {
    // Reset state
    setStatus('pending');
    setProgress(0);
    setMessage('Starting...');
    setResult(null);
    setError(null);
    setIsPolling(true);
    
    taskIdRef.current = taskId;

    // Initial poll immediately
    poll();

    // Set up interval polling
    intervalRef.current = setInterval(poll, pollInterval);
  }, [poll, pollInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    status,
    progress,
    message,
    result,
    error,
    isPolling,
    startPolling,
    stopPolling,
  };
}
