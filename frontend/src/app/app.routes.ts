import { Routes } from '@angular/router';
import { authGuard } from './core/auth.guard';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ProjectDetailComponent } from './pages/project-detail/project-detail.component';
import { DiagramDetailComponent } from './pages/diagram-detail/diagram-detail.component';

export const routes: Routes = [
  { path: '', redirectTo: 'projects', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'projects', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'projects/:id', component: ProjectDetailComponent, canActivate: [authGuard] },
  {
    path: 'projects/:id/diagrams/:diagramId',
    component: DiagramDetailComponent,
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: 'projects' },
];
