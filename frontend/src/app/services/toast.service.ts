import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description: string;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private toasts$ = new BehaviorSubject<Toast[]>([]);
  private maxToasts = 3;

  get toasts() {
    return this.toasts$.asObservable();
  }

  show(toast: Omit<Toast, 'id'>) {
    const id = Date.now().toString();
    const newToast: Toast = {
      id,
      duration: 5000,
      ...toast
    };

    // Prevent duplicate toasts
    const currentToasts = this.toasts$.value;
    const duplicate = currentToasts.find(t =>
      t.title === newToast.title && t.description === newToast.description
    );

    if (duplicate) {
      return;
    }

    const updatedToasts = [newToast, ...currentToasts].slice(0, this.maxToasts);
    this.toasts$.next(updatedToasts);

    // Auto-dismiss
    setTimeout(() => {
      this.remove(id);
    }, newToast.duration);
  }

  remove(id: string) {
    const currentToasts = this.toasts$.value;
    const updatedToasts = currentToasts.filter(t => t.id !== id);
    this.toasts$.next(updatedToasts);
  }

  // Convenience methods
  success(title: string, description: string) {
    this.show({ type: 'success', title, description });
  }

  error(title: string, description: string) {
    this.show({ type: 'error', title, description });
  }

  warning(title: string, description: string) {
    this.show({ type: 'warning', title, description });
  }

  info(title: string, description: string) {
    this.show({ type: 'info', title, description });
  }
}