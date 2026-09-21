import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.diagram import Diagram
from app.models.report import AnalysisReport
from app.schemas.diagram import DiagramCreate, DiagramOut
from app.schemas.report import AnalysisReportOut
from app.services.auth_dependency import get_current_user
from app.services.ownership import get_owned_project_or_404
from app.services.mermaid_parser import parse_mermaid_to_json_string, normalize_arrows
from app.agents.uml_analyzer import run_uml_analyzer
from app.agents.solid_reviewer import run_solid_reviewer
from app.agents.architecture_reviewer import run_architecture_reviewer
from app.agents.improvement_agent import run_improvement_agent
from app.agents.graph import run_full_analysis

router = APIRouter(tags=["diagrams"])


@router.post(
    "/projects/{project_id}/diagrams",
    response_model=DiagramOut,
    status_code=status.HTTP_201_CREATED,
)
def create_diagram(
    project_id: int,
    diagram_in: DiagramCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_project_or_404(project_id, current_user, db)

    raw_content = diagram_in.raw_content
    parsed_structure = None
    if diagram_in.format.value == "mermaid":
        # Corrige automatiquement les flèches abîmées par l'autocorrection
        # du clavier/OS (espace parasite "-- >", flèche unicode "→"...)
        # AVANT de stocker : le diagramme reste ainsi correct aussi bien
        # pour le rendu Mermaid côté frontend que pour ce parseur.
        raw_content = normalize_arrows(raw_content)
        parsed_structure = parse_mermaid_to_json_string(raw_content)

    new_diagram = Diagram(
        project_id=project_id,
        format=diagram_in.format.value,
        raw_content=raw_content,
        parsed_structure=parsed_structure,
    )
    db.add(new_diagram)
    db.commit()
    db.refresh(new_diagram)
    return new_diagram


@router.get("/projects/{project_id}/diagrams", response_model=list[DiagramOut])
def list_diagrams(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_project_or_404(project_id, current_user, db)
    return db.query(Diagram).filter(Diagram.project_id == project_id).all()


def _get_owned_diagram_or_404(
    diagram_id: int, current_user: User, db: Session
) -> Diagram:
    """Retrouve un diagramme et vérifie (via son projet) qu'il appartient
    bien à l'utilisateur connecté. Réutilisé par toutes les routes
    /diagrams/{id}/... de ce fichier."""
    diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
    if diagram is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diagramme introuvable."
        )
    get_owned_project_or_404(diagram.project_id, current_user, db)
    return diagram


@router.get("/diagrams/{diagram_id}", response_model=DiagramOut)
def get_diagram(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_diagram_or_404(diagram_id, current_user, db)


def _run_analysis_and_save(
    diagram: Diagram, db: Session, agent_fn
) -> AnalysisReport:
    """Fonction interne partagée par les routes d'analyse à agent UNIQUE
    (/analyze, /analyze/solid, /analyze/architecture) : vérifie que la
    structure est disponible, appelle l'agent donné en paramètre, et
    sauvegarde le résultat comme un nouveau rapport."""
    if diagram.parsed_structure is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce diagramme n'a pas encore de structure exploitable.",
        )

    structure = json.loads(diagram.parsed_structure)
    analysis_result = agent_fn(structure)

    new_report = AnalysisReport(
        diagram_id=diagram.id,
        score=None,
        content=json.dumps(analysis_result, ensure_ascii=False),
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.post(
    "/diagrams/{diagram_id}/analyze",
    response_model=AnalysisReportOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_diagram(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lance le UML Analyzer Agent (structure, couplage, dépendances)."""
    diagram = _get_owned_diagram_or_404(diagram_id, current_user, db)
    return _run_analysis_and_save(diagram, db, run_uml_analyzer)


@router.post(
    "/diagrams/{diagram_id}/analyze/solid",
    response_model=AnalysisReportOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_diagram_solid(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lance le SOLID Reviewer Agent (principes SOLID)."""
    diagram = _get_owned_diagram_or_404(diagram_id, current_user, db)
    return _run_analysis_and_save(diagram, db, run_solid_reviewer)


@router.post(
    "/diagrams/{diagram_id}/analyze/architecture",
    response_model=AnalysisReportOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_diagram_architecture(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lance l'Architecture Reviewer Agent (scalabilité, disponibilité, sécurité...)."""
    diagram = _get_owned_diagram_or_404(diagram_id, current_user, db)
    return _run_analysis_and_save(diagram, db, run_architecture_reviewer)


@router.post(
    "/diagrams/{diagram_id}/analyze/improve",
    response_model=AnalysisReportOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_diagram_improve(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lance l'Improvement Agent. Exécute D'ABORD les 3 autres agents
    (UML, SOLID, Architecture) sur le diagramme, pour que l'Improvement
    Agent base ses recommandations sur des problèmes déjà confirmés,
    plutôt que de les redeviner seul.
    """
    diagram = _get_owned_diagram_or_404(diagram_id, current_user, db)

    if diagram.parsed_structure is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce diagramme n'a pas encore de structure exploitable.",
        )
    structure = json.loads(diagram.parsed_structure)

    uml_result = run_uml_analyzer(structure)
    solid_result = run_solid_reviewer(structure)
    architecture_result = run_architecture_reviewer(structure)

    improvement_result = run_improvement_agent(
        structure, uml_result, solid_result, architecture_result
    )

    new_report = AnalysisReport(
        diagram_id=diagram.id,
        score=None,
        content=json.dumps(improvement_result, ensure_ascii=False),
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.post(
    "/diagrams/{diagram_id}/analyze/full",
    response_model=AnalysisReportOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze_diagram_full(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Exécute les 5 agents (UML, SOLID, Architecture, Improvement, Report
    Generator) orchestrés par LangGraph : les 3 premiers tournent en
    parallèle. Sauvegarde le rapport final AVEC un score numérique.
    C'est la route destinée à l'usage réel : "analyser mon diagramme".
    """
    diagram = _get_owned_diagram_or_404(diagram_id, current_user, db)

    if diagram.parsed_structure is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce diagramme n'a pas encore de structure exploitable.",
        )
    structure = json.loads(diagram.parsed_structure)

    final_report = run_full_analysis(structure)

    new_report = AnalysisReport(
        diagram_id=diagram.id,
        score=final_report["score"],
        content=json.dumps(final_report, ensure_ascii=False),
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report
