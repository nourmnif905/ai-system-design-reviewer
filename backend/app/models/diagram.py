from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # "mermaid", "plantuml" ou "image"
    format = Column(String, nullable=False)

    # Le contenu original importé par l'utilisateur (texte Mermaid/PlantUML,
    # ou chemin/URL du fichier image).
    raw_content = Column(Text, nullable=False)

    # La structure JSON générée (components / relations), stockée en texte.
    # On la parsera avec json.loads() quand on en a besoin.
    parsed_structure = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="diagrams")
    reports = relationship(
        "AnalysisReport", back_populates="diagram", cascade="all, delete-orphan"
    )
