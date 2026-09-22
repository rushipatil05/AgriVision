import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { environment } from '../../environments/environment';
import { HealthResponse } from '../models/health.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  /**
   * Check backend health and connectivity.
   * Returns HealthResponse if online, or null if offline/error.
   */
  getHealth(): Observable<HealthResponse | null> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health`).pipe(
      catchError((error) => {
        console.warn('Backend health check error (expected if backend offline):', error);
        return of(null);
      })
    );
  }
}
