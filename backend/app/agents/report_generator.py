from collections import defaultdict

SEVERITY_PENALTY = {"low": 3, "medium": 8, "high": 15}

# Un problème supplémentaire sur un composant déjà signalé compte pour
# seulement 30% de sa pénalité normale : plusieurs agents qui pointent
# le même composant confirment souvent UN SEUL défaut réel, vu sous
# des angles différents (structure, SOLID, architecture) — ça ne doit
# pas être puni comme 3 défauts indépendants.
ADDITIONAL_FINDING_WEIGHT = 0.3


def _compute_score(all_problems: list[dict]) -> float:
    """Calcule un score sur 100. Regroupe d'abord les problèmes par
    composant, applique la pénalité pleine pour le pire problème de
    chaque composant, et une pénalité réduite pour les suivants (qui
    confirment probablement le même défaut plutôt que d'en signaler
    un nouveau). Ne descend jamais sous 0."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for index, problem in enumerate(all_problems):
        # Si le composant n'est pas précisé, on le traite comme un cas
        # isolé (pas de regroupement injustifié avec d'autres problèmes).
        key = problem.get("component") or f"__unspecified_{index}"
        groups[key].append(problem)

    score = 100.0
    for component_problems in groups.values():
        penalties = sorted(
            (SEVERITY_PENALTY.get(p.get("severity"), 5) for p in component_problems),
            reverse=True,
        )
        worst_penalty = penalties[0]
        additional_penalty = sum(p * ADDITIONAL_FINDING_WEIGHT for p in penalties[1:])
        score -= worst_penalty + additional_penalty

    return round(max(score, 0.0), 1)


def _collect_problems(uml_result: dict, solid_result: dict, architecture_result: dict) -> list[dict]:
    """Rassemble les problèmes des 3 agents d'analyse dans une seule
    liste uniforme, en gardant une trace de quel agent l'a détecté."""
    problems = []

    for issue in uml_result.get("issues", []):
        problems.append({
            "source": "UML Analyzer",
            "component": issue.get("component"),
            "description": issue.get("problem"),
            "severity": issue.get("severity", "medium"),
        })

    for violation in solid_result.get("violations", []):
        problems.append({
            "source": "SOLID Reviewer",
            "component": violation.get("component"),
            "description": f"[{violation.get('principle')}] {violation.get('explanation')}",
            "severity": violation.get("severity", "medium"),
        })

    for risk in architecture_result.get("risks", []):
        problems.append({
            "source": "Architecture Reviewer",
            "component": risk.get("component"),
            "description": f"[{risk.get('category')}] {risk.get('explanation')}",
            "severity": risk.get("severity", "medium"),
        })

    return problems


def _collect_positive_notes(uml_result: dict, solid_result: dict, architecture_result: dict) -> list[str]:
    """Rassemble tous les points positifs relevés par les 3 agents,
    sans doublons."""
    notes = []
    for result in (uml_result, solid_result, architecture_result):
        for note in result.get("positive_notes", []):
            if note not in notes:
                notes.append(note)
    return notes


def run_report_generator(
    uml_result: dict,
    solid_result: dict,
    architecture_result: dict,
    improvement_result: dict,
) -> dict:
    """
    Combine les résultats des 4 agents précédents en un rapport final.
    Ne fait AUCUN appel LLM : c'est un calcul déterministe (règles),
    pour que le score soit stable et reproductible d'une analyse à l'autre.
    """
    problems = _collect_problems(uml_result, solid_result, architecture_result)
    positive_notes = _collect_positive_notes(uml_result, solid_result, architecture_result)
    score = _compute_score(problems)

    # Tri par sévérité décroissante, pour que les problèmes les plus
    # graves apparaissent en premier dans le rapport.
    severity_order = {"high": 0, "medium": 1, "low": 2}
    problems.sort(key=lambda p: severity_order.get(p["severity"], 1))

    return {
        "score": score,
        "problems": problems,
        "positive_notes": positive_notes,
        "recommendations": improvement_result.get("recommendations", []),
        "improved_diagram_mermaid": improvement_result.get("improved_diagram_mermaid", ""),
    }
