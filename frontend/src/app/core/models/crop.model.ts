export interface CropRecommendationRequest {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
  top_k?: number;
}

export interface RankedCropProbability {
  crop: string;
  probability: number;
}

export interface CropRecommendationResponse {
  recommended_crop: string;
  confidence: number;
  recommendations: RankedCropProbability[];
  execution_time_ms: number;
}
