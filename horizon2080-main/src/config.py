"""
Réglages centralisés du projet.
"""

import os
from pathlib import Path

# Charge le fichier .env s'il existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# config.py est dans src/, mais data/ et models/ sont à la racine du projet (un niveau
# au-dessus) : d'où le .parent.parent. Si ce fichier bouge, cette ligne doit être ajustée.
ROOT_DIR = Path(__file__).resolve().parent.parent

# --- Sensors ---
# "simulated": valeurs générées par le code, aucun matériel nécessaire (par défaut).
# "hybrid"   : contrat matériel FINAL [23/09, après échec de l'I2C côté infra] — le capteur
#              de chaleur est réel (1-Wire, branché directement sur le Pi, voir
#              OneWireTemperatureSensor dans sensors.py), le pouls reste simulé (pas de
#              solution matérielle disponible à temps). C'est la valeur à utiliser sur le
#              Pi final. Voir docs/CONTRAT_CAPTEUR_TEMPERATURE.md.
# "serial"   : ANCIEN contrat (Arduino relais en USB) — obsolète, gardé en référence.
# "i2c"      : ANCIEN contrat (Arduino esclave I2C) — obsolète, abandonné le 23/09 faute de
#              réussir la mise en place de l'I2C côté infra. Gardé en référence.
SENSOR_SOURCE = os.environ.get("SENSOR_SOURCE", "simulated")
SERIAL_PORT = os.environ.get("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUDRATE = int(os.environ.get("SERIAL_BAUDRATE", "115200"))
I2C_BUS_NUMBER = int(os.environ.get("I2C_BUS_NUMBER", "1"))  # bus 1 = standard sur Raspberry Pi
# Utilisé seulement si SENSOR_SOURCE=hybrid. Optionnel : identifiant exact du capteur 1-Wire
# (ex. "28-000001234567", visible avec `ls /sys/bus/w1/devices/`). Laisser vide pour une
# auto-détection (suffisant tant qu'un seul capteur 1-Wire est branché).
ONEWIRE_DEVICE_ID = os.environ.get("ONEWIRE_DEVICE_ID") or None

# --- Storage ---
DB_PATH = ROOT_DIR / os.environ.get("DB_PATH", "data/kit.db")
KNOWLEDGE_SHEET_PATH = ROOT_DIR / "data" / "knowledge_sheet.txt"

# --- Language model (Ollama) ---
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "medical_box")

# Ne pas dupliquer ces seuils ailleurs dans le code : tout passe par ce fichier.
THRESHOLDS = {
    "spo2": {"critical_below": 90, "low_below": 95},              # en %
    "temperature": {"critical_above": 40.0, "fever_above": 38.0},  # en °C
    "pouls": {"low_below": 50, "high_above": 120},                # battements/min au repos
}

EMERGENCY_MESSAGE = (
    "activez le protocole d'urgence médicale du bord et contactez immédiatement "
    "l'infirmerie (rappel prototype : en dehors de cette simulation, appelez le 15 ou le 112)"
)

WARNING_BANNER = (
    "⚠️ Simulation éducative — assistant médical embarqué (mallette médicale avancée, "
    "vaisseau en mission longue durée, 2080). Ne remplace pas l'avis d'un médecin ou "
    f"d'un officier médical qualifié. En cas de signe grave : {EMERGENCY_MESSAGE}."
)
