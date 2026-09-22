import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { CropRecommendationRequest, CropRecommendationResponse } from '../models/crop.model';

@Injectable({
  providedIn: 'root'
})
export class CropService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/crop`;

  public recommendCrop(request: CropRecommendationRequest): Observable<ApiResponse<CropRecommendationResponse>> {
    return this.http.post<ApiResponse<CropRecommendationResponse>>(`${this.baseUrl}/recommend`, request);
  }
}
