import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { LoginComponent } from './login.component';
import { AuthService } from '../../../core/services/auth.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let authServiceSpy: any;

  beforeEach(async () => {
    authServiceSpy = {
      login: () => of({
        success: true,
        data: {
          access_token: 'fake-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: { id: 1, name: 'Farmer Bob', email: 'bob@farmer.com' }
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: AuthService, useValue: authServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
  });

  it('should initialize form with validations', () => {
    expect(component).toBeTruthy();
    expect(component.loginForm.valid).toBe(false);

    component.loginForm.patchValue({
      email: 'bob@farmer.com',
      password: 'password123'
    });

    expect(component.loginForm.valid).toBe(true);
  });

  it('should toggle password visibility', () => {
    expect(component.showPassword()).toBe(false);
    component.togglePasswordVisibility();
    expect(component.showPassword()).toBe(true);
  });
});
