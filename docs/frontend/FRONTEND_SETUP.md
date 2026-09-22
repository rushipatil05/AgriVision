# AgriPulse Frontend Setup & Developer Guide

## 1. Prerequisites

- **Node.js**: $\ge 18.0.0$ (Tested on Node.js v26.7.0 / v20.x)
- **NPM**: $\ge 9.0.0$
- **Backend API**: AgriPulse FastAPI server running on `http://localhost:8000`

---

## 2. Quickstart Installation

From the project root:

```bash
cd frontend
npm install --legacy-peer-deps
```

---

## 3. Development Server

Run the development server:

```bash
npm start
# OR
npx ng serve
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any source files.

---

## 4. Production Build

Build the optimized production bundles:

```bash
npm run build
# OR
npx ng build
```

The build artifacts will be stored in the `frontend/dist/agripulse-ui` directory.

---

## 5. Running Automated Unit Tests

Run unit tests via Vitest:

```bash
npm test
# OR
npx ng test --watch=false
```

---

## 6. Environment Configuration

Environment settings are configured in:
- `src/environments/environment.ts` (Production)
- `src/environments/environment.development.ts` (Development)

Default configuration points to the local FastAPI backend:
```ts
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/api/v1'
};
```
