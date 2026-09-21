from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agents.uml_analyzer import run_uml_analyzer
from app.agents.solid_reviewer import run_solid_reviewer
from app.agents.architecture_reviewer import run_architecture_reviewer
from app.agents.improvement_agent import run_improvement_agent
from app.agents.report_generator import run_report_generator


class AnalysisState(TypedDict):
    """L'état partagé qui circule à travers tout le graphe.
    Chaque nœud lit ce dont il a besoin, et ajoute son résultat."""
    structure: dict
    uml_result: dict
    solid_result: dict
    architecture_result: dict
    improvement_result: dict
    final_report: dict


def uml_node(state: AnalysisState) -> dict:
    """Nœud du UML Analyzer. Ne lit que 'structure' dans l'état."""
    return {"uml_result": run_uml_analyzer(state["structure"])}


def solid_node(state: AnalysisState) -> dict:
    """Nœud du SOLID Reviewer. Ne lit que 'structure' dans l'état."""
    return {"solid_result": run_solid_reviewer(state["structure"])}


def architecture_node(state: AnalysisState) -> dict:
    """Nœud de l'Architecture Reviewer. Ne lit que 'structure' dans l'état."""
    return {"architecture_result": run_architecture_reviewer(state["structure"])}


def improvement_node(state: AnalysisState) -> dict:
    """
    Nœud de l'Improvement Agent. LangGraph n'exécute ce nœud qu'une fois
    que TOUS ses prédécesseurs (uml, solid, architecture) ont fini,
    donc les 3 résultats sont garantis présents dans l'état ici.
    """
    result = run_improvement_agent(
        state["structure"],
        state["uml_result"],
        state["solid_result"],
        state["architecture_result"],
    )
    return {"improvement_result": result}


def report_node(state: AnalysisState) -> dict:
    """Nœud du Report Generator. Combine tout, sans appel LLM."""
    result = run_report_generator(
        state["uml_result"],
        state["solid_result"],
        state["architecture_result"],
        state["improvement_result"],
    )
    return {"final_report": result}


def _build_graph():
    """Construit et compile le graphe. Appelé une seule fois au chargement
    du module (voir plus bas), pas à chaque analyse."""
    graph = StateGraph(AnalysisState)

    graph.add_node("uml", uml_node)
    graph.add_node("solid", solid_node)
    graph.add_node("architecture", architecture_node)
    graph.add_node("improvement", improvement_node)
    graph.add_node("report", report_node)

    # Les 3 premiers partent tous de START : LangGraph les exécute
    # en parallèle, puisqu'aucun ne dépend des autres.
    graph.add_edge(START, "uml")
    graph.add_edge(START, "solid")
    graph.add_edge(START, "architecture")

    # "improvement" attend que les 3 soient términés avant de démarrer.
    graph.add_edge("uml", "improvement")
    graph.add_edge("solid", "improvement")
    graph.add_edge("architecture", "improvement")

    graph.add_edge("improvement", "report")
    graph.add_edge("report", END)

    return graph.compile()


# Compilé une seule fois, réutilisé à chaque appel (comme le client Groq).
_compiled_graph = _build_graph()


def run_full_analysis(structure: dict) -> dict:
    """
    Point d'entrée du pipeline complet. Exécute les 5 agents dans le bon
    ordre (avec parallélisation des 3 premiers), et renvoie le rapport final.
    """
    result_state = _compiled_graph.invoke({"structure": structure})
    return result_state["final_report"]
