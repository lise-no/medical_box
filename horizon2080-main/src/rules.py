"""
Moteur de règles déterministe.

Principe central du projet : le LLM explique et reformule, ce fichier décide.
Toute alerte, toute classification et le score final (l'"indice de concordance",
jamais "probabilité") doivent pouvoir se justifier sans le modèle de langage.

Ce module est volontairement un squelette : les fonctions sont écrites avec une
logique minimale pour être testables tout de suite, à enrichir au fil du projet
(table symptômes ↔ causes, pondérations de l'indice de concordance...).
"""

import config


def classify_reading(sensor_name: str, value: float) -> str:
    """Retourne "normal", "low", "high" ou "critical" selon les seuils de config.THRESHOLDS."""
    thresholds = config.THRESHOLDS.get(sensor_name)
    if thresholds is None:
        return "normal"  # capteur non couvert par des seuils : pas de classification

    if sensor_name == "spo2":
        if value < thresholds["critical_below"]:
            return "critical"
        if value < thresholds["low_below"]:
            return "low"
        return "normal"

    if sensor_name == "temperature":
        if value >= thresholds["critical_above"]:
            return "critical"
        if value >= thresholds["fever_above"]:
            return "high"
        return "normal"

    if sensor_name == "pouls":
        if value < thresholds["low_below"]:
            return "low"
        if value > thresholds["high_above"]:
            return "high"
        return "normal"

    return "normal"


# Mots-clés en français : ils sont comparés au texte tapé par l'utilisateur dans le chat,
# qui reste en français (voir la note de convention dans config.py).
ALERT_KEYWORDS = [
    "douleur thoracique",
    "détresse respiratoire",
    "difficulté à respirer",
    "perte de connaissance",
]


def detect_alerts(readings: list[dict], symptoms_text: str = "") -> list[str]:
    """
    Renvoie la liste des alertes critiques déclenchées, à partir :
    - des mesures classées "critical" par classify_reading()
    - de mots-clés dangereux dans le texte des symptômes déclarés

    Une liste vide signifie "pas d'alerte", pas "tout est sûr" : ce module reste un filet
    de sécurité minimal, pas un diagnostic.
    """
    alerts = []

    for reading in readings:
        level = classify_reading(reading["capteur"], reading["valeur"])
        if level == "critical":
            alerts.append(
                f"{reading['capteur']} = {reading['valeur']}{reading.get('unite', '')} "
                f"(seuil critique dépassé) — {config.EMERGENCY_MESSAGE}"
            )

    text = symptoms_text.lower()
    for keyword in ALERT_KEYWORDS:
        if keyword in text:
            alerts.append(f"Symptôme signalé : « {keyword} » — {config.EMERGENCY_MESSAGE}")

    return alerts


def compute_concordance_index(
    rules_score: float, sheet_score: float, llm_score: float,
    rules_weight: float = 0.5, sheet_weight: float = 0.3, llm_weight_cap: float = 0.2,
) -> float:
    """
    Combine trois sources en un seul score entre 0 et 1, appelé "indice de concordance"
    (jamais "probabilité" : un LLM ne produit pas de probabilité calibrée).

    - rules_score : concordance symptômes/mesures avec les règles ci-dessus (0 à 1)
    - sheet_score : la cause est-elle bien couverte par la fiche de connaissances (0 à 1)
    - llm_score   : confiance affichée par le modèle, plafonnée par llm_weight_cap

    Les pondérations par défaut sont une proposition de départ [RECOMMANDÉ, à valider
    avec l'équipe] — voir la section 5 du fichier de contexte.
    """
    capped_llm_score = min(llm_score, 1.0) * llm_weight_cap
    index = (rules_score * rules_weight) + (sheet_score * sheet_weight) + capped_llm_score
    return round(min(index, 1.0), 2)


# Mots-clés en français, cherchés dans le texte des symptômes déclarés (comme
# ALERT_KEYWORDS, mais ici pour repérer des signes non critiques). Chaque "tag" (clé,
# en anglais car c'est un identifiant de code) peut avoir plusieurs formulations possibles.
SYMPTOM_KEYWORDS = {
    "fever": ["fièvre"],
    "cough": ["toux", "touss"],  # "touss" couvre "tousse"/"tousser"/"toussez" en une entrée
    "sore_throat": ["mal de gorge", "gorge"],
    "fatigue": ["fatigue", "fatigué", "fatiguée"],
    "anxiety": ["anxiété", "anxieux", "anxieuse", "stress"],
    "sweating": ["sueurs", "transpiration"],
    "chest_pain": ["douleur thoracique"],
    "breathlessness": ["essoufflement", "détresse respiratoire", "difficulté à respirer"],
}


def detect_signs(readings: list[dict], symptoms_text: str = "") -> set[str]:
    """
    Rassemble en un seul ensemble de "tags" (ex: {"fever", "cough", "low_spo2"}) :
    - les symptômes reconnus dans le texte tapé par l'utilisateur (SYMPTOM_KEYWORDS)
    - les mesures anormales (via classify_reading), sous forme de tags comme "low_spo2"

    Un set (ensemble) ne contient jamais de doublon et ne garde pas d'ordre : c'est
    fait pour ce genre de "quels signes sont présents ?", comparé ensuite avec `&`
    (intersection) dans find_candidate_causes().
    """
    signs = set()

    text = symptoms_text.lower()
    for tag, keywords in SYMPTOM_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            signs.add(tag)

    for reading in readings:
        sensor_name = reading["capteur"]
        level = classify_reading(sensor_name, reading["valeur"])
        if sensor_name == "spo2" and level in ("low", "critical"):
            signs.add("low_spo2")
        if sensor_name == "temperature" and level in ("high", "critical"):
            signs.add("fever_reading")
        if sensor_name == "pouls" and level == "high":
            signs.add("high_pulse")
        if sensor_name == "pouls" and level == "low":
            signs.add("low_pulse")

    return signs


# Table symptômes -> causes candidates. Chaque cause est associée à l'ensemble des tags
# qu'on s'attend à voir si cette cause est la bonne. Point de départ (~8 causes), à
# compléter jusqu'à ~20 avec une source médicale fiable (HAS, MSD...) — voir
# data/knowledge_sheet.txt section 2, qui doit rester cohérente avec cette table.
CAUSE_TABLE = {
    "rhume": {"cough", "sore_throat"},
    "grippe": {"fever", "cough", "fatigue"},
    "bronchite": {"cough", "fever", "fever_reading", "breathlessness"},
    "angine": {"sore_throat", "fever", "fever_reading"},
    "fièvre isolée à surveiller": {"fever", "fever_reading"},
    "crise d'anxiété": {"anxiety", "sweating", "high_pulse"},
    "urgence cardio-respiratoire (à écarter en priorité)": {"chest_pain", "breathlessness", "low_spo2"},
    "fatigue non spécifique (informations insuffisantes)": {"fatigue"},
}


def find_candidate_causes(readings: list[dict], symptoms_text: str = "", min_matches: int = 1) -> list[dict]:
    """
    Propose des causes candidates de façon 100% déterministe (aucun appel au LLM ici),
    en comparant les signes détectés (detect_signs) à CAUSE_TABLE.

    Retourne une liste de dicts {"cause", "matched_signs", "coverage"}, triée par
    "coverage" décroissant. "coverage" = proportion des tags attendus pour cette cause
    qui sont bien présents (ex: 2 tags trouvés sur 3 attendus -> 0.67) : c'est une base
    possible pour le "sheet_score" de compute_concordance_index (à brancher plus tard).

    Sert de secours si le LLM échoue (voir llm.analyze, qui renvoie None dans ce cas),
    et de garde-fou pour vérifier que les causes proposées par le LLM sont plausibles.
    """
    signs = detect_signs(readings, symptoms_text)
    results = []

    for cause, expected_signs in CAUSE_TABLE.items():
        matched = signs & expected_signs  # "&" = intersection : les tags communs aux deux ensembles
        if len(matched) >= min_matches:
            results.append({
                "cause": cause,
                "matched_signs": sorted(matched),
                "coverage": round(len(matched) / len(expected_signs), 2),
            })

    results.sort(key=lambda result: result["coverage"], reverse=True)
    return results
