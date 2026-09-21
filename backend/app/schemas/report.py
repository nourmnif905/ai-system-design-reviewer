from datetime import datetime

from pydantic import BaseModel


class AnalysisReportOut(BaseModel):
    """Ce que l'API renvoie après une analyse."""
    id: int
    diagram_id: int
    score: float | None
    content: str  # JSON (en texte) contenant le détail de l'analyse
    created_at: datetime

    class Config:
        from_attributes = True
