import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { DashboardComponent } from './dashboard.component';
import { SystemService } from '../../core/services/system.service';
import { PredictionHistoryService } from '../../core/services/prediction-history.service';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let systemServiceSpy: any;
  let historyServiceSpy: any;

  beforeEach(async () => {
    systemServiceSpy = {
      getModelsStatus: () => of({
        success: true,
        data: {
          crop_recommendation: 'LOADED',
          price_forecasting: 'LOADED',
          yield_forecasting: 'LOADED',
          details: {}
        }
      })
    };

    historyServiceSpy = {
      getHistory: () => of({
        success: true,
        data: {
          total: 3,
          records: [
            {
              id: 1,
              prediction_type: 'CROP_RECOMMENDATION',
              input_data: {},
              prediction_result: { recommended_crop: 'rice', confidence: 0.99 },
              latency_ms: 12,
              created_at: '2026-09-04T12:00:00Z'
            }
          ]
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: SystemService, useValue: systemServiceSpy },
        { provide: PredictionHistoryService, useValue: historyServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    component.ngOnInit();
  });

  it('should initialize and load dashboard metrics', () => {
    expect(component).toBeTruthy();
    expect(component.modelsStatus()?.crop_recommendation).toBe('LOADED');
    expect(component.totalPredictions()).toBe(3);
    expect(component.recentHistory().length).toBe(1);
  });
});
