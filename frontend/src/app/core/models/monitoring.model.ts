export interface ModelMetadataItem {
  model_id: string;
  model_name: string;
  version: string;
  model_type: string;
  framework: string;
  status: string;
  dataset_source: string;
  input_features: string[];
  metrics: Record<string, any>;
  epochs_trained?: number | null;
  latency_ms?: number | null;
}

export interface ModelsMetadataResponse {
  total_models: number;
  models: ModelMetadataItem[];
}

export interface EndpointMetricItem {
  endpoint: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_latency_ms: float;
  min_latency_ms: float;
  max_latency_ms: float;
}

type float = number;

export interface ApiPerformanceMetricsResponse {
  uptime_seconds: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate_percentage: number;
  overall_avg_latency_ms: number;
  total_predictions: number;
  predictions_by_type: Record<string, number>;
  endpoint_breakdown: EndpointMetricItem[];
}

export interface SystemMonitoringHealthResponse {
  status: string;
  uptime_seconds: number;
  timestamp: string;
  database: {
    status: string;
    latency_ms?: number;
    error?: string;
  };
  models: Record<string, { status: string; model_type: string }>;
}

export interface FeatureDriftItem {
  feature: string;
  drift_score: number;
  status: string; // HEALTHY | MODERATE_DRIFT | DRIFT_DETECTED | INSUFFICIENT_DATA
  p_value?: number | null;
  baseline_stats: {
    mean: number;
    std: number;
    min: number;
    max: number;
  };
  current_stats: {
    mean: number;
    std: number;
    min: number;
    max: number;
  };
}

export interface DataDriftResponse {
  status: string;
  sample_size: number;
  method: string;
  evaluated_at: string;
  features: FeatureDriftItem[];
  message: string;
}

export interface CropClassFrequency {
  crop: string;
  count: number;
  percentage: number;
}

export interface YieldDistributionStats {
  count: number;
  mean_yield_tonnes_per_ha: number;
  min_yield_tonnes_per_ha: number;
  max_yield_tonnes_per_ha: number;
  median_yield_tonnes_per_ha: number;
}

export interface PriceTrendFrequency {
  trend: string;
  count: number;
  percentage: number;
}

export interface DecisionScoreDistributionStats {
  count: number;
  mean_score: number;
  min_score: number;
  max_score: number;
  median_score: number;
}

export interface PredictionDistributionResponse {
  status: string;
  total_predictions: number;
  crop_recommendations?: CropClassFrequency[] | null;
  yield_forecasting?: YieldDistributionStats | null;
  price_forecasting?: PriceTrendFrequency[] | null;
  decision_support?: DecisionScoreDistributionStats | null;
  message: string;
}
