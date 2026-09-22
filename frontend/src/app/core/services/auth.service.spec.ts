import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';
import { User } from '../models/user.model';
import { TokenResponse } from '../models/auth.model';

describe('AuthService', () => {
  let service: AuthService;
  let httpTesting: HttpTestingController;

  let store: Record<string, string> = {};
  const mockLocalStorage = {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };

  const mockUser: User = {
    id: 1,
    name: 'Farmer Bob',
    email: 'bob@farmer.com',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  };

  const mockToken: TokenResponse = {
    access_token: 'fake-jwt-token-123',
    token_type: 'bearer',
    expires_in: 3600,
    user: mockUser
  };

  beforeEach(() => {
    store = {};
    if (typeof window !== 'undefined') {
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      });
    }

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(AuthService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    if (httpTesting) {
      httpTesting.verify();
    }
    store = {};
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should handle registration request', () => {
    service.register({ name: 'Farmer Bob', email: 'bob@farmer.com', password: 'password123' }).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(res.data?.name).toBe('Farmer Bob');
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/auth/register`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockUser });
  });

  it('should handle login and store session tokens', () => {
    service.login({ email: 'bob@farmer.com', password: 'password123' }).subscribe((res) => {
      expect(res.success).toBe(true);
      expect(service.getToken()).toBe('fake-jwt-token-123');
      expect(service.currentUser()?.name).toBe('Farmer Bob');
      expect(service.isAuthenticated()).toBe(true);
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, data: mockToken });
  });

  it('should clear session on logout', () => {
    service.setSession(mockToken);

    expect(service.isAuthenticated()).toBe(true);

    service.logout().subscribe(() => {
      expect(service.getToken()).toBeNull();
      expect(service.currentUser()).toBeNull();
      expect(service.isAuthenticated()).toBe(false);
    });

    const req = httpTesting.expectOne(`${environment.apiBaseUrl}/auth/logout`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, message: 'Logged out successfully' });
  });
});
