"""
Lecture des capteurs.

Deux façons d'obtenir des mesures, avec la MÊME interface : le reste de l'application
appelle .read() sans savoir s'il s'agit de valeurs simulées ou d'un vrai capteur.
Le choix se fait via config.SENSOR_SOURCE ("simulated" ou "serial").
"""

import json
import random
import time
from pathlib import Path

import config


class SimulatedSensor:
    """Génère des mesures fictives. Aucun matériel requis. Sert aussi de plan B pour la démo."""

    def __init__(self):
        # Plages "normales" approximatives, juste pour générer des valeurs plausibles.
        # Les vrais seuils cliniques utilisés pour les alertes sont dans config.THRESHOLDS.
        self._ranges = {
            "spo2": (95, 99),
            "pouls": (60, 90),
            "temperature": (36.5, 37.5),
        }

    def read(self, sensor_name: str) -> dict:
        """Retourne une mesure simulée pour le capteur demandé."""
        if sensor_name not in self._ranges:
            raise ValueError(f"Capteur inconnu : {sensor_name}")
        low, high = self._ranges[sensor_name]
        value = round(random.uniform(low, high), 1)
        unit = "%" if sensor_name == "spo2" else ("°C" if sensor_name == "temperature" else "bpm")
        return {
            "capteur": sensor_name,
            "valeur": value,
            "unite": unit,
            "valide": True,
            "t": int(time.time()),
        }

    def force_value(self, sensor_name: str, value: float) -> dict:
        """Utile pour tester un scénario précis (ex. SpO2 basse) sans attendre le hasard."""
        unit = "%" if sensor_name == "spo2" else ("°C" if sensor_name == "temperature" else "bpm")
        return {"capteur": sensor_name, "valeur": value, "unite": unit, "valide": True, "t": int(time.time())}


class SerialSensor:
    """
    Lit les vraies mesures envoyées par le firmware sur le port série (une ligne JSON par mesure).

    Le flux série mélange les 2 capteurs (pouls et temperature envoyés à tour de rôle,
    voir scripts/serial_simulator.py) : read() lit donc ligne par ligne jusqu'à tomber sur
    une mesure valide du capteur demandé, et abandonne après max_attempts lignes pour ne
    jamais bloquer l'application indéfiniment (port débranché, firmware silencieux, etc.).
    """

    def __init__(self, port: str = None, baudrate: int = None):
        self.port = port or config.SERIAL_PORT
        self.baudrate = baudrate or config.SERIAL_BAUDRATE
        self._connection = None  # ouvert au premier read(), pas dans __init__ (voir _ensure_connected)

    def _ensure_connected(self):
        """Ouvre le port série au premier besoin seulement (pas à la création de l'objet)."""
        if self._connection is None:
            import serial  # importé ici seulement : inutile d'avoir pyserial installé
            self._connection = serial.Serial(self.port, self.baudrate, timeout=1)

    @staticmethod
    def _parse_line(raw_line: str) -> dict | None:
        """
        Transforme UNE ligne brute reçue du port série en mesure exploitable, ou renvoie
        None si la ligne est corrompue, vide, incomplète, ou marquée "valide": false par
        le firmware — dans tous ces cas, on ignore la ligne plutôt que de faire planter
        l'application (contrat encore fragile, voir section 7 du fichier de contexte).

        Fonction "pure" (aucun accès au port série) : testable sans matériel ni pyserial,
        voir tests/test_sensors.py.
        """
        raw_line = raw_line.strip()
        if not raw_line:
            return None  # rien reçu pendant le timeout : pas une erreur, juste à retenter

        try:
            reading = json.loads(raw_line)
        except json.JSONDecodeError:
            return None  # ligne corrompue (coupure série, parasite...) : on l'ignore

        required_keys = {"capteur", "valeur", "unite", "valide", "t"}
        if not required_keys.issubset(reading.keys()):
            return None  # ne respecte pas le contrat : il manque au moins une clé attendue

        if not reading["valide"]:
            return None  # mesure explicitement marquée invalide par le firmware lui-même

        return reading

    def read(self, sensor_name: str, max_attempts: int = 20) -> dict:
        """
        Renvoie la prochaine mesure valide du capteur demandé, au même format que
        SimulatedSensor.read(). Lève TimeoutError si rien de valide n'est trouvé en
        max_attempts lignes (port débranché, mauvais port, firmware arrêté...).
        """
        self._ensure_connected()
        for _ in range(max_attempts):
            raw_bytes = self._connection.readline()
            reading = self._parse_line(raw_bytes.decode("utf-8", errors="ignore"))
            if reading is not None and reading["capteur"] == sensor_name:
                return reading

        raise TimeoutError(
            f"Aucune mesure valide reçue pour '{sensor_name}' après {max_attempts} lignes "
            f"sur {self.port}. Vérifier : le bon port est configuré (SERIAL_PORT dans .env), "
            f"le simulateur ou le firmware tourne bien côté émission, et le débit "
            f"(SERIAL_BAUDRATE) correspond des deux côtés."
        )

    def close(self):
        """À appeler en fin de session pour libérer le port proprement (pas obligatoire en test)."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None


class I2CSensor:
    """
    Lit les mesures relayées par l'Arduino sur le bus I2C du Raspberry Pi.

    Abandonné faute de réussite de mise en place du protocole côté infra
    """

    # Une seule adresse (l'Arduino), pas une par capteur : À COMPLÉTER avec l'équipe infra.
    ARDUINO_I2C_ADDRESS = None

    def __init__(self, bus_number: int = None):
        self.bus_number = bus_number if bus_number is not None else config.I2C_BUS_NUMBER
        self._bus = None  # ouvert au premier read(), même logique que SerialSensor

    def _ensure_connected(self):
        """Ouvre le bus I2C au premier besoin seulement (pas à la création de l'objet)."""
        if self._bus is None:
            import smbus2  # importé ici seulement : inutile d'avoir smbus2 installé pour tester en simulé
            self._bus = smbus2.SMBus(self.bus_number)

    def read(self, sensor_name: str) -> dict:
        """
        Renvoie une mesure au même format que SimulatedSensor.read() et SerialSensor.read().
        Lève NotImplementedError tant que le TODO ci-dessus n'est pas résolu : mieux vaut un
        échec explicite et compréhensible qu'un plantage confus plus tard dans l'application.
        """
        self._ensure_connected()
        if sensor_name not in ("pouls", "temperature"):
            raise ValueError(
                f"Capteur '{sensor_name}' non prévu en I2C (SpO2 abandonné, voir "
                "docs/CONTRAT_I2C.md)."
            )
        if self.ARDUINO_I2C_ADDRESS is None:
            raise NotImplementedError(
                "Adresse I2C de l'Arduino inconnue. Compléter ARDUINO_I2C_ADDRESS dans "
                "I2CSensor (sensors.py) avec l'équipe infra avant de pouvoir lire un capteur."
            )
        raise NotImplementedError(
            "Lecture I2C réelle pas encore écrite : la répartition des registres "
            "(pouls / temperature / validité) doit encore être confirmée avec l'équipe "
            "infra. Voir le TODO en tête de I2CSensor et docs/CONTRAT_I2C.md."
        )

    def close(self):
        """À appeler en fin de session pour libérer le bus proprement (pas obligatoire en test)."""
        if self._bus is not None:
            self._bus.close()
            self._bus = None


class OneWireTemperatureSensor:
    """
    Lit un capteur de température 1-Wire (type DS18B20) branché directement sur le Pi.

    Fonctionnement : le noyau Linux du Pi expose chaque capteur 1-Wire détecté comme un
    fichier sous /sys/bus/w1/devices/<id>/w1_slave — pas besoin de bibliothèque Python
    supplémentaire, une simple lecture de fichier suffit.

    Abandonné suite au plantage su Pi.
    """

    W1_DEVICES_PATH = Path("/sys/bus/w1/devices")

    def __init__(self, device_id: str = None):
        # device_id optionnel (ex. "28-000001234567") : si absent, auto-détection du
        # premier capteur trouvé (suffisant tant qu'il n'y en a qu'un seul).
        self.device_id = device_id

    def _find_device_path(self) -> Path:
        if self.device_id:
            return self.W1_DEVICES_PATH / self.device_id / "w1_slave"
        candidates = sorted(self.W1_DEVICES_PATH.glob("28-*"))  # "28-" = famille DS18B20
        if not candidates:
            raise RuntimeError(
                "Aucun capteur 1-Wire détecté dans /sys/bus/w1/devices. Vérifier : "
                "l'interface 1-Wire est activée (raspi-config → Interface Options → 1-Wire), "
                "le capteur est bien câblé (résistance de tirage 4.7kΩ entre donnée et 3.3V), "
                "et brancher sur GPIO4 (broche par défaut) sauf configuration différente."
            )
        return candidates[0] / "w1_slave"

    def read(self, sensor_name: str) -> dict:
        """Renvoie une mesure au même format que les autres lecteurs (voir en tête de fichier)."""
        if sensor_name != "temperature":
            raise ValueError(
                f"OneWireTemperatureSensor ne gère que 'temperature', pas '{sensor_name}'."
            )

        path = self._find_device_path()
        content = path.read_text()
        lines = content.strip().split("\n")

        if not lines[0].strip().endswith("YES"):
            # Le capteur 1-Wire ajoute une vérification (CRC) sur chaque lecture ; "NO" en
            # fin de première ligne signifie une lecture corrompue (parasite électrique) —
            # à retenter, pas une panne définitive.
            raise ValueError(
                "Lecture 1-Wire invalide (vérification CRC échouée) — retenter la lecture."
            )

        value = int(lines[1].split("t=")[-1]) / 1000.0  # le capteur donne des millièmes de degré
        return {
            "capteur": "temperature",
            "valeur": round(value, 1),
            "unite": "°C",
            "valide": True,
            "t": int(time.time()),
        }

    def close(self):
        pass  # rien à fermer : chaque lecture rouvre le fichier, pas de connexion persistante


class HybridSensor:
    """
    Combine un capteur réel pour la température et des valeurs simulées pour le pouls.
    """

    def __init__(self):
        self._temperature_sensor = OneWireTemperatureSensor(device_id=config.ONEWIRE_DEVICE_ID)
        self._simulated = SimulatedSensor()

    def read(self, sensor_name: str) -> dict:
        if sensor_name == "temperature":
            return self._temperature_sensor.read(sensor_name)
        return self._simulated.read(sensor_name)  # "pouls" (et "spo2" si jamais redemandé)

    def close(self):
        self._temperature_sensor.close()

class SerialHybridSensor:
    """
    Combine la température réelle reçue par le port série (Arduino/USB) avec des
    valeurs simulées pour le pouls et le spo2 (non envoyés par l'Arduino actuellement).
    """

    def __init__(self):
        self._temperature_sensor = SerialSensor()
        self._simulated = SimulatedSensor()

    def read(self, sensor_name: str) -> dict:
        if sensor_name == "temperature":
            return self._temperature_sensor.read(sensor_name)
        return self._simulated.read(sensor_name)

    def close(self):
        self._temperature_sensor.close()

def get_sensor() -> SimulatedSensor | SerialSensor | I2CSensor | HybridSensor | SerialHybridSensor:
    """Point d'entrée unique : renvoie le bon lecteur selon config.SENSOR_SOURCE."""
    if config.SENSOR_SOURCE == "hybrid":
        return HybridSensor()
    if config.SENSOR_SOURCE == "serial_hybrid":
        return SerialHybridSensor()
    if config.SENSOR_SOURCE == "i2c":
        return I2CSensor()  # obsolète, gardé en référence
    if config.SENSOR_SOURCE == "serial":
        return SerialSensor()  # obsolète, gardé en référence
    return SimulatedSensor()