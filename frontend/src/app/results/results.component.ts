import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

interface AnalysisResult {
  results?: {
    overall_score?: number;
    rating?: string;
    strengths?: string[];
    recommendations?: string[];
    keyword_match?: {
      missing_keywords?: string[];
      matched_keywords?: string[];
    };
    skills_analysis?: {
      technical_skills?: string[];
      soft_skills?: string[];
      missing_skills?: string[];
    };
    experience_years?: number;
    summary?: string;
  };
}

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
  results = signal<AnalysisResult | null>(null);
  jobDescription = signal<string>('');

  ngOnInit(): void {
    const navigation = history.state;
    if (navigation.results) {
      this.results.set(navigation.results);
      this.jobDescription.set(navigation.jobDescription || '');
    } else {
      // If no results, redirect to home
      this.router.navigate(['/']);
    }
  }

  constructor(private router: Router) {}

  getScoreColor(score: number): string {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  }

  getScoreText(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  }

  goBack(): void {
    this.router.navigate(['/analyze']);
  }

  startNewAnalysis(): void {
    this.router.navigate(['/analyze']);
  }
}