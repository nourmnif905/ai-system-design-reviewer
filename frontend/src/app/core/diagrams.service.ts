import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AnalysisReport, Diagram, DiagramFormat } from './models';

@Injectable({ providedIn: 'root' })
export class DiagramsService {
  constructor(private http: HttpClient) {}

  list(projectId: number): Observable<Diagram[]> {
    return this.http.get<Diagram[]>(`${environment.apiUrl}/projects/${projectId}/diagrams`);
  }

  get(diagramId: number): Observable<Diagram> {
    return this.http.get<Diagram>(`${environment.apiUrl}/diagrams/${diagramId}`);
  }

  create(projectId: number, format: DiagramFormat, rawContent: string): Observable<Diagram> {
    return this.http.post<Diagram>(`${environment.apiUrl}/projects/${projectId}/diagrams`, {
      format,
      raw_content: rawContent,
    });
  }

  /** Lance le pipeline complet des 5 agents (orchestré par LangGraph côté backend) */
  analyzeFull(diagramId: number): Observable<AnalysisReport> {
    return this.http.post<AnalysisReport>(
      `${environment.apiUrl}/diagrams/${diagramId}/analyze/full`,
      {}
    );
  }
}
