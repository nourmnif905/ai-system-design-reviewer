import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

let renderCount = 0;

@Component({
  selector: 'app-mermaid-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mermaid-box" *ngIf="!error">
      <div *ngIf="svg" [innerHTML]="svg"></div>
      <div class="loading" *ngIf="!svg">
        <div class="spinner spinner-dark"></div>
        <span>Rendu du diagramme…</span>
      </div>
    </div>
    <div class="error-banner" *ngIf="error">
      Impossible d'afficher ce diagramme ({{ error }}).
    </div>
  `,
  styles: [
    `
      .mermaid-box {
        overflow-x: auto;
        display: flex;
        justify-content: center;
        padding: 8px 0;
      }
      .loading {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--text-muted);
        font-size: 13.5px;
        padding: 20px;
      }
    `,
  ],
})
export class MermaidViewComponent implements OnChanges {
  @Input() code = '';

  svg: SafeHtml | null = null;
  error: string | null = null;

  constructor(private sanitizer: DomSanitizer) {}

  async ngOnChanges(changes: SimpleChanges): Promise<void> {
    if (!changes['code'] || !this.code) {
      return;
    }
    this.svg = null;
    this.error = null;

    try {
      const mermaid = (await import('mermaid')).default;
      mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'strict' });

      const id = `mermaid-${renderCount++}`;
      const { svg } = await mermaid.render(id, this.code);
      this.svg = this.sanitizer.bypassSecurityTrustHtml(svg);
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'erreur inconnue';
    }
  }
}
