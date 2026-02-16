import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cta',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cta.component.html',
  styleUrls: ['./cta.component.css']
})
export class CtaComponent {
  @Output() startAnalysis = new EventEmitter<void>();

  onStartAnalysis() {
    this.startAnalysis.emit();
  }
}