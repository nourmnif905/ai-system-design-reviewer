import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { Token, User } from './models';

const TOKEN_KEY = 'asdr_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  /** Signal réactif : les composants peuvent lire isAuthenticated() directement */
  readonly isAuthenticated = signal<boolean>(!!localStorage.getItem(TOKEN_KEY));

  constructor(private http: HttpClient) {}

  register(email: string, password: string): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, { email, password });
  }

  login(email: string, password: string): Observable<Token> {
    return this.http
      .post<Token>(`${environment.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap((token) => {
          localStorage.setItem(TOKEN_KEY, token.access_token);
          this.isAuthenticated.set(true);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.isAuthenticated.set(false);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }
}
