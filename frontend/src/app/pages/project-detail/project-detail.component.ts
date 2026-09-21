import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';
import { ProjectsService } from '../../core/projects.service';
import { DiagramsService } from '../../core/diagrams.service';
import { Diagram, DiagramFormat, Project } from '../../core/models';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="page-shell" *ngIf="project">
      <a routerLink="/projects" class="back-link">&larr; Tous les projets</a>

      <div class="page-head">
        <div>
          <h1>{{ project.name }}</h1>
          <p class="sub">{{ project.description || 'Pas de description.' }}</p>
        </div>
        <button class="btn btn-primary" (click)="showForm = !showForm">
          {{ showForm ? 'Annuler' : '+ Importer un diagramme' }}
        </button>
      </div>

      <form class="card new-form fade-in-up" *ngIf="showForm" (ngSubmit)="createDiagram()">
        <div class="field">
          <label>Format</label>
          <select name="format" [(ngModel)]="newFormat">
            <option value="mermaid">Mermaid</option>
            <option value="plantuml">PlantUML (non analysé automatiquement)</option>
          </select>
        </div>
        <div class="field">
          <label>Contenu du diagramme</label>
          <textarea
            name="rawContent"
            [(ngModel)]="newRawContent"
            placeholder="Ex : User --> Order --> PaymentService"
            required
          ></textarea>
        </div>
        <button type="submit" class="btn btn-primary" [disabled]="creating || !newRawContent">
          <span class="spinner" *ngIf="creating"></span>
          Importer
        </button>
      </form>

      <div class="loading-state" *ngIf="loading">
        <div class="spinner spinner-dark"></div>
        <span>Chargement des diagrammes…</span>
      </div>

      <div class="empty-state card" *ngIf="!loading && diagrams.length === 0">
        <div class="empty-mark">⌁</div>
        <h3>Aucun diagramme importé</h3>
        <p>Ajoutez un diagramme Mermaid pour lancer votre première analyse.</p>
      </div>

      <div class="list">
        <a
          class="card diagram-row fade-in-up"
          *ngFor="let diagram of diagrams"
          [routerLink]="['/projects', project.id, 'diagrams', diagram.id]"
        >
          <div class="diagram-icon">⌁</div>
          <div class="diagram-info">
            <span class="format-badge">{{ diagram.format }}</span>
            <p class="preview">{{ diagram.raw_content | slice: 0 : 90 }}{{ diagram.raw_content.length > 90 ? '…' : '' }}</p>
          </div>
          <span class="date">{{ diagram.created_at | date: 'dd/MM/yyyy HH:mm' }}</span>
        </a>
      </div>
    </div>
  `,
  styles: [
    `
      .back-link {
        display: inline-block;
        font-size: 13.5px;
        color: var(--text-muted);
        font-weight: 600;
        margin-bottom: 18px;
      }
      .back-link:hover {
        color: var(--primary-dark);
      }

      .page-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 28px;
      }

      h1 {
        font-size: 24px;
      }

      .sub {
        margin-top: 6px;
        color: var(--text-muted);
        font-size: 14.5px;
      }

      .new-form {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 22px;
        margin-bottom: 24px;
      }

      .new-form select {
        padding: 11px 14px;
        border: 1.5px solid var(--border);
        border-radius: var(--radius-sm);
        font-size: 14.5px;
        background: var(--surface);
        color: var(--text);
      }

      .loading-state,
      .empty-state {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--text-muted);
        padding: 30px;
      }

      .empty-state {
        flex-direction: column;
        text-align: center;
        padding: 60px 30px;
      }

      .empty-mark {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: var(--surface-alt);
        color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 14px;
      }

      .empty-state h3 {
        font-size: 16px;
      }
      .empty-state p {
        font-size: 14px;
        color: var(--text-faint);
      }

      .list {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .diagram-row {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px 20px;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
      }

      .diagram-row:hover {
        transform: translateX(3px);
        box-shadow: var(--shadow-sm);
        border-color: rgba(34, 195, 195, 0.35);
      }

      .diagram-icon {
        flex-shrink: 0;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: var(--surface-alt);
        color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
      }

      .diagram-info {
        flex: 1;
        min-width: 0;
      }

      .format-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: var(--primary-dark);
        background: var(--surface-alt);
        padding: 2px 9px;
        border-radius: 999px;
        margin-bottom: 6px;
      }

      .preview {
        font-size: 13.5px;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .date {
        flex-shrink: 0;
        font-size: 12px;
        color: var(--text-faint);
      }
    `,
  ],
})
export class ProjectDetailComponent implements OnInit {
  project: Project | null = null;
  diagrams: Diagram[] = [];
  loading = true;
  showForm = false;
  creating = false;
  newFormat: DiagramFormat = 'mermaid';
  newRawContent = '';

  constructor(
    private route: ActivatedRoute,
    private projectsService: ProjectsService,
    private diagramsService: DiagramsService
  ) {}

  ngOnInit(): void {
    // Même correction que diagram-detail : s'abonner à paramMap plutôt
    // que de lire le snapshot une seule fois, pour bien réagir quand on
    // navigue d'un projet à un autre sans recréation du composant.
    this.route.paramMap
      .pipe(
        switchMap((params) => {
          this.project = null;
          this.diagrams = [];
          const projectId = Number(params.get('id'));
          this.fetchDiagrams(projectId);
          return this.projectsService.get(projectId);
        })
      )
      .subscribe((project) => (this.project = project));
  }

  fetchDiagrams(projectId: number): void {
    this.loading = true;
    this.diagramsService.list(projectId).subscribe({
      next: (diagrams) => {
        this.diagrams = diagrams;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  createDiagram(): void {
    if (!this.project || !this.newRawContent) return;
    this.creating = true;
    this.diagramsService.create(this.project.id, this.newFormat, this.newRawContent).subscribe({
      next: (diagram) => {
        this.diagrams = [diagram, ...this.diagrams];
        this.creating = false;
        this.showForm = false;
        this.newRawContent = '';
      },
      error: () => (this.creating = false),
    });
  }
}
