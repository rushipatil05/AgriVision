# AgriPulse Frontend Architecture Specification

**Project**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Framework**: Angular 18+ (Standalone Component Architecture)  
**Location**: `frontend/`  
**API Integration**: FastAPI REST Endpoints (`http://localhost:8000/api/v1`)

---

## 1. Architecture Overview

The AgriPulse frontend is built with Angular standalone components, modern signals for state reactivity, Chart.js for data visualization, and token-based JWT authentication.

```
                           [ Angular 18 Single Page App ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  [ Layout & Shell ]             [ Reactive Forms ]             [ Visualizations ]
  - App Root                     - Login / Register Form        - Top-5 Probabilities Bar
  - Sticky Top Navbar            - Crop Soil Form (7 params)    - Nutrient & Climate Radar
  - Collapsible Sidebar          - Price Lookback Config (30d)  - Multi-Day Price Trajectory
  - Footer                       - Yield Geographic Inputs      - Prediction Doughnut Chart
                                         │
                                         ▼
                             [ Core Service Layer ]
                             - AuthService (JWT & Signals)
                             - CropService (/crop/recommend)
                             - PriceService (/price/forecast)
                             - YieldService (/yield/predict)
                             - HistoryService (/predictions/history)
                             - SystemService (/health, /models/status)
                                         │
                             [ Auth Interceptor (HTTP) ]
                             - Auto-attaches Bearer <JWT>
                             - Auto-redirects 401 to /login
                                         │
                                         ▼
                           [ FastAPI Backend REST API ]
```

---

## 2. Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.ts                  # Root App shell hosting Navbar, Sidebar, Footer, RouterOutlet
│   │   ├── app.html
│   │   ├── app.css
│   │   ├── app.routes.ts           # Route declarations with authGuard protection
│   │   ├── app.config.ts           # Application config (HttpClient, Interceptors, Router, Animations)
│   │   ├── core/
│   │   │   ├── guards/
│   │   │   │   └── auth.guard.ts           # Route guard protecting private views
│   │   │   ├── interceptors/
│   │   │   │   └── auth.interceptor.ts     # Injects Authorization Bearer header
│   │   │   ├── models/                     # TypeScript interfaces matching backend schemas
│   │   │   │   ├── auth.model.ts
│   │   │   │   ├── common.model.ts
│   │   │   │   ├── crop.model.ts
│   │   │   │   ├── price.model.ts
│   │   │   │   ├── yield.model.ts
│   │   │   │   ├── user.model.ts
│   │   │   │   └── prediction-history.model.ts
│   │   │   └── services/                   # HTTP client service providers
│   │   │       ├── auth.service.ts
│   │   │       ├── crop.service.ts
│   │   │       ├── price.service.ts
│   │   │       ├── yield.service.ts
│   │   │       ├── prediction-history.service.ts
│   │   │       └── system.service.ts
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── login/                  # Login page with validation & error handling
│   │   │   │   └── register/               # User registration page
│   │   │   ├── dashboard/                  # Central overview dashboard with status & charts
│   │   │   ├── crop-recommendation/        # LSTM 7-feature soil form + Bar & Radar charts
│   │   │   ├── price-forecast/             # LSTM multi-step lookback + Price line chart
│   │   │   ├── yield-forecast/             # DNN yield regressor + Productivity metric card
│   │   │   ├── history/                    # Paginated audit history + JSON modal & delete
│   │   │   ├── profile/                    # User account & session details
│   │   │   └── not-found/                  # 404 page
│   │   ├── layout/
│   │   │   ├── navbar/                     # Brand header with active user menu
│   │   │   ├── sidebar/                    # Collapsible navigation drawer
│   │   │   └── footer/                     # Platform footer
│   │   └── shared/
│   │       └── components/
│   │           ├── loading-spinner/        # Pulse loading indicator
│   │           ├── stat-card/              # Metric card with color themes
│   │           └── empty-state/            # Empty list display
│   ├── environments/
│   │   ├── environment.ts                  # Production API baseUrl (http://localhost:8000/api/v1)
│   │   └── environment.development.ts      # Development API baseUrl
│   ├── styles.css                          # Global dark theme & typography
│   └── index.html                          # HTML shell with Google Fonts & Material Symbols
├── angular.json
├── package.json
└── tsconfig.json
```

---

## 3. Visualization Subsystems

| Module | Chart Type | Library | Purpose |
| :--- | :--- | :--- | :--- |
| **Crop Recommendation** | Horizontal Bar Chart | `Chart.js` | Top-5 ranked crop probability distributions |
| **Crop Recommendation** | Radar Chart | `Chart.js` | Normalized soil & climate profile (N, P, K, Temp, Humidity, pH, Rain) |
| **Price Forecasting** | Multi-Line Chart | `Chart.js` | Historical 30-day lookback (solid) vs. 1–30d forecast trajectory (dashed) |
| **Yield Forecasting** | Productivity Gauge Card | Custom SVG/CSS | Real-time harvest estimation & Tonnes/Ha classification |
| **Dashboard** | Doughnut Chart | `Chart.js` | User prediction activity breakdown across AI subsystems |

---

## 4. Security & Authentication Flow

1. **Token Persistence**: JWT tokens are securely stored in browser `localStorage` and managed reactively with Angular Signals.
2. **Auto Header Injection**: `authInterceptor` inspects every outgoing HTTP call and attaches `Authorization: Bearer <token>` when a valid token is present.
3. **Route Protection**: `authGuard` verifies user authentication state prior to route activation. Unauthenticated requests are redirected to `/login` with return URL parameters.
4. **401 Interception**: When token expiration occurs, the interceptor automatically clears session state and redirects to `/login`.
