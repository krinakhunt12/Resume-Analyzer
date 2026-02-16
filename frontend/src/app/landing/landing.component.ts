import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpEventType, HttpClientModule } from '@angular/common/http';
import { HeroComponent } from './hero/hero.component';
import { FeaturesComponent } from './features/features.component';
import { HowItWorksComponent } from './how-it-works/how-it-works.component';
import { SocialProofComponent } from './social-proof/social-proof.component';
import { CtaComponent } from './cta/cta.component';
import { FooterComponent } from './footer/footer.component';
import { ToastService } from '../services/toast.service';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    HeroComponent,
    FeaturesComponent,
    HowItWorksComponent,
    SocialProofComponent,
    CtaComponent,
    FooterComponent
  ],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent {
  showUploader: boolean = false;
  resumeFile: File | null = null;
  jdFile: File | null = null;
  loading = false;
  progress = 0;
  result: any = null;
  error: string | null = null;

  constructor(private http: HttpClient, private toastService: ToastService) {}

  scrollToSection(sectionId: string) {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  startAnalysis() {
    this.showUploader = true;
    setTimeout(() => this.scrollToSection('uploader'), 100);
  }

  onResumeSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.resumeFile = input.files && input.files.length ? input.files[0] : null;
  }

  onJDSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.jdFile = input.files && input.files.length ? input.files[0] : null;
  }

  uploadAnalyze() {
    this.error = null;

    // Check if resume is selected
    if (!this.resumeFile) {
      this.toastService.warning('Resume Required', 'Please upload your resume before starting the analysis.');
      return;
    }

    // Check file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(this.resumeFile.type)) {
      this.toastService.error('Unsupported File Type', 'Only PDF and DOCX files are supported.');
      return;
    }

    // Check file size (5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (this.resumeFile.size > maxSize) {
      this.toastService.warning('File Too Large', 'Please upload a file smaller than 5MB.');
      return;
    }

    const form = new FormData();
    form.append('resume', this.resumeFile, this.resumeFile.name);

    if (this.jdFile) {
      form.append('job_description', this.jdFile, this.jdFile.name);
    }

    this.loading = true;
    this.progress = 0;

    this.http.post('http://localhost:5000/analyze', form, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (evt: any) => {
        if (evt.type === HttpEventType.UploadProgress && evt.total) {
          this.progress = Math.round(100 * (evt.loaded / evt.total));
        } else if (evt.type === HttpEventType.Response) {
          this.result = evt.body;
          this.loading = false;
          this.progress = 100;
          this.toastService.success('Resume Uploaded', 'Your resume has been uploaded successfully.');
        }
      },
      error: (err) => {
        this.error = err?.error?.error || err.message || 'Upload failed';
        this.loading = false;
        this.toastService.error('Analysis Failed', 'Something went wrong while analyzing your resume. Please try again.');
      }
    });
  }

  viewFullReport() {
    // For now, just log or open a modal
    console.log('Full report:', this.result);
    alert('Full report feature coming soon!');
  }

  getScoreItems() {
    const scores = this.result?.results?.scores || {};
    const labels: { [key: string]: string } = {
      'keyword_match': 'Keyword Match',
      'skills_match': 'Skills Match',
      'format_ats_friendly': 'ATS Format',
      'impact_score': 'Impact Score',
      'completeness': 'Completeness',
      'experience_relevance': 'Experience',
      'education': 'Education'
    };

    return Object.keys(scores).map(key => ({
      label: labels[key] || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: scores[key]
    }));
  }

  getScoreStyle(score: number) {
    return {
      '--score': score / 100
    };
  }
}