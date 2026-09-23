import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { YieldService } from '../../core/services/yield.service';
import { YieldForecastResponse } from '../../core/models/yield.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

interface YieldPreset {
  name: string;
  state: string;
  district: string;
  crop: string;
  season: string;
  area: number;
}

@Component({
  selector: 'app-yield-forecast',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, LoadingSpinnerComponent],
  templateUrl: './yield-forecast.component.html',
  styleUrl: './yield-forecast.component.css'
})
export class YieldForecastComponent {
  private fb = inject(FormBuilder);
  private yieldService = inject(YieldService);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public result = signal<YieldForecastResponse | null>(null);

  public states = [
    'Punjab',
    'Haryana',
    'Uttar Pradesh',
    'Maharashtra',
    'Karnataka',
    'Tamil Nadu',
    'Andhra Pradesh',
    'Madhya Pradesh',
    'West Bengal',
    'Gujarat',
    'Rajasthan',
    'Bihar'
  ];

  public seasons = ['Kharif', 'Rabi', 'Summer', 'Autumn', 'Winter', 'Whole Year'];

  public crops = [
    'Wheat',
    'Rice',
    'Maize',
    'Cotton',
    'Sugarcane',
    'Potato',
    'Onion',
    'Soyabean',
    'Groundnut',
    'Gram',
    'Bajra',
    'Jowar'
  ];

  public presets: YieldPreset[] = [
    { name: 'Punjab Wheat (Rabi)', state: 'Punjab', district: 'Ludhiana', crop: 'Wheat', season: 'Rabi', area: 10.0 },
    { name: 'Maharashtra Cotton (Kharif)', state: 'Maharashtra', district: 'Nagpur', crop: 'Cotton', season: 'Kharif', area: 15.0 },
    { name: 'UP Sugarcane (Whole Year)', state: 'Uttar Pradesh', district: 'Muzaffarnagar', crop: 'Sugarcane', season: 'Whole Year', area: 8.5 },
    { name: 'Bengal Rice (Autumn)', state: 'West Bengal', district: 'Bardhaman', crop: 'Rice', season: 'Autumn', area: 12.0 },
    { name: 'Karnataka Maize (Kharif)', state: 'Karnataka', district: 'Belagavi', crop: 'Maize', season: 'Kharif', area: 6.0 }
  ];

  public yieldForm = this.fb.group({
    state: ['Punjab', Validators.required],
    district: ['Ludhiana', [Validators.required, Validators.minLength(2)]],
    crop: ['Wheat', Validators.required],
    season: ['Rabi', Validators.required],
    area: [10.0, [Validators.required, Validators.min(0.01)]],
    crop_year: [2024, [Validators.required, Validators.min(1990), Validators.max(2035)]],
    model_type: ['dnn']
  });

  public applyPreset(preset: YieldPreset): void {
    this.yieldForm.patchValue({
      state: preset.state,
      district: preset.district,
      crop: preset.crop,
      season: preset.season,
      area: preset.area
    });
  }

  public onSubmit(): void {
    if (this.yieldForm.invalid) {
      this.yieldForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const val = this.yieldForm.getRawValue();
    const req = {
      state: val.state!,
      district: val.district!,
      crop: val.crop!,
      season: val.season!,
      area: Number(val.area),
      crop_year: Number(val.crop_year),
      model_type: val.model_type!
    };

    this.yieldService.predictYield(req).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.result.set(response.data);
        } else {
          this.errorMessage.set(response.error?.message || 'Yield prediction failed.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to connect to Yield Forecasting service.'
        );
      }
    });
  }

  public getProductivityLevel(yieldValue: number): { label: string; class: string } {
    if (yieldValue >= 4.0) {
      return { label: 'High Productivity', class: 'high' };
    } else if (yieldValue >= 2.0) {
      return { label: 'Moderate Productivity', class: 'moderate' };
    } else {
      return { label: 'Low / Dryland Yield', class: 'low' };
    }
  }
}
