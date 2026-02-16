export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface AnalysisResult {
  results: {
    overall_score: number;
    rating: string;
    strengths: string[];
    recommendations: string[];
    keyword_match?: {
      missing_keywords: string[];
      matched_keywords: string[];
      match_percentage?: number;
    };
    skills_analysis?: {
      technical_skills: string[];
      soft_skills: string[];
      missing_skills: string[];
    };
    experience_years?: number;
    summary?: string;
    ats_score?: number;
    completeness_score?: number;
    impact_score?: number;
  };
  parsed_resume?: {
    contact_info?: {
      name?: string;
      email?: string;
      phone?: string;
    };
    education?: any[];
    experience?: any[];
  };
  report_text?: string;
  recruiter_insights?: any;
}

export interface ApiError {
  error: string;
  message?: string;
  details?: string;
}

export enum LoadingState {
  IDLE = 'idle',
  LOADING = 'loading',
  SUCCESS = 'success',
  ERROR = 'error'
}