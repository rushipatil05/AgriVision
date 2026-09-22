import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { Chart, ChartConfiguration, ChartData, registerables } from 'chart.js';
import { AuthService } from '../../core/services/auth.service';
import { SystemService } from '../../core/services/system.service';
import { PredictionHistoryService } from '../../core/services/prediction-history.service';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { ModelsStatusResponse } from '../../core/models/common.model';
import { PredictionHistoryItem } from '../../core/models/prediction-history.model';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    BaseChartDirective,
    StatCardComponent,
    LoadingSpinnerComponent,
    EmptyStateComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  public authService = inject(AuthService);
  private systemService = inject(SystemService);
  private historyService = inject(PredictionHistoryService);

  public isLoading = signal<boolean>(true);
  public modelsStatus = signal<ModelsStatusResponse | null>(null);
  public recentHistory = signal<PredictionHistoryItem[]>([]);
  public totalPredictions = signal<number>(0);

  // Doughnut Chart for Prediction Type Distribution
  public doughnutChartType = 'doughnut' as const;
  public doughnutChartData: ChartData<'doughnut'> = {
    labels: ['Crop Recommendation', 'Price Forecast', 'Yield Forecast', 'Decision Support'],
    datasets: [
      {
        data: [0, 0, 0, 0],
        backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'],
        hoverBackgroundColor: ['#059669', '#d97706', '#2563eb', '#7c3aed'],
        borderColor: '#1e293b',
        borderWidth: 2
      }
    ]
  };

  public doughnutChartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#cbd5e1',
          padding: 16,
          font: {
            family: 'Inter, system-ui, sans-serif',
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6
      }
    },
    cutout: '70%'
  };

  ngOnInit(): void {
    this.loadDashboardData();
  }

  public loadDashboardData(): void {
    this.isLoading.set(true);

    // Fetch Models Status
    this.systemService.getModelsStatus().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.modelsStatus.set(res.data);
        }
      },
      error: () => console.warn('Could not load models status')
    });

    // Fetch Recent Predictions
    this.historyService.getHistory(1, 5).subscribe({
      next: (res) => {
        this.isLoading.set(false);
        if (res.success && res.data) {
          this.totalPredictions.set(res.data.total);
          this.recentHistory.set(res.data.records);
          this.updateChartDistribution(res.data.records);
        }
      },
      error: () => {
        this.isLoading.set(false);
      }
    });
  }

  private updateChartDistribution(records: PredictionHistoryItem[]): void {
    let cropCount = 0;
    let priceCount = 0;
    let yieldCount = 0;
    let decisionCount = 0;

    records.forEach((r) => {
      const type = r.prediction_type.toUpperCase();
      if (type.includes('DECISION')) decisionCount++;
      else if (type.includes('CROP')) cropCount++;
      else if (type.includes('PRICE')) priceCount++;
      else if (type.includes('YIELD')) yieldCount++;
    });

    // If no records yet, provide initial baseline sample
    if (cropCount === 0 && priceCount === 0 && yieldCount === 0 && decisionCount === 0) {
      cropCount = 1;
      priceCount = 1;
      yieldCount = 1;
      decisionCount = 1;
    }

    this.doughnutChartData = {
      labels: ['Crop Recommendation', 'Price Forecast', 'Yield Forecast', 'Decision Support'],
      datasets: [
        {
          data: [cropCount, priceCount, yieldCount, decisionCount],
          backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'],
          hoverBackgroundColor: ['#059669', '#d97706', '#2563eb', '#7c3aed'],
          borderColor: '#1e293b',
          borderWidth: 2
        }
      ]
    };
  }

  public formatTypeBadge(type: string): string {
    return type.replace(/_/g, ' ');
  }
}
