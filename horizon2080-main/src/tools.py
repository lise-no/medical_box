import config
import streamlit as st

def format_value(value, unit=""):
    """Affiche une valeur ou '—' si elle n'existe pas."""

    if value is None:
        return "—"

    return f"{value} {unit}".strip()

#a modifier
def get_status(parameter, value):
    """
    Cette fonction permet d'afficher un statut simple.

    ATTENTION :
    Les seuils ci-dessous sont uniquement des exemples d'affichage.
    Ils devront être validés avec votre encadrement/projet médical
    avant utilisation réelle.

    --- AJOUT : ces seuils sont indicatifs pour l'affichage seulement. Les VRAIES alertes
    (celles qui comptent) viennent de rules.detect_alerts(), qui utilise config.THRESHOLDS
    (déjà validées côté équipe) — voir plus bas dans la page Assistant IA et le Dashboard.
    """

    if value is None:
        return "En attente", "status-waiting"

    try:
        value = float(value)
    except (ValueError, TypeError):
        return "Disponible", "status-normal"

    if parameter == "temperature":

        if value >= 38:
            return "Valeur à surveiller", "status-warning"

        return "Mesure disponible", "status-normal"

    if parameter == "spo2":

        if value < 94:
            return "Valeur à surveiller", "status-warning"

        return "Mesure disponible", "status-normal"

    if parameter == "heart_rate":

        if value < 50 or value > 100:
            return "Valeur à surveiller", "status-warning"

        return "Mesure disponible", "status-normal"

    return "Mesure disponible", "status-normal"


def display_vital_card(icon, title, value, unit):
    """
    Affiche une carte de mesure.
    """

    if value is None:
        value_display = "—"
        status = "En attente des capteurs"
    else:
        value_display = f"{value} {unit}"
        status = "Mesure disponible"

    card = f"""
    <div style="
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        height: 150px;
    ">

        <div style="
            font-size: 15px;
            color: #6b7280;
            margin-bottom: 12px;
        ">
            {icon}&nbsp;&nbsp;{title}
        </div>

        <div style="
            font-size: 30px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 10px;
        ">
            {value_display}
        </div>

        <div style="
            font-size: 13px;
            color: #16a34a;
        ">
            ● {status}
        </div>

    </div>
    """

    st.html(card)


def build_vitals_context(vitals):
    """
    Transforme les données des capteurs en texte pour Ollama.

    L'IA reçoit uniquement les mesures réellement disponibles.
    """

    if not vitals:
        return (
            "Aucune donnée vitale n'est actuellement disponible depuis les capteurs."
        )

    lines = []

    # Dictionnaire permettant d'avoir des noms compréhensibles
    labels = {
        "temperature": "Température corporelle",
        "heart_rate": "Fréquence cardiaque",
        "spo2": "Saturation en oxygène (SpO₂)",
        "systolic": "Pression systolique",
        "diastolic": "Pression diastolique",
        "respiratory_rate": "Fréquence respiratoire"
    }

    units = {
        "temperature": "°C",
        "heart_rate": "bpm",
        "spo2": "%",
        "systolic": "mmHg",
        "diastolic": "mmHg",
        "respiratory_rate": "resp/min"
    }

    for key, value in vitals.items():

        label = labels.get(
            key,
            key.replace("_", " ").capitalize()
        )

        unit = units.get(
            key,
            ""
        )

        lines.append(
            f"- {label} : {value} {unit}"
        )

    return "\n".join(lines)


# Contenu de la fiche de connaissances
def load_knowledge_sheet() -> str:
    try:
        return config.KNOWLEDGE_SHEET_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


KNOWLEDGE_SHEET = load_knowledge_sheet()
