import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { YieldForecastRequest, YieldForecastResponse } from '../models/yield.model';

@Injectable({
  providedIn: 'root'
})
export class YieldService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/yield`;

  public predictYield(request: YieldForecastRequest): Observable<ApiResponse<YieldForecastResponse>> {
    return this.http.post<ApiResponse<YieldForecastResponse>>(`${this.baseUrl}/predict`, request);
  }
}
