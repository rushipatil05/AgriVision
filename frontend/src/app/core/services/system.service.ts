import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse, HealthResponse, ModelsStatusResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class SystemService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  public getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health`);
  }

  public getModelsStatus(): Observable<ApiResponse<ModelsStatusResponse>> {
    return this.http.get<ApiResponse<ModelsStatusResponse>>(`${this.baseUrl}/models/status`);
  }
}
