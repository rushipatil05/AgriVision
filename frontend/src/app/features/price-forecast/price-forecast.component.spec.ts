import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { PriceForecastComponent } from './price-forecast.component';
import { PriceService } from '../../core/services/price.service';

describe('PriceForecastComponent', () => {
  let component: PriceForecastComponent;
  let priceServiceSpy: any;

  beforeEach(async () => {
    priceServiceSpy = {
      forecastPrice: () => of({
        success: true,
        data: {
          commodity: 'Wheat',
          market: 'Azadpur',
          forecast_horizon_days: 7,
          current_price: 2200,
          forecasted_end_price: 2250,
          price_change_absolute: 50,
          price_change_percentage: 2.27,
          trend_direction: 'UPWARD',
          forecasts: [{ day: 1, forecasted_price: 2208 }],
          execution_time_ms: 12.0,
          model_type: 'LSTM'
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [PriceForecastComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: PriceService, useValue: priceServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(PriceForecastComponent);
    component = fixture.componentInstance;
  });

  it('should initialize and generate sample sequence', () => {
    expect(component).toBeTruthy();
    expect(component.priceForm.get('commodity')?.value).toBe('Wheat');
    expect(component.priceForm.get('pricesInput')?.value).toBeTruthy();
  });

  it('should forecast prices and populate chart data', () => {
    component.onSubmit();
    expect(component.result()).toBeTruthy();
    expect(component.result()?.trend_direction).toBe('UPWARD');
    expect(component.lineChartData.datasets.length).toBe(2);
  });
});
