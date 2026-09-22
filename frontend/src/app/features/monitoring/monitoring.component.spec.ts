import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { MonitoringComponent } from './monitoring.component';
import { MonitoringService } from '../../core/services/monitoring.service';

describe('MonitoringComponent', () => {
  let component: MonitoringComponent;
  let monitoringServiceSpy: any;

  beforeEach(async () => {
    monitoringServiceSpy = {
      getMonitoringHealth: () => of({
        success: true,
        data: {
          status: 'healthy',
          uptime_seconds: 3600,
          timestamp: '2026-09-12T12:00:00Z',
          database: { status: 'connected', latency_ms: 1.2 },
          models: {
            crop_recommendation_lstm: { status: 'LOADED', model_type: 'LSTM' },
            price_forecasting_lstm: { status: 'LOADED', model_type: 'LSTM' }
          }
        }
      }),
      getModelsMetadata: () => of({
        success: true,
        data: {
          total_models: 4,
          models: [
            {
              model_id: 'crop_recommendation_lstm',
              model_name: 'Crop Recommendation Model',
              version: 'v1.0.0-prod',
              model_type: 'Deep Learning LSTM',
              framework: 'TensorFlow 2.15+',
              status: 'active',
              dataset_source: 'ICAR & Kaggle Soil Dataset',
              input_features: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
              metrics: { accuracy: '98.79%' }
            }
          ]
        }
      }),
      getPerformanceMetrics: () => of({
        success: true,
        data: {
          uptime_seconds: 3600,
          total_requests: 120,
          successful_requests: 120,
          failed_requests: 0,
          success_rate_percentage: 100,
          overall_avg_latency_ms: 15.4,
          total_predictions: 85,
          predictions_by_type: { CROP_RECOMMENDATION: 40, PRICE_FORECAST: 45 },
          endpoint_breakdown: []
        }
      }),
      getDataDrift: () => of({
        success: true,
        data: {
          status: 'INSUFFICIENT_DATA',
          sample_size: 2,
          method: 'Z-shift & KS statistical divergence',
          evaluated_at: '2026-09-12T12:00:00Z',
          features: [],
          message: 'Insufficient sample size'
        }
      }),
      getPredictionDistributions: () => of({
        success: true,
        data: {
          status: 'success',
          total_predictions: 85,
          crop_recommendations: [{ crop: 'rice', count: 40, percentage: 100 }],
          message: 'Distributions retrieved'
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [MonitoringComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: MonitoringService, useValue: monitoringServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(MonitoringComponent);
    component = fixture.componentInstance;
    component.ngOnInit();
  });

  afterEach(() => {
    component.ngOnDestroy();
  });

  it('should initialize and load all monitoring telemetry data', () => {
    expect(component).toBeTruthy();
    expect(component.healthData()?.status).toBe('healthy');
    expect(component.modelsData()?.total_models).toBe(4);
    expect(component.metricsData()?.total_requests).toBe(120);
    expect(component.driftData()?.status).toBe('INSUFFICIENT_DATA');
    expect(component.distributionData()?.total_predictions).toBe(85);
  });

  it('should switch tabs properly', () => {
    expect(component.activeTab()).toBe('overview');
    component.setTab('models');
    expect(component.activeTab()).toBe('models');
    component.setTab('telemetry');
    expect(component.activeTab()).toBe('telemetry');
    component.setTab('drift');
    expect(component.activeTab()).toBe('drift');
    component.setTab('distributions');
    expect(component.activeTab()).toBe('distributions');
  });

  it('should open and close model inspection modal', () => {
    const model = component.modelsData()!.models[0];
    component.openModelModal(model);
    expect(component.selectedModel()).toEqual(model);
    component.closeModelModal();
    expect(component.selectedModel()).toBeNull();
  });

  it('should format uptime duration correctly', () => {
    expect(component.formatUptime(45)).toBe('45s');
    expect(component.formatUptime(3665)).toBe('1h 1m 5s');
    expect(component.formatUptime(90000)).toBe('1d 1h');
  });
});
