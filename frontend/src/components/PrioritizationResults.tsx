'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { PrioritizationPlan } from '@/types/api';

interface PrioritizationResultsProps {
  plan: PrioritizationPlan;
  method: string;
  duration: number;
  budget: number;
  businessGoal: string;
  onStartOver: () => void;
}

export function PrioritizationResults({
  plan,
  method,
  duration,
  budget,
  businessGoal,
  onStartOver,
}: PrioritizationResultsProps) {
  const { prioritized_categories, summary } = plan;

  const getCategoryColor = (categoryName: string) => {
    const name = categoryName.toLowerCase();
    if (name.includes('must') || name.includes('high impact/low effort')) {
      return 'bg-red-100 text-red-800 border-red-200';
    }
    if (name.includes('should') || name.includes('high impact/high effort')) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
    if (name.includes('could') || name.includes('low impact')) {
      return 'bg-green-100 text-green-800 border-green-200';
    }
    if (name.includes('won\'t') || name.includes('wont')) {
      return 'bg-gray-100 text-gray-800 border-gray-200';
    }
    return 'bg-purple-100 text-purple-800 border-purple-200';
  };

  const getTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'bug': return '🐛';
      case 'feature': return '✨';
      case 'requirement': return '📋';
      case 'usability': return '🔧';
      case 'pain_point': return '😤';
      default: return '📌';
    }
  };

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          📈 Prioritization Results
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Configuration Summary */}
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-3">Configuration</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Method:</span>
              <div className="font-medium">{method}</div>
            </div>
            <div>
              <span className="text-gray-500">Sprint Duration:</span>
              <div className="font-medium">{duration} days</div>
            </div>
            <div>
              <span className="text-gray-500">Budget:</span>
              <div className="font-medium">{budget} hours</div>
            </div>
            <div>
              <span className="text-gray-500">Goal:</span>
              <div className="font-medium truncate" title={businessGoal}>
                {businessGoal}
              </div>
            </div>
          </div>
        </div>

        {/* Prioritized Categories */}
        {prioritized_categories && prioritized_categories.length > 0 ? (
          <div className="space-y-4">
            <h3 className="font-semibold">Prioritized Tasks</h3>
            
            {prioritized_categories.map((category, catIndex) => (
              <div key={catIndex} className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge className={getCategoryColor(category.category_name)}>
                    {category.category_name}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    ({category.tasks?.length || 0} items)
                  </span>
                </div>
                
                <div className="space-y-2 pl-4 border-l-2 border-purple-200">
                  {category.tasks?.map((task, taskIndex) => (
                    <div
                      key={taskIndex}
                      className="bg-white p-4 rounded-lg border hover:border-purple-300 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-medium text-gray-900">
                          {getTypeIcon(task.type)} {task.title}
                        </h4>
                        <div className="flex gap-2">
                          <Badge variant="outline">
                            {task.type}
                          </Badge>
                          <Badge variant="secondary">
                            {task.estimated_hours}h
                          </Badge>
                        </div>
                      </div>
                      {task.impact_reasoning && (
                        <p className="text-sm text-gray-600 mt-2">{task.impact_reasoning}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No prioritized tasks generated.</p>
            <p className="text-sm mt-2">
              The analysis may not have found enough data to generate priorities.
            </p>
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              🎯 Sprint Summary
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Total Estimated Hours:</span>
                <div className="font-bold text-lg">{summary.total_estimated_hours}h</div>
              </div>
              <div>
                <span className="text-gray-500">Budget Utilization:</span>
                <div className="font-bold text-lg">{summary.budget_utilization_percentage?.toFixed(1)}%</div>
              </div>
              <div>
                <span className="text-gray-500">Budget Available:</span>
                <div className="font-bold text-lg">{budget}h</div>
              </div>
            </div>
            {summary.key_risks && summary.key_risks.length > 0 && (
              <div className="mt-4">
                <span className="text-gray-500 text-sm">Key Risks:</span>
                <ul className="list-disc list-inside space-y-1 ml-2 text-sm text-gray-700">
                  {summary.key_risks.map((risk, i) => (
                    <li key={i}>{risk}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-center pt-4 border-t">
          <Button
            onClick={onStartOver}
            className="bg-gradient-to-r from-[#8458B3] to-[#9b6fc4] hover:from-[#9b6fc4] hover:to-[#8458B3] text-white"
          >
            🔄 Start New Analysis
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
