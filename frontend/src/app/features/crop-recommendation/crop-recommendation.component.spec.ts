import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { CropRecommendationComponent } from './crop-recommendation.component';
import { CropService } from '../../core/services/crop.service';

describe('CropRecommendationComponent', () => {
  let component: CropRecommendationComponent;
  let cropServiceSpy: any;

  beforeEach(async () => {
    cropServiceSpy = {
      recommendCrop: () => of({
        success: true,
        data: {
          recommended_crop: 'rice',
          recommendations: [
            { crop: 'rice', probability: 0.998 },
            { crop: 'jute', probability: 0.001 }
          ],
          top_recommendations: [
            { crop: 'rice', probability: 0.998, rank: 1 },
            { crop: 'jute', probability: 0.001, rank: 2 }
          ],
          input_parameters: { N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9 },
          execution_time_ms: 10.5,
          model_type: 'LSTM'
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [CropRecommendationComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: CropService, useValue: cropServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(CropRecommendationComponent);
    component = fixture.componentInstance;
  });

  it('should initialize with default parameters', () => {
    expect(component).toBeTruthy();
    expect(component.cropForm.valid).toBe(true);
    expect(component.cropForm.get('N')?.value).toBe(90);
  });

  it('should apply presets correctly', () => {
    const maizePreset = component.presets.find((p) => p.name.includes('Maize'));
    expect(maizePreset).toBeDefined();
    component.applyPreset(maizePreset!);
    expect(component.cropForm.get('N')?.value).toBe(71);
    expect(component.cropForm.get('P')?.value).toBe(54);
  });

  it('should trigger inference and update chart data', () => {
    component.onSubmit();
    expect(component.result()).toBeTruthy();
    expect(component.result()?.recommended_crop).toBe('rice');
    expect(component.barChartData.labels?.length).toBe(2);
  });
});
