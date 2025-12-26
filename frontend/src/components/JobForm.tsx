'use client';

import { useState } from 'react';
import { jobsApi } from '@/lib/api';
import { PlusCircle } from 'lucide-react';

interface JobFormProps {
  onJobCreated: () => void;
}

export default function JobForm({ onJobCreated }: JobFormProps) {
  const [appName, setAppName] = useState('');
  const [appId, setAppId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await jobsApi.createJob(appName, appId);
      setAppName('');
      setAppId('');
      onJobCreated();
    } catch (err) {
      setError('Failed to create job. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Analyze App Reviews</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="app-name">
            App Name
          </label>
          <input
            id="app-name"
            type="text"
            className="input"
            value={appName}
            onChange={(e) => setAppName(e.target.value)}
            placeholder="e.g., My Awesome App"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="app-id">
            App ID / Package Name
          </label>
          <input
            id="app-id"
            type="text"
            className="input"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            placeholder="e.g., com.example.app"
            required
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">{error}</div>
        )}

        <button
          type="submit"
          className="btn btn-primary w-full flex items-center justify-center gap-2"
          disabled={loading}
        >
          <PlusCircle size={20} />
          {loading ? 'Creating Job...' : 'Start Analysis'}
        </button>
      </form>
    </div>
  );
}
