import json

from app.services.llm_client import call_llm, parse_json_response


def _build_prompt(structure: dict) -> str:
    """Construit le prompt pour l'analyse de l'architecture globale."""
    structure_json = json.dumps(structure, ensure_ascii=False, indent=2)

    return f"""Tu es un architecte logiciel expert en systèmes distribués et en infrastructure.

Voici la structure d'une architecture logicielle, extraite d'un diagramme :

{structure_json}

Analyse cette architecture au regard de ces 5 critères :
- Scalabilité : un composant peut-il devenir un goulot d'étranglement si le trafic augmente ?
- Disponibilité : y a-t-il un composant qui, s'il tombe en panne, casse tout le système (Single Point of Failure) ? Cherche en particulier les composants dont le nom évoque une base de données, un cache, ou une file de messages, connectés à plusieurs autres composants.
- Performance : y a-t-il des chemins de communication qui semblent inutilement longs ou indirects ?
- Sécurité : un composant censé être interne (base de données, service de paiement) semble-t-il exposé directement à un composant externe (utilisateur, frontend) sans intermédiaire ?
- Maintenabilité : la structure globale est-elle facile à faire évoluer ?

Ne te prononce que sur ce qui est réellement observable à partir des noms de composants et de leurs relations. Ne fabrique pas de risque si rien ne l'indique clairement.

Réponds STRICTEMENT en JSON, avec ce format exact, sans texte avant ni après :
{{
  "risks": [
    {{"category": "scalability|availability|performance|security|maintainability", "component": "NomDuComposant", "explanation": "explication courte", "severity": "low|medium|high", "recommendation": "suggestion concrète et courte"}}
  ],
  "positive_notes": ["observation positive 1", "..."]
}}

Si aucun risque n'est détecté, renvoie "risks": []."""


def run_architecture_reviewer(structure: dict) -> dict:
    """
    Point d'entrée de l'agent. Prend la structure {components, relations}
    d'un diagramme et renvoie une analyse d'architecture structurée :
        {"risks": [...], "positive_notes": [...]}
    """
    prompt = _build_prompt(structure)
    raw_response = call_llm(prompt)
    result = parse_json_response(raw_response)

    if "error" in result:
        result.setdefault("risks", [])
        result.setdefault("positive_notes", [])

    return result
