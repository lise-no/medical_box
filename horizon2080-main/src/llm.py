"""
Interface avec le modèle de langage local (Ollama).

Non utilisé par src/app.py actuellement.
Ce fichier reste comme référence pour l'approche "sortie JSON structurée" (via Pydantic),
utile si l'équipe décide de brancher l'indice de concordance complet.

Rappel du principe central : le LLM explique et reformule, il ne décide pas
(pas d'alerte, pas de score calculé par lui — voir rules.py).

Le chatbot reste entièrement en français (prompt système dans models/Modelfile,
textes ci-dessous) : seuls les noms de variables/fonctions sont en anglais.
"""

import ollama
from pydantic import BaseModel, ValidationError

import config

_KNOWLEDGE_SHEET_PATH = config.KNOWLEDGE_SHEET_PATH


def _load_knowledge_sheet() -> str:
    if _KNOWLEDGE_SHEET_PATH.exists():
        return _KNOWLEDGE_SHEET_PATH.read_text(encoding="utf-8")
    return "(fiche de connaissances non encore rédigée)"


# --- Chat libre, avec mémoire de la conversation ---

class Conversation:
    """Le modèle n'a pas de mémoire propre : on lui renvoie l'historique à chaque message."""

    def __init__(self, model: str = None):
        self.model = model or config.OLLAMA_MODEL
        self.history: list[dict] = []

    def send(self, text: str):
        """Générateur : produit la réponse morceau par morceau (streaming)."""
        self.history.append({"role": "user", "content": text})
        chunks = []
        for part in ollama.chat(model=self.model, messages=self.history, stream=True):
            chunk = part.message.content
            chunks.append(chunk)
            yield chunk
        self.history.append({"role": "assistant", "content": "".join(chunks)})


def build_prompt(symptoms: str, readings: list[dict], alerts: list[str]) -> str:
    """Assemble symptômes, mesures classées et fiche de connaissances en un seul prompt."""
    readings_txt = "\n".join(
        f"- {r['capteur']} : {r['valeur']}{r.get('unite', '')}" for r in readings
    ) or "(aucune mesure)"
    alerts_txt = "\n".join(f"- {a}" for a in alerts) or "(aucune)"

    return f"""Symptômes déclarés : {symptoms}

Mesures :
{readings_txt}

Alertes détectées par le système (ne pas les ignorer) :
{alerts_txt}

Fiche de référence :
{_load_knowledge_sheet()}

Propose les causes possibles en t'appuyant uniquement sur ces informations."""


# --- Sortie structurée (JSON) pour l'interprétation ---

class Cause(BaseModel):
    cause: str
    justification: str


class Analysis(BaseModel):
    causes: list[Cause]
    warning: str


def analyze(prompt: str, model: str = None, attempts: int = 3) -> Analysis | None:
    """
    Demande une interprétation structurée. Le score n'est PAS demandé au modèle :
    il est calculé par rules.compute_concordance_index() à partir du résultat.
    Renvoie None après plusieurs échecs (l'appelant doit alors se rabattre sur les règles seules).
    """
    model = model or config.OLLAMA_MODEL
    for _ in range(attempts):
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                format=Analysis.model_json_schema(),
            )
            return Analysis.model_validate_json(response.message.content)
        except (ValidationError, Exception):
            # ValidationError : JSON reçu mais qui ne respecte pas le schéma attendu.
            # Exception générale : erreur de connexion à Ollama, modèle non chargé, etc.
            # Dans les deux cas, on retente (jusqu'à "attempts" fois) avant d'abandonner.
            continue
    return None
