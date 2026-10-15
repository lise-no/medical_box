"""
Test simple du simulateur de capteurs. Lancer avec : python -m pytest tests/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sensors import SimulatedSensor, SerialSensor


def test_spo2_reading_within_range():
    sensor = SimulatedSensor()
    reading = sensor.read("spo2")
    assert reading["capteur"] == "spo2"
    assert reading["valide"] is True
    assert 90 <= reading["valeur"] <= 100


def test_force_value():
    sensor = SimulatedSensor()
    reading = sensor.force_value("spo2", 85)
    assert reading["valeur"] == 85


def test_unknown_sensor_raises_error():
    sensor = SimulatedSensor()
    try:
        sensor.read("unknown_sensor")
        assert False, "aurait dû lever une ValueError"
    except ValueError:
        pass


# --- SerialSensor._parse_line : fonction "pure", testable sans port série ni pyserial ---

def test_parse_line_valid_reading():
    line = '{"capteur": "spo2", "valeur": 97, "unite": "%", "valide": true, "t": 1000}\n'
    reading = SerialSensor._parse_line(line)
    assert reading == {"capteur": "spo2", "valeur": 97, "unite": "%", "valide": True, "t": 1000}


def test_parse_line_marked_invalid_is_ignored():
    line = '{"capteur": "spo2", "valeur": null, "unite": "%", "valide": false, "t": 1000}'
    assert SerialSensor._parse_line(line) is None


def test_parse_line_corrupted_json_is_ignored():
    assert SerialSensor._parse_line("pas du json valable") is None


def test_parse_line_missing_key_is_ignored():
    line = '{"capteur": "spo2", "valeur": 97, "valide": true}'  # "unite" et "t" manquants
    assert SerialSensor._parse_line(line) is None


def test_parse_line_empty_is_ignored():
    assert SerialSensor._parse_line("") is None
    assert SerialSensor._parse_line("   \n") is None


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print(f"OK : {name}")
    print("Tous les tests sont passés.")
