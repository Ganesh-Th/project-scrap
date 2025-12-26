export interface Job {
  id: number;
  app_name: string;
  app_id: string;
  state: 'queued' | 'fetching' | 'analyzing' | 'clustering' | 'done' | 'failed';
  created_at: string;
  updated_at: string;
  error_message?: string;
}

export interface Review {
  id: number;
  author?: string;
  rating?: number;
  content?: string;
  date?: string;
  sentiment?: string;
  sentiment_score?: number;
  is_bug: number;
  is_feature: number;
  is_usability: number;
  is_requirement: number;
  is_praise: number;
  cluster_id?: number;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  reach: number;
  impact: number;
  confidence: number;
  effort: number;
  rice_score: number;
  confirmed: number;
}

export interface Theme {
  id: number;
  cluster_id: number;
  title: string;
  description: string;
  review_count: number;
  avg_sentiment: number;
  tasks: Task[];
}

export interface JobResults {
  job: Job;
  reviews: Review[];
  themes: Theme[];
}
