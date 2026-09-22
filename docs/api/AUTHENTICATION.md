# AgriPulse Authentication & User Management Documentation

## Overview

AgriPulse implements a stateless JSON Web Token (JWT) authentication and user management subsystem built with **FastAPI**, **SQLAlchemy ORM**, **bcrypt** password hashing, and **PyJWT**.

The authentication architecture provides:
1. Secure account registration with email validation and strong password enforcement ($\ge 8$ characters).
2. Constant-time bcrypt password hashing with 12 salt rounds (plain passwords and hashes are never returned).
3. Signed, time-bounded JWT access tokens (`HS256`, 60-minute default expiration).
4. Strict multi-tenant user data isolation for historical inference audit trails.
5. OpenAPI Bearer Authentication integration in Swagger UI (`/docs`).

---

## Architecture Flow

```
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  Client / UI    │       │ FastAPI Backend │       │ Database / Model │
└────────┬────────┘       └────────┬────────┘       └────────┬─────────┘
         │                         │                         │
         │ 1. POST /auth/register  │                         │
         ├────────────────────────>│ Hash password (bcrypt)  │
         │                         │ Save User record        │
         │                         ├────────────────────────>│
         │ 2. HTTP 201 (User Profile)                        │
         │<────────────────────────┤                         │
         │                         │                         │
         │ 3. POST /auth/login     │                         │
         ├────────────────────────>│ Check password hash     │
         │                         │ Generate JWT Token      │
         │ 4. HTTP 200 (JWT Token) │                         │
         │<────────────────────────┤                         │
         │                         │                         │
         │ 5. GET /predictions/hist│                         │
         │   (Authorization: Bearer)                         │
         ├────────────────────────>│ Validate JWT signature  │
         │                         │ Extract sub (user_id)   │
         │                         │ Query user_id records   │
         │                         ├────────────────────────>│
         │ 6. Isolated User History│                         │
         │<────────────────────────┤                         │
```

---

## Authentication Endpoints

### 1. User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "name": "Kisan Sharma",
  "email": "kisan.sharma@example.com",
  "password": "StrongPassword123!"
}
```
- **Validation Rules**:
  - `name`: String, 2 to 100 characters.
  - `email`: Valid RFC email format.
  - `password`: String, 8 to 128 characters.
- **Responses**:
  - `201 Created`: User successfully registered.
    ```json
    {
      "success": true,
      "data": {
        "id": 1,
        "name": "Kisan Sharma",
        "email": "kisan.sharma@example.com",
        "is_active": true,
        "created_at": "2026-09-04T23:36:25.037000",
        "updated_at": "2026-09-04T23:36:25.037000"
      },
      "error": null
    }
    ```
  - `409 Conflict`: Email already exists.
  - `422 Unprocessable Entity`: Validation error.

---

### 2. User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "kisan.sharma@example.com",
  "password": "StrongPassword123!"
}
```
- **Responses**:
  - `200 OK`: Successful authentication.
    ```json
    {
      "success": true,
      "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
          "id": 1,
          "name": "Kisan Sharma",
          "email": "kisan.sharma@example.com",
          "is_active": true,
          "created_at": "2026-09-04T23:36:25.037000",
          "updated_at": "2026-09-04T23:36:25.037000"
        }
      },
      "error": null
    }
    ```
  - `401 Unauthorized`: `"Invalid email or password."` (Generic error to prevent user enumeration).

---

### 3. Current User Profile
- **Endpoint**: `GET /api/v1/auth/me`
- **Access**: Protected (`Authorization: Bearer <token>`)
- **Responses**:
  - `200 OK`: Current authenticated user details.
  - `401 Unauthorized`: Token missing, expired, or invalid.

---

### 4. Logout
- **Endpoint**: `POST /api/v1/auth/logout`
- **Access**: Protected (`Authorization: Bearer <token>`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "success": true,
      "message": "Logged out successfully",
      "data": {
        "message": "Logged out successfully"
      },
      "error": null
    }
    ```

---

## User-Isolated Prediction History

### 1. Retrieve User Prediction History
- **Endpoint**: `GET /api/v1/predictions/history`
- **Access**: Protected (`Authorization: Bearer <token>`)
- **Query Parameters**:
  - `page` (int, default: 1): 1-indexed page number.
  - `page_size` (int, default: 20, max: 100): Records per page.
  - `prediction_type` (optional string): Filter by `CROP_RECOMMENDATION`, `PRICE_FORECAST`, or `YIELD_FORECAST`.
- **User Isolation**:
  - Queries filter strictly by `user_id == current_user.id`.
  - User A can never see User B's historical records.
- **Responses**:
  - `200 OK`:
    ```json
    {
      "success": true,
      "data": {
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
        "records": [
          {
            "id": 1,
            "user_id": 1,
            "prediction_type": "CROP_RECOMMENDATION",
            "input_data": {
              "N": 90.0, "P": 42.0, "K": 43.0,
              "temperature": 20.87, "humidity": 82.0,
              "ph": 6.5, "rainfall": 202.93, "top_k": 3
            },
            "prediction_result": {
              "recommended_crop": "rice",
              "confidence": 0.997,
              "top_recommendations": [...]
            },
            "latency_ms": 289.96,
            "created_at": "2026-09-04T23:36:25.568000"
          }
        ]
      },
      "error": null
    }
    ```

---

### 2. Delete Prediction Record
- **Endpoint**: `DELETE /api/v1/predictions/history/{prediction_id}`
- **Access**: Protected (`Authorization: Bearer <token>`)
- **Security Rule**:
  - Deletes the record only if `record.id == prediction_id` AND `record.user_id == current_user.id`.
  - If the record does not exist or belongs to another user, returns `HTTP 404 Not Found` with `"Prediction record not found"`. Zero information is leaked about other users' data.

---

## Security Implementation Details

1. **Password Hashing**:
   - Algorithm: `bcrypt` (`bcrypt.gensalt(rounds=12)`).
   - Plaintext passwords are never logged, stored, or cached.
2. **JWT Payload**:
   - Standard claims: `sub` (user ID), `email`, `name`, `exp` (expiration), `iat` (issued at).
   - Secret key loaded via `JWT_SECRET_KEY` environment variable.
3. **HTTP 401 Error Handling**:
   - Expired tokens, corrupted signatures, and missing bearer headers return uniform `HTTP 401 Unauthorized` with `WWW-Authenticate: Bearer`.
4. **SQL Parameterization**:
   - All database lookups are executed via SQLAlchemy ORM parameterized queries, completely neutralizing SQL injection risks.

---

## Angular Frontend Integration Guide (Level 6)

```typescript
// Example: Angular HTTP Interceptor
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('agripulse_token');
    if (token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next.handle(cloned);
    }
    return next.handle(req);
  }
}
```
