export interface Font {
  name: string;
  desc: string;
  category: string;
  tags?: string[];
  source?: string;
  files?: Record<string, string>;
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface SeedJob {
  id: string;
  font_name: string;
  source: string;
  source_payload: any;
  status: JobStatus;
  attempts: number;
  max_attempts: number;
  priority: number;
  last_error?: string;
  created_at: string;
  updated_at: string;
  claimed_at?: string;
  finished_at?: string;
}

export interface ChatMessage {
  role: "user" | "model";
  text: string;
}

export interface SearchResponse {
  reply: string;
  fonts: Font[];
}
