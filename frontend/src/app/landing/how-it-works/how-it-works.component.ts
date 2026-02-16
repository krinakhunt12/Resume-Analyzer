import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-how-it-works',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './how-it-works.component.html',
  styleUrls: ['./how-it-works.component.css']
})
export class HowItWorksComponent {
  steps = [
    {
      number: 1,
      title: 'Upload Resume',
      description: 'Simply upload your resume in PDF or DOCX format. Our system securely processes your document.'
    },
    {
      number: 2,
      title: 'AI Analysis',
      description: 'Advanced AI algorithms analyze your resume for ATS compatibility, skills, and job matching.'
    },
    {
      number: 3,
      title: 'Get Actionable Insights',
      description: 'Receive detailed reports with scores, recommendations, and suggestions to improve your resume.'
    }
  ];
}