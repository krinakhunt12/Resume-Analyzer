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
  // track auto-dismiss timers so we can clear them if a toast is removed manually
  private timers: Record<string, any> = {};

  get toasts() {
    return this.toasts$.asObservable();
  }

  show(toast: Omit<Toast, 'id'>) {
    const id = Date.now().toString();
    const newToast: Toast = {
      id,
      // default to 3 seconds unless caller provides a different duration
      duration: toast.duration ?? 3000,
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

    // Auto-dismiss after the toast duration
    const t = setTimeout(() => {
      this.remove(id);
    }, newToast.duration);
    this.timers[id] = t;
  }

  remove(id: string) {
    const currentToasts = this.toasts$.value;
    const updatedToasts = currentToasts.filter(t => t.id !== id);
    this.toasts$.next(updatedToasts);
    // clear any pending timer
    if (this.timers[id]) {
      clearTimeout(this.timers[id]);
      delete this.timers[id];
    }
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