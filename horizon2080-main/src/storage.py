"""
Stockage local en SQLite : mesures d'une session en cours, et plus tard historique patient
"""

import sqlite3

import config


def get_connection() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize():
    # Crée les tables si elles n'existent pas encore. À appeler une fois au démarrage de l'app.
    connection = get_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            capteur TEXT NOT NULL,
            valeur REAL NOT NULL,
            unite TEXT,
            valide INTEGER NOT NULL DEFAULT 1,
            timestamp INTEGER NOT NULL
        )
        """
    )
    # Table pour le bonus "historique patient" pas encore utilisée dans cette version
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient TEXT NOT NULL,
            symptoms TEXT,
            result_json TEXT,
            timestamp INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


def save_reading(session_id: str, reading: dict):
    connection = get_connection()
    connection.execute(
        "INSERT INTO readings (session_id, capteur, valeur, unite, valide, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            session_id,
            reading["capteur"],
            reading["valeur"],
            reading.get("unite"),
            int(reading.get("valide", True)),
            reading["t"],
        ),
    )
    connection.commit()
    connection.close()


def get_session_readings(session_id: str) -> list[sqlite3.Row]:
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM readings WHERE session_id = ? ORDER BY timestamp", (session_id,)
    ).fetchall()
    connection.close()
    return rows
