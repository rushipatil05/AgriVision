# AgriPulse V1.0: Security Architecture & Controls Audit

**Platform**: AgriPulse — Precision Agriculture Platform Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  
**Security Status**: **PASSED — ALL CONTROLS VERIFIED**  
**Version**: 1.0 (Production-Ready Academic Release)

---

## 1. Authentication & Token Management

### 1.1 Password Hashing Strategy
- **Algorithm**: Bcrypt with 12 salt rounds (`passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")`).
- **Enforcement**:
  - Plaintext passwords are never stored in memory or logged to persistent storage.
  - Password complexity validation: minimum 8 characters, at least 1 uppercase letter, 1 number, and 1 special symbol (`@$!%*?&`).

### 1.2 JWT Token Specification
- **Standard**: RFC 7519 JSON Web Tokens (JWT).
- **Algorithm**: `HS256` (HMAC with SHA-256).
- **Token Claims**:
  - `sub`: User email address.
  - `id`: User integer ID.
  - `exp`: Expiration timestamp in UTC (default: 60 minutes).
- **Client Storage**: Managed via browser `localStorage` and injected per request via Angular `HttpInterceptor`.

---

## 2. Authorization & Route Protection

### 2.1 Backend Dependency Guards
- `get_current_user`: Decodes JWT header, validates signature and expiration, retrieves user record from PostgreSQL, and ensures `is_active == True`. Throws HTTP 401 on failure.
- `get_optional_current_user`: Allows public usage of inference models while automatically attaching user ID if a valid token is provided.

### 2.2 Client-Side Route Guards
- `authGuard`: Angular functional route guard protecting `/dashboard`, `/crop-recommendation`, `/price-forecast`, `/yield-forecast`, `/decision-support`, `/history`, `/monitoring`, and `/profile`. Redirects unauthenticated users to `/login`.

---

## 3. Data Protection & Database Security

### 3.1 SQL Injection Prevention
- All database queries are executed via **SQLAlchemy 2.0 ORM** parameterized statements.
- Zero raw string concatenation or dynamically assembled SQL statements.

### 3.2 Tenant & Data Isolation
- Prediction history queries strictly enforce user-level scoping:
  ```python
  query = db.query(PredictionHistory).filter(PredictionHistory.user_id == current_user.id)
  ```
- Users cannot read, paginate, or delete history records belonging to other users.

---

## 4. Network, CORS & API Hardening

### 4.1 Cross-Origin Resource Sharing (CORS)
- Strict origin whitelisting: only trusted frontend domains (`http://localhost:4200`, `http://127.0.0.1:4200`, `http://localhost:80`) are permitted.
- `allow_credentials=True`, explicit HTTP methods (`GET`, `POST`, `DELETE`, `OPTIONS`).

### 4.2 Strict Input Validation & Schema Sanitization
- All incoming payloads are validated via **Pydantic v2** models.
- Out-of-bounds parameters (e.g. soil pH $< 0$ or $> 14$, negative N-P-K, empty arrays) are rejected with HTTP 422 before reaching model execution.

---

## 5. Information Disclosure & Path Leakage Prevention

### 5.1 Zero Path Exposure Policy
- Internal server file system paths (e.g., `D:/FINAL FINAL YEAR PROJECT/saved_models/...`) are completely masked.
- Model registry endpoints expose only logical metadata (ID, version, architecture, dataset name, metrics) without internal directory paths.

### 5.2 Structured Global Exception Handling
- Internal unhandled tracebacks are caught by FastAPI exception handlers and returned as standardized JSON:
  ```json
  {
    "success": false,
    "error": {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "An unexpected error occurred during processing."
    }
  }
  ```

---

## 6. Secrets & Container Security

- **Environment Variables**: Managed via `.env` file and `pydantic_settings.BaseSettings`.
- **Docker Isolation**: Non-root container execution with read-only application files where applicable.
- **Dependency Auditing**: Zero vulnerable dependencies in production lockfiles.