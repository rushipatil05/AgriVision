import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PredictionHistoryService } from '../../core/services/prediction-history.service';
import { PredictionHistoryItem } from '../../core/models/prediction-history.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, RouterModule, LoadingSpinnerComponent, EmptyStateComponent],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css'
})
export class HistoryComponent implements OnInit {
  private historyService = inject(PredictionHistoryService);

  public isLoading = signal<boolean>(true);
  public errorMessage = signal<string | null>(null);
  public records = signal<PredictionHistoryItem[]>([]);
  public total = signal<number>(0);
  public totalPages = signal<number>(1);
  public currentPage = signal<number>(1);
  public pageSize = 10;
  public selectedFilter = signal<string>('ALL');

  // Modals state
  public selectedItem = signal<PredictionHistoryItem | null>(null);
  public itemToDelete = signal<PredictionHistoryItem | null>(null);
  public isDeleting = signal<boolean>(false);

  ngOnInit(): void {
    this.fetchHistory();
  }

  public setFilter(type: string): void {
    this.selectedFilter.set(type);
    this.currentPage.set(1);
    this.fetchHistory();
  }

  public setPage(page: number): void {
    if (page < 1 || page > this.totalPages()) return;
    this.currentPage.set(page);
    this.fetchHistory();
  }

  public fetchHistory(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    const filter = this.selectedFilter();
    this.historyService.getHistory(this.currentPage(), this.pageSize, filter).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.records.set(response.data.records);
          this.total.set(response.data.total);
          this.totalPages.set(response.data.total_pages || Math.ceil(response.data.total / this.pageSize) || 1);
        } else {
          this.errorMessage.set(response.error?.message || 'Failed to retrieve prediction history.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to communicate with prediction history service.'
        );
      }
    });
  }

  public openDetailModal(item: PredictionHistoryItem): void {
    this.selectedItem.set(item);
  }

  public closeDetailModal(): void {
    this.selectedItem.set(null);
  }

  public promptDelete(item: PredictionHistoryItem): void {
    this.itemToDelete.set(item);
  }

  public cancelDelete(): void {
    this.itemToDelete.set(null);
  }

  public confirmDelete(): void {
    const item = this.itemToDelete();
    if (!item) return;

    this.isDeleting.set(true);
    this.historyService.deletePrediction(item.id).subscribe({
      next: (response) => {
        this.isDeleting.set(false);
        this.itemToDelete.set(null);
        if (response.success) {
          this.fetchHistory();
        }
      },
      error: (err) => {
        this.isDeleting.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to delete record.'
        );
      }
    });
  }

  public formatJson(data: any): string {
    return JSON.stringify(data, null, 2);
  }

  public formatSummary(item: PredictionHistoryItem): string {
    const type = item.prediction_type.toUpperCase();
    const res = item.prediction_result;
    if (!res) return 'Completed';

    if (type.includes('DECISION')) {
      return `Decision: ${res.recommended_crop} (Score: ${res.decision_score?.toFixed(1)}/100, Yield: ${res.predicted_yield?.toFixed(2)} t/ha, ₹${res.forecast_price?.toFixed(2)}/qtl)`;
    } else if (type.includes('CROP')) {
      return `Recommended: ${res.recommended_crop} (${(res.confidence * 100).toFixed(1)}%)`;
    } else if (type.includes('PRICE')) {
      return `${res.commodity} (${res.market}): ₹${res.forecasted_end_price?.toFixed(2)} (${res.trend_direction})`;
    } else if (type.includes('YIELD')) {
      return `${res.crop} (${res.district}): ${res.predicted_yield_tonnes_per_hectare?.toFixed(2)} t/ha`;
    }
    return 'Inference recorded';
  }
}
