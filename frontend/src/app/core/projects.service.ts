import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Project } from './models';

@Injectable({ providedIn: 'root' })
export class ProjectsService {
  constructor(private http: HttpClient) {}

  list(): Observable<Project[]> {
    return this.http.get<Project[]>(`${environment.apiUrl}/projects`);
  }

  get(projectId: number): Observable<Project> {
    return this.http.get<Project>(`${environment.apiUrl}/projects/${projectId}`);
  }

  create(name: string, description: string): Observable<Project> {
    return this.http.post<Project>(`${environment.apiUrl}/projects`, { name, description });
  }

  delete(projectId: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/projects/${projectId}`);
  }
}
