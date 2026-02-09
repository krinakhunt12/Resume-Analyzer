import { Component, signal, WritableSignal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AtsService } from './services/ats.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = 'ATS Resume Analyzer Pro';

  // Form signals
  resumeFile = signal<File | null>(null);
  resumeFileName = signal<string>('');
  jdFile = signal<File | null>(null);
  jdText = signal<string>('');

  // State signals
  isLoading = signal<boolean>(false);
  errorMsg = signal<string>('');
  results = signal<any>(null);
  recruiterInsights = signal<any>(null);
  reports = signal<any>(null);

  // Advanced features
  coverLetter = signal<string>('');
  isGeneratingLetter = signal<boolean>(false);

  constructor(private atsService: AtsService) { }

  onFileChange(event: any, type: 'resume' | 'jd') {
    const file = event.target.files[0];
    if (file) {
      if (type === 'resume') {
        this.resumeFile.set(file);
        this.resumeFileName.set(file.name);
      } else {
        this.jdFile.set(file);
      }
    }
  }

  onSubmit(event: Event) {
    event.preventDefault();

    if (!this.resumeFile()) {
      this.errorMsg.set('Please select a resume file.');
      return;
    }

    this.isLoading.set(true);
    this.results.set(null);
    this.recruiterInsights.set(null);
    this.errorMsg.set('');
    this.coverLetter.set('');

    const formData = new FormData();
    formData.append('resume', this.resumeFile()!);

    if (this.jdFile()) {
      formData.append('job_description', this.jdFile()!);
    }

    if (this.jdText()) {
      formData.append('job_description_text', this.jdText());
    }

    this.atsService.analyzeResume(formData).subscribe({
      next: (data: any) => {
        this.results.set(data.results);
        this.recruiterInsights.set(data.recruiter_insights);
        this.reports.set(data.reports);
        this.isLoading.set(false);
        setTimeout(() => {
          document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      },
      error: (err: any) => {
        this.errorMsg.set(err.error?.error || 'An error occurred during analysis.');
        this.isLoading.set(false);
      }
    });
  }

  onGenerateLetter() {
    if (!this.results()) return;
    this.isGeneratingLetter.set(true);
    const data = {
      name: this.results().candidate_name,
      skills: this.results().skills,
      job_description: this.jdText()
    };
    this.atsService.generateCoverLetter(data).subscribe({
      next: (res: any) => {
        this.coverLetter.set(res.cover_letter);
        this.isGeneratingLetter.set(false);
      },
      error: () => this.isGeneratingLetter.set(false)
    });
  }

  getRatingClass(rating: string): string {
    if (!rating) return '';
    const r = rating.toLowerCase();
    if (r.includes('excellent')) return 'badge-excellent';
    if (r.includes('good')) return 'badge-good';
    return 'badge-fair';
  }

  getDownloadUrl(filename: string): string {
    return this.atsService.getDownloadUrl(filename);
  }

  getScoreKeys(scores: any): string[] {
    const order = [
      'keyword_match', 'skills_match', 'impact_score',
      'experience_relevance', 'education', 'format_ats_friendly', 'completeness'
    ];
    return order.filter(key => scores[key] !== undefined);
  }

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
