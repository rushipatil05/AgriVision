import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { Chart, ChartConfiguration, ChartData, registerables } from 'chart.js';

Chart.register(...registerables);
import { PriceService } from '../../core/services/price.service';
import { PriceForecastResponse } from '../../core/models/price.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-price-forecast',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, BaseChartDirective, LoadingSpinnerComponent],
  templateUrl: './price-forecast.component.html',
  styleUrl: './price-forecast.component.css'
})
export class PriceForecastComponent {
  private fb = inject(FormBuilder);
  private priceService = inject(PriceService);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public result = signal<PriceForecastResponse | null>(null);

  public commodities = [
    { name: 'Wheat', basePrice: 2200, volatility: 40 },
    { name: 'Rice', basePrice: 3100, volatility: 50 },
    { name: 'Onion', basePrice: 1650, volatility: 80 },
    { name: 'Potato', basePrice: 1250, volatility: 35 },
    { name: 'Tomato', basePrice: 1950, volatility: 110 },
    { name: 'Cotton', basePrice: 6800, volatility: 120 },
    { name: 'Maize', basePrice: 1950, volatility: 45 },
    { name: 'Soybean', basePrice: 4400, volatility: 90 },
    { name: 'Mustard', basePrice: 5200, volatility: 75 }
  ];

  public markets = ['Azadpur (Delhi)', 'Lasalgaon (Nashik)', 'Khanna (Punjab)', 'Agra (UP)', 'Karnal (Haryana)', 'Vashi (Mumbai)', 'Guntur (AP)'];

  public priceForm = this.fb.group({
    commodity: ['Wheat', Validators.required],
    market: ['Azadpur (Delhi)', Validators.required],
    forecast_horizon: [7, [Validators.required, Validators.min(1), Validators.max(30)]],
    pricesInput: ['', Validators.required]
  });

  // Price Trajectory Multi-Line Chart
  public lineChartType = 'line' as const;
  public lineChartData: ChartData<'line'> = {
    labels: [],
    datasets: []
  };

  public lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#cbd5e1',
          font: { family: 'Inter, system-ui, sans-serif', size: 12 }
        }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#fbbf24',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context) => ` Price: ₹${Number(context.raw).toFixed(2)} / qtl`
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.3)' },
        ticks: { color: '#94a3b8' }
      },
      y: {
        grid: { color: 'rgba(51, 65, 85, 0.4)' },
        ticks: {
          color: '#cbd5e1',
          callback: (value) => `₹${value}`
        }
      }
    }
  };

  constructor() {
    this.generateSampleSequence('Wheat');
  }

  public onCommodityChange(event: Event): void {
    const selected = (event.target as HTMLSelectElement).value;
    this.generateSampleSequence(selected);
  }

  public generateSampleSequence(commodityName?: string): void {
    const comm = commodityName || this.priceForm.get('commodity')?.value || 'Wheat';
    const match = this.commodities.find((c) => c.name.toLowerCase() === comm.toLowerCase()) || this.commodities[0];

    const sequence: number[] = [];
    let current = match.basePrice;

    for (let i = 0; i < 30; i++) {
      const delta = (Math.random() - 0.48) * match.volatility;
      current = Math.max(100, Math.round((current + delta) * 100) / 100);
      sequence.push(current);
    }

    this.priceForm.patchValue({
      pricesInput: sequence.join(', ')
    });
  }

  public onSubmit(): void {
    if (this.priceForm.invalid) {
      this.priceForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const formVal = this.priceForm.getRawValue();
    const rawPrices = (formVal.pricesInput || '')
      .split(',')
      .map((s) => parseFloat(s.trim()))
      .filter((n) => !isNaN(n));

    if (rawPrices.length < 30) {
      this.isLoading.set(false);
      this.errorMessage.set('Please provide at least 30 historical price points for LSTM accuracy (use "Generate Real Sequence").');
      return;
    }

    const req = {
      commodity: formVal.commodity!,
      market: formVal.market!,
      historical_prices: rawPrices,
      forecast_horizon: Number(formVal.forecast_horizon)
    };

    this.priceService.forecastPrice(req).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.result.set(response.data);
          this.updateChart(rawPrices, response.data);
        } else {
          this.errorMessage.set(response.error?.message || 'Price forecast failed.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to connect to Price Forecasting service.'
        );
      }
    });
  }

  private updateChart(historical: number[], res: PriceForecastResponse): void {
    const histLabels = historical.map((_, i) => `T-${historical.length - 1 - i}`);
    const forecastLabels = res.forecasts.map((f) => `Day +${f.day}`);
    const labels = [...histLabels, ...forecastLabels];

    const histData = [...historical, ...Array(res.forecasts.length).fill(null)];

    const forecastData = [
      ...Array(historical.length - 1).fill(null),
      historical[historical.length - 1],
      ...res.forecasts.map((f) => f.predicted_modal_price)
    ];

    this.lineChartData = {
      labels,
      datasets: [
        {
          label: 'Historical Lookback (₹)',
          data: histData,
          borderColor: '#94a3b8',
          backgroundColor: 'rgba(148, 163, 184, 0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 2,
          pointHoverRadius: 5
        },
        {
          label: 'Forecast Trajectory (₹)',
          data: forecastData,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          borderDash: [6, 4],
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: '#fbbf24',
          pointHoverRadius: 7
        }
      ]
    };
  }
}
