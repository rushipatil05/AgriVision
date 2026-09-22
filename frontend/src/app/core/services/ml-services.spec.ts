import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { CropService } from './crop.service';
import { PriceService } from './price.service';
import { YieldService } from './yield.service';
import { DecisionService } from './decision.service';
import { PredictionHistoryService } from './prediction-history.service';
import { MonitoringService } from './monitoring.service';
import { environment } from '../../../environments/environment';

describe('ML & Prediction API Services', () => {
  let httpTesting: HttpTestingController;
  let cropService: CropService;
  let priceService: PriceService;
  let yieldService: YieldService;
  let decisionService: DecisionService;
  let historyService: PredictionHistoryService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        CropService,
        PriceService,
        YieldService,
        DecisionService,
        PredictionHistoryService,
        MonitoringService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    httpTesting = TestBed.inject(HttpTestingController);
    cropService = TestBed.inject(CropService);
    priceService = TestBed.inject(PriceService);
    yieldService = TestBed.inject(YieldService);
    decisionService = TestBed.inject(DecisionService);
    historyService = TestBed.inject(PredictionHistoryService);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('CropService should send recommend request', () => {
    const mockReq = { N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9 };
    const mockRes = {
      recommended_crop: 'rice',
      confidence: 0.998,
      top_recommendations: [{ crop: 'rice', probability: 0.998, rank: 1 }],
      input_parameters: mockReq,
      execution_time_ms: 12.5,
      model_type: 'LSTM'
    };

    cropService.recommendCrop(mockReq).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.recommended_crop).toBe('rice');
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/crop/recommend`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockRes });
  });

  it('PriceService should send forecast request', () => {
    const mockReq = { commodity: 'Wheat', market: 'Azadpur', historical_prices: [2100, 2150, 2200], forecast_horizon: 7 };
    const mockRes = {
      commodity: 'Wheat',
      market: 'Azadpur',
      forecast_horizon_days: 7,
      current_price: 2200,
      forecasted_end_price: 2245,
      price_change_absolute: 45,
      price_change_percentage: 2.05,
      trend_direction: 'UPWARD',
      forecasts: [{ day: 1, forecasted_price: 2205 }],
      execution_time_ms: 8.2,
      model_type: 'LSTM'
    };

    priceService.forecastPrice(mockReq).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.trend_direction).toBe('UPWARD');
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/price/forecast`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockRes });
  });

  it('YieldService should send prediction request', () => {
    const mockReq = { state: 'Punjab', district: 'Ludhiana', crop: 'Wheat', season: 'Rabi', area: 10 };
    const mockRes = {
      state: 'Punjab',
      district: 'Ludhiana',
      crop: 'Wheat',
      season: 'Rabi',
      area_hectares: 10,
      crop_year: 2024,
      predicted_yield_tonnes_per_hectare: 4.52,
      estimated_total_production_tonnes: 45.2,
      unit: 'Tonnes/Hectare',
      model_used: 'Deep Neural Network',
      execution_time_ms: 5.4
    };

    yieldService.predictYield(mockReq).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.predicted_yield_tonnes_per_hectare).toBe(4.52);
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/yield/predict`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockRes });
  });

  it('DecisionService should send multi-factor decision recommendation request', () => {
    const mockReq = {
      N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9,
      state: 'Punjab', district: 'Ludhiana', season: 'Rabi', area: 10, crop_year: 2024,
      market: 'Azadpur', forecast_horizon: 7
    };
    const mockRes = {
      recommended_crop: 'wheat',
      decision_score: 89.5,
      crop_confidence: 0.98,
      suitability_score: 98.0,
      predicted_yield: 4.52,
      yield_score: 90.4,
      estimated_production_tonnes: 45.2,
      market: 'Azadpur',
      forecast_price: 2245.0,
      market_score: 82.3,
      price_trend: 'UPWARD',
      forecast_horizon_days: 7,
      alternatives: [
        {
          rank: 1,
          crop: 'wheat',
          decision_score: 89.5,
          suitability_probability: 0.98,
          suitability_score: 98.0,
          predicted_yield_tonnes_per_hectare: 4.52,
          yield_score: 90.4,
          forecasted_market_price: 2245.0,
          market_score: 82.3,
          price_trend: 'UPWARD'
        }
      ],
      explanation: {
        summary: 'Optimal choice',
        soil_compatibility: 'High',
        climatic_suitability: 'High',
        yield_potential: 'High',
        market_outlook: 'Strong',
        key_advantages: ['High score']
      },
      execution_time_ms: 22.4
    };

    decisionService.recommendDecision(mockReq).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.recommended_crop).toBe('wheat');
      expect(res.data?.decision_score).toBe(89.5);
      expect(res.data?.alternatives.length).toBe(1);
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/decision/recommend`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockRes });
  });

  it('PredictionHistoryService should fetch paginated history and delete item', () => {
    historyService.getHistory(1, 10, 'CROP_RECOMMENDATION').subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.total).toBe(1);
    });

    const getReq = httpTesting.expectOne((r) => r.url === `${environment.apiBaseUrl}/predictions/history`);
    expect(getReq.request.params.get('page')).toBe('1');
    expect(getReq.request.params.get('prediction_type')).toBe('CROP_RECOMMENDATION');
    getReq.flush({ success: true, data: { total: 1, records: [] } });

    historyService.deletePrediction(42).subscribe((res) => {
      expect(res.success).toBe(true);
    });

    const delReq = httpTesting.expectOne(`${environment.apiBaseUrl}/predictions/history/42`);
    expect(delReq.request.method).toBe('DELETE');
    delReq.flush({ success: true, data: { message: 'Deleted', deleted_id: 42 } });
  });

  it('MonitoringService should fetch health, metrics, models, drift, and distributions', () => {
    const monitoringService = TestBed.inject(MonitoringService);

    monitoringService.getMonitoringHealth().subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.status).toBe('healthy');
    });
    const reqHealth = httpTesting.expectOne(`${environment.apiBaseUrl}/monitoring/health`);
    expect(reqHealth.request.method).toBe('GET');
    reqHealth.flush({ success: true, data: { status: 'healthy', uptime_seconds: 120, timestamp: '2026-09-12T12:00:00Z', database: { status: 'connected' }, models: {} } });

    monitoringService.getModelsMetadata().subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.total_models).toBe(4);
    });
    const reqModels = httpTesting.expectOne(`${environment.apiBaseUrl}/monitoring/models`);
    expect(reqModels.request.method).toBe('GET');
    reqModels.flush({ success: true, data: { total_models: 4, models: [] } });

    monitoringService.getPerformanceMetrics().subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.total_requests).toBe(15);
    });
    const reqMetrics = httpTesting.expectOne(`${environment.apiBaseUrl}/monitoring/metrics`);
    expect(reqMetrics.request.method).toBe('GET');
    reqMetrics.flush({ success: true, data: { uptime_seconds: 120, total_requests: 15, successful_requests: 15, failed_requests: 0, success_rate_percentage: 100, overall_avg_latency_ms: 12.5, total_predictions: 10, predictions_by_type: {}, endpoint_breakdown: [] } });

    monitoringService.getDataDrift(5).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.status).toBe('INSUFFICIENT_DATA');
    });
    const reqDrift = httpTesting.expectOne(`${environment.apiBaseUrl}/monitoring/drift?min_samples=5`);
    expect(reqDrift.request.method).toBe('GET');
    reqDrift.flush({ success: true, data: { status: 'INSUFFICIENT_DATA', sample_size: 0, method: 'z_shift', evaluated_at: '2026-09-12T12:00:00Z', features: [], message: 'Insufficient data' } });

    monitoringService.getPredictionDistributions().subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.total_predictions).toBe(0);
    });
    const reqDist = httpTesting.expectOne(`${environment.apiBaseUrl}/monitoring/distributions`);
    expect(reqDist.request.method).toBe('GET');
    reqDist.flush({ success: true, data: { status: 'success', total_predictions: 0, message: 'No predictions' } });
  });
});
