'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { TaskResult, Finding } from '@/types/api';

interface ResultsViewProps {
  result: TaskResult;
  onContinue: () => void;
  onBack: () => void;
}

interface StatCardProps {
  label: string;
  value: number;
  icon: string;
  colorClass: string;
}

function StatCard({ label, value, icon, colorClass }: StatCardProps) {
  return (
    <div className={`bg-gray-50 p-4 rounded-lg border-l-4 ${colorClass} transition-all hover:shadow-md hover:-translate-y-1`}>
      <div className="text-xs font-bold uppercase tracking-wide text-gray-600 mb-1">
        {icon} {label}
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
      <div className="text-xs text-gray-500">identified</div>
    </div>
  );
}

function FindingsList({ findings, type }: { findings: Finding[]; type: string }) {
  if (!findings || findings.length === 0) {
    return <p className="text-gray-500 italic">No {type} identified</p>;
  }

  return (
    <div className="space-y-3">
      {findings.slice(0, 10).map((finding, index) => (
        <div
          key={index}
          className="bg-white p-4 rounded-lg border border-gray-100 hover:border-purple-200 transition-colors"
        >
          <div className="flex items-start justify-between gap-2 mb-2">
            <h4 className="font-medium text-gray-900">{finding.title}</h4>
            {finding.severity && (
              <Badge variant={finding.severity === 'high' ? 'destructive' : 'secondary'}>
                {finding.severity}
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-600 mb-3">{finding.description}</p>
          {finding.sample_reviews && finding.sample_reviews.length > 0 && (
            <div className="bg-gray-50 p-3 rounded text-xs text-gray-500 italic">
              &ldquo;{finding.sample_reviews[0]}&rdquo;
            </div>
          )}
          <div className="flex flex-wrap gap-2 mt-3">
            {finding.frequency > 0 && (
              <Badge variant="outline" className="text-xs">
                Frequency: {finding.frequency}
              </Badge>
            )}
            {finding.sources?.map((source, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {source}
              </Badge>
            ))}
          </div>
        </div>
      ))}
      {findings.length > 10 && (
        <p className="text-sm text-gray-500 text-center py-2">
          And {findings.length - 10} more...
        </p>
      )}
    </div>
  );
}

export function ResultsView({ result, onContinue, onBack }: ResultsViewProps) {
  const { sentiment_analysis } = result;
  const counts = sentiment_analysis.summary_counts;

  const statCards: StatCardProps[] = [
    { label: 'Bugs', value: counts.bugs, icon: '🐛', colorClass: 'border-pink-500' },
    { label: 'Features', value: counts.features, icon: '✨', colorClass: 'border-indigo-500' },
    { label: 'Requirements', value: counts.requirements, icon: '📋', colorClass: 'border-violet-500' },
    { label: 'Usability', value: counts.usability, icon: '🔧', colorClass: 'border-orange-500' },
    { label: 'Pain Points', value: counts.pain_points, icon: '😤', colorClass: 'border-red-500' },
    { label: 'Positive', value: counts.positive, icon: '💚', colorClass: 'border-green-500' },
  ];

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          ✨ Analysis Results
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Sentiment */}
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-3">Overall Sentiment</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {sentiment_analysis.overall_sentiment.positive_percentage.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Positive</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">
                {sentiment_analysis.overall_sentiment.neutral_percentage.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Neutral</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {sentiment_analysis.overall_sentiment.negative_percentage.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Negative</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {sentiment_analysis.overall_sentiment.total_reviews_analyzed}
              </div>
              <div className="text-xs text-gray-500">Total Reviews</div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {statCards.map((card) => (
            <StatCard key={card.label} {...card} />
          ))}
        </div>

        {/* Key Insights */}
        {sentiment_analysis.key_insights && sentiment_analysis.key_insights.length > 0 && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              💡 Key Insights
            </h3>
            <ul className="space-y-2">
              {sentiment_analysis.key_insights.map((insight, i) => (
                <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Detailed Findings */}
        <Accordion type="multiple" className="space-y-2">
          <AccordionItem value="bugs" className="bg-pink-50 border-pink-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                🐛 Bugs ({counts.bugs})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.bugs} type="bugs" />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="features" className="bg-indigo-50 border-indigo-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                ✨ Feature Requests ({counts.features})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.feature_requests} type="feature requests" />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="requirements" className="bg-violet-50 border-violet-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                📋 Requirements ({counts.requirements})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.requirements} type="requirements" />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="usability" className="bg-orange-50 border-orange-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                🔧 Usability Issues ({counts.usability})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.usability_frictions} type="usability issues" />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="painpoints" className="bg-red-50 border-red-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                😤 Pain Points ({counts.pain_points})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.pain_points} type="pain points" />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="positive" className="bg-green-50 border-green-200 rounded-lg px-4">
            <AccordionTrigger className="hover:no-underline">
              <span className="flex items-center gap-2">
                💚 Positive Feedback ({counts.positive})
              </span>
            </AccordionTrigger>
            <AccordionContent>
              <FindingsList findings={sentiment_analysis.positive_reviews} type="positive feedback" />
            </AccordionContent>
          </AccordionItem>

          {sentiment_analysis.ai_insights && sentiment_analysis.ai_insights.length > 0 && (
            <AccordionItem value="ai" className="bg-purple-50 border-purple-200 rounded-lg px-4">
              <AccordionTrigger className="hover:no-underline">
                <span className="flex items-center gap-2">
                  🤖 AI Insights ({counts.ai_insights})
                </span>
              </AccordionTrigger>
              <AccordionContent>
                <FindingsList findings={sentiment_analysis.ai_insights} type="AI insights" />
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between gap-4 pt-4 border-t">
          <Button variant="secondary" onClick={onBack}>
            ← Back to Step 1
          </Button>
          <Button
            onClick={onContinue}
            className="bg-gradient-to-r from-[#8458B3] to-[#9b6fc4] hover:from-[#9b6fc4] hover:to-[#8458B3] text-white"
          >
            Continue to Prioritization →
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
