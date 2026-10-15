# Contrat série — à transmettre à l'équipe infra (Arduino/C++)

Ce document décrit exactement ce que le firmware Arduino doit envoyer sur le port série
pour que l'application Python (`sensors.SerialSensor`) puisse le lire. Rien côté Python ne
lit vos capteurs à votre place : c'est le firmware qui doit produire ce format.

## Le format attendu (une ligne JSON par mesure)

```
{"capteur": "spo2", "valeur": 97.0, "unite": "%", "valide": true, "t": 1234}
```

- **Une ligne = une mesure d'UN capteur.** Envoyer les 3 capteurs (spo2, pouls,
  temperature) chacun sur leur propre ligne, à tour de rôle.
- **Terminer chaque ligne par un retour à la ligne** (`Serial.println(...)`, pas
  `Serial.print(...)`) : le côté Python lit ligne par ligne.
- **Débit (baudrate) : 115200**, à configurer identique des deux côtés
  (`Serial.begin(115200)` côté Arduino, `SERIAL_BAUDRATE=115200` dans `.env` côté Python).
- **Rythme : environ 1 mesure par capteur par seconde** (donc ~3 lignes/seconde au total).
- Les clés du JSON restent **exactement** ces noms, en minuscules, en français
  (`capteur`, `valeur`, `unite`, `valide`, `t`) — ne pas les traduire ni les renommer,
  c'est le contrat déjà convenu avec le code Python.

## Le champ obligatoire "capteur"

Doit être exactement l'une de ces 3 chaînes :
- `"spo2"` — unité `"%"`
- `"pouls"` — unité `"bpm"`
- `"temperature"` — unité `"°C"`

## Le champ "valide" — très important

Si la lecture du capteur échoue, est hors plage physiquement possible, ou que le capteur
est débranché : envoyer `"valide": false` (avec `"valeur": null` si besoin) plutôt que
d'inventer une valeur ou de ne rien envoyer. Le code Python ignore silencieusement les
lignes marquées `false` — c'est voulu, ça permet de tester que l'application ne plante pas
sur une mesure ratée.

## Le champ "t"

Un nombre entier. Peu importe qu'il s'agisse d'un vrai timestamp Unix (l'Arduino n'a pas
l'heure sans module RTC) : **`millis() / 1000` (secondes depuis le démarrage de la carte)
suffit très bien pour ce prototype.** Le code Python ne fait aucun calcul dessus, il le
stocke tel quel.

## Exemple minimal de sketch Arduino (à adapter à vos capteurs réels)

```cpp
// Nécessite la bibliothèque ArduinoJson (Bibliothèque > Gérer les bibliothèques > "ArduinoJson")
#include <ArduinoJson.h>

void setup() {
  Serial.begin(115200);
}

void envoyerMesure(const char* capteur, float valeur, const char* unite, bool valide) {
  StaticJsonDocument<200> doc;
  doc["capteur"] = capteur;
  doc["valeur"] = valide ? valeur : (float)0;  // valeur ignorée côté Python si valide=false
  doc["unite"] = unite;
  doc["valide"] = valide;
  doc["t"] = millis() / 1000;

  serializeJson(doc, Serial);
  Serial.println();  // le retour à la ligne est INDISPENSABLE
}

void loop() {
  // TODO équipe infra : remplacer ces lignes par la vraie lecture de vos capteurs
  // (ex. bibliothèque MAX30100/MAX30102 pour SpO2 + pouls, DS18B20 ou similaire pour
  // la température). Mettre valide=false si le capteur renvoie une erreur.
  envoyerMesure("spo2", 97.0, "%", true);
  delay(100);
  envoyerMesure("pouls", 72.0, "bpm", true);
  delay(100);
  envoyerMesure("temperature", 36.8, "°C", true);
  delay(700);  // total ~1 seconde pour les 3 mesures
}
```

## Comment tester leur firmware sans attendre le code Python

Ouvrir le **Moniteur série** de l'Arduino IDE (115200 baud) : ils doivent voir défiler des
lignes qui ressemblent exactement à celles que produit notre simulateur Python
(`scripts/serial_simulator.py`) — comparer les deux formats côte à côte est le moyen le
plus rapide de repérer un écart avant de brancher sur l'application.

## Comment ça se branche ensuite côté application (rien à faire pour l'infra ici)

Une fois la carte reliée en USB, il suffit de mettre dans `.env` :
```
SENSOR_SOURCE=serial
SERIAL_PORT=/dev/ttyUSB0   # ou /dev/ttyACM0 (Linux/Pi), COM3 (Windows) — voir le port réel
```
`sensors.get_sensor()` bascule alors automatiquement sur `SerialSensor`, sans changer une
ligne de code applicatif (voir `src/sensors.py`).
