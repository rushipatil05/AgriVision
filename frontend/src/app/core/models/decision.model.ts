export interface DecisionRecommendationRequest {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
  state: string;
  district: string;
  season: string;
  area: number;
  crop_year?: number;
  market?: string;
  forecast_horizon?: number;
  historical_prices?: number[];
}

export interface AlternativeCropEvaluation {
  crop: string;
  rank: number;
  decision_score: number;
  suitability_probability: number;
  suitability_score: number;
  predicted_yield_tonnes_per_hectare: number;
  estimated_total_production_tonnes: number;
  yield_score: number;
  forecasted_market_price: number;
  price_trend: 'UPWARD' | 'DOWNWARD' | 'STABLE' | string;
  market_score: number;
}

export interface DecisionExplanation {
  summary: string;
  soil_compatibility: string;
  climatic_suitability: string;
  yield_potential: string;
  market_outlook: string;
  key_advantages: string[];
}

export interface DecisionRecommendationResponse {
  recommended_crop: string;
  decision_score: number;
  crop_confidence: number;
  suitability_score: number;
  predicted_yield: number;
  yield_unit: string;
  estimated_production_tonnes: number;
  yield_score: number;
  forecast_price: number;
  price_unit: string;
  price_trend: string;
  market: string;
  market_score: number;
  explanation: DecisionExplanation;
  alternatives: AlternativeCropEvaluation[];
  execution_time_ms: number;
}
