import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then((m) => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register.component').then((m) => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'crop-recommendation',
    loadComponent: () =>
      import('./features/crop-recommendation/crop-recommendation.component').then(
        (m) => m.CropRecommendationComponent
      ),
    canActivate: [authGuard]
  },
  {
    path: 'price-forecast',
    loadComponent: () =>
      import('./features/price-forecast/price-forecast.component').then(
        (m) => m.PriceForecastComponent
      ),
    canActivate: [authGuard]
  },
  {
    path: 'yield-forecast',
    loadComponent: () =>
      import('./features/yield-forecast/yield-forecast.component').then(
        (m) => m.YieldForecastComponent
      ),
    canActivate: [authGuard]
  },
  {
    path: 'decision-support',
    loadComponent: () =>
      import('./features/decision-support/decision-support.component').then(
        (m) => m.DecisionSupportComponent
      ),
    canActivate: [authGuard]
  },
  {
    path: 'history',
    loadComponent: () =>
      import('./features/history/history.component').then((m) => m.HistoryComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./features/profile/profile.component').then((m) => m.ProfileComponent),
    canActivate: [authGuard]
  },
  {
    path: 'monitoring',
    loadComponent: () =>
      import('./features/monitoring/monitoring.component').then((m) => m.MonitoringComponent),
    canActivate: [authGuard]
  },
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found.component').then((m) => m.NotFoundComponent)
  }
];
