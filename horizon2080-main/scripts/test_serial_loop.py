# CONTEXTE DU PROJET : Mallette médicale (prototype offline)

> Document de reprise pour toute nouvelle conversation. Rédigé le lundi 21 septembre 2026 (16 h 30, heure de Paris), à partir de la première conversation de cadrage.
> **Ce fichier est la source de vérité.** Quand une décision change, mettre à jour ce fichier (section 13) plutôt que de la redire de mémoire.
> Légende des statuts : **[DÉCIDÉ]** = validé par l'équipe ou imposé ; **[RECOMMANDÉ]** = proposé par Claude, non confirmé par l'équipe ; **[OUVERT]** = question sans réponse.

---

## 0. Instructions à coller dans les « instructions du projet »

```
Tu aides deux étudiants de 3e année de bachelor (EPSI) à développer un prototype de « mallette médicale » :
chatbot médical avec LLM local (Ollama), fonctionnant hors ligne, + dashboard de capteurs.
Lis d'abord le fichier CONTEXTE_PROJET_mallette_medicale.md de la base de connaissances : c'est la référence.
Règles de collaboration :
- Réponds en français.
- L'utilisateur est débutant en Python et n'a jamais utilisé de LLM : explique en détail, pas à pas, sans jargon non défini.
- Rappelle le calendrier : rendu (code + rapport) jeudi 24 septembre 2026 au soir, présentation vendredi 25 septembre.
- Principe central : le LLM explique et reformule, le code (règles) décide (alertes, classification, score).
- Le score s'appelle « indice de concordance », jamais « probabilité ».
- Uniquement des patients fictifs. Bandeau permanent « prototype éducatif, ne remplace pas un avis médical ».
- Pour toute information récente (modèles Ollama, versions d'outils), vérifier par recherche plutôt que de se fier à la mémoire.
- Si une décision change, proposer de mettre à jour le fichier de contexte.
```

---

## 1. Objectif du projet

Développer un **prototype de mallette médicale** :

1. **Chatbot** : discussion avec un modèle de langage possédant des informations médicales, capable de répondre à partir de symptômes donnés.
2. **Dashboard** en deux zones : d'un côté le chat avec le modèle ; de l'autre des **petites interfaces pour déclencher le démarrage des capteurs pendant une durée donnée** et **enregistrer temporairement les résultats**.
3. **Interprétation** : le modèle reçoit les mesures (et les symptômes) et propose des **causes probables avec un score de fiabilité**.
4. **Bonus si le temps le permet** : historique médical par patient.

Nature du livrable : prototype éducatif, démontré devant un jury (présentation vendredi).

### Habillage narratif [DÉCIDÉ, 22/09]

Le projet est présenté sous un thème de science-fiction : nous sommes en l'an 2080, la
mallette est un équipement médical avancé embarqué sur un **vaisseau en mission
d'exploration longue durée**. L'assistant du chatbot est utilisable par **n'importe quel
membre d'équipage formé à l'usage des capteurs**, pas nécessairement un médecin ; son rôle
est de fournir des **pistes de diagnostic**, jamais un diagnostic définitif. La liaison avec
la Terre pouvant être retardée ou indisponible, les messages d'urgence renvoient vers un
**protocole fictif du bord** plutôt que directement vers un service terrestre.

Ce thème est purement narratif (persona et formulations du prompt et des messages
d'interface) : **l'architecture, les principes de sécurité et le moteur de règles ne
changent pas**. Pour rester robuste si un cas réel était testé, chaque message d'urgence
combine la formulation fictive et un rappel technique réel (« appelez le 15 ou le 112 »).
Ce rappel est centralisé dans `config.EMERGENCY_MESSAGE` (voir section 6bis) : ne jamais le
réécrire séparément ailleurs dans le code.

## 2. Contraintes [DÉCIDÉ]

- **Le modèle de langage doit fonctionner hors ligne (offline).**
- **Petit budget** (cible indicative : moins de 50 € de capteurs, matériel géré par une autre équipe).
- **Délai très court** : projet démarré le lundi 21 septembre 2026 dans l'après-midi ; **rendu jeudi 24 septembre au soir** ; **présentation vendredi 25 septembre**.
- **Jamais de vraies données de santé** : patients fictifs uniquement.
- Les deux développeurs n'ont **jamais développé avec un modèle de langage** auparavant.

## 3. Équipe

| Rôle | Personne | Niveau / périmètre |
|---|---|---|
| Développeur A | **L'utilisateur** (celui qui dialogue avec Claude) | **Très peu de Python.** Code uniquement. |
| Développeur B | Sa collègue | **Un peu de Python.** Code uniquement. |
| Matériel (2 étudiants) | Infrastructure, montage des capteurs, **firmware** de la carte | Ne font pas le code Python ; livrent un flux de données série |

- Contexte scolaire : **3e année de bachelor, EPSI**.
- **Temps d'apprentissage** autorisé hors cours : **3 h maximum par personne**.
- Les développeurs travaillent **uniquement sur la partie code**.
- La mémoire de Claude n'est **pas activée** sur ce compte : Claude ne retient rien d'une conversation à l'autre, d'où ce fichier.

## 4. Calendrier [DÉCIDÉ pour les dates, RECOMMANDÉ pour le détail]

| Jour | Date | Événement |
|---|---|---|
| J0 | **Lundi 21 sept. (après-midi)** | Démarrage. Ollama installé (par l'utilisateur). |
| J1 | Mardi 22 sept. | Développement |
| J2 | Mercredi 23 sept. | Développement, première démo de bout en bout |
| J3 | **Jeudi 24 sept.** | Matin : dernières fonctions. Midi : gel du code. Après-midi : tests et rapport. **Soir : rendu code + rapport.** |
| — | **Vendredi 25 sept.** | **Présentation / démo devant le jury** |

### Planning détaillé recommandé

| | **Utilisateur (débutant Python)** | **Collègue** |
|---|---|---|
| **Lundi après-midi** | Ensemble : installer Ollama, tester 2-3 modèles sur 5 cas cliniques, **fixer le contrat série avec l'équipe matériel**, créer le dépôt Git et le squelette | Idem |
| **Lundi soir (hors cours, 3 h max)** | Python essentiel (1 h 30), Streamlit (1 h), Git (30 min) | Ollama en Python + sortie JSON + Pydantic (1 h), RAG/notions (optionnel), `pyserial` (1 h) |
| **Mardi (J1)** | Simulateur de capteurs, moteur de règles v1 (normale/basse/haute, alertes critiques), layout Streamlit | Chat branché sur Ollama avec streaming, prompt système v1, premier JSON validé |
| **Mercredi matin (J2)** | Sessions de mesure (démarrer, durée, stockage temporaire, cartes capteurs avec graphe) | Pipeline « symptômes + mesures → LLM → JSON », relance si JSON invalide |
| **Mercredi après-midi** | **Première démo de bout en bout, même moche.** Essai avec vrais capteurs si le firmware est arrivé. **Premier test sur la Raspberry Pi si elle est utilisée.** | Fiche de connaissances injectée dans le prompt |
| **Jeudi matin (J3)** | Table symptômes ↔ causes (~20 pathologies), indice de concordance, affichage | Intégration chat ↔ mesures, affichage des sources, corrections |
| **Jeudi midi** | **GEL DU CODE** : plus aucune nouvelle fonction | |
| **Jeudi après-midi** | Tests complets PC en mode avion, captures d'écran, README d'installation | Rédaction du rapport |
| **Jeudi soir** | Relecture croisée, **tag Git `v1-rendu`**, livraison code + rapport | |
| **Vendredi matin** | Diapositives (5 à 8), répétition de la démo | Répétition, **vidéo de secours de la démo** |

Conseils pour vendredi : faire la démo sur la version taguée `v1-rendu` ; répéter deux fois avec chronomètre en répartissant la parole ; préparer 2-3 scénarios dont un avec alerte critique ; anticiper les questions du jury (« pourquoi un score et pas une probabilité ? », « et si le modèle se trompe ? », « où sont les données ? »).

## 5. Architecture [RECOMMANDÉ]

```
[Capteurs] → [Carte ESP32/Arduino + firmware] → USB série (JSON) → [PC ou Raspberry Pi]
                                                                        │
                                                         ┌──────────────┴───────────────┐
                                                         │  Application Python           │
                                                         │  - lecteur de capteurs        │
                                                         │  - sessions de mesure (SQLite)│
                                                         │  - moteur de règles + score   │
                                                         │  - fiche de connaissances     │
                                                         └──────────────┬───────────────┘
                                                                        │ HTTP local (localhost:11434)
                                                                   [Ollama + modèle]
                                                                        │
                                                    [Dashboard Streamlit : chat | capteurs]
```

### Principes de conception clés [RECOMMANDÉ, à garder]

1. **Le LLM explique et reformule ; le code décide.** Les petits modèles locaux se trompent plus, respectent moins bien les formats et calculent mal. Alertes, classification des mesures et score sont calculés en Python.
2. **Moteur de règles déterministe** : alertes critiques (exemples à valider avec une source médicale fiable : SpO₂ < 90 %, température > 40 °C, fréquence cardiaque extrême, mots-clés comme « douleur thoracique » ou « détresse respiratoire » → alerte rouge « appelez le 15/112 »), classification de chaque mesure (normale/basse/haute), petite table symptômes ↔ causes candidates (~20 pathologies courantes).
3. **Score hybride appelé « indice de concordance »** (pas « probabilité », car un LLM ne produit pas de probabilité calibrée) : part issue de la concordance symptômes/mesures avec les règles (par ex. 50 %) ; part issue de la couverture par la fiche de connaissances ; part issue de l'avis du LLM, **plafonnée**. Les pondérations exactes **restent à définir**.
4. **Plan B si le LLM plante** : l'application reste utile grâce aux règles.
5. **Bandeau permanent** rappelant qu'il s'agit d'une simulation et que ça ne remplace pas un avis médical qualifié. Depuis le 22/09, formulé selon le thème narratif (voir « Habillage narratif » en section 1) : texte centralisé dans `config.WARNING_BANNER` et `config.EMERGENCY_MESSAGE` (repris par `rules.py` et `models/Modelfile`, ne pas dupliquer ailleurs).
6. **Patients fictifs uniquement.** Si le RGPD est abordé dans le rapport : données de santé = données sensibles ; en production il faudrait chiffrement, consentement, hébergement HDS.

### JSON de sortie du modèle (proposition)

Le score n'est **pas** demandé au modèle (calculé par le code). Schéma minimal actuellement envisagé :

```json
{
  "causes": [ {"cause": "...", "justification": "..."} ],
  "warning": "..."
}
```
Champ conservé en anglais (`warning`) pour coller à la classe `Analysis` réelle dans `llm.py`.
Version élargie possible : `signes_alerte`, `examens_ou_actions_suggerees`, `elements_concordants`.

## 6. Stack technique [RECOMMANDÉ, non confirmé par l'équipe]

- **Python**, tout dans une seule application (pas de React/JavaScript).
- **Streamlit** pour le dashboard (composants de chat, boutons, deux colonnes). **Plan B : NiceGUI** si le rafraîchissement en direct des mesures est trop pénible.
- **Ollama** + bibliothèque Python `ollama` (LLM local).
- **Pydantic** (validation du JSON du modèle).
- **SQLite** (mesures temporaires, historique patient).
- **pyserial** (lecture du port USB).
- **Git** : une branche par personne ; 5 commandes de base (`add`, `commit`, `push`, `pull`, `branch`).
- **FastAPI : non retenu** (inutile tant qu'il n'y a qu'une application).
- **ChromaDB / RAG vectoriel : abandonné pour cette échéance**, remplacé par une **fiche de connaissances** texte (5 à 10 pages issues de sources fiables : HAS, Ameli, Manuel MSD grand public, Santé publique France, référentiels de constantes vitales) injectée dans le prompt, ou seulement la partie pertinente selon les symptômes. Vérifier les conditions de réutilisation des sources et les citer dans le rapport. Le vrai RAG est présenté comme une amélioration future.
- Structure de fichiers (mise à jour 22/09, voir la convention de nommage ci-dessous et la section 14 pour l'arborescence complète) : `src/app.py`, `src/sensors.py`, `src/rules.py`, `src/llm.py`, `data/knowledge_sheet.txt`, `models/Modelfile`, `README.md`.

### Convention de nommage du code [DÉCIDÉ, 22/09]

- **Identifiants (variables, fonctions, classes) : en anglais** dans tout le projet.
- **Commentaires : en français.**
- **Chatbot** (prompt système, messages affichés, contenu de la fiche de connaissances) : **en français**.
- **Exception assumée** : les clés du contrat de données avec l'équipe infra
  (`capteur`, `valeur`, `unite`, `valide`, `t`) et les identifiants de capteurs (`spo2`,
  `pouls`, `temperature`) restent en français, car ils correspondent au format déjà
  convenu avec leur firmware Arduino/C++ (section 7). Les traduire casserait la
  compatibilité avec leur code sans bénéfice pour le projet. Documenté en tête de
  `src/config.py` et `src/sensors.py`.
- Modules renommés en conséquence : `sensors.py` → `sensors.py`, `rules.py` → `rules.py`,
  `storage.py` → `storage.py`, `models/` → `models/`, `serial_simulator.py` →
  `serial_simulator.py`, `knowledge_sheet.txt` → `knowledge_sheet.txt`,
  `clinical_cases.md` → `clinical_cases.md`, `model_results.md` → `model_results.md`.
  `README.md` et `docs/CONTEXTE_PROJET_mallette_medicale.md` restent tels quels
  (documentation, pas du code).

### Dossier `src/` [DÉCIDÉ, 22/09]

Les 6 modules applicatifs (`app.py`, `config.py`, `sensors.py`, `rules.py`, `llm.py`,
`storage.py`) sont regroupés dans `src/`, pour séparer clairement le code livré du reste
(données, tests, scripts de dev, docs) — voir le détail et la justification par fichier
dans le README (section "Pourquoi un dossier `src/` ?"). Conséquences pratiques :
- Lancement : `streamlit run src/app.py` (au lieu de `streamlit run app.py`).
- `config.ROOT_DIR` remonte d'un niveau supplémentaire (`parent.parent`) pour continuer à
  pointer vers la racine du projet, où restent `data/` et `models/`.
- `tests/conftest.py` ajoute `src/` au chemin d'import Python, pour que les tests puissent
  continuer à faire `from sensors import ...` sans changement.
- `scripts/serial_simulator.py` reste **hors** de `src/` (outil de développement, pas une
  dépendance de l'application).

## 7. Contrat d'interface avec l'équipe matériel

**Statut au 22/09 (mardi matin) : contrat pas encore complètement validé.** L'équipe infra teste de son côté, avec un accès limité au matériel de l'école. Ne pas attendre une validation formelle pour avancer côté code : continuer avec `SimulatedSensor`, et préparer/tester `SerialSensor` via un port série virtuel (voir plus bas) pendant que l'infra teste en parallèle. Le firmware est fait par l'équipe matériel (en Arduino/C++), pas par les développeurs.

Le **firmware** est le programme qui tourne sur la carte électronique : il lit les capteurs (souvent via I2C), convertit les données brutes en mesures (le MAX30102 fournit des signaux lumineux bruts, une bibliothèque calcule pouls/SpO₂), signale les mesures invalides, et envoie tout au PC par USB.

Proposition de contrat [RECOMMANDÉ] :

| Point | Proposition |
|---|---|
| Format | **Une ligne JSON par mesure**, ex. `{"capteur": "spo2", "valeur": 97, "unite": "%", "valide": true, "t": 1024}` |
| Vitesse du port série | Valeur commune, par ex. 115200 bauds |
| Durée de mesure | **Le firmware envoie en continu ; Python décide quand enregistrer et pendant combien de temps.** Pas de commandes à écouter côté firmware |
| Fréquence | ~1 mesure par seconde par capteur |
| Noms/unités | Liste figée : `spo2`, `pouls`, `temperature`… |
| Mesure invalide | Champ `valide: false` (jamais un 0 ou une valeur absurde) |
| Livraison | **Un premier firmware, même avec un seul capteur, mercredi matin au plus tard** |

À demander à l'équipe matériel : quelle carte, quels capteurs, quel langage (Arduino C++ ou MicroPython), s'ils savent déjà lire les capteurs. Matériel suggéré à petit budget (non confirmé) : ESP32 ou Arduino, MAX30102 (pouls/SpO₂), MLX90614 ou DS18B20 (température).

### Côté code : deux lecteurs interchangeables

- `SimulatedSensor` : valeurs fictives (à écrire en premier, sert aussi de **plan B de démo**).
- `SerialSensor` : lit le vrai port USB.
- Choix par un **réglage de configuration** (ex. variable `SENSOR_SOURCE=simulated|serial`) ; le reste de l'application ne sait pas lequel est utilisé.
- Astuce de test sans matériel : **port série virtuel** (`socat` sous Linux/macOS, `com0com` sous Windows) et un script Python qui joue le rôle du firmware, en envoyant aussi des cas piégeux (mesure invalide, valeur absurde, ligne corrompue, câble débranché).

## 8. Raspberry Pi pour la démo [OUVERT, mise à jour 22/09]

**La Raspberry Pi est le support principal souhaité par l'équipe** (mise à jour du 22/09, mardi matin). Décision encore **conditionnée à la puissance maximale de la Pi disponible**, en cours de vérification. Tant que ses specs ne sont pas connues, développer avec `SimulatedSensor` et un modèle compact, et rester prêt à basculer sur le PC de secours (voir section 9, RAM/GPU connus depuis le 22/09) si la Pi s'avère trop faible.

Éléments de décision :
- **Cas A, passerelle** : le modèle tourne sur un PC, la Pi lit seulement les capteurs.
- **Cas B, la Pi fait tout (visé en priorité)** : risqué si la Pi est peu puissante (ex. Pi 3/4 avec peu de RAM) — dans ce cas, se limiter à un modèle très compact (~0,5-1,5 milliard de paramètres) ou repasser en cas A. Une Pi 5 (8 Go) peut faire tourner un petit modèle, avec des réponses plus lentes que sur un PC correct. **Un test sur PC ne renseigne pas sur la vitesse réelle.** Test complet sur la Pi **au plus tard mercredi après-midi**, avec chronométrage d'une réponse. Si trop lent : modèle plus petit, ou PC pour le modèle et Pi en passerelle.
- Simulation sur PC : même code + réglage de configuration ; port série virtuel ; environnement Pi (Raspberry Pi OS 64 bits) et installation des dépendances tôt (certaines bibliothèques posent problème sur ARM) ; Docker `--platform linux/arm64` (lent, sert à vérifier l'installation, pas la vitesse) ; limiter les ressources Docker (`--cpus`, `--memory`) pour une idée grossière ; affichage : la Pi héberge l'application et un PC/tablette l'ouvre dans un navigateur via un réseau local (sans internet).

**À faire dès que les specs de la Pi sont connues** : renseigner ici son modèle exact (Pi 3/4/5), sa RAM, et mettre à jour `models/Modelfile` en conséquence dans le dépôt.

## 9. Ollama et modèle : décisions et guide

### État
- **Ollama installé** par l'utilisateur (lundi 21 sept.). Aucun modèle choisi à ce jour.
- **RAM/GPU du PC de secours connu (22/09) : 4 Go de RAM, GPU 2 Go de VRAM.** C'est en dessous du minimum confortable identifié plus bas (8 Go) : si ce PC sert un jour de secours pour la démo, ne viser qu'un modèle très compact (~0,5 à 1,5 milliard de paramètres quantifiés) et un `num_ctx` réduit (4096, à baisser à 2048 si besoin — voir `models/Modelfile`). **Le support principal visé reste la Raspberry Pi** (section 8), en attente de ses specs exactes.

### Choix du modèle [RECOMMANDÉ]
| RAM du PC | Taille réaliste (quantifié) | Ressenti |
|---|---|---|
| 8 Go | 1 à 3 milliards de paramètres | Rapide, qualité limitée |
| 16 Go | 7 à 9 milliards | Bon compromis, quelques secondes à dizaines de secondes sur CPU |
| GPU dédié ≥ 6 Go VRAM | 7 à 9 milliards | Confortable |

- **Candidats retenus le 22/09, compte tenu du PC de secours à 4 Go de RAM** (catalogue vérifié ce jour-là sur ollama.com/library, à revérifier si le catalogue a changé) :
  - `qwen2.5:0.5b` — le plus léger, filet de sécurité si tout le reste est trop lent.
  - `qwen2.5:1.5b` — candidat principal, meilleur compromis qualité/légèreté attendu (bon en français).
  - `llama3.2:1b` — second candidat multilingue, à comparer au précédent.
  Estimation RAM par modèle quantifié (ordre de grandeur, à vérifier avec `ollama ps`) : ~1 Go pour 0,5-1 milliard de paramètres, ~2 Go pour 1-1,5 milliard. Avec seulement 4 Go de RAM au total (OS + Streamlit + Ollama inclus), rester sur ces tailles est indispensable.
  Comparer aussi **2 ou 3 modèles** plus largement si le temps le permet (familles Qwen, Llama, Mistral, Gemma ; variante médicale type **MedGemma** si une taille convient). **Vérifier noms et tailles actuels sur ollama.com/library**, le catalogue change vite.
- Critères : qualité en français, respect du format JSON, vitesse sur la machine de démo.
- **Test de sélection** (1-2 h) : 5 cas cliniques fictifs dans chaque modèle ; noter français /5, prudence /5, pertinence médicale (relue avec une source fiable) /5, vitesse (tokens/s). Ne changer qu'un paramètre à la fois. Ce tableau alimente le rapport.
- **Piège : éviter les modèles `cloud`** (nom contenant `cloud`) : ils tournent sur internet et cassent la contrainte offline.
- Exemples de cas de test : (1) fièvre 38,9 °C + toux + SpO₂ 93 % ; (2) pouls 130 au repos + sueurs + anxiété ; (3) fièvre légère + mal de gorge, reste normal ; (4) douleur thoracique + essoufflement (doit déclencher l'alerte) ; (5) symptômes vagues (« je suis fatigué ») pour vérifier que le modèle demande des précisions.

### Spécialiser le modèle sans l'entraîner
Pas de fine-tuning (irréaliste et inutile ici). Trois leviers : (1) **prompt système** (rôle, prudence, langue, format) ; (2) **contexte injecté** (symptômes, mesures classifiées, alertes, fiche de connaissances) ; (3) **réglages** (température, contexte).

### Commandes Ollama à connaître
| Commande | Rôle |
|---|---|
| `ollama --version` | Vérifier l'installation |
| `ollama pull NOM` | Télécharger un modèle |
| `ollama run NOM --verbose` | Discuter ; affiche la vitesse (« eval rate ») |
| `ollama list` | Modèles téléchargés |
| `ollama ps` | Modèles chargés en mémoire |
| `ollama show NOM` | Informations (contexte, etc.) |
| `ollama stop NOM` / `ollama rm NOM` | Décharger / supprimer |
| `ollama create NOM -f Modelfile` | Créer un modèle configuré |
| `ollama serve` | Lancer le serveur si besoin |
Vérifier que le serveur tourne : `http://localhost:11434` affiche « Ollama is running ».

### Le contexte (`num_ctx`), réglage critique
Ollama choisit par défaut un contexte bien inférieur au maximum du modèle et **coupe silencieusement le début du texte** s'il est trop long (le modèle « oublie » alors consignes ou fiche, sans erreur). Ollama indique que les usages lourds (agents, outils de code) demandent au moins 64 000 tokens. Pour cette application (prompt + mesures + fiche) : **8 192** comme point de départ. Plus grand = plus de RAM et plus lent. Vérifier la valeur réelle avec `ollama ps` / `ollama show`.

### Modelfile de départ

Le vrai fichier, tenu à jour, est dans le dépôt : `models/Modelfile` (voir aussi
tests/model_results.md pour les résultats de vitesse par modèle candidat). Il contient le
prompt système en français (thème « vaisseau, 2080 »), `num_ctx 2048` (prudence RAM sur le
PC de test à 4 Go), et une limite de longueur de réponse. Construction :
`ollama create mallette -f models/Modelfile`, puis `ollama run mallette`. À chaque
modification du fichier, relancer `ollama create`.

### Code Python de départ [mis à jour 22/09 — identifiants en anglais, voir la convention de nommage en section 1]
Installation : `pip install ollama pydantic` (idéalement dans un environnement virtuel).
Le code réel et à jour est dans `llm.py` ; les extraits ci-dessous en résument la logique.

**Chat avec streaming et mémoire** (le modèle n'a pas de mémoire propre : on renvoie tout l'historique à chaque message) — voir `llm.Conversation` :
```python
import ollama

class Conversation:
    def __init__(self, model="mallette"):
        self.model = model
        self.history = []

    def send(self, text):
        self.history.append({"role": "user", "content": text})
        chunks = []
        for part in ollama.chat(model=self.model, messages=self.history, stream=True):
            chunk = part.message.content
            chunks.append(chunk)
            yield chunk
        self.history.append({"role": "assistant", "content": "".join(chunks)})
```

**Injection des mesures et de la fiche** (contenu du prompt en français) — voir `llm.build_prompt` :
```python
knowledge_sheet = open("data/knowledge_sheet.txt", encoding="utf-8").read()

def build_prompt(symptoms, readings, alerts):
    return f"""Symptômes déclarés : {symptoms}
Mesures (classées par le système) : {readings}
Alertes détectées par le système : {alerts}

Fiche de référence :
{knowledge_sheet}

Propose les causes possibles en t'appuyant uniquement sur ces informations."""
```

**Sortie JSON structurée avec relances** — voir `llm.analyze` :
```python
from pydantic import BaseModel, ValidationError

class Cause(BaseModel):
    cause: str
    justification: str

class Analysis(BaseModel):
    causes: list[Cause]
    warning: str

def analyze(prompt, attempts=3):
    for _ in range(attempts):
        response = ollama.chat(
            model="mallette",
            messages=[{"role": "user", "content": prompt}],
            format=Analysis.model_json_schema(),
        )
        try:
            return Analysis.model_validate_json(response.message.content)
        except ValidationError:
            continue
    return None   # plan B : le moteur de règles (rules.py) prend le relais
```

### Améliorer la pertinence, dans cet ordre
1. Reformuler le prompt système (précis, court, sans contradictions ; ajouter un exemple de bonne réponse si le format dérive).
2. Vérifier le contexte (augmenter `num_ctx` ou raccourcir la fiche).
3. Réduire la fiche aux passages utiles selon les symptômes.
4. Changer de modèle si le français ou la stabilité restent faibles.

### Dépannage
| Symptôme | Piste |
|---|---|
| Commande `ollama` inconnue | Fermer et rouvrir le terminal |
| Erreur de connexion `localhost:11434` | Lancer l'application ou `ollama serve` |
| Réponses très lentes | Modèle trop gros : `ollama ps`, prendre plus petit |
| Le modèle oublie consignes ou données | Augmenter `num_ctx`, raccourcir la fiche |
| Réponse en anglais | Renforcer la consigne de langue |
| JSON invalide | Paramètre `format=` + relances |
| Première réponse lente | Modèle déchargé après inactivité : faire une requête de chauffe avant la démo |

### Préparation de la démo offline
- Tout est téléchargé à l'avance (modèles, dépendances, documents).
- **Test complet PC en mode avion** avant le jour J.
- Requête de chauffe juste avant de passer devant le jury.
- Nom exact du modèle, version d'Ollama et Modelfile dans le README/Git.
- Ne pas exposer Ollama sur le réseau (des instances Ollama exposées sans authentification ont été repérées en nombre) : garder le réglage par défaut (écoute locale).
- Latence attendue : 10 à 60 s par réponse sur CPU → streaming + indicateur de chargement, réponses concises.

## 10. Paliers du MVP [RECOMMANDÉ]

Chaque palier est présentable ; on s'arrête au dernier atteint.

1. **Palier 1 (indispensable, fin de mardi)** : chat avec le modèle local, mesures simulées avec durée choisie, alertes critiques déterministes, interprétation avec causes et indice de concordance.
2. **Palier 2 (fin de mercredi)** : démo de bout en bout ; fiche de connaissances injectée, sources affichées.
3. **Palier 3 (jeudi midi)** : vrais capteurs branchés si disponibles, sinon simulateur.
4. **Palier 4 (bonus, peu probable)** : historique patient (table `patients`/`consultations`), graphiques d'évolution, export PDF.

Si le palier 1 n'est pas atteint mardi soir : réduire (moins de pathologies, un seul capteur, interface plus simple). Un petit projet qui marche vaut mieux qu'un grand qui plante en démo.

**Exclus** : fine-tuning, authentification, multi-utilisateurs, application mobile, vrai RAG vectoriel.

## 11. Agents d'aide au code : évaluation faite le 21 sept. 2026

Hypothèse : « agent » = assistant qui aide les développeurs à coder (pas le cerveau du chatbot médical, qui appelle directement Ollama).

| Agent | Verdict | Résumé |
|---|---|---|
| **ChatGPT** (ou tout assistant cloud) | **À utiliser pour coder** | Sans installation, bon en explications en français, mais **cloud uniquement** (donc utile pour le développement, pas pour l'application offline) ; ne coller que du code et des données fictives ; vérifier la charte de l'école sur l'usage de l'IA ; relire tout le code généré. |
| **OpenCode** | **À tester, 1 h max**, seulement si le PC a 16 Go de RAM ou un GPU | Agent de code open source en terminal, intégration officielle Ollama (`ollama launch opencode`), mais exige un contexte ≥ 64k (lourd) ; un rapport de blocage avec Ollama local a été signalé (peut être corrigé). |
| **Hermes Agent** (Nous Research) | Écarté | Open source, mémoire et compétences auto-créées, mais jeune et instable (versions rapides), orienté assistant/messageries, trop de concepts pour 3 jours. |
| **OpenClaw** | Écarté | Assistant personnel relié aux messageries ; exécute des commandes shell et accède aux fichiers ; risques de sécurité rapportés (identifiants en clair, compétences communautaires suspectes, injection de prompt) ; contexte ≥ 64k recommandé ; hors sujet et risqué pour des données de santé, même fictives. |

Protocole de test recommandé (1 h max) : donner la même tâche à chaque candidat (« fonction Python qui classe la SpO₂ en normale/basse/critique et lève une alerte sous 90 % ») et comparer qualité, vitesse et corrections nécessaires. Si OpenCode bloque : passer à ChatGPT. Pour OpenCode : créer d'abord un modèle avec `num_ctx` 65536 dans un Modelfile séparé (ne pas alourdir le modèle de démo).

Sources consultées : docs.ollama.com/integrations/opencode ; docs.ollama.com/integrations/openclaw ; docs.ollama.com/integrations/hermes ; docs.ollama.com/context-length ; documentation OpenClaw (docs.openclaw.ai/gateway/local-models) ; dépôt NousResearch/hermes-agent. Ces outils évoluent vite : revérifier avant utilisation.

## 12. Éléments à intégrer au rapport [RECOMMANDÉ]

- **Comparaison de modèles locaux** (tableau de l'étape de sélection).
- **Architecture hybride règles + LLM** et justification (fiabilité, plan B).
- **Fiabilité et éthique** : limites du score (indice de concordance et non probabilité), données de santé (RGPD, HDS en production), absence d'entraînement, risques d'hallucination et mesures prises (réponses uniquement à partir du contexte fourni, sources affichées).
- **Limites connues assumées** : sensibilité du capteur de SpO₂ aux mouvements et à la lumière, modèle local moins précis qu'un grand modèle cloud, fiche de connaissances limitée, pas de RAG vectoriel, pas d'authentification.
- **Pistes d'amélioration** : vrai RAG (ChromaDB + embeddings locaux), historique patient, Raspberry Pi/embarqué, plus de capteurs, validation médicale.
- Citer les sources de la fiche de connaissances (HAS, Ameli, MSD, etc.) et leurs conditions de réutilisation.

## 13. Journal de bord et décisions (à tenir à jour)

### Fait
- [x] Cadrage du projet, architecture, planning (conversation du 21/09/2026).
- [x] Ollama installé par l'utilisateur.
- [x] Squelette du projet et structure Git proposés (22/09, voir section 14bis).
- [x] RAM/GPU du PC de secours relevées : 4 Go RAM, GPU 2 Go VRAM (22/09).

### À faire immédiatement (mardi 22/09)
- [ ] **Contrat série : suivre les tests de l'équipe infra** (en cours, accès école limité) — valider dès que possible.
- [ ] Obtenir les specs de la Raspberry Pi (support principal visé) pour trancher son rôle définitif (section 8).
- [ ] Télécharger 2-3 modèles candidats compacts, écrire/tester les 5 cas cliniques (`tests/clinical_cases.md`), en gardant à l'esprit la contrainte forte du PC de secours (4 Go RAM).
- [ ] Initialiser le dépôt Git à partir du squelette proposé, pousser sur le dépôt distant.
- [ ] Confirmer le choix Streamlit (vs NiceGUI) — le squelette part sur Streamlit par défaut.
- [ ] Vérifier avec l'école : ce qui est exactement attendu dans le rapport, et la charte sur l'usage de l'IA.

### Questions ouvertes
1. Specs exactes de la Raspberry Pi (modèle, RAM) ? — conditionne son rôle définitif (section 8).
2. Carte, capteurs et langage du firmware de l'équipe matériel ? Contrat série définitivement validé ?
3. Streamlit confirmé ?
4. Structure et format exacts attendus du rapport ?
5. Règles de l'école sur l'usage de l'IA pour le développement ?
6. Pondérations de l'indice de concordance ? Liste des ~20 pathologies ? Seuils cliniques à sourcer ?

### Décisions prises
| Date | Décision | Statut |
|---|---|---|
| 21/09 | LLM local via Ollama, hors ligne | DÉCIDÉ |
| 21/09 | Deux développeurs sur le code ; matériel et firmware par l'équipe matériel (en Arduino/C++) | DÉCIDÉ |
| 21/09 | Rendu jeudi 24/09 au soir (code + rapport), présentation vendredi 25/09 | DÉCIDÉ |
| 21/09 | Historique patient et vrai RAG vectoriel abandonnés pour cette échéance (l'historique redevient possible seulement si de l'avance jeudi matin) | RECOMMANDÉ |
| 21/09 | Fiche de connaissances dans le prompt à la place du RAG | RECOMMANDÉ |
| 21/09 | Score = « indice de concordance » calculé par le code | RECOMMANDÉ |
| 21/09 | Stack Python/Streamlit/Ollama/Pydantic/SQLite/pyserial | RECOMMANDÉ |
| 22/09 | Raspberry Pi visée comme **support principal** (sous réserve de sa puissance) | RECOMMANDÉ (préférence équipe, à confirmer) |
| 22/09 | PC de secours identifié : 4 Go RAM / GPU 2 Go VRAM → modèle très compact obligatoire sur cette machine | DÉCIDÉ (fait constaté) |
| 22/09 | Squelette de projet et workflow Git proposés (voir section 14bis) | RECOMMANDÉ |
| 22/09 | Répartition du travail LLM : l'utilisateur prend le choix du modèle et `models/Modelfile` (peu de Python, surtout ligne de commande) ; la collègue prend `llm.py` (chat, streaming, JSON). Point de coordination : nom du modèle `mallette` créé tôt pour ne pas la bloquer | DÉCIDÉ |
| 22/09 | Candidats modèle retenus pour le test : qwen2.5:1.5b (principal), llama3.2:1b, qwen2.5:0.5b (filet de sécurité) ; num_ctx provisoire à 2048 (prudence RAM) | RECOMMANDÉ |
| 22/09 | Habillage narratif « Horizon 2080 » : vaisseau en mission longue durée, assistant utilisable par tout membre d'équipage formé, messages d'urgence fictifs + rappel réel 15/112 centralisé dans `config.EMERGENCY_MESSAGE` | DÉCIDÉ |
| 22/09 | Identifiants du code (variables/fonctions/classes) en anglais, commentaires et chatbot en français ; exception assumée pour les clés du contrat capteurs/série (restent en français) | DÉCIDÉ |
| 22/09 | Dossier `src/` créé pour regrouper les 6 modules applicatifs (`app.py`, `config.py`, `sensors.py`, `rules.py`, `llm.py`, `storage.py`), séparés des données/tests/scripts/docs | DÉCIDÉ |
| 22/09 | `rules.CAUSE_TABLE` + `rules.detect_signs()` / `rules.find_candidate_causes()` implémentés (8 causes de départ, déterministe, testé sur les 5 cas cliniques) — filet de sécurité si le LLM échoue, base future du `sheet_score` | DÉCIDÉ |
| 22/09 | Modèle final retenu : **qwen2.5:1.5b** (voir tests/model_results.md, section "Décision finale") ; `models/Modelfile` déjà sur ce `FROM` | DÉCIDÉ |
| 22/09 | La collègue garde son propre code de chat (`app.py`/`llm.py` réécrits par elle) plutôt que le squelette fourni ; transmis à l'utilisateur plus tard une fois avancé. Voir `docs/CHECKLIST_INTEGRATION.md` pour ce qui devra être rebranché (alertes, causes candidates, storage, fiche de connaissances, bannière) | DÉCIDÉ |
| 22/09 | `sensors.SerialSensor` implémenté (lecture ligne à ligne, filtrage par capteur, ignore les lignes invalides/corrompues, `TimeoutError` après 20 tentatives) ; testé sur `_parse_line` (5 tests, sans matériel ni pyserial). Reste à valider en conditions réelles avec `scripts/serial_simulator.py` + port série virtuel (socat/com0com), puis avec le vrai firmware | DÉCIDÉ (code) / À VALIDER (conditions réelles) |
| 22/09 | `docs/CONTRAT_SERIE_ARDUINO.md` créé : document autonome à transmettre à l'équipe infra (format JSON exact attendu, exemple de sketch Arduino avec ArduinoJson, méthode de test au moniteur série) — rien côté Python ne lit les capteurs à la place du firmware | DÉCIDÉ |
| 22/09 | `scripts/test_serial_loop.py` ajouté : teste `SerialSensor` sans installer socat/com0com (mode `loop://` de pyserial), utile sur le PC Windows de l'utilisateur où `socat` n'existe pas nativement. Logique de lecture/parsing validée | DÉCIDÉ |

### Journal quotidien (à remplir chaque soir)
```
Date : 22/09/2026
Ce qui marche : qwen2.5:1.5b tourne sur le PC de test (4 Go RAM / 2 Go VRAM) sans planter, num_ctx 2048. Résultat : 456 tokens de prompt en 16,25 s (28,06 tok/s), 131 tokens de réponse en 18,02 s (7,27 tok/s), total 34,6 s. Voir tests/model_results.md pour le détail et les prochains tests.
Ce qui est cassé / bloquant : contrat série pas encore validé (tests infra en cours, accès école limité) ; specs Raspberry Pi inconnues ; ~16 s de silence avant le premier mot côté interface (à masquer avec un indicateur de chargement dans app.py)
Décisions prises : Pi visée comme support principal (le test du jour sur PC est seulement un test pratique, pas un changement de support) ; PC de secours = 4 Go RAM / 2 Go VRAM (très limité) ; répartition LLM actée (utilisateur = Modelfile/choix du modèle, collègue = llm.py)
Prochaine étape : tester llama3.2:1b et qwen2.5:0.5b sur le même cas clinique pour comparer équitablement (tests/model_results.md) ; ajouter un indicateur "réflexion en cours" dans app.py ; ajouter une limite de longueur de réponse dans le Modelfile pour accélérer la génération ; avancer avec SimulatedSensor + port série virtuel en attendant la validation du contrat

Date : 22/09/2026 (soir)
Ce qui marche : `rules.py` complet (alertes, classification, CAUSE_TABLE + causes candidates, indice de concordance) et testé. `sensors.py` complet (SimulatedSensor + SerialSensor), logique de lecture série validée. Fiche de connaissances (8 pathologies) terminée côté utilisateur. Modèle final choisi et Modelfile prêt. La collègue a un chat Streamlit/Ollama fonctionnel (son propre code, pas le squelette).
Ce qui est cassé / bloquant : le code de la collègue (app.py/llm.py) n'est pas encore intégré avec rules.py/storage.py/config.py — c'est le plus gros risque restant (voir docs/CHECKLIST_INTEGRATION.md). Contrat série toujours pas validé avec l'infra (voir docs/CONTRAT_SERIE_ARDUINO.md, à leur transmettre). Specs Raspberry Pi toujours inconnues. Rapport et présentation pas commencés.
Décisions prises : modèle qwen2.5:1.5b entériné sans avoir testé les 2 autres candidats (choix pragmatique vu le temps) ; la collègue garde son code de chat, transmission différée.
Prochaine étape : voir la liste "Ce qui reste à faire" ci-dessous, envoyée à l'utilisateur le 22/09 en fin d'après-midi.

Date : 23/09/2026 (nuit, ~2h)
Ce qui marche : `chatbot.py` de la collègue reçu et intégré dans `src/app.py` (remplace l'ancien squelette). Branché sur `config.WARNING_BANNER`, `rules.detect_alerts`, `rules.find_candidate_causes` (avec secours si Ollama plante), `sensors.get_sensor`, `storage.save_reading`, et la fiche de connaissances injectée dans le prompt. Sa structure/style (multi-pages, cartes) conservés intégralement.
Ce qui est cassé / bloquant : l'indice de concordance n'est PAS branché (son code utilise du texte libre via httpx, pas de sortie JSON structurée pour en tirer une confiance LLM — voir docs/CHECKLIST_INTEGRATION.md). `httpx` manquait dans requirements.txt (ajouté). `llm.py` (ancien) n'est plus utilisé du tout par l'appli, gardé en référence seulement.
Décisions prises : le modèle reste nommé `"medical_box"` dans le code (pas `"mallette"`) — décision explicite de l'utilisateur le 23/09 ; à vérifier que ce modèle existe bien sur la machine de démo, et à clarifier avec la collègue s'il a le thème Horizon 2080/les réglages validés par l'équipe.
Prochaine étape : installer httpx, lancer `streamlit run src/app.py`, rejouer les 5 cas cliniques dans l'interface réelle, trancher la question du nom du modèle avec la collègue.

Date :
Ce qui marche :
Ce qui est cassé / bloquant :
Décisions prises :
Prochaine étape :
```

### Ce qui reste à faire côté dev [22/09, mardi soir]

**Mercredi (jour critique) :**
1. Récupérer le code de la collègue et dérouler `docs/CHECKLIST_INTEGRATION.md` point par point (bannière, alertes, causes candidates, indice de concordance, storage, fiche de connaissances, nom du modèle).
2. Transmettre `docs/CONTRAT_SERIE_ARDUINO.md` à l'équipe infra si pas encore fait ; relancer sur les specs Raspberry Pi.
3. Test de bout en bout une fois l'intégration faite : symptôme tapé + mesure simulée → alerte/causes/indice affichés correctement, sur les 5 cas de `tests/clinical_cases.md`.
4. Démarrer le rapport (rien commencé à ce stade) : au minimum l'architecture, les choix techniques et leurs raisons, les contraintes (offline, budget, délai).

**Jeudi (avant rendu du soir) :**
5. Finaliser et tester sur Raspberry Pi si les specs le permettent, sinon confirmer le PC de secours pour la démo.
6. Relire le rapport, vérifier que le zip/dépôt Git rendu correspond bien à ce qui tourne réellement.
7. Si le temps le permet seulement : étoffer `CAUSE_TABLE` au-delà de 8 causes, historique patient (bonus).

**Avant vendredi :**
8. Préparer la présentation (pas commencée).

**Point de vigilance à vérifier dès que possible** : confirmer qu'un dépôt Git est bien initialisé quelque part (avec les deux branches `dev-utilisateur`/`dev-collegue`) — le workflow Git décrit dans le README suppose que c'est fait, mais ça n'a pas été confirmé dans cette conversation.

## 14. Squelette du projet et workflow Git [mis en place le 22/09, RECOMMANDÉ]

Un squelette de dépôt a été généré et livré à l'utilisateur (fichier zip), à décompresser
et initialiser en Git. Arborescence :

```
mallette-medicale/
├── src/                             # Code applicatif (voir "Dossier src/" ci-dessus)
│   ├── app.py                         # Squelette Streamlit (chat + capteurs), branché sur les autres modules
│   ├── config.py                      # Réglages centralisés (SENSOR_SOURCE, seuils, nom du modèle...)
│   ├── sensors.py                     # SimulatedSensor (fonctionnel) + SerialSensor (stub, en attente du contrat)
│   ├── rules.py                       # classify_reading(), detect_alerts(), compute_concordance_index()
│   ├── llm.py                         # Conversation (chat streaming), build_prompt(), analyze() (JSON)
│   └── storage.py                     # SQLite : table readings (colonnes contrat en français) + historique
├── data/knowledge_sheet.txt     # Squelette à remplir avec les sources médicales
├── models/Modelfile                 # num_ctx=2048 (adapté au PC 4 Go de test), voir tests/model_results.md
├── scripts/serial_simulator.py        # Simule le firmware sur un port série virtuel (socat/com0com), hors src/
├── tests/conftest.py, clinical_cases.md, test_rules.py, test_sensors.py
├── docs/CONTEXTE_PROJET_mallette_medicale.md  # Ce fichier, versionné avec le code
├── docs/CHECKLIST_INTEGRATION.md              # À cocher quand le code de la collègue est intégré
├── docs/CONTRAT_SERIE_ARDUINO.md              # À transmettre à l'équipe infra (format JSON attendu)
├── scripts/test_serial_loop.py                # Test SerialSensor sans socat/com0com (Windows)
├── .env.example, .gitignore, requirements.txt, README.md
```

Workflow Git retenu : `main` toujours démontrable, une branche par développeur
(`dev-utilisateur`, `dev-collegue`), fusions fréquentes (au moins 2×/jour) pour éviter les
conflits en fin de sprint. `.gitignore` exclut l'environnement virtuel, le `.env`, et la
base SQLite générée.

**À faire pour finaliser la mise en place** : décompresser l'archive, `git init`, premier
commit, créer le dépôt distant (GitHub/GitLab de l'école), pousser, créer les deux branches
de développement.

## 15. Conversations suivantes : aspects du projet à traiter

Chaque sujet peut faire l'objet d'une conversation dédiée, en s'appuyant sur ce fichier :
1. **Squelette du projet et Git** (arborescence, environnement virtuel, README, branches).
2. **Simulateur et lecteur série de capteurs**, tests avec port série virtuel.
3. **Moteur de règles** : classification des mesures, alertes critiques, table symptômes ↔ causes, calcul de l'indice de concordance (pas à pas, l'utilisateur étant débutant).
4. **Interface Streamlit** : chat à gauche, cartes capteurs avec durée et graphes à droite.
5. **Pipeline LLM** : prompt, sortie JSON, relances, fiche de connaissances.
6. **Sélection du modèle et rédaction des cas cliniques**.
7. **Raspberry Pi** : installation, test de vitesse, simulation sur PC.
8. **Rapport** puis **présentation et démo**.

Amorce suggérée pour un nouveau chat : « Lis CONTEXTE_PROJET_mallette_medicale.md. Aujourd'hui je veux travailler sur : [sujet]. Voici l'état actuel : [copier le journal de bord]. »
