"""
Tests simples du moteur de règles. Lancer avec : python -m pytest tests/
(ou, sans pytest installé : python tests/test_rules.py)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rules import classify_reading, detect_alerts, detect_signs, find_candidate_causes


def test_spo2_critical():
    assert classify_reading("spo2", 88) == "critical"


def test_spo2_low():
    assert classify_reading("spo2", 93) == "low"


def test_spo2_normal():
    assert classify_reading("spo2", 98) == "normal"


def test_alert_on_critical_reading():
    readings = [{"capteur": "spo2", "valeur": 85, "unite": "%"}]
    alerts = detect_alerts(readings)
    assert len(alerts) == 1


def test_alert_on_symptom_keyword():
    alerts = detect_alerts([], symptoms_text="J'ai une douleur thoracique depuis ce matin")
    assert len(alerts) == 1


def test_no_alert_when_everything_normal():
    readings = [{"capteur": "spo2", "valeur": 98, "unite": "%"}]
    assert detect_alerts(readings, symptoms_text="fatigue légère") == []


# --- Cas cliniques de tests/clinical_cases.md, appliqués à find_candidate_causes ---

def test_signs_detect_fever_cough_and_low_spo2():
    # Cas 1 : fièvre 38,9°C, toux, SpO2 93% (donc "low", pas "critical" — cf. cas 1)
    readings = [{"capteur": "spo2", "valeur": 93, "unite": "%"}]
    signs = detect_signs(readings, symptoms_text="J'ai de la fièvre et je tousse depuis 3 jours")
    assert signs == {"fever", "cough", "low_spo2"}


def test_candidate_causes_case1_includes_bronchite_or_grippe():
    readings = [{"capteur": "spo2", "valeur": 93, "unite": "%"}]
    causes = find_candidate_causes(readings, symptoms_text="fièvre et toux")
    names = [result["cause"] for result in causes]
    assert "grippe" in names or "bronchite" in names


def test_candidate_causes_case2_anxiety():
    # Cas 2 : pouls 130, sueurs, anxiété, pas de fièvre, SpO2 normale
    readings = [{"capteur": "pouls", "valeur": 130, "unite": "bpm"}]
    causes = find_candidate_causes(readings, symptoms_text="je suis anxieux et j'ai des sueurs")
    assert causes[0]["cause"] == "crise d'anxiété"
    assert causes[0]["coverage"] == 1.0


def test_candidate_causes_case5_insufficient_information():
    # Cas 5 : "je suis fatigué", aucune mesure -> la meilleure piste doit rester vague
    # (pas de diagnostic inventé à partir d'un seul symptôme non spécifique)
    causes = find_candidate_causes([], symptoms_text="Je suis fatigué.")
    assert causes[0]["cause"] == "fatigue non spécifique (informations insuffisantes)"
    assert causes[0]["coverage"] == 1.0


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print(f"OK : {name}")
    print("Tous les tests sont passés.")
