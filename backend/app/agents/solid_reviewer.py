import json

from app.services.llm_client import call_llm, parse_json_response


def _build_prompt(structure: dict) -> str:
    """Construit le prompt pour l'analyse des principes SOLID."""
    structure_json = json.dumps(structure, ensure_ascii=False, indent=2)

    return f"""Tu es un architecte logiciel expert en conception orientée objet.

Voici la structure d'une architecture logicielle, extraite d'un diagramme :

{structure_json}

Analyse cette structure au regard des 5 principes SOLID :
- Single Responsibility Principle (SRP) : un composant a-t-il l'air de porter plusieurs responsabilités distinctes (son nom suggère plusieurs rôles, ou il est connecté à des domaines très différents) ?
- Open/Closed Principle (OCP) : la structure semble-t-elle facile à étendre sans modifier l'existant ?
- Liskov Substitution Principle (LSP) : rien à signaler si la structure ne montre pas d'héritage/interfaces.
- Interface Segregation Principle (ISP) : un composant semble-t-il dépendre de trop de choses différentes à la fois ?
- Dependency Inversion Principle (DIP) : des composants de haut niveau semblent-ils dépendre directement de détails de bas niveau (ex: une base de données nommée explicitement) plutôt que d'abstractions ?

Ne te prononce que sur les principes réellement observables à partir des noms de composants et de leurs relations. Ne fabrique pas de violation si rien ne l'indique clairement.

Réponds STRICTEMENT en JSON, avec ce format exact, sans texte avant ni après :
{{
  "violations": [
    {{"principle": "SRP|OCP|LSP|ISP|DIP", "component": "NomDuComposant", "explanation": "explication courte", "severity": "low|medium|high"}}
  ],
  "positive_notes": ["observation positive 1", "..."]
}}

Si aucune violation n'est détectée, renvoie "violations": []."""


def run_solid_reviewer(structure: dict) -> dict:
    """
    Point d'entrée de l'agent. Prend la structure {components, relations}
    d'un diagramme et renvoie une analyse SOLID structurée :
        {"violations": [...], "positive_notes": [...]}
    """
    prompt = _build_prompt(structure)
    raw_response = call_llm(prompt)
    result = parse_json_response(raw_response)

    if "error" in result:
        result.setdefault("violations", [])
        result.setdefault("positive_notes", [])

    return result
