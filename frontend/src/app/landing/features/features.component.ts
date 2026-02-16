import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-features',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './features.component.html',
  styleUrls: ['./features.component.css']
})
export class FeaturesComponent {
  features = [
    {
      icon: '📊',
      title: 'ATS Compatibility Score',
      description: 'Get a comprehensive score showing how well your resume performs with Applicant Tracking Systems.'
    },
    {
      icon: '🎯',
      title: 'Skill Gap Detection',
      description: 'Identify missing skills and competencies that could strengthen your job applications.'
    },
    {
      icon: '🤖',
      title: 'AI Career Suggestions',
      description: 'Receive intelligent recommendations to optimize your resume and advance your career.'
    }
  ];
}