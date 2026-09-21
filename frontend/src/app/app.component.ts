import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, CommonModule],
  template: `
    <header class="topbar" *ngIf="auth.isAuthenticated()">
      <a routerLink="/projects" class="brand">
        <span class="brand-mark">◈</span>
        <span>AI System Design Reviewer</span>
      </a>
      <button class="btn btn-ghost btn-sm" (click)="logout()">Se déconnecter</button>
    </header>

    <router-outlet></router-outlet>
  `,
  styles: [
    `
      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 32px;
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border);
        position: sticky;
        top: 0;
        z-index: 10;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 16px;
        color: var(--text);
      }

      .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 9px;
        background: var(--gradient-brand);
        color: white;
        font-size: 15px;
      }
    `,
  ],
})
export class AppComponent {
  constructor(
    public auth: AuthService,
    private router: Router
  ) {}

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
