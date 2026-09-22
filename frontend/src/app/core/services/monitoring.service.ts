import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import {
  ModelsMetadataResponse,
  ApiPerformanceMetricsResponse,
  SystemMonitoringHealthResponse,
  DataDriftResponse,
  PredictionDistributionResponse
} from '../models/monitoring.model';

@Injectable({
  providedIn: 'root'
})
export class MonitoringService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/monitoring`;

  public getModelsMetadata(): Observable<ApiResponse<ModelsMetadataResponse>> {
    return this.http.get<ApiResponse<ModelsMetadataResponse>>(`${this.baseUrl}/models`);
  }

  public getPerformanceMetrics(): Observable<ApiResponse<ApiPerformanceMetricsResponse>> {
    return this.http.get<ApiResponse<ApiPerformanceMetricsResponse>>(`${this.baseUrl}/metrics`);
  }

  public getMonitoringHealth(): Observable<ApiResponse<SystemMonitoringHealthResponse>> {
    return this.http.get<ApiResponse<SystemMonitoringHealthResponse>>(`${this.baseUrl}/health`);
  }

  public getDataDrift(minSamples: number = 5): Observable<ApiResponse<DataDriftResponse>> {
    return this.http.get<ApiResponse<DataDriftResponse>>(`${this.baseUrl}/drift?min_samples=${minSamples}`);
  }

  public getPredictionDistributions(): Observable<ApiResponse<PredictionDistributionResponse>> {
    return this.http.get<ApiResponse<PredictionDistributionResponse>>(`${this.baseUrl}/distributions`);
  }
}
