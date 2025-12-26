'use client';

import { useState, useEffect } from 'react';
import { jobsApi } from '@/lib/api';
import { Job, JobResults } from '@/types';
import JobForm from '@/components/JobForm';
import JobList from '@/components/JobList';
import ResultsView from '@/components/ResultsView';
import { Loader, AlertCircle } from 'lucide-react';

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | undefined>();
  const [jobResults, setJobResults] = useState<JobResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadJobs = async () => {
    try {
      const jobsList = await jobsApi.listJobs();
      setJobs(jobsList);
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError('Failed to load jobs. Please check if the backend is running.');
    }
  };

  const loadJobResults = async (jobId: number) => {
    setLoading(true);
    setError('');
    try {
      const results = await jobsApi.getJobResults(jobId);
      setJobResults(results);
    } catch (err) {
      console.error('Failed to load job results:', err);
      setError('Failed to load job results.');
    } finally {
      setLoading(false);
    }
  };

  const handleJobCreated = () => {
    loadJobs();
  };

  const handleSelectJob = (jobId: number) => {
    setSelectedJobId(jobId);
    loadJobResults(jobId);
  };

  const handleUpdate = () => {
    if (selectedJobId) {
      loadJobResults(selectedJobId);
    }
  };

  useEffect(() => {
    loadJobs();
    // Poll for updates every 5 seconds
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-refresh results if job is not done
  useEffect(() => {
    if (selectedJobId && jobResults) {
      const job = jobs.find(j => j.id === selectedJobId);
      if (job && job.state !== 'done' && job.state !== 'failed') {
        const interval = setInterval(() => {
          loadJobResults(selectedJobId);
        }, 3000);
        return () => clearInterval(interval);
      }
    }
  }, [selectedJobId, jobResults, jobs]);

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">AI Review Intelligence System</h1>
          <p className="text-gray-600">
            Analyze app reviews with AI-powered sentiment analysis, classification, and task prioritization
          </p>
        </header>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <JobForm onJobCreated={handleJobCreated} />
            <JobList 
              jobs={jobs} 
              onSelectJob={handleSelectJob} 
              selectedJobId={selectedJobId}
            />
          </div>

          <div className="lg:col-span-2">
            {loading && (
              <div className="card flex items-center justify-center py-12">
                <Loader className="animate-spin text-primary" size={48} />
              </div>
            )}

            {!loading && jobResults && jobResults.job.state === 'done' && (
              <ResultsView results={jobResults} onUpdate={handleUpdate} />
            )}

            {!loading && jobResults && jobResults.job.state !== 'done' && (
              <div className="card text-center py-12">
                <Loader className="animate-spin text-primary mx-auto mb-4" size={48} />
                <h3 className="text-xl font-semibold mb-2">Processing Reviews</h3>
                <p className="text-gray-600">
                  Current state: <span className="font-medium">{jobResults.job.state}</span>
                </p>
                <p className="text-sm text-gray-500 mt-2">This may take a few moments...</p>
              </div>
            )}

            {!loading && !jobResults && selectedJobId && (
              <div className="card text-center py-12">
                <Loader className="animate-spin text-primary mx-auto mb-4" size={48} />
              </div>
            )}

            {!loading && !jobResults && !selectedJobId && (
              <div className="card text-center py-12 text-gray-500">
                <p>Select a job from the list to view results</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
