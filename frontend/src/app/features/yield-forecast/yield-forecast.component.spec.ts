import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { YieldForecastComponent } from './yield-forecast.component';
import { YieldService } from '../../core/services/yield.service';

describe('YieldForecastComponent', () => {
  let component: YieldForecastComponent;
  let yieldServiceSpy: any;

  beforeEach(async () => {
    yieldServiceSpy = {
      predictYield: () => of({
        success: true,
        data: {
          state: 'Punjab',
          district: 'Ludhiana',
          crop: 'Wheat',
          season: 'Rabi',
          area_hectares: 10.0,
          crop_year: 2024,
          predicted_yield_tonnes_per_hectare: 4.85,
          estimated_total_production_tonnes: 48.5,
          unit: 'Tonnes/Hectare',
          model_used: 'Deep Neural Network',
          execution_time_ms: 6.2
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [YieldForecastComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: YieldService, useValue: yieldServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(YieldForecastComponent);
    component = fixture.componentInstance;
  });

  it('should initialize with default parameters', () => {
    expect(component).toBeTruthy();
    expect(component.yieldForm.valid).toBe(true);
    expect(component.yieldForm.get('state')?.value).toBe('Punjab');
  });

  it('should apply regional preset', () => {
    const cottonPreset = component.presets.find((p) => p.crop === 'Cotton');
    expect(cottonPreset).toBeDefined();
    component.applyPreset(cottonPreset!);
    expect(component.yieldForm.get('crop')?.value).toBe('Cotton');
    expect(component.yieldForm.get('state')?.value).toBe('Maharashtra');
  });

  it('should predict yield successfully', () => {
    component.onSubmit();
    expect(component.result()).toBeTruthy();
    expect(component.result()?.predicted_yield_tonnes_per_hectare).toBe(4.85);
    expect(component.result()?.estimated_total_production_tonnes).toBe(48.5);
  });
});
