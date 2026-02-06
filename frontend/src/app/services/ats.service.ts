import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AtsService {
    private apiUrl = 'http://localhost:5000';

    constructor(private http: HttpClient) { }

    analyzeResume(formData: FormData): Observable<any> {
        return this.http.post(`${this.apiUrl}/analyze`, formData);
    }

    generateCoverLetter(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/generate-cover-letter`, data);
    }

    generateAtsPdf(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/generate-ats-pdf`, data);
    }

    getDownloadUrl(filename: string): string {
        return `${this.apiUrl}/download/${filename}`;
    }
}
