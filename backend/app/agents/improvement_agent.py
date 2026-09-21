import json

from app.services.llm_client import call_llm, parse_json_response


def _build_prompt(
    structure: dict,
    uml_result: dict,
    solid_result: dict,
    architecture_result: dict,
) -> str:
    """Construit le prompt en s'appuyant sur les analyses DÉJÀ FAITES par
    les 3 agents précédents, plutôt que de redevoir deviner les problèmes."""
    structure_json = json.dumps(structure, ensure_ascii=False, indent=2)
    uml_json = json.dumps(uml_result, ensure_ascii=False, indent=2)
    solid_json = json.dumps(solid_result, ensure_ascii=False, indent=2)
    architecture_json = json.dumps(architecture_result, ensure_ascii=False, indent=2)

    return f"""Tu es un architecte logiciel expert chargé de proposer des améliorations concrètes.

Voici la structure d'origine d'une architecture logicielle :

{structure_json}

Voici les résultats de 3 analyses déjà réalisées par d'autres experts sur cette même architecture :

Analyse structurelle (couplage, dépendances) :
{uml_json}

Analyse des principes SOLID :
{solid_json}

Analyse de l'architecture (scalabilité, disponibilité, sécurité, maintenabilité) :
{architecture_json}

En te basant SPÉCIFIQUEMENT sur les problèmes déjà identifiés ci-dessus (ne les ignore pas, ne les redécouvre pas différemment), propose :
1. Une liste de recommandations techniques concrètes qui répondent directement aux problèmes signalés dans ces 3 analyses
2. Une nouvelle version améliorée du diagramme, au format Mermaid (syntaxe : NomComposant --> AutreComposant, une relation par ligne), qui résout ces problèmes précis (par exemple : séparer un composant signalé pour violation SRP, ajouter une réplication pour un composant signalé comme SPOF, ajouter un cache ou un API Gateway si un goulot d'étranglement a été signalé)

Le nouveau diagramme doit rester simple et lisible (10 composants maximum), et cohérent avec l'architecture d'origine (ne renomme pas les composants existants sans raison).

Réponds STRICTEMENT en JSON, avec ce format exact, sans texte avant ni après :
{{
  "recommendations": [
    {{"title": "titre court", "description": "explication de la recommandation, en citant le problème précis qu'elle résout"}}
  ],
  "improved_diagram_mermaid": "NomComposant --> AutreComposant\\nAutreComposant --> Troisieme"
}}"""


def run_improvement_agent(
    structure: dict,
    uml_result: dict,
    solid_result: dict,
    architecture_result: dict,
) -> dict:
    """
    Point d'entrée de l'agent. Contrairement aux 3 premiers agents, celui-ci
    a besoin des résultats des autres analyses pour baser ses recommandations
    sur des problèmes déjà confirmés, plutôt que de les redeviner.
    """
    prompt = _build_prompt(structure, uml_result, solid_result, architecture_result)
    # Prompt plus long (contient 3 analyses) + réponse plus longue
    # (recommandations + diagramme) : on augmente encore la limite.
    raw_response = call_llm(prompt, max_tokens=2000)
    result = parse_json_response(raw_response)

    if "error" in result:
        result.setdefault("recommendations", [])
        result.setdefault("improved_diagram_mermaid", "")

    return result
