import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="wrap">
      <div class="panel card fade-in-up">
        <div class="brand-mark">◈</div>
        <h1>{{ mode === 'login' ? 'Content de vous revoir' : 'Créer un compte' }}</h1>
        <p class="sub">
          {{
            mode === 'login'
              ? 'Connectez-vous pour reprendre l\\'analyse de vos architectures.'
              : 'Quelques secondes suffisent pour commencer.'
          }}
        </p>

        <form (ngSubmit)="submit()" class="form">
          <div class="field">
            <label>Email</label>
            <input type="email" name="email" [(ngModel)]="email" required autocomplete="email" />
          </div>
          <div class="field">
            <label>Mot de passe</label>
            <input
              type="password"
              name="password"
              [(ngModel)]="password"
              required
              minlength="8"
              autocomplete="current-password"
            />
          </div>

          <div class="error-banner" *ngIf="errorMessage">{{ errorMessage }}</div>

          <button type="submit" class="btn btn-primary" [disabled]="loading">
            <span class="spinner" *ngIf="loading"></span>
            {{ mode === 'login' ? 'Se connecter' : "S'inscrire" }}
          </button>
        </form>

        <button class="switch" (click)="toggleMode()">
          {{
            mode === 'login'
              ? "Pas encore de compte ? S'inscrire"
              : 'Déjà un compte ? Se connecter'
          }}
        </button>
      </div>
    </div>
  `,
  styles: [
    `
      .wrap {
        min-height: calc(100vh - 68px);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
      }

      .panel {
        width: 100%;
        max-width: 400px;
        padding: 40px 36px;
        text-align: center;
      }

      .brand-mark {
        width: 52px;
        height: 52px;
        margin: 0 auto 20px;
        border-radius: 16px;
        background: var(--gradient-brand);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 10px 24px -8px rgba(109, 91, 208, 0.55);
      }

      h1 {
        font-size: 22px;
      }

      .sub {
        margin-top: 8px;
        color: var(--text-muted);
        font-size: 14px;
        line-height: 1.5;
      }

      .form {
        margin-top: 28px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        text-align: left;
      }

      .form .btn-primary {
        width: 100%;
        margin-top: 4px;
        padding: 12px;
      }

      .switch {
        margin-top: 22px;
        background: none;
        border: none;
        color: var(--primary-dark);
        font-size: 13.5px;
        font-weight: 600;
      }

      .switch:hover {
        text-decoration: underline;
      }
    `,
  ],
})
export class LoginComponent {
  mode: 'login' | 'register' = 'login';
  email = '';
  password = '';
  loading = false;
  errorMessage = '';

  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  toggleMode(): void {
    this.mode = this.mode === 'login' ? 'register' : 'login';
    this.errorMessage = '';
  }

  submit(): void {
    if (!this.email || !this.password) {
      return;
    }
    this.loading = true;
    this.errorMessage = '';

    if (this.mode === 'register') {
      this.auth.register(this.email, this.password).subscribe({
        next: () => {
          // Inscription réussie : on connecte directement l'utilisateur.
          this.auth.login(this.email, this.password).subscribe({
            next: () => this.router.navigate(['/projects']),
            error: () => (this.loading = false),
          });
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage = err?.error?.detail ?? "L'inscription a échoué.";
        },
      });
    } else {
      this.auth.login(this.email, this.password).subscribe({
        next: () => this.router.navigate(['/projects']),
        error: (err) => {
          this.loading = false;
          this.errorMessage = err?.error?.detail ?? 'Email ou mot de passe incorrect.';
        },
      });
    }
  }
}
