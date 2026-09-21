export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
}

export type DiagramFormat = 'mermaid' | 'plantuml' | 'image';

export interface Diagram {
  id: number;
  project_id: number;
  format: DiagramFormat;
  raw_content: string;
  parsed_structure: string | null;
  created_at: string;
}

export interface ReportProblem {
  source: string;
  component: string | null;
  description: string | null;
  severity: 'low' | 'medium' | 'high';
}

export interface ReportRecommendation {
  title: string;
  description: string;
}

/** Forme du champ `content` (JSON en texte) une fois parsé, pour /analyze/full */
export interface FullAnalysisContent {
  score: number;
  problems: ReportProblem[];
  positive_notes: string[];
  recommendations: ReportRecommendation[];
  improved_diagram_mermaid: string;
}

export interface AnalysisReport {
  id: number;
  diagram_id: number;
  score: number | null;
  content: string;
  created_at: string;
}
