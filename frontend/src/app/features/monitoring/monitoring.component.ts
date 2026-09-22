import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { forkJoin, Subscription, timer } from 'rxjs';
import { MonitoringService } from '../../core/services/monitoring.service';
import {
  ModelsMetadataResponse,
  ApiPerformanceMetricsResponse,
  SystemMonitoringHealthResponse,
  DataDriftResponse,
  PredictionDistributionResponse,
  ModelMetadataItem
} from '../../core/models/monitoring.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-monitoring',
  standalone: true,
  imports: [CommonModule, RouterModule, LoadingSpinnerComponent],
  templateUrl: './monitoring.component.html',
  styleUrl: './monitoring.component.css'
})
export class MonitoringComponent implements OnInit, OnDestroy {
  private monitoringService = inject(MonitoringService);
  private refreshSubscription?: Subscription;

  public activeTab = signal<'overview' | 'models' | 'telemetry' | 'drift' | 'distributions'>('overview');
  public isLoading = signal<boolean>(true);
  public isRefreshing = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public lastUpdated = signal<Date | null>(null);

  // Auto-refresh interval (0 = off, 15 = 15s, 30 = 30s, 60 = 60s)
  public autoRefreshInterval = signal<number>(30);

  // Data signals
  public healthData = signal<SystemMonitoringHealthResponse | null>(null);
  public modelsData = signal<ModelsMetadataResponse | null>(null);
  public metricsData = signal<ApiPerformanceMetricsResponse | null>(null);
  public driftData = signal<DataDriftResponse | null>(null);
  public distributionData = signal<PredictionDistributionResponse | null>(null);

  // Selected model for modal view
  public selectedModel = signal<ModelMetadataItem | null>(null);

  ngOnInit(): void {
    this.loadAllMonitoringData();
    this.setupAutoRefresh();
  }

  ngOnDestroy(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  public setTab(tab: 'overview' | 'models' | 'telemetry' | 'drift' | 'distributions'): void {
    this.activeTab.set(tab);
  }

  public setAutoRefresh(seconds: number): void {
    this.autoRefreshInterval.set(seconds);
    this.setupAutoRefresh();
  }

  private setupAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
    const intervalSec = this.autoRefreshInterval();
    if (intervalSec > 0) {
      this.refreshSubscription = timer(intervalSec * 1000, intervalSec * 1000).subscribe(() => {
        this.refreshData(true);
      });
    }
  }

  public loadAllMonitoringData(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      health: this.monitoringService.getMonitoringHealth(),
      models: this.monitoringService.getModelsMetadata(),
      metrics: this.monitoringService.getPerformanceMetrics(),
      drift: this.monitoringService.getDataDrift(),
      distributions: this.monitoringService.getPredictionDistributions()
    }).subscribe({
      next: (results) => {
        this.isLoading.set(false);
        this.isRefreshing.set(false);
        this.lastUpdated.set(new Date());

        if (results.health.success && results.health.data) {
          this.healthData.set(results.health.data);
        }
        if (results.models.success && results.models.data) {
          this.modelsData.set(results.models.data);
        }
        if (results.metrics.success && results.metrics.data) {
          this.metricsData.set(results.metrics.data);
        }
        if (results.drift.success && results.drift.data) {
          this.driftData.set(results.drift.data);
        }
        if (results.distributions.success && results.distributions.data) {
          this.distributionData.set(results.distributions.data);
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.isRefreshing.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to retrieve telemetry and monitoring telemetry.'
        );
      }
    });
  }

  public refreshData(background: boolean = false): void {
    if (!background) {
      this.isRefreshing.set(true);
    }
    this.monitoringService.getMonitoringHealth().subscribe({
      next: (res) => {
        if (res.success && res.data) this.healthData.set(res.data);
      }
    });
    this.monitoringService.getPerformanceMetrics().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.metricsData.set(res.data);
          this.lastUpdated.set(new Date());
          this.isRefreshing.set(false);
        }
      },
      error: () => this.isRefreshing.set(false)
    });
    this.monitoringService.getDataDrift().subscribe({
      next: (res) => {
        if (res.success && res.data) this.driftData.set(res.data);
      }
    });
    this.monitoringService.getPredictionDistributions().subscribe({
      next: (res) => {
        if (res.success && res.data) this.distributionData.set(res.data);
      }
    });
  }

  public openModelModal(model: ModelMetadataItem): void {
    this.selectedModel.set(model);
  }

  public closeModelModal(): void {
    this.selectedModel.set(null);
  }

  public formatUptime(seconds: number): string {
    if (!seconds || seconds <= 0) return '0s';
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor((seconds % (3600 * 24)) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);

    const parts: string[] = [];
    if (d > 0) parts.push(`${d}d`);
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    if (s > 0 || parts.length === 0) parts.push(`${s}s`);
    return parts.join(' ');
  }

  public getDriftBadgeClass(status: string): string {
    switch (status) {
      case 'HEALTHY':
        return 'badge-success';
      case 'MODERATE_DRIFT':
        return 'badge-warning';
      case 'DRIFT_DETECTED':
        return 'badge-danger';
      case 'INSUFFICIENT_DATA':
      default:
        return 'badge-neutral';
    }
  }

  public getHealthBadgeClass(status: string): string {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'loaded':
      case 'active':
        return 'badge-success';
      case 'degraded':
      case 'warning':
        return 'badge-warning';
      default:
        return 'badge-danger';
    }
  }
}
