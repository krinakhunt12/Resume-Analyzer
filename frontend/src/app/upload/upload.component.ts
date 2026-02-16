import { Component, signal, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AtsService } from '../services/ats.service';
import { ToastService } from '../services/toast.service';
import { LoadingState } from '../models/api.interfaces';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  resumeFile = signal<File | null>(null);
  jobDescription = '';  // Regular property for ngModel compatibility
  loadingState = signal<LoadingState>(LoadingState.IDLE);
  errorMessage = signal<string>('');
  
  readonly LoadingState = LoadingState;
  private isDragOverSignal = signal<boolean>(false);

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(
    private router: Router,
    private atsService: AtsService,
    private toastService: ToastService
  ) {}

  // Public getter methods for template access
  isDragOver(): boolean {
    return this.isDragOverSignal();
  }

  triggerFileInput(): void {
    if (this.fileInput && this.fileInput.nativeElement) {
      this.fileInput.nativeElement.click();
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.handleFileSelection(file);
    }
  }

  clearFile(): void {
    this.resumeFile.set(null);
    this.errorMessage.set('');
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  get canAnalyze(): boolean {
    return this.loadingState() !== LoadingState.LOADING;
  }

  get isLoading(): boolean {
    return this.loadingState() === LoadingState.LOADING;
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOverSignal.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOverSignal.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOverSignal.set(false);

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFileSelection(files[0]);
    }
  }

  private handleFileSelection(file: File): void {
    if (this.isValidFile(file)) {
      this.resumeFile.set(file);
      this.errorMessage.set('');
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
    // Prevent multiple concurrent requests
    if (this.loadingState() === LoadingState.LOADING) {
      return;
    }

    // Validate inputs
    if (!this.validateInputs()) {
      return;
    }

    this.loadingState.set(LoadingState.LOADING);
    this.errorMessage.set('');

    const formData = new FormData();
    formData.append('resume', this.resumeFile()!);
    
    if (this.jobDescription.trim()) {
      formData.append('job_description_text', this.jobDescription.trim());
    }

    this.atsService.analyzeResume(formData).subscribe({
      next: (response) => {
        this.loadingState.set(LoadingState.SUCCESS);
        
        // Navigate to results page with data
        this.router.navigate(['/results'], {
          state: { 
            results: response, 
            jobDescription: this.jobDescription.trim() || null
          }
        });
      },
      error: (error) => {
        this.loadingState.set(LoadingState.ERROR);
        const errorMsg = error.error || 'Analysis failed. Please try again.';
        this.errorMessage.set(errorMsg);
        
        this.toastService.show({
          type: 'error',
          title: 'Analysis Failed',
          description: errorMsg
        });
      }
    });
  }

  private validateInputs(): boolean {
    const file = this.resumeFile();
    
    if (!file) {
      this.showValidationError('Please select a resume file to analyze.');
      return false;
    }

    if (!this.isValidFile(file)) {
      this.showValidationError('Please upload a valid PDF or DOCX file.');
      return false;
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      this.showValidationError('File size must be less than 10MB.');
      return false;
    }

    return true;
  }

  private showValidationError(message: string): void {
    this.errorMessage.set(message);
    this.toastService.show({
      type: 'warning',
      title: 'Validation Error',
      description: message
    });
  }
}