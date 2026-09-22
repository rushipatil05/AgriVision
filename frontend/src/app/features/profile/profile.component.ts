import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { PredictionHistoryService } from '../../core/services/prediction-history.service';
import { User } from '../../core/models/user.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  public authService = inject(AuthService);
  private historyService = inject(PredictionHistoryService);
  private router = inject(Router);

  public user = signal<User | null>(null);
  public totalPredictions = signal<number>(0);
  public isLoading = signal<boolean>(true);

  ngOnInit(): void {
    this.user.set(this.authService.currentUser());
    this.authService.fetchCurrentUser().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.user.set(res.data);
        }
      }
    });

    this.historyService.getHistory(1, 1).subscribe({
      next: (res) => {
        this.isLoading.set(false);
        if (res.success && res.data) {
          this.totalPredictions.set(res.data.total);
        }
      },
      error: () => this.isLoading.set(false)
    });
  }

  public onLogout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/login']);
    });
  }
}
