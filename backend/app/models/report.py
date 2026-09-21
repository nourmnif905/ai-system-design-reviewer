from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    diagram_id = Column(Integer, ForeignKey("diagrams.id"), nullable=False)

    # Score global de l'architecture (ex: 78.0 pour "78/100")
    score = Column(Float, nullable=True)

    # Le rapport complet généré par les agents (JSON stocké en texte) :
    # problèmes détectés, gravité, recommandations, etc.
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    diagram = relationship("Diagram", back_populates="reports")
