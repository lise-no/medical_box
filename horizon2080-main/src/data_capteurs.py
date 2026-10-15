
from sensors import get_sensor
import storage
import streamlit as st


def get_vital_data():
    """
    Branché sur sensors.get_sensor() (SimulatedSensor tant que
    SENSOR_SOURCE=simulated dans .env)

    Chaque mesure valide est aussi enregistrée dans la base (storage.save_reading), pour
    l'historique de session.
    """
    sensor = get_sensor()
    vitals = {}

    mapping = {"temperature": "temperature", "pouls": "heart_rate", "spo2": "spo2"}
    for sensor_name, vital_key in mapping.items():
        try:
            reading = sensor.read(sensor_name)
        except NotImplementedError:
            continue  # SerialSensor pas encore branché sur du vrai matériel : on laisse vide
        if reading.get("valide", False):
            vitals[vital_key] = reading["valeur"]
            storage.save_reading(st.session_state.session_id, reading)

    return vitals




# Mesures "brutes", utiles à rules.py ---
def get_raw_readings(session_id: str) -> list[dict]:
    """Relit les dernières mesures de la session depuis storage.py, au format contrat
    (capteur/valeur/unite/valide), pour les passer à rules.detect_alerts/find_candidate_causes."""
    rows = storage.get_session_readings(session_id)
    return [dict(row) for row in rows]
