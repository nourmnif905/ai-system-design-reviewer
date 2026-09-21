import json

from app.services.llm_client import call_llm, parse_json_response


def _build_prompt(structure: dict) -> str:
    """Construit le texte envoyé au LLM à partir de la structure
    {components, relations} extraite du diagramme."""
    structure_json = json.dumps(structure, ensure_ascii=False, indent=2)

    return f"""Tu es un architecte logiciel expert qui analyse des diagrammes UML.

Voici la structure d'une architecture logicielle, extraite d'un diagramme :

{structure_json}

Analyse cette structure et identifie :
1. Les composants qui ont trop de dépendances (couplage élevé)
2. Les signes de mauvaise conception (dépendances circulaires, composant central surchargé, etc.)
3. Une observation positive si la structure est raisonnable

Réponds STRICTEMENT en JSON, avec ce format exact, sans texte avant ni après :
{{
  "issues": [
    {{"component": "NomDuComposant", "problem": "description courte du problème", "severity": "low|medium|high"}}
  ],
  "positive_notes": ["observation positive 1", "..."]
}}

Si aucun problème n'est détecté, renvoie "issues": []."""


def run_uml_analyzer(structure: dict) -> dict:
    """
    Point d'entrée de l'agent. Prend la structure {components, relations}
    d'un diagramme et renvoie une analyse structurée :
        {"issues": [...], "positive_notes": [...]}
    """
    prompt = _build_prompt(structure)
    raw_response = call_llm(prompt)
    result = parse_json_response(raw_response)

    # Si le parsing a échoué, on garantit quand même la présence de
    # "issues" et "positive_notes" (vides), pour que le code appelant
    # (l'endpoint /analyze) n'ait pas à gérer un format surprise.
    if "error" in result:
        result.setdefault("issues", [])
        result.setdefault("positive_notes", [])

    return result
