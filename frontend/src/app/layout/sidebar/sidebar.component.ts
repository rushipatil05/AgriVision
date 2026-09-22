import { Component, input, output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent {
  public isOpen = input<boolean>(false);
  public closeSidebar = output<void>();

  public authService = inject(AuthService);
  private router = inject(Router);

  public navItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: 'dashboard',
      description: 'Overview & Model Metrics'
    },
    {
      label: 'Crop Recommendation',
      path: '/crop-recommendation',
      icon: 'eco',
      description: 'LSTM Soil & Climate AI'
    },
    {
      label: 'Price Forecasting',
      path: '/price-forecast',
      icon: 'trending_up',
      description: 'LSTM Market Trajectory'
    },
    {
      label: 'Yield Forecasting',
      path: '/yield-forecast',
      icon: 'agriculture',
      description: 'DNN Production Regressor'
    },
    {
      label: 'AI Decision Support',
      path: '/decision-support',
      icon: 'psychology',
      description: 'Integrated Multi-Factor AI'
    },
    {
      label: 'Prediction History',
      path: '/history',
      icon: 'history',
      description: 'Audited Prediction Logs'
    },
    {
      label: 'System Monitoring',
      path: '/monitoring',
      icon: 'monitoring',
      description: 'MLOps, Drift & Health'
    },
    {
      label: 'User Profile',
      path: '/profile',
      icon: 'person',
      description: 'Account & Preferences'
    }
  ];

  public onClose(): void {
    this.closeSidebar.emit();
  }

  public onLogout(): void {
    this.authService.logout().subscribe(() => {
      this.onClose();
      this.router.navigate(['/login']);
    });
  }
}
