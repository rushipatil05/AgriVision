import time
import threading
from typing import Dict, List, Any
from app.schemas.monitoring import ApiPerformanceMetricsResponse, EndpointMetricItem


class MetricsCollector:
    """
    Thread-safe in-memory performance and telemetry metrics collector.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance._start_time = time.time()
                cls._instance._total_requests = 0
                cls._instance._successful_requests = 0
                cls._instance._failed_requests = 0
                cls._instance._total_latency = 0.0
                cls._instance._endpoints = {}  # path -> {count, success, fail, total_lat, min_lat, max_lat}
                cls._instance._predictions_by_type = {}
                cls._instance._pred_lock = threading.Lock()
        return cls._instance

    def record_request(self, endpoint: str, status_code: int, duration_ms: float):
        with self._pred_lock:
            self._total_requests += 1
            self._total_latency += duration_ms

            if status_code < 400:
                self._successful_requests += 1
            else:
                self._failed_requests += 1

            if endpoint not in self._endpoints:
                self._endpoints[endpoint] = {
                    "count": 0,
                    "success": 0,
                    "fail": 0,
                    "total_lat": 0.0,
                    "min_lat": duration_ms,
                    "max_lat": duration_ms
                }

            ep = self._endpoints[endpoint]
            ep["count"] += 1
            if status_code < 400:
                ep["success"] += 1
            else:
                ep["fail"] += 1
            ep["total_lat"] += duration_ms
            ep["min_lat"] = min(ep["min_lat"], duration_ms)
            ep["max_lat"] = max(ep["max_lat"], duration_ms)

    def record_prediction(self, prediction_type: str):
        with self._pred_lock:
            p_type = prediction_type.upper()
            self._predictions_by_type[p_type] = self._predictions_by_type.get(p_type, 0) + 1

    def get_metrics(self) -> ApiPerformanceMetricsResponse:
        with self._pred_lock:
            uptime = round(time.time() - self._start_time, 1)
            total = self._total_requests
            success = self._successful_requests
            failed = self._failed_requests

            success_rate = round((success / total * 100.0), 2) if total > 0 else 100.0
            avg_latency = round(self._total_latency / total, 2) if total > 0 else 0.0

            endpoint_items = []
            for ep_name, data in self._endpoints.items():
                ep_avg = round(data["total_lat"] / data["count"], 2) if data["count"] > 0 else 0.0
                endpoint_items.append(EndpointMetricItem(
                    endpoint=ep_name,
                    total_requests=data["count"],
                    successful_requests=data["success"],
                    failed_requests=data["fail"],
                    avg_latency_ms=ep_avg,
                    min_latency_ms=round(data["min_lat"], 2),
                    max_latency_ms=round(data["max_lat"], 2)
                ))

            total_preds = sum(self._predictions_by_type.values())

            return ApiPerformanceMetricsResponse(
                uptime_seconds=uptime,
                total_requests=total,
                successful_requests=success,
                failed_requests=failed,
                success_rate_percentage=success_rate,
                overall_avg_latency_ms=avg_latency,
                total_predictions=total_preds,
                predictions_by_type=dict(self._predictions_by_type),
                endpoint_breakdown=endpoint_items
            )


metrics_collector = MetricsCollector()
