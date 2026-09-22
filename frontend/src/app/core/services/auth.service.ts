import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { User } from '../models/user.model';
import {
  UserRegisterRequest,
  UserLoginRequest,
  TokenResponse,
  LogoutResponse
} from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'agripulse_jwt_token';
  private readonly USER_KEY = 'agripulse_user_profile';
  private readonly baseUrl = `${environment.apiBaseUrl}/auth`;

  public currentUser = signal<User | null>(this.getStoredUser());
  public isAuthenticatedSignal = signal<boolean>(!!this.getToken());

  constructor(private http: HttpClient) {}

  private isBrowser(): boolean {
    return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
  }

  public register(request: UserRegisterRequest): Observable<ApiResponse<User>> {
    return this.http.post<ApiResponse<User>>(`${this.baseUrl}/register`, request);
  }

  public login(request: UserLoginRequest): Observable<ApiResponse<TokenResponse>> {
    return this.http.post<ApiResponse<TokenResponse>>(`${this.baseUrl}/login`, request).pipe(
      tap((response) => {
        if (response.success && response.data) {
          this.setSession(response.data);
        }
      })
    );
  }

  public logout(): Observable<ApiResponse<LogoutResponse>> {
    const token = this.getToken();
    if (!token) {
      this.clearSession();
      return of({ success: true, message: 'Logged out successfully' });
    }

    return this.http.post<ApiResponse<LogoutResponse>>(`${this.baseUrl}/logout`, {}).pipe(
      tap(() => this.clearSession()),
      catchError(() => {
        this.clearSession();
        return of({ success: true, message: 'Logged out successfully' });
      })
    );
  }

  public fetchCurrentUser(): Observable<ApiResponse<User>> {
    return this.http.get<ApiResponse<User>>(`${this.baseUrl}/me`).pipe(
      tap((response) => {
        if (response.success && response.data) {
          this.setUser(response.data);
        }
      })
    );
  }

  public setSession(tokenData: TokenResponse): void {
    if (this.isBrowser()) {
      try {
        window.localStorage.setItem(this.TOKEN_KEY, tokenData.access_token);
      } catch {}
    }
    this.setUser(tokenData.user);
    this.isAuthenticatedSignal.set(true);
  }

  public setUser(user: User): void {
    if (this.isBrowser()) {
      try {
        window.localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      } catch {}
    }
    this.currentUser.set(user);
  }

  public clearSession(): void {
    if (this.isBrowser()) {
      try {
        window.localStorage.removeItem(this.TOKEN_KEY);
        window.localStorage.removeItem(this.USER_KEY);
      } catch {}
    }
    this.currentUser.set(null);
    this.isAuthenticatedSignal.set(false);
  }

  public getToken(): string | null {
    if (!this.isBrowser()) return null;
    try {
      return window.localStorage.getItem(this.TOKEN_KEY);
    } catch {
      return null;
    }
  }

  public isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private getStoredUser(): User | null {
    if (!this.isBrowser()) return null;
    try {
      const stored = window.localStorage.getItem(this.USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }
}
