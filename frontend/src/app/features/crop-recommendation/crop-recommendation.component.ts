import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { Chart, ChartConfiguration, ChartData, registerables } from 'chart.js';

Chart.register(...registerables);
import { CropService } from '../../core/services/crop.service';
import { CropRecommendationResponse } from '../../core/models/crop.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

interface PresetOption {
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
  };
}

@Component({
  selector: 'app-crop-recommendation',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, BaseChartDirective, LoadingSpinnerComponent],
  templateUrl: './crop-recommendation.component.html',
  styleUrl: './crop-recommendation.component.css'
})
export class CropRecommendationComponent {
  private fb = inject(FormBuilder);
  private cropService = inject(CropService);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public result = signal<CropRecommendationResponse | null>(null);

  public presets: PresetOption[] = [
    {
      name: 'Rice Condition',
      description: 'High moisture & rainfall alluvial soil',
      values: { N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9 }
    },
    {
      name: 'Maize Condition',
      description: 'Moderate nitrogen & warm temperate climate',
      values: { N: 71, P: 54, K: 20, temperature: 22.6, humidity: 65.4, ph: 5.7, rainfall: 82.3 }
    },
    {
      name: 'Cotton Condition',
      description: 'High nitrogen & black cotton soil profile',
      values: { N: 117, P: 46, K: 19, temperature: 24.0, humidity: 79.8, ph: 6.9, rainfall: 90.8 }
    },
    {
      name: 'Coffee Condition',
      description: 'Subtropical highland loam with good rain',
      values: { N: 101, P: 29, K: 30, temperature: 26.5, humidity: 58.1, ph: 6.8, rainfall: 158.1 }
    },
    {
      name: 'Apple Condition',
      description: 'High potassium cold temperate soil',
      values: { N: 20, P: 134, K: 199, temperature: 22.7, humidity: 92.3, ph: 5.9, rainfall: 112.7 }
    }
  ];

  public cropForm = this.fb.group({
    N: [90, [Validators.required, Validators.min(0), Validators.max(140)]],
    P: [42, [Validators.required, Validators.min(5), Validators.max(145)]],
    K: [43, [Validators.required, Validators.min(5), Validators.max(205)]],
    temperature: [20.9, [Validators.required, Validators.min(8), Validators.max(45)]],
    humidity: [82.0, [Validators.required, Validators.min(14), Validators.max(100)]],
    ph: [6.5, [Validators.required, Validators.min(3.5), Validators.max(10.0)]],
    rainfall: [202.9, [Validators.required, Validators.min(20), Validators.max(300)]]
  });

  // Top 5 Probabilities Horizontal Bar Chart
  public barChartType = 'bar' as const;
  public barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#ccfbf1'],
        borderRadius: 8,
        barThickness: 24
      }
    ]
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` Probability: ${(Number(context.raw) * 100).toFixed(2)}%`
        },
        backgroundColor: '#0f172a',
        borderColor: '#334155',
        borderWidth: 1,
        titleColor: '#f8fafc',
        bodyColor: '#34d399'
      }
    },
    scales: {
      x: {
        min: 0,
        max: 1,
        grid: { color: 'rgba(51, 65, 85, 0.4)' },
        ticks: {
          color: '#94a3b8',
          callback: (value) => `${(Number(value) * 100).toFixed(0)}%`
        }
      },
      y: {
        grid: { display: false },
        ticks: { color: '#f8fafc', font: { weight: 'bold' } }
      }
    }
  };

  // Radar Chart for Normalized Soil Profile
  public radarChartType = 'radar' as const;
  public radarChartData: ChartData<'radar'> = {
    labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH', 'Rainfall'],
    datasets: [
      {
        data: [],
        label: 'Input Soil Profile (Normalized)',
        backgroundColor: 'rgba(16, 185, 129, 0.25)',
        borderColor: '#10b981',
        pointBackgroundColor: '#34d399',
        pointBorderColor: '#ffffff',
        borderWidth: 2
      }
    ]
  };

  public radarChartOptions: ChartConfiguration<'radar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#cbd5e1' }
      }
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { display: false, stepSize: 20 },
        grid: { color: 'rgba(51, 65, 85, 0.5)' },
        angleLines: { color: 'rgba(51, 65, 85, 0.5)' },
        pointLabels: {
          color: '#cbd5e1',
          font: { size: 11, weight: 'bold' }
        }
      }
    }
  };

  public applyPreset(preset: PresetOption): void {
    this.cropForm.setValue(preset.values);
  }

  public onSubmit(): void {
    if (this.cropForm.invalid) {
      this.cropForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const formVal = this.cropForm.getRawValue();
    const req = {
      N: Number(formVal.N),
      P: Number(formVal.P),
      K: Number(formVal.K),
      temperature: Number(formVal.temperature),
      humidity: Number(formVal.humidity),
      ph: Number(formVal.ph),
      rainfall: Number(formVal.rainfall),
      top_k: 5
    };

    this.cropService.recommendCrop(req).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.result.set(response.data);
          this.updateCharts(response.data, req);
        } else {
          this.errorMessage.set(response.error?.message || 'Recommendation failed.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to connect to Crop Recommendation service.'
        );
      }
    });
  }

  private updateCharts(res: CropRecommendationResponse, inputs: any): void {
    const top = res.recommendations || (res as any).top_recommendations || [];
    const labels = top.map((t) => t.crop.charAt(0).toUpperCase() + t.crop.slice(1));
    const probs = top.map((t) => t.probability);

    this.barChartData = {
      labels,
      datasets: [
        {
          data: probs,
          backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#ccfbf1'],
          borderRadius: 8,
          barThickness: 24
        }
      ]
    };

    const normN = Math.min(100, Math.max(0, (inputs.N / 140) * 100));
    const normP = Math.min(100, Math.max(0, (inputs.P / 145) * 100));
    const normK = Math.min(100, Math.max(0, (inputs.K / 205) * 100));
    const normTemp = Math.min(100, Math.max(0, ((inputs.temperature - 8) / (45 - 8)) * 100));
    const normHum = Math.min(100, Math.max(0, ((inputs.humidity - 14) / (100 - 14)) * 100));
    const normPh = Math.min(100, Math.max(0, ((inputs.ph - 3.5) / (10 - 3.5)) * 100));
    const normRain = Math.min(100, Math.max(0, ((inputs.rainfall - 20) / (300 - 20)) * 100));

    this.radarChartData = {
      labels: ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall'],
      datasets: [
        {
          data: [normN, normP, normK, normTemp, normHum, normPh, normRain],
          label: 'Soil & Climate Profile (%)',
          backgroundColor: 'rgba(16, 185, 129, 0.25)',
          borderColor: '#10b981',
          pointBackgroundColor: '#34d399',
          pointBorderColor: '#ffffff',
          borderWidth: 2
        }
      ]
    };
  }
}
