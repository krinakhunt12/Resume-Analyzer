import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-hero',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './hero.component.html',
  styleUrls: ['./hero.component.css']
})
export class HeroComponent {
  @Output() uploadResume = new EventEmitter<void>();
  @Output() seeHowItWorks = new EventEmitter<void>();

  onUploadResume() {
    this.uploadResume.emit();
  }

  onSeeHowItWorks() {
    this.seeHowItWorks.emit();
  }
}