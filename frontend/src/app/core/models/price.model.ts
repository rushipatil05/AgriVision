export interface PriceForecastPoint {
  day: number;
  predicted_modal_price: number;
  unit?: string;
}

export interface PriceForecastRequest {
  commodity: string;
  market: string;
  historical_prices: number[];
  forecast_horizon?: number;
}

export interface PriceForecastResponse {
  commodity: string;
  market: string;
  forecast_horizon_days: number;
  last_observed_price: number;
  predicted_end_price: number;
  projected_percentage_change: number;
  trend_direction: 'UPWARD' | 'DOWNWARD' | 'STABLE';
  forecasts: PriceForecastPoint[];
  execution_time_ms: number;
}
