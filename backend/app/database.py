from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Le "moteur" : gère la connexion réelle vers PostgreSQL.
engine = create_engine(settings.DATABASE_URL)

# Une "fabrique de sessions" : chaque requête HTTP créera sa propre session
# pour parler à la base, puis la fermera.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Toutes les classes de modèles (User, Project, ...) hériteront de cette Base.
# C'est ce qui permet à SQLAlchemy (et à Alembic) de savoir quelles tables créer.
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : ouvre une session le temps d'une requête,
    puis la ferme automatiquement (même en cas d'erreur).
    Utilisation dans un endpoint : db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
