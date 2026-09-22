export interface YieldForecastRequest {
  state: string;
  district: string;
  crop: string;
  season: string;
  area: number;
  crop_year?: number;
  model_type?: string;
}

export interface YieldForecastResponse {
  state: string;
  district: string;
  crop: string;
  season: string;
  area_hectares: number;
  crop_year: number;
  predicted_yield_tonnes_per_hectare: number;
  estimated_total_production_tonnes: number;
  unit: string;
  model_used: string;
  execution_time_ms: number;
}
