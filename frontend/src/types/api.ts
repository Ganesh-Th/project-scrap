// Request Types
export interface GooglePlayParams {
  product_id: string;
  platform: 'phone' | 'tablet' | 'chromebook';
}

export interface AppleStoreParams {
  product_id: string;
  country: string;
  target_reviews?: number;
}

export interface RedditParams {
  keyword: string;
  limit_pages?: number;
}

export interface GoogleSearchParams {
  product_name: string;
}

export interface ScrapeRequest {
  product_name: string;
  google_play?: GooglePlayParams;
  apple_store?: AppleStoreParams;
  reddit?: RedditParams;
  google_search?: GoogleSearchParams;
  include_reddit?: boolean;
  include_google_search?: boolean;
}

export interface PrioritizationRequest {
  task_id: string;
  method: 'MoSCoW' | 'Lean';
  duration: number;
  budget: number;
  business_goal: string;
}

// Response Types
export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
  websocket_url: string;
}

export interface OverallSentiment {
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
  average_rating: number;
  total_reviews_analyzed: number;
}

export interface SummaryCounts {
  bugs: number;
  features: number;
  requirements: number;
  usability: number;
  pain_points: number;
  positive: number;
  ai_insights: number;
}

export interface Finding {
  type: string;
  category: string;
  title: string;
  description: string;
  frequency: number;
  severity: string;
  sample_reviews: string[];
  recommendation: string;
  priority_score: number;
  sources: string[];
}

export interface PriorityAction {
  action: string;
  priority: string;
  impact: string;
  effort: string;
  rationale: string;
}

export interface SentimentAnalysis {
  overall_sentiment: OverallSentiment;
  summary_counts: SummaryCounts;
  bugs: Finding[];
  feature_requests: Finding[];
  requirements: Finding[];
  usability_frictions: Finding[];
  pain_points: Finding[];
  positive_reviews: Finding[];
  ai_insights: Finding[];
  priority_actions: PriorityAction[];
  key_insights: string[];
}

export interface TaskResult {
  task_id: string;
  status: string;
  created_at: string;
  completed_at: string;
  sources: string[];
  sentiment_analysis: SentimentAnalysis;
  data_summary: Record<string, unknown>;
  processing_mode: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: TaskResult;
  error?: string;
}

export interface ProgressUpdate {
  task_id: string;
  status: string;
  progress: number;
  total: number;
  message: string;
  timestamp: string;
}

// Prioritization Response (matching backend PrioritizationPlan)
export interface PrioritizationPlanMetadata {
  method: string;
  goal: string;
  budget_hours: number;
  sprint_duration_days: number;
}

export interface PrioritizedTask {
  title: string;
  type: string;
  impact_reasoning: string;
  estimated_hours: number;
}

export interface PrioritizedCategory {
  category_name: string;
  tasks: PrioritizedTask[];
}

export interface PrioritizationSummary {
  total_estimated_hours: number;
  budget_utilization_percentage: number;
  key_risks: string[];
}

export interface PrioritizationPlan {
  plan_metadata: PrioritizationPlanMetadata;
  prioritized_categories: PrioritizedCategory[];
  summary: PrioritizationSummary;
}

export interface PrioritizationResponse {
  task_id: string;
  plan?: PrioritizationPlan;
  error?: string;
}

// Legacy types kept for compatibility
export interface PrioritizedItem {
  title: string;
  type: string;
  category: string;
  priority: string;
  effort_hours: number;
  impact_score: number;
  recommendation: string;
  sprint_assignment?: string;
}

export interface PrioritizationResult {
  method: string;
  items: PrioritizedItem[];
  sprint_plan: {
    sprint_name: string;
    items: PrioritizedItem[];
    total_hours: number;
  }[];
  summary: {
    total_items: number;
    must_have: number;
    should_have: number;
    could_have: number;
    wont_have: number;
  };
}

// Country options for the form
export interface CountryOption {
  code: string;
  name: string;
}

export const COUNTRIES: CountryOption[] = [
  { code: 'us', name: 'United States' },
  { code: 'gb', name: 'United Kingdom' },
  { code: 'ca', name: 'Canada' },
  { code: 'au', name: 'Australia' },
  { code: 'de', name: 'Germany' },
  { code: 'fr', name: 'France' },
  { code: 'es', name: 'Spain' },
  { code: 'it', name: 'Italy' },
  { code: 'jp', name: 'Japan' },
  { code: 'kr', name: 'South Korea' },
  { code: 'cn', name: 'China' },
  { code: 'in', name: 'India' },
  { code: 'br', name: 'Brazil' },
  { code: 'mx', name: 'Mexico' },
  { code: 'nl', name: 'Netherlands' },
  { code: 'se', name: 'Sweden' },
  { code: 'no', name: 'Norway' },
  { code: 'dk', name: 'Denmark' },
  { code: 'fi', name: 'Finland' },
  { code: 'pl', name: 'Poland' },
  { code: 'ru', name: 'Russia' },
  { code: 'tr', name: 'Turkey' },
  { code: 'sa', name: 'Saudi Arabia' },
  { code: 'ae', name: 'United Arab Emirates' },
  { code: 'sg', name: 'Singapore' },
  { code: 'hk', name: 'Hong Kong' },
  { code: 'tw', name: 'Taiwan' },
  { code: 'th', name: 'Thailand' },
  { code: 'id', name: 'Indonesia' },
  { code: 'my', name: 'Malaysia' },
  { code: 'ph', name: 'Philippines' },
  { code: 'vn', name: 'Vietnam' },
  { code: 'za', name: 'South Africa' },
  { code: 'eg', name: 'Egypt' },
  { code: 'ng', name: 'Nigeria' },
  { code: 'ar', name: 'Argentina' },
  { code: 'cl', name: 'Chile' },
  { code: 'co', name: 'Colombia' },
  { code: 'pe', name: 'Peru' },
  { code: 'nz', name: 'New Zealand' },
];

export const PLATFORMS = [
  { value: 'phone', label: '📱 Phone' },
  { value: 'tablet', label: '📑 Tablet' },
  { value: 'chromebook', label: '💻 Chromebook' },
] as const;

export const PRIORITIZATION_METHODS = [
  { value: 'MoSCoW', label: '🎯 MoSCoW (Must, Should, Could, Won\'t)' },
  { value: 'Lean', label: '📊 Lean Prioritization (Impact vs Effort)' },
] as const;
