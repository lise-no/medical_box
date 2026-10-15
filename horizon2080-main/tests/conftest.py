"""
Permet aux tests d'importer les modules de src/ (sensors, rules, ...) directement,
par ex. `from sensors import SimulatedSensor`, sans avoir à préfixer par "src.".

pytest charge ce fichier automatiquement avant les tests du dossier : rien à faire
ailleurs. Si un test échoue avec "ModuleNotFoundError: No module named 'sensors'",
vérifier que ce fichier est bien présent dans tests/.
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
