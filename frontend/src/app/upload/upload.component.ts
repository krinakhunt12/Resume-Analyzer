import { Component, signal, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AtsService } from '../services/ats.service';
import { ToastService } from '../services/toast.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  resumeFile = signal<File | null>(null);
  jobDescription = signal<string>('');
  isAnalyzing = signal<boolean>(false);

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(
    private router: Router,
    private atsService: AtsService,
    private toastService: ToastService
  ) {}

  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      if (this.isValidFile(file)) {
        this.resumeFile.set(file);
        this.toastService.show({
          type: 'success',
          title: 'File Selected',
          description: `${file.name} is ready for analysis.`
        });
      } else {
        this.toastService.show({
          type: 'error',
          title: 'Invalid File',
          description: 'Please select a PDF or DOCX file.'
        });
      }
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (this.isValidFile(file)) {
        this.resumeFile.set(file);
        this.toastService.show({
          type: 'success',
          title: 'File Selected',
          description: `${file.name} is ready for analysis.`
        });
      } else {
        this.toastService.show({
          type: 'error',
          title: 'Invalid File',
          description: 'Please drop a PDF or DOCX file.'
        });
      }
    }
  }

  private isValidFile(file: File): boolean {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword'
    ];
    const validExtensions = ['.pdf', '.docx', '.doc'];
    const fileName = file.name.toLowerCase();
    const hasValidType = validTypes.includes(file.type);
    const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

    console.log('File validation:', {
      fileName: file.name,
      mimeType: file.type,
      hasValidType,
      hasValidExtension
    });

    return hasValidType || hasValidExtension;
  }

  analyzeResume(): void {
    console.log('Analyze button clicked');
    console.log('Resume file:', this.resumeFile());
    console.log('Job description:', this.jobDescription());

    if (!this.resumeFile()) {
      console.log('No resume file selected');
      this.toastService.show({
        type: 'warning',
        title: 'No Resume Selected',
        description: 'Please select a resume file to analyze.'
      });
      return;
    }

    console.log('Starting analysis...');
    this.isAnalyzing.set(true);

    const formData = new FormData();
    formData.append('resume', this.resumeFile()!);
    if (this.jobDescription().trim()) {
      formData.append('job_description_text', this.jobDescription());
    }

    console.log('FormData created, calling API...');
    this.atsService.analyzeResume(formData).subscribe({
      next: (response) => {
        console.log('API response received:', response);
        this.isAnalyzing.set(false);
        // Navigate to results with data
        this.router.navigate(['/results'], {
          state: { results: response, jobDescription: this.jobDescription() }
        });
      },
      error: (error) => {
        console.error('API error:', error);
        this.isAnalyzing.set(false);
        this.toastService.show({
          type: 'error',
          title: 'Analysis Failed',
          description: 'There was an error analyzing your resume. Please try again.'
        });
        console.error('Analysis error:', error);
      }
    });
  }
}