import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';
import { DiagramsService } from '../../core/diagrams.service';
import { Diagram, FullAnalysisContent } from '../../core/models';
import { MermaidViewComponent } from '../../shared/mermaid-view/mermaid-view.component';

@Component({
  selector: 'app-diagram-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, MermaidViewComponent],
  template: `
    <div class="page-shell" *ngIf="diagram">
      <a [routerLink]="['/projects', diagram.project_id]" class="back-link">&larr; Retour au projet</a>

      <div class="page-head">
        <div>
          <h1>Diagramme #{{ diagram.id }}</h1>
          <span class="format-badge">{{ diagram.format }}</span>
        </div>
        <button
          class="btn btn-primary"
          (click)="runAnalysis()"
          [disabled]="analyzing || diagram.format !== 'mermaid'"
        >
          <span class="spinner" *ngIf="analyzing"></span>
          {{ analyzing ? 'Analyse en cours (5 agents)…' : "Lancer l'analyse complète" }}
        </button>
      </div>

      <p class="unsupported-note" *ngIf="diagram.format !== 'mermaid'">
        Seul le format Mermaid est analysé automatiquement pour l'instant.
      </p>

      <section class="card section">
        <h2>Diagramme original</h2>
        <app-mermaid-view [code]="diagram.raw_content"></app-mermaid-view>
      </section>

      <div class="error-banner fade-in-up" *ngIf="errorMessage">{{ errorMessage }}</div>

      <ng-container *ngIf="report as r">
        <section class="score-section fade-in-up">
          <div class="score-ring" [class]="scoreClass(r.score)">
            <svg viewBox="0 0 120 120">
              <circle class="ring-bg" cx="60" cy="60" r="52" />
              <circle
                class="ring-fg"
                cx="60"
                cy="60"
                r="52"
                [style.strokeDasharray]="ringCircumference"
                [style.strokeDashoffset]="ringOffset(r.score)"
              />
            </svg>
            <div class="score-value">
              <strong>{{ r.score }}</strong>
              <span>/ 100</span>
            </div>
          </div>
          <div class="score-summary">
            <h2>{{ scoreLabel(r.score) }}</h2>
            <p>
              {{ r.problems.length }} problème(s) détecté(s) ·
              {{ r.positive_notes.length }} point(s) positif(s)
            </p>
          </div>
        </section>

        <section class="card section fade-in-up" *ngIf="r.positive_notes.length">
          <h2>Points positifs</h2>
          <ul class="positive-list">
            <li *ngFor="let note of r.positive_notes">{{ note }}</li>
          </ul>
        </section>

        <section class="card section fade-in-up" *ngIf="r.problems.length">
          <h2>Problèmes détectés</h2>
          <div class="problem" *ngFor="let problem of r.problems">
            <span class="badge" [class]="'badge-' + problem.severity">{{ problem.severity }}</span>
            <div>
              <p class="problem-component">{{ problem.component || 'Architecture générale' }}</p>
              <p class="problem-desc">{{ problem.description }}</p>
              <span class="problem-source">Détecté par {{ problem.source }}</span>
            </div>
          </div>
        </section>

        <section class="card section fade-in-up" *ngIf="r.recommendations.length">
          <h2>Recommandations</h2>
          <div class="reco" *ngFor="let reco of r.recommendations">
            <h4>{{ reco.title }}</h4>
            <p>{{ reco.description }}</p>
          </div>
        </section>

        <section class="card section fade-in-up" *ngIf="r.improved_diagram_mermaid">
          <h2>Architecture améliorée proposée</h2>
          <app-mermaid-view [code]="r.improved_diagram_mermaid"></app-mermaid-view>
        </section>
      </ng-container>
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
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 6px;
      }

      h1 {
        font-size: 22px;
        display: inline;
        margin-right: 10px;
      }

      .format-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: var(--primary-dark);
        background: var(--surface-alt);
        padding: 3px 10px;
        border-radius: 999px;
      }

      .unsupported-note {
        font-size: 13px;
        color: var(--text-faint);
        margin-top: 10px;
      }

      .section {
        padding: 24px;
        margin-top: 24px;
      }

      .section h2 {
        font-size: 16px;
        margin-bottom: 14px;
      }

      /* ---------- Score ---------- */

      .score-section {
        display: flex;
        align-items: center;
        gap: 26px;
        margin-top: 30px;
        padding: 26px 28px;
        border-radius: var(--radius-lg);
        background: var(--surface);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
      }

      .score-ring {
        position: relative;
        width: 108px;
        height: 108px;
        flex-shrink: 0;
      }

      .score-ring svg {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
      }

      .ring-bg {
        fill: none;
        stroke: var(--surface-alt);
        stroke-width: 10;
      }

      .ring-fg {
        fill: none;
        stroke-width: 10;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.6s ease;
      }

      .score-good .ring-fg { stroke: var(--success); }
      .score-mid .ring-fg { stroke: var(--warning); }
      .score-bad .ring-fg { stroke: var(--danger); }

      .score-value {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }

      .score-value strong {
        font-size: 26px;
        line-height: 1;
      }

      .score-value span {
        font-size: 11px;
        color: var(--text-faint);
      }

      .score-summary h2 {
        font-size: 19px;
      }

      .score-summary p {
        margin-top: 6px;
        color: var(--text-muted);
        font-size: 14px;
      }

      /* ---------- Listes ---------- */

      .positive-list {
        margin: 0;
        padding-left: 20px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .positive-list li {
        font-size: 14px;
        color: var(--text);
        line-height: 1.5;
      }

      .problem {
        display: flex;
        gap: 14px;
        padding: 14px 0;
        border-top: 1px solid var(--border);
      }

      .problem:first-of-type {
        border-top: none;
        padding-top: 0;
      }

      .problem-component {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 3px;
      }

      .problem-desc {
        font-size: 13.5px;
        color: var(--text-muted);
        line-height: 1.5;
      }

      .problem-source {
        display: block;
        margin-top: 6px;
        font-size: 11.5px;
        color: var(--text-faint);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.02em;
      }

      .reco {
        padding: 14px 16px;
        border-radius: var(--radius-sm);
        background: var(--surface-alt);
        margin-bottom: 10px;
      }

      .reco:last-child {
        margin-bottom: 0;
      }

      .reco h4 {
        font-size: 14px;
        margin-bottom: 4px;
        color: var(--primary-dark);
      }

      .reco p {
        font-size: 13.5px;
        color: var(--text-muted);
        line-height: 1.5;
      }
    `,
  ],
})
export class DiagramDetailComponent implements OnInit {
  diagram: Diagram | null = null;
  report: FullAnalysisContent | null = null;
  analyzing = false;
  errorMessage = '';

  readonly ringCircumference = 2 * Math.PI * 52;

  constructor(
    private route: ActivatedRoute,
    private diagramsService: DiagramsService
  ) {}

  ngOnInit(): void {
    // On s'abonne à paramMap (au lieu de lire route.snapshot une seule
    // fois) : Angular réutilise ce composant quand on navigue d'un
    // diagramme à un autre (même route, juste l'id qui change), donc
    // ngOnInit ne se redéclenche PAS tout seul. Cet abonnement permet
    // de réagir à chaque changement d'id, même sans recréation du composant.
    this.route.paramMap
      .pipe(
        switchMap((params) => {
          // Réinitialise l'affichage avant de charger le nouveau diagramme,
          // pour ne pas montrer un ancien rapport pendant le chargement.
          this.diagram = null;
          this.report = null;
          this.errorMessage = '';
          const diagramId = Number(params.get('diagramId'));
          return this.diagramsService.get(diagramId);
        })
      )
      .subscribe((diagram) => (this.diagram = diagram));
  }

  runAnalysis(): void {
    if (!this.diagram) return;
    this.analyzing = true;
    this.errorMessage = '';

    this.diagramsService.analyzeFull(this.diagram.id).subscribe({
      next: (report) => {
        this.report = JSON.parse(report.content) as FullAnalysisContent;
        this.analyzing = false;
      },
      error: (err) => {
        this.analyzing = false;
        this.errorMessage = err?.error?.detail ?? "L'analyse a échoué. Réessayez.";
      },
    });
  }

  ringOffset(score: number): number {
    const ratio = Math.max(0, Math.min(score, 100)) / 100;
    return this.ringCircumference * (1 - ratio);
  }

  scoreClass(score: number): string {
    if (score >= 70) return 'score-good';
    if (score >= 40) return 'score-mid';
    return 'score-bad';
  }

  scoreLabel(score: number): string {
    if (score >= 70) return 'Architecture globalement saine';
    if (score >= 40) return 'Des améliorations sont recommandées';
    return "L'architecture nécessite une refonte";
  }
}
