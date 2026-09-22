import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

function passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password')?.value;
  const confirmPassword = control.get('confirmPassword')?.value;
  if (password && confirmPassword && password !== confirmPassword) {
    return { passwordMismatch: true };
  }
  return null;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public successMessage = signal<string | null>(null);
  public showPassword = signal<boolean>(false);

  public registerForm = this.fb.group(
    {
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]]
    },
    { validators: passwordMatchValidator }
  );

  public togglePasswordVisibility(): void {
    this.showPassword.update((val) => !val);
  }

  public onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const { name, email, password } = this.registerForm.getRawValue();

    this.authService.register({ name: name!, email: email!, password: password! }).subscribe({
      next: (response) => {
        if (response.success) {
          // Auto login after registration
          this.authService.login({ email: email!, password: password! }).subscribe({
            next: () => {
              this.isLoading.set(false);
              this.router.navigate(['/dashboard']);
            },
            error: () => {
              this.isLoading.set(false);
              this.successMessage.set('Account registered successfully! Please sign in.');
              setTimeout(() => this.router.navigate(['/login']), 1500);
            }
          });
        } else {
          this.isLoading.set(false);
          this.errorMessage.set(response.error?.message || 'Registration failed');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        const msg =
          err.error?.detail ||
          err.error?.error?.message ||
          (err.status === 409 ? 'An account with this email already exists.' : 'Registration failed. Please check your details.');
        this.errorMessage.set(msg);
      }
    });
  }
}
