# LEVEL 8 PRODUCTION RUNBOOK & OPERATIONS MANUAL

**Platform**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Environment**: Production Orchestration (Docker / FastAPI / PostgreSQL / Angular)  
**Status**: Operations & Disaster Recovery Specification  

---

## 1. System Services & Architecture Overview

| Service | Port | Base URL | Health Check Route |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 15** | 5432 | `localhost:5432` | `pg_isready -U postgres` |
| **FastAPI Backend** | 8000 | `http://localhost:8000/api/v1` | `/api/v1/monitoring/health` |
| **Angular Frontend** | 4200 / 80 | `http://localhost:4200` | `/health` (Nginx probe) |

---

## 2. Standard Startup & Shutdown Procedures

### 2.1 Starting Services via Docker Compose
```bash
# Build and launch all services in detached mode
docker-compose -f docker/docker-compose.yml up -d --build

# Verify running container health
docker-compose -f docker/docker-compose.yml ps
```

### 2.2 Local Development Startup
```bash
# 1. Start PostgreSQL (ensure postgres service is running)

# 2. Start FastAPI Backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start Angular Frontend
cd frontend
npm start
```

### 2.3 Graceful Shutdown
```bash
docker-compose -f docker/docker-compose.yml down
```

---

## 3. Production Health Probes & Monitoring

### 3.1 Automated Liveness & Readiness Probes
- **Liveness Probe**: `GET /api/v1/health`
  - Returns `{"status": "healthy"}`
  - Frequency: 15 seconds
  - Timeout: 3 seconds
- **Readiness Probe**: `GET /api/v1/monitoring/health`
  - Validates PostgreSQL database connection latency
  - Validates preloaded status for all 4 neural models
  - Frequency: 30 seconds

### 3.2 Key Alert Thresholds
| Metric | Healthy | Warning Threshold | Critical Incident Threshold | Action |
| :--- | :--- | :--- | :--- | :--- |
| **API Error Rate** | < 1% | > 3% | > 5% | Check backend logs & database connection pool |
| **Inference Latency (p95)** | < 100ms | > 200ms | > 500ms | Scale CPU worker replicas |
| **Feature Data Drift (Z-Score)** | < 0.5 | 0.5 to 1.0 | >= 1.0 | Schedule model retraining pipeline |
| **Database Query Latency** | < 5ms | > 20ms | > 100ms | Vacuum tables / check connection pool exhaust |

---

## 4. Disaster Recovery & Rollback Procedures

### 4.1 Database Backup & Restoration
```bash
# Backup PostgreSQL database
docker exec -t agripulse_postgres pg_dump -U postgres agripulse_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup file
docker exec -i agripulse_postgres psql -U postgres agripulse_db < backups/backup_YYYYMMDD_HHMMSS.sql
```

### 4.2 Model Rollback Protocol
1. Model artifacts are versioned in `docs/level8/MODEL_REGISTRY.md`.
2. Previous model weights are preserved in `saved_models/archive/`.
3. To rollback:
   - Update model checkpoint path in `backend/app/config/settings.py`.
   - Restart the backend worker pool (`docker-compose restart backend`).
   - Run `python scripts/verify_system.py` to confirm verification status.