import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { DecisionRecommendationRequest, DecisionRecommendationResponse } from '../models/decision.model';

@Injectable({
  providedIn: 'root'
})
export class DecisionService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/decision`;

  public recommendDecision(request: DecisionRecommendationRequest): Observable<ApiResponse<DecisionRecommendationResponse>> {
    return this.http.post<ApiResponse<DecisionRecommendationResponse>>(`${this.baseUrl}/recommend`, request);
  }
}
