import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { DecisionSupportComponent } from './decision-support.component';
import { DecisionService } from '../../core/services/decision.service';

describe('DecisionSupportComponent', () => {
  let component: DecisionSupportComponent;
  let decisionServiceSpy: any;

  const mockDecisionResponse = {
    success: true,
    data: {
      recommended_crop: 'wheat',
      decision_score: 88.5,
      crop_confidence: 0.96,
      suitability_score: 96.0,
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
          decision_score: 88.5,
          suitability_probability: 0.96,
          suitability_score: 96.0,
          predicted_yield_tonnes_per_hectare: 4.52,
          yield_score: 90.4,
          forecasted_market_price: 2245.0,
          market_score: 82.3,
          price_trend: 'UPWARD'
        },
        {
          rank: 2,
          crop: 'rice',
          decision_score: 75.2,
          suitability_probability: 0.82,
          suitability_score: 82.0,
          predicted_yield_tonnes_per_hectare: 3.10,
          yield_score: 62.0,
          forecasted_market_price: 1980.0,
          market_score: 71.0,
          price_trend: 'STABLE'
        }
      ],
      explanation: {
        summary: 'Optimal choice under current soil and market parameters.',
        soil_compatibility: 'Optimal NPK and pH.',
        climatic_suitability: 'Favorable rainfall and humidity.',
        yield_potential: 'Robust 4.52 t/ha productivity.',
        market_outlook: 'Strong upward price trend.',
        key_advantages: [
          'High suitability score of 96.0 pts',
          'Forecasted market price ₹2245.00/qtl'
        ]
      },
      execution_time_ms: 18.2
    }
  };

  beforeEach(async () => {
    decisionServiceSpy = {
      recommendDecision: () => of(mockDecisionResponse)
    };

    await TestBed.configureTestingModule({
      imports: [DecisionSupportComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: DecisionService, useValue: decisionServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(DecisionSupportComponent);
    component = fixture.componentInstance;
  });

  it('should initialize with valid form defaults', () => {
    expect(component).toBeTruthy();
    expect(component.decisionForm.valid).toBe(true);
    expect(component.decisionForm.get('N')?.value).toBe(90);
    expect(component.decisionForm.get('state')?.value).toBe('Punjab');
  });

  it('should apply decision presets correctly', () => {
    const cottonPreset = component.presets.find((p) => p.name.includes('Cotton'));
    expect(cottonPreset).toBeDefined();
    component.applyPreset(cottonPreset!);
    expect(component.decisionForm.get('state')?.value).toBe('Maharashtra');
    expect(component.decisionForm.get('district')?.value).toBe('Nagpur');
    expect(component.decisionForm.get('N')?.value).toBe(117);
  });

  it('should execute decision recommendation and populate result and chart', () => {
    component.onSubmit();
    expect(component.result()).toBeTruthy();
    expect(component.result()?.recommended_crop).toBe('wheat');
    expect(component.result()?.decision_score).toBe(88.5);
    expect(component.barChartData.labels?.length).toBe(2);
    expect(component.barChartData.datasets.length).toBe(4);
  });

  it('should handle API failure gracefully', () => {
    decisionServiceSpy.recommendDecision = () => throwError(() => ({ error: { detail: 'Neural inference engine unavailable' } }));
    component.onSubmit();
    expect(component.isLoading()).toBe(false);
    expect(component.errorMessage()).toBe('Neural inference engine unavailable');
    expect(component.result()).toBeNull();
  });
});
