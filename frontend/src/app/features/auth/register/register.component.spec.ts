import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { RegisterComponent } from './register.component';
import { AuthService } from '../../../core/services/auth.service';

describe('RegisterComponent', () => {
  let component: RegisterComponent;
  let authServiceSpy: any;

  beforeEach(async () => {
    authServiceSpy = {
      register: () => of({
        success: true,
        data: { id: 1, name: 'Farmer Bob', email: 'bob@farmer.com' }
      }),
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
      imports: [RegisterComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: AuthService, useValue: authServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;
  });

  it('should validate form and detect password mismatch', () => {
    expect(component).toBeTruthy();
    expect(component.registerForm.valid).toBe(false);

    component.registerForm.patchValue({
      name: 'Bob',
      email: 'bob@farmer.com',
      password: 'password123',
      confirmPassword: 'mismatchpassword'
    });

    expect(component.registerForm.errors?.['passwordMismatch']).toBe(true);

    component.registerForm.patchValue({
      confirmPassword: 'password123'
    });

    expect(component.registerForm.valid).toBe(true);
  });
});
