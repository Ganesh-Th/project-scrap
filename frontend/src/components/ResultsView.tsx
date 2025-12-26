'use client';

import { JobResults, Task } from '@/types';
import { useState } from 'react';
import { jobsApi } from '@/lib/api';
import { CheckCircle, XCircle, Edit, BarChart3 } from 'lucide-react';

interface ResultsViewProps {
  results: JobResults;
  onUpdate: () => void;
}

export default function ResultsView({ results, onUpdate }: ResultsViewProps) {
  const [editingTask, setEditingTask] = useState<number | null>(null);
  const [taskUpdates, setTaskUpdates] = useState<Partial<Task>>({});

  const handleEditTask = (task: Task) => {
    setEditingTask(task.id);
    setTaskUpdates({
      reach: task.reach,
      impact: task.impact,
      confidence: task.confidence,
      effort: task.effort,
    });
  };

  const handleSaveTask = async (taskId: number) => {
    try {
      await jobsApi.updateTask(taskId, taskUpdates);
      setEditingTask(null);
      onUpdate();
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };

  const handleConfirmTask = async (taskId: number, confirmed: number) => {
    try {
      await jobsApi.updateTask(taskId, { confirmed });
      onUpdate();
    } catch (err) {
      console.error('Failed to confirm task:', err);
    }
  };

  const sentimentStats = {
    positive: results.reviews.filter(r => r.sentiment === 'positive').length,
    negative: results.reviews.filter(r => r.sentiment === 'negative').length,
    neutral: results.reviews.filter(r => r.sentiment === 'neutral').length,
  };

  const avgRating = results.reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / results.reviews.length;

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{results.reviews.length}</div>
            <div className="text-sm text-gray-600">Total Reviews</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-500">{avgRating.toFixed(1)}</div>
            <div className="text-sm text-gray-600">Avg Rating</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-500">{sentimentStats.positive}</div>
            <div className="text-sm text-gray-600">Positive</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-500">{sentimentStats.negative}</div>
            <div className="text-sm text-gray-600">Negative</div>
          </div>
        </div>
      </div>

      {/* Themes and Tasks */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <BarChart3 size={24} />
          Themes & Prioritized Tasks
        </h3>
        <div className="space-y-4">
          {results.themes.map((theme) => (
            <div key={theme.id} className="border border-gray-200 rounded-lg p-4">
              <div className="mb-3">
                <h4 className="font-semibold text-lg">{theme.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{theme.description}</p>
                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                  <span>{theme.review_count} reviews</span>
                  <span>Sentiment: {theme.avg_sentiment.toFixed(2)}</span>
                </div>
              </div>

              {theme.tasks.map((task) => (
                <div key={task.id} className="bg-gray-50 rounded p-3 mt-2">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h5 className="font-medium">{task.title}</h5>
                      <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      {task.confirmed === 0 && (
                        <>
                          <button
                            onClick={() => handleConfirmTask(task.id, 1)}
                            className="p-1 text-green-600 hover:bg-green-100 rounded"
                            title="Confirm"
                          >
                            <CheckCircle size={20} />
                          </button>
                          <button
                            onClick={() => handleConfirmTask(task.id, -1)}
                            className="p-1 text-red-600 hover:bg-red-100 rounded"
                            title="Reject"
                          >
                            <XCircle size={20} />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleEditTask(task)}
                        className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                        title="Edit RICE"
                      >
                        <Edit size={20} />
                      </button>
                    </div>
                  </div>

                  {editingTask === task.id ? (
                    <div className="grid grid-cols-4 gap-2 mt-2">
                      <input
                        type="number"
                        placeholder="Reach"
                        className="input text-sm"
                        value={taskUpdates.reach || 0}
                        onChange={(e) => setTaskUpdates({ ...taskUpdates, reach: parseInt(e.target.value) })}
                      />
                      <input
                        type="number"
                        placeholder="Impact"
                        className="input text-sm"
                        value={taskUpdates.impact || 0}
                        onChange={(e) => setTaskUpdates({ ...taskUpdates, impact: parseInt(e.target.value) })}
                      />
                      <input
                        type="number"
                        placeholder="Confidence"
                        className="input text-sm"
                        value={taskUpdates.confidence || 0}
                        onChange={(e) => setTaskUpdates({ ...taskUpdates, confidence: parseInt(e.target.value) })}
                      />
                      <input
                        type="number"
                        placeholder="Effort"
                        className="input text-sm"
                        value={taskUpdates.effort || 1}
                        onChange={(e) => setTaskUpdates({ ...taskUpdates, effort: parseInt(e.target.value) })}
                      />
                      <button
                        onClick={() => handleSaveTask(task.id)}
                        className="btn btn-primary text-sm col-span-2"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingTask(null)}
                        className="btn btn-secondary text-sm col-span-2"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex gap-4 text-xs mt-2">
                      <span className="font-medium">RICE Score: {task.rice_score.toFixed(2)}</span>
                      <span>Reach: {task.reach}</span>
                      <span>Impact: {task.impact}</span>
                      <span>Confidence: {task.confidence}%</span>
                      <span>Effort: {task.effort}w</span>
                      {task.confirmed === 1 && (
                        <span className="text-green-600 font-medium">✓ Confirmed</span>
                      )}
                      {task.confirmed === -1 && (
                        <span className="text-red-600 font-medium">✗ Rejected</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Sample Reviews */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Sample Reviews</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {results.reviews.slice(0, 10).map((review) => (
            <div key={review.id} className="border-l-4 pl-3 py-2" style={{
              borderColor: review.sentiment === 'positive' ? '#22c55e' : review.sentiment === 'negative' ? '#ef4444' : '#6b7280'
            }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-sm">{review.author || 'Anonymous'}</span>
                <span className="text-yellow-500">{'★'.repeat(Math.round(review.rating || 0))}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-gray-100">
                  {review.sentiment}
                </span>
              </div>
              <p className="text-sm text-gray-700">{review.content}</p>
              <div className="flex gap-2 mt-1 text-xs text-gray-500">
                {review.is_bug > 0.3 && <span className="bg-red-100 px-2 py-0.5 rounded">Bug</span>}
                {review.is_feature > 0.3 && <span className="bg-blue-100 px-2 py-0.5 rounded">Feature</span>}
                {review.is_usability > 0.3 && <span className="bg-purple-100 px-2 py-0.5 rounded">Usability</span>}
                {review.is_praise > 0.3 && <span className="bg-green-100 px-2 py-0.5 rounded">Praise</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
