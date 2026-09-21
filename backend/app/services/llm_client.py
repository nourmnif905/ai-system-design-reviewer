import json

from groq import Groq

from app.config import settings

# Modèle recommandé par Groq pour remplacer llama-3.3-70b-versatile
# (retiré en juin 2026). Utilisé par tous les agents.
GROQ_MODEL = "openai/gpt-oss-120b"

_client = Groq(api_key=settings.GROQ_API_KEY)


def call_llm(prompt: str, temperature: float = 0.2, max_tokens: int = 1000) -> str:
    """
    Appelle Groq avec un prompt et renvoie le texte brut de la réponse.
    Fonction générique : n'importe quel agent peut l'utiliser, quel que
    soit son prompt ou le format de sortie qu'il attend.
    """
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def parse_json_response(raw_text: str) -> dict:
    """
    Convertit la réponse texte d'un LLM en dict Python.
    Nettoie les balises ```json ... ``` que les modèles ajoutent parfois
    malgré la consigne. Si le JSON reste invalide, renvoie une structure
    d'erreur exploitable plutôt que de faire planter l'appelant.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "error": "Réponse du LLM non parsable en JSON.",
            "raw_response": raw_text,
        }
