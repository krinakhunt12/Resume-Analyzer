import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, timeout } from 'rxjs';
import { catchError, map, retry } from 'rxjs/operators';
import { AnalysisResult, ApiError } from '../models/api.interfaces';

@Injectable({
    providedIn: 'root'
})
export class AtsService {
    private readonly apiUrl = 'http://localhost:5000';
    private readonly requestTimeout = 60000; // 60 seconds

    constructor(private http: HttpClient) { }

    analyzeResume(formData: FormData): Observable<AnalysisResult> {
        console.log('ATS Service: Calling analyze API');
        
        return this.http.post<AnalysisResult>(`${this.apiUrl}/analyze`, formData).pipe(
            timeout(this.requestTimeout),
            retry(1), // Retry once on failure
            catchError(this.handleError.bind(this))
        );
    }

    private handleError(error: HttpErrorResponse): Observable<never> {
        console.error('API Error:', error);
        
        let errorMessage = 'An unexpected error occurred. Please try again.';
        
        if (error.error instanceof ErrorEvent) {
            // Client-side error
            errorMessage = 'Network error. Please check your connection.';
        } else {
            // Server-side error
            switch (error.status) {
                case 0:
                    errorMessage = 'Unable to connect to the server. Please try again.';
                    break;
                case 400:
                    errorMessage = error.error?.error || 'Invalid file or request. Please check your resume format.';
                    break;
                case 413:
                    errorMessage = 'File too large. Please upload a file smaller than 10MB.';
                    break;
                case 415:
                    errorMessage = 'Unsupported file format. Please upload PDF or DOCX files only.';
                    break;
                case 500:
                    errorMessage = 'Server error occurred during analysis. Please try again.';
                    break;
                case 504:
                    errorMessage = 'Analysis is taking longer than expected. Please try again with a smaller file.';
                    break;
                default:
                    errorMessage = error.error?.error || errorMessage;
            }
        }
        
        return throwError(() => ({ error: errorMessage }));
    }

    generateCoverLetter(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/generate-cover-letter`, data);
    }

    generateAtsPdf(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/generate-ats-pdf`, data);
    }

    compareJobs(formData: FormData): Observable<any> {
        return this.http.post(`${this.apiUrl}/compare-jobs`, formData);
    }

    chatWithAI(message: string, context: any = {}): Observable<any> {
        return this.http.post(`${this.apiUrl}/chat`, { message, context });
    }

    analyzeLinkedIn(text: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/analyze-linkedin`, { text });
    }

    getDownloadUrl(filename: string): string {
        return `${this.apiUrl}/download/${filename}`;
    }
}
