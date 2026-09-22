export interface PredictionHistoryItem {
  id: number;
  user_id?: number;
  prediction_type: string;
  input_data: any;
  prediction_result: any;
  latency_ms?: number;
  created_at: string;
}

export interface PredictionHistoryListResponse {
  total: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  records: PredictionHistoryItem[];
}

export interface PredictionDeleteResponse {
  message: string;
  deleted_id: number;
}
