import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { PredictionHistoryListResponse, PredictionDeleteResponse } from '../models/prediction-history.model';

@Injectable({
  providedIn: 'root'
})
export class PredictionHistoryService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/predictions/history`;

  public getHistory(
    page: number = 1,
    pageSize: number = 10,
    predictionType?: string
  ): Observable<ApiResponse<PredictionHistoryListResponse>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());

    if (predictionType && predictionType.trim() !== '' && predictionType !== 'ALL') {
      params = params.set('prediction_type', predictionType);
    }

    return this.http.get<ApiResponse<PredictionHistoryListResponse>>(this.baseUrl, { params });
  }

  public deletePrediction(id: number): Observable<ApiResponse<PredictionDeleteResponse>> {
    return this.http.delete<ApiResponse<PredictionDeleteResponse>>(`${this.baseUrl}/${id}`);
  }
}
