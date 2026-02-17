import { Component } from '@angular/core';
import { HttpClient, HttpEventType, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent {
  resumeFile: File | null = null;
  jdFile: File | null = null;
  jdText: string = '';
  loading = false;
  progress = 0;
  result: any = null;
  error: string | null = null;
  showUploader: boolean = false;

  constructor(private http: HttpClient) {}

  onResumeSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.resumeFile = input.files && input.files.length ? input.files[0] : null;
  }

  startAnalysis() {
    this.showUploader = true;
    setTimeout(() => this.scrollToUploader(), 120);
  }

  scrollToSection(event: Event, id: string) {
    event.preventDefault();
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  private scrollToUploader() {
    const el = document.getElementById('uploader');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  onJDSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.jdFile = input.files && input.files.length ? input.files[0] : null;
  }

  clear() {
    this.resumeFile = null;
    this.jdFile = null;
    this.jdText = '';
    this.result = null;
    this.error = null;
    this.progress = 0;
  }

  uploadAnalyze() {
    this.error = null;
    if (!this.resumeFile) {
      this.error = 'Please select a resume file to upload.';
      return;
    }

    const form = new FormData();
    form.append('resume', this.resumeFile, this.resumeFile.name);

    if (this.jdFile) {
      form.append('job_description', this.jdFile, this.jdFile.name);
    } else if (this.jdText && this.jdText.trim().length > 0) {
      form.append('job_description_text', this.jdText.trim());
    }

    this.loading = true;
    this.progress = 0;

    this.http.post('/analyze', form, {
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
        }
      },
      error: (err) => {
        this.error = err?.error?.error || err.message || 'Upload failed';
        this.loading = false;
      }
    });
  }
}
