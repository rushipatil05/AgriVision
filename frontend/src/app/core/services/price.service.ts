import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { PriceForecastRequest, PriceForecastResponse } from '../models/price.model';

@Injectable({
  providedIn: 'root'
})
export class PriceService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/price`;

  public forecastPrice(request: PriceForecastRequest): Observable<ApiResponse<PriceForecastResponse>> {
    return this.http.post<ApiResponse<PriceForecastResponse>>(`${this.baseUrl}/forecast`, request);
  }
}
