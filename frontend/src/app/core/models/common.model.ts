export interface ErrorDetail {
  code: string;
  message: string;
  details?: any;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: ErrorDetail;
}

export interface HealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
}

export interface ModelStatusItem {
  status: string;
  model_type: string;
  artifact_path: string;
  latency_ms?: number;
}

export interface ModelsStatusResponse {
  crop_recommendation: string;
  price_forecasting: string;
  yield_forecasting: string;
  details: { [key: string]: ModelStatusItem };
}
