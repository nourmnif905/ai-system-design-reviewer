from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, projects, diagrams

app = FastAPI()

# Sans ça, le navigateur bloque les requêtes envoyées depuis le frontend
# Angular (localhost:4200) vers l'API (localhost:8000) : deux ports
# différents = deux "origines" différentes pour le navigateur.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(diagrams.router)


@app.get("/health")
def health():
    return {"status": "ok"}