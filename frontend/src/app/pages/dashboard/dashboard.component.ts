import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProjectsService } from '../../core/projects.service';
import { Project } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="page-shell">
      <div class="page-head">
        <div>
          <h1>Vos projets</h1>
          <p class="sub">Importez un diagramme d'architecture et laissez les agents l'analyser.</p>
        </div>
        <button class="btn btn-primary" (click)="showForm = !showForm">
          {{ showForm ? 'Annuler' : '+ Nouveau projet' }}
        </button>
      </div>

      <form
        class="card new-form fade-in-up"
        *ngIf="showForm"
        (ngSubmit)="createProject()"
      >
        <div class="field">
          <label>Nom du projet</label>
          <input name="name" [(ngModel)]="newName" required placeholder="Ex : API e-commerce" />
        </div>
        <div class="field">
          <label>Description (optionnelle)</label>
          <input name="description" [(ngModel)]="newDescription" placeholder="Quelques mots..." />
        </div>
        <button type="submit" class="btn btn-primary" [disabled]="creating || !newName">
          <span class="spinner" *ngIf="creating"></span>
          Créer le projet
        </button>
      </form>

      <div class="loading-state" *ngIf="loading">
        <div class="spinner spinner-dark"></div>
        <span>Chargement des projets…</span>
      </div>

      <div class="empty-state card" *ngIf="!loading && projects.length === 0">
        <div class="empty-mark">◈</div>
        <h3>Aucun projet pour l'instant</h3>
        <p>Créez votre premier projet pour importer un diagramme.</p>
      </div>

      <div class="grid">
        <a
          class="card project-card fade-in-up"
          *ngFor="let project of projects"
          [routerLink]="['/projects', project.id]"
        >
          <div class="project-icon">◈</div>
          <h3>{{ project.name }}</h3>
          <p class="desc">{{ project.description || 'Pas de description.' }}</p>
          <span class="date">Créé le {{ project.created_at | date: 'dd/MM/yyyy' }}</span>
        </a>
      </div>
    </div>
  `,
  styles: [
    `
      .page-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 28px;
      }

      h1 {
        font-size: 26px;
      }

      .sub {
        margin-top: 6px;
        color: var(--text-muted);
        font-size: 14.5px;
      }

      .new-form {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-end;
        gap: 16px;
        padding: 22px;
        margin-bottom: 24px;
      }

      .new-form .field {
        flex: 1;
        min-width: 200px;
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
        color: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 14px;
      }

      .empty-state h3 {
        font-size: 16px;
        margin-bottom: 4px;
      }

      .empty-state p {
        font-size: 14px;
        color: var(--text-faint);
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
        gap: 18px;
      }

      .project-card {
        padding: 22px;
        display: block;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
      }

      .project-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: rgba(109, 91, 208, 0.3);
      }

      .project-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: var(--gradient-brand);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        margin-bottom: 14px;
      }

      .project-card h3 {
        font-size: 16px;
        margin-bottom: 6px;
      }

      .desc {
        font-size: 13.5px;
        color: var(--text-muted);
        line-height: 1.5;
        min-height: 40px;
      }

      .date {
        display: block;
        margin-top: 14px;
        font-size: 12px;
        color: var(--text-faint);
      }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  projects: Project[] = [];
  loading = true;
  showForm = false;
  creating = false;
  newName = '';
  newDescription = '';

  constructor(
    private projectsService: ProjectsService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.fetchProjects();
  }

  fetchProjects(): void {
    this.loading = true;
    this.projectsService.list().subscribe({
      next: (projects) => {
        this.projects = projects;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  createProject(): void {
    if (!this.newName) return;
    this.creating = true;
    this.projectsService.create(this.newName, this.newDescription).subscribe({
      next: (project) => {
        this.creating = false;
        this.showForm = false;
        this.newName = '';
        this.newDescription = '';
        this.router.navigate(['/projects', project.id]);
      },
      error: () => (this.creating = false),
    });
  }
}
