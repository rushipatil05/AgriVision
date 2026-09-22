import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { DecisionService } from '../../core/services/decision.service';
import { DecisionRecommendationResponse, AlternativeCropEvaluation } from '../../core/models/decision.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

interface DecisionPreset {
  name: string;
  description: string;
  values: {
    N: number;
    P: number;
    K: number;
    temperature: number;
    humidity: number;
    ph: number;
    rainfall: number;
    state: string;
    district: string;
    season: string;
    area: number;
    market: string;
    forecast_horizon: number;
  };
}

@Component({
  selector: 'app-decision-support',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    BaseChartDirective,
    LoadingSpinnerComponent
  ],
  templateUrl: './decision-support.component.html',
  styleUrl: './decision-support.component.css'
})
export class DecisionSupportComponent {
  private fb = inject(FormBuilder);
  private decisionService = inject(DecisionService);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public result = signal<DecisionRecommendationResponse | null>(null);

  public states = [
    'Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka',
    'Tamil Nadu', 'Andhra Pradesh', 'Madhya Pradesh', 'West Bengal', 'Gujarat', 'Rajasthan', 'Bihar'
  ];

  public seasons = ['Kharif', 'Rabi', 'Summer', 'Autumn', 'Winter', 'Whole Year'];

  public markets = [
    'Azadpur (Delhi)', 'Lasalgaon (Nashik)', 'Khanna (Punjab)', 'Agra (UP)',
    'Karnal (Haryana)', 'Vashi (Mumbai)', 'Guntur (AP)'
  ];

  public presets: DecisionPreset[] = [
    {
      name: 'Punjab Wheat (Rabi)',
      description: 'Temperate loam, optimal N-P-K, Ludhiana district',
      values: {
        N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9,
        state: 'Punjab', district: 'Ludhiana', season: 'Rabi', area: 10.0,
        market: 'Khanna (Punjab)', forecast_horizon: 7
      }
    },
    {
      name: 'Maharashtra Cotton (Kharif)',
      description: 'High nitrogen black soil profile, Nagpur district',
      values: {
        N: 117, P: 46, K: 19, temperature: 24.0, humidity: 79.8, ph: 6.9, rainfall: 90.8,
        state: 'Maharashtra', district: 'Nagpur', season: 'Kharif', area: 12.0,
        market: 'Lasalgaon (Nashik)', forecast_horizon: 7
      }
    },
    {
      name: 'UP Sugarcane (Whole Year)',
      description: 'Alluvial soil with high water retention, Muzaffarnagar',
      values: {
        N: 100, P: 35, K: 40, temperature: 26.0, humidity: 70.0, ph: 6.8, rainfall: 140.0,
        state: 'Uttar Pradesh', district: 'Muzaffarnagar', season: 'Whole Year', area: 8.0,
        market: 'Agra (UP)', forecast_horizon: 7
      }
    },
    {
      name: 'Bengal Rice (Autumn)',
      description: 'Deltaic alluvial clay loam with heavy monsoon rain',
      values: {
        N: 90, P: 42, K: 43, temperature: 25.5, humidity: 85.0, ph: 6.4, rainfall: 220.0,
        state: 'West Bengal', district: 'Bardhaman', season: 'Autumn', area: 15.0,
        market: 'Azadpur (Delhi)', forecast_horizon: 7
      }
    },
    {
      name: 'Karnataka Maize (Kharif)',
      description: 'Moderate nitrogen warm red sandy loam, Belagavi',
      values: {
        N: 71, P: 54, K: 20, temperature: 22.6, humidity: 65.4, ph: 5.7, rainfall: 82.3,
        state: 'Karnataka', district: 'Belagavi', season: 'Kharif', area: 6.0,
        market: 'Vashi (Mumbai)', forecast_horizon: 7
      }
    }
  ];

  public decisionForm = this.fb.group({
    N: [90, [Validators.required, Validators.min(0), Validators.max(200)]],
    P: [42, [Validators.required, Validators.min(0), Validators.max(200)]],
    K: [43, [Validators.required, Validators.min(0), Validators.max(250)]],
    temperature: [20.9, [Validators.required, Validators.min(0), Validators.max(60)]],
    humidity: [82.0, [Validators.required, Validators.min(0), Validators.max(100)]],
    ph: [6.5, [Validators.required, Validators.min(3.0), Validators.max(10.0)]],
    rainfall: [202.9, [Validators.required, Validators.min(0), Validators.max(500)]],
    state: ['Punjab', Validators.required],
    district: ['Ludhiana', [Validators.required, Validators.minLength(2)]],
    season: ['Rabi', Validators.required],
    area: [10.0, [Validators.required, Validators.min(0.1)]],
    crop_year: [2024, [Validators.required, Validators.min(1990), Validators.max(2050)]],
    market: ['Azadpur (Delhi)', Validators.required],
    forecast_horizon: [7, Validators.required]
  });

  // Comparison Multi-Bar Chart
  public barChartType = 'bar' as const;
  public barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#cbd5e1',
          font: { family: 'Inter, system-ui, sans-serif', size: 11 }
        }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 10
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#f8fafc', font: { weight: 'bold' } }
      },
      y: {
        min: 0,
        max: 100,
        grid: { color: 'rgba(51, 65, 85, 0.4)' },
        ticks: {
          color: '#94a3b8',
          callback: (value) => `${value} pts`
        }
      }
    }
  };

  public applyPreset(preset: DecisionPreset): void {
    this.decisionForm.patchValue(preset.values);
  }

  public onSubmit(): void {
    if (this.decisionForm.invalid) {
      this.decisionForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const val = this.decisionForm.getRawValue();
    const req = {
      N: Number(val.N),
      P: Number(val.P),
      K: Number(val.K),
      temperature: Number(val.temperature),
      humidity: Number(val.humidity),
      ph: Number(val.ph),
      rainfall: Number(val.rainfall),
      state: val.state!,
      district: val.district!,
      season: val.season!,
      area: Number(val.area),
      crop_year: Number(val.crop_year),
      market: val.market!.split(' ')[0], // clean market city name
      forecast_horizon: Number(val.forecast_horizon)
    };

    this.decisionService.recommendDecision(req).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.result.set(response.data);
          this.updateComparisonChart(response.data.alternatives);
        } else {
          this.errorMessage.set(response.error?.message || 'Decision support failed.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to connect to Decision Support service.'
        );
      }
    });
  }

  private updateComparisonChart(alternatives: AlternativeCropEvaluation[]): void {
    const labels = alternatives.map((a) => `#${a.rank} ${a.crop}`);
    const suitScores = alternatives.map((a) => a.suitability_score);
    const yieldScores = alternatives.map((a) => a.yield_score);
    const marketScores = alternatives.map((a) => a.market_score);
    const decisionScores = alternatives.map((a) => a.decision_score);

    this.barChartData = {
      labels,
      datasets: [
        {
          label: 'Overall Decision Score',
          data: decisionScores,
          backgroundColor: '#10b981',
          borderRadius: 6
        },
        {
          label: 'Suitability (40%)',
          data: suitScores,
          backgroundColor: '#3b82f6',
          borderRadius: 6
        },
        {
          label: 'Yield Score (35%)',
          data: yieldScores,
          backgroundColor: '#8b5cf6',
          borderRadius: 6
        },
        {
          label: 'Market Score (25%)',
          data: marketScores,
          backgroundColor: '#f59e0b',
          borderRadius: 6
        }
      ]
    };
  }
}
