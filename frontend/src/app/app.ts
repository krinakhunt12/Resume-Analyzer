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

  // UI State Signals
  isDarkMode = signal<boolean>(false);
  isSticky = signal<boolean>(false);
  showJd = signal<boolean>(false);
  currentStep = signal<number>(1); // 1: Upload, 2: Scan, 3: Insights

  // Temporary inputs for ngModel
  tempJdText = '';
  tempChatInput = '';

  // Advanced features
  coverLetter = signal<string>('');
  isGeneratingLetter = signal<boolean>(false);

  // Phase 4 Signals
  isChatOpen = signal<boolean>(false);
  chatMessages = signal<any[]>([
    { role: 'assistant', text: 'Hello! I am your AI Career Assistant. How can I help you optimize your resume today?' }
  ]);
  isPdfLoading = signal<boolean>(false);

  linkedInUrl = signal<string>('');
  linkedInResult = signal<any>(null);

  constructor(private atsService: AtsService) {
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      this.toggleTheme();
    }

    // Scroll listener for sticky header
    window.addEventListener('scroll', () => {
      this.isSticky.set(window.scrollY > 150);
    });
  }

  toggleTheme() {
    this.isDarkMode.update(d => !d);
    if (this.isDarkMode()) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }

  toggleChat() {
    this.isChatOpen.update(v => !v);
  }

  sendMessage() {
    const msg = this.tempChatInput.trim();
    if (!msg) return;

    // Add user message
    this.chatMessages.update(msgs => [...msgs, { role: 'user', text: msg }]);
    const currentMsg = msg; // capture for API call
    this.tempChatInput = '';

    // Call API with context
    const context = {
      score: this.results()?.overall_score,
      missing: this.results()?.keyword_match?.missing_keywords || []
    };

    this.atsService.chatWithAI(currentMsg, context).subscribe({
      next: (res: any) => {
        this.chatMessages.update(msgs => [...msgs, { role: 'assistant', text: res.response }]);
      },
      error: () => {
        this.chatMessages.update(msgs => [...msgs, { role: 'assistant', text: 'Sorry, I am having trouble connecting to the AI. Please try again.' }]);
      }
    });
  }

  downloadReport() {
    if (!this.results()) return;
    this.isPdfLoading.set(true);

    this.atsService.generateAtsPdf({ results: this.results() }).subscribe({
      next: (res: any) => {
        if (res.success && res.download_url) {
          window.open(res.download_url, '_blank');
        }
        this.isPdfLoading.set(false);
      },
      error: (err) => {
        alert('Failed to generate PDF report.');
        this.isPdfLoading.set(false);
      }
    });
  }

  analyzeLinkedIn() {
    const txt = this.linkedInUrl();
    if (!txt) return;

    this.atsService.analyzeLinkedIn(txt).subscribe({
      next: (res: any) => {
        if (res.success) {
          this.linkedInResult.set(res.insights);
        }
      }
    });
  }

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
    this.currentStep.set(2); // Move to "Scan" step interaction
    this.results.set(null);
    this.recruiterInsights.set(null);
    this.errorMsg.set('');
    this.coverLetter.set('');

    const formData = new FormData();
    formData.append('resume', this.resumeFile()!);

    if (this.jdFile()) {
      formData.append('job_description', this.jdFile()!);
    }

    if (this.tempJdText) {
      formData.append('job_description_text', this.tempJdText);
    }

    this.atsService.analyzeResume(formData).subscribe({
      next: (data: any) => {
        this.results.set(data.results);
        this.recruiterInsights.set(data.recruiter_insights);
        this.reports.set(data.reports);
        this.isLoading.set(false);
        this.currentStep.set(3); // Result Step
        setTimeout(() => {
          document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      },
      error: (err: any) => {
        this.errorMsg.set(err.error?.error || 'An error occurred during analysis.');
        this.isLoading.set(false);
        this.currentStep.set(1); // Reset
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
    if (r.includes('excellent')) return 'tag-excellent';
    if (r.includes('good')) return 'tag-success';
    if (r.includes('fair')) return 'tag-warning';
    return 'tag-danger';
  }

  getSkillLevel(count: number): number {
    if (count > 8) return 4;
    if (count > 5) return 3;
    if (count > 2) return 2;
    return 1;
  }

  getSortedTimeline(): any[] {
    const timeline = this.recruiterInsights()?.timeline?.events || [];
    return timeline.sort((a: any, b: any) => parseInt(b.year) - parseInt(a.year));
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
