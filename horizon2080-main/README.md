# Medical Box — Horizon 2080

Prototype de mallette médicale intelligente : chatbot avec un modèle de langage local (Ollama, 100 % hors ligne) + dashboard de capteurs (mesures en temps réel, alertes automatiques) + moteur de règles qui propose des causes probables à partir des symptômes et des mesures.

> Prototype éducatif : ne remplace pas un avis médical. Utilisé uniquement avec des données fictives ou des patients fictifs.

## Contexte de production

Ce projet a été développé dans le cadre du **Workshop EPSI 2026 (B3)**, sur une durée de 4 jours, par une équipe de 2 personnes côté développement logiciel et 2 personnes côté infrastructure/matériel (capteurs, câblage, microcontrôleur).

Le thème choisi est une mallette médicale embarquée à bord d'un vaisseau en mission longue durée, où la liaison avec la Terre peut être retardée — ce qui justifie un fonctionnement 100 % local (aucune dépendance à un service cloud, y compris pour la partie IA).

L'architecture matérielle a évolué plusieurs fois pendant le développement : un capteur de température est aujourd'hui lu soit directement sur un Raspberry Pi (protocole 1-Wire), soit via un Arduino relié en USB à un ordinateur (liaison série) — selon le matériel disponible au moment du test. Les autres mesures (pouls, SpO₂) restent simulées, faute de capteur physique disponible.

## Dépendances nécessaires (en plus de `requirements.txt`)

`requirements.txt` couvre les paquets Python du projet, mais quelques éléments doivent être installés **séparément**, en dehors de l'environnement virtuel Python :

- **Python 3.10 ou plus récent** (nécessaire pour la syntaxe utilisée dans le code, ex. `str | None`).
- **[Ollama](https://ollama.com/download)** — le moteur qui fait tourner le modèle de langage en local. Ce n'est pas une bibliothèque Python : c'est une application à part, qui doit être installée et démarrée sur la machine (elle expose une API locale sur `http://localhost:11434`, utilisée par `src/assistante.py`).
- **Un modèle Ollama construit à partir de `models/Modelfile`** — voir la procédure ci-dessous. Sans ça, le chat affichera une erreur de connexion.
- **Si vous utilisez un vrai capteur branché en USB (Arduino)** : le pilote du port série USB peut être nécessaire selon la carte utilisée (généralement installé automatiquement par Windows/macOS/Linux, mais parfois un pilote CH340 ou CP2102 doit être ajouté manuellement selon le modèle d'adaptateur USB-série de la carte).
- **Sur Linux/Raspberry Pi uniquement**, pour lire un vrai port série sans droits administrateur : l'utilisateur doit appartenir au groupe `dialout` (`sudo usermod -a -G dialout $USER`, puis se reconnecter).
- **Sur Raspberry Pi uniquement**, pour le capteur de température réel : l'interface 1-Wire doit être activée dans la configuration du système (`sudo raspi-config` → *Interface Options* → *1-Wire*), ce n'est pas un réglage du projet mais du système d'exploitation.

## Installation et lancement sur une nouvelle machine

1. **Récupérer le projet**
   ```bash
   git clone <url-du-depot>
   cd mallette-medicale
   ```

2. **Créer et activer un environnement virtuel Python**
   ```bash
   python -m venv venv
   ```
   - Windows : `venv\Scripts\activate`
   - Linux/macOS : `source venv/bin/activate`

3. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

4. **Installer Ollama** (voir [ollama.com/download](https://ollama.com/download)), puis télécharger un modèle de base compact :
   ```bash
   ollama pull qwen2.5:1.5b
   ```
   Adapter le nom du modèle dans `models/Modelfile` (ligne `FROM ...`) si un autre modèle est retenu.

5. **Construire le modèle personnalisé** (thème narratif, ton, garde-fous de sécurité) :
   ```bash
   ollama create medical_box -f models/Modelfile
   ```
   Vérifier que le nom utilisé ici correspond bien à celui attendu dans `src/assistante.py` (`OLLAMA_MODEL`).

6. **Configurer l'environnement du projet**
   Copier `.env.example` en `.env` (à la racine du projet), puis ajuster au minimum `SENSOR_SOURCE` selon le matériel disponible sur cette machine :
   - `simulated` — aucun matériel requis, toutes les mesures sont générées automatiquement (à utiliser par défaut si aucun capteur n'est branché).
   - `hybrid` — capteur de température réel en 1-Wire, uniquement sur Raspberry Pi.
   - `serial_hybrid` — capteur de température réel via un Arduino branché en USB (PC ou Pi) ; renseigner aussi `SERIAL_PORT` avec le port détecté sur la machine (voir `docs/CONTRAT_SERIE_ARDUINO.md` pour savoir comment le trouver).

7. **Lancer l'application**
   ```bash
   streamlit run src/app.py
   ```
   L'interface s'ouvre automatiquement dans le navigateur (généralement sur `http://localhost:8501`).

> **Important** : si `.env` est modifié après que l'application ait déjà démarré, il faut arrêter complètement le processus (`Ctrl+C` dans le terminal) et relancer `streamlit run src/app.py` — un simple rafraîchissement de la page ne suffit pas, le fichier `.env` n'est lu qu'au démarrage.
