'use client';

import { Job } from '@/types';
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

interface JobListProps {
  jobs: Job[];
  onSelectJob: (jobId: number) => void;
  selectedJobId?: number;
}

export default function JobList({ jobs, onSelectJob, selectedJobId }: JobListProps) {
  const getStateIcon = (state: Job['state']) => {
    switch (state) {
      case 'done':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'failed':
        return <XCircle className="text-red-500" size={20} />;
      case 'queued':
      case 'fetching':
      case 'analyzing':
      case 'clustering':
        return <Loader className="text-blue-500 animate-spin" size={20} />;
      default:
        return <Clock className="text-gray-400" size={20} />;
    }
  };

  const getStateLabel = (state: Job['state']) => {
    return state.charAt(0).toUpperCase() + state.slice(1);
  };

  const getStateColor = (state: Job['state']) => {
    switch (state) {
      case 'done':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  if (jobs.length === 0) {
    return (
      <div className="card text-center text-gray-500">
        <p>No jobs yet. Create your first analysis above!</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Analysis Jobs</h2>
      <div className="space-y-2">
        {jobs.map((job) => (
          <div
            key={job.id}
            onClick={() => onSelectJob(job.id)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedJobId === job.id
                ? 'border-primary bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  {getStateIcon(job.state)}
                  <h3 className="font-semibold">{job.app_name}</h3>
                </div>
                <p className="text-sm text-gray-600">{job.app_id}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(job.created_at).toLocaleString()}
                </p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStateColor(job.state)}`}>
                {getStateLabel(job.state)}
              </span>
            </div>
            {job.error_message && (
              <p className="text-sm text-red-600 mt-2">{job.error_message}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
