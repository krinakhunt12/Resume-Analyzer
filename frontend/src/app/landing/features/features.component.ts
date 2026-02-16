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
      title: 'ATS Score Analysis',
      description: 'Get detailed insights on how ATS systems score your resume with actionable recommendations.'
    },
    {
      icon: '🎯',
      title: 'Skill Gap Detection',
      description: 'Identify missing skills and competencies needed for your target job role.'
    },
    {
      icon: '🔍',
      title: 'Job Description Matching',
      description: 'Compare your resume against job descriptions to see keyword alignment and match percentage.'
    },
    {
      icon: '🤖',
      title: 'AI Career Suggestions',
      description: 'Receive personalized career advice and suggestions to improve your professional profile.'
    }
  ];
}