import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AnalysisResult } from '../models/api.interfaces';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
  results = signal<AnalysisResult | null>(null);
  jobDescription = signal<string | null>(null);
  isLoading = signal<boolean>(true);

  constructor(private router: Router) {}

  ngOnInit(): void {
    const navigation = history.state;
    
    if (navigation.results) {
      this.results.set(navigation.results);
      this.jobDescription.set(navigation.jobDescription || null);
      this.isLoading.set(false);
    } else {
      // If no results, redirect to upload page
      this.router.navigate(['/analyze']);
      return;
    }
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  }

  getScoreGradient(score: number): string {
    const color = this.getScoreColor(score);
    return `conic-gradient(${color} ${score * 3.6}deg, #e5e7eb 0deg)`;
  }

  getScoreText(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Work';
  }

  getMatchPercentage(): number | null {
    const results = this.results();
    if (!results?.results?.keyword_match) return null;
    
    const matched = results.results.keyword_match.matched_keywords?.length || 0;
    const total = matched + (results.results.keyword_match.missing_keywords?.length || 0);
    
    return total > 0 ? Math.round((matched / total) * 100) : null;
  }

  formatExperienceYears(years: number | string | undefined): string {
    if (!years) return 'Not specified';
    if (typeof years === 'string') return years;
    return years === 1 ? '1 year' : `${years} years`;
  }

  goBack(): void {
    this.router.navigate(['/analyze']);
  }

  startNewAnalysis(): void {
    this.router.navigate(['/analyze']);
  }

  hasJobDescription(): boolean {
    return !!this.jobDescription();
  }

  // Helper methods for checking data availability
  hasStrengths(): boolean {
    return !!(this.results()?.results?.strengths?.length);
  }

  hasSkillsAnalysis(): boolean {
    const skills = this.results()?.results?.skills_analysis;
    return !!(skills?.technical_skills?.length || skills?.soft_skills?.length || skills?.missing_skills?.length);
  }

  hasKeywordMatch(): boolean {
    const match = this.results()?.results?.keyword_match;
    return !!(match?.matched_keywords?.length || match?.missing_keywords?.length);
  }

  hasRecommendations(): boolean {
    return !!(this.results()?.results?.recommendations?.length);
  }
}