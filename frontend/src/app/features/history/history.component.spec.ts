import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { HistoryComponent } from './history.component';
import { PredictionHistoryService } from '../../core/services/prediction-history.service';

describe('HistoryComponent', () => {
  let component: HistoryComponent;
  let historyServiceSpy: any;

  beforeEach(async () => {
    historyServiceSpy = {
      getHistory: () => of({
        success: true,
        data: {
          total: 2,
          total_pages: 1,
          records: [
            {
              id: 101,
              prediction_type: 'CROP_RECOMMENDATION',
              input_data: { N: 90 },
              prediction_result: { recommended_crop: 'rice', confidence: 0.99 },
              latency_ms: 10.0,
              created_at: '2026-09-04T12:00:00Z'
            }
          ]
        }
      }),
      deletePrediction: () => of({
        success: true,
        data: { message: 'Deleted', deleted_id: 101 }
      })
    };

    await TestBed.configureTestingModule({
      imports: [HistoryComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: PredictionHistoryService, useValue: historyServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(HistoryComponent);
    component = fixture.componentInstance;
    component.ngOnInit();
  });

  it('should initialize and fetch history list', () => {
    expect(component).toBeTruthy();
    expect(component.records().length).toBe(1);
    expect(component.total()).toBe(2);
  });

  it('should open and close modal dialogs', () => {
    const item = component.records()[0];
    component.openDetailModal(item);
    expect(component.selectedItem()).toEqual(item);
    component.closeDetailModal();
    expect(component.selectedItem()).toBeNull();

    component.promptDelete(item);
    expect(component.itemToDelete()).toEqual(item);
    component.cancelDelete();
    expect(component.itemToDelete()).toBeNull();
  });
});
