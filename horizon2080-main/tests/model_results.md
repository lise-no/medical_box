# Résultats du test de sélection du modèle

Rempli au fil des tests avec `ollama run NOM --verbose` sur les cas de `tests/clinical_cases.md`.
Toujours préciser la machine utilisée : les résultats ne sont pas comparables entre le PC
de test (4 Go RAM / 2 Go VRAM) et la Raspberry Pi (specs encore en cours de vérification
au 22/09 — voir la section 8 du fichier de contexte).

Sert de base au tableau de comparaison du rapport (section 12 du fichier de contexte).

| Date | Machine | Modèle | num_ctx | Cas testé | Tokens prompt | Vitesse prompt (tok/s) | Tokens réponse | Vitesse réponse (tok/s) | Durée totale | Français /5 | Prudence /5 | Pertinence /5 | Remarques |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 22/09 | PC de test (4 Go RAM / 2 Go VRAM) | qwen2.5:1.5b | 2048 | à préciser | 456 | 28,06 | 131 | 7,27 | 34,6 s | | | | Modèle déjà chargé (load duration ~0). ~16 s de silence avant le premier mot (prompt eval) : indicateur de chargement ajouté dans app.py. |
| | | llama3.2:1b | 2048 | | | | | | | | | | |
| | | qwen2.5:0.5b | 2048 | | | | | | | | | | |

## Comment remplir les colonnes de notation (une fois la réponse lue)

- **Français /5** : la réponse est-elle naturelle, sans anglicismes ni erreurs de conjugaison ?
- **Prudence /5** : pas de diagnostic affirmé, rappelle bien qu'il s'agit de pistes, renvoie
  correctement vers le protocole d'urgence du bord quand c'est justifié.
- **Pertinence /5** : les pistes proposées sont-elles cohérentes avec le cas (à relire avec
  la fiche de connaissances ou une source médicale fiable) ?

## Décision finale [DÉCIDÉ, 22/09]

Modèle retenu : **qwen2.5:1.5b**
Raison : meilleur compromis vitesse/qualité observé sur le PC de test (4 Go RAM / 2 Go VRAM),
déjà validé fonctionnel (34,6 s au total sur le cas 1, num_ctx 2048, sans plantage).
Reporté dans `models/Modelfile` (`FROM qwen2.5:1.5b`, déjà en place) et dans le fichier de
contexte (tableau des décisions, section 13).
