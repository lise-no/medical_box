# My Contributions — Lise No

This file describes my personal contributions to the Medical Box — Horizon 2080 project. It can be linked from the main README or used in a contributors section.

## Short summary

- Role: Frontend engineer & Conversational AI integrator
- Main contributions: development of the user interface and implementation/integration of the chatbot (local LLM with Ollama).

## Summary (one-liner)

I developed the user interface and integrated the conversational AI for Medical Box, building responsive and accessible components and connecting a local language model (Ollama) to the application for context-aware chat functionality.

## Detailed contributions

1. Interface (Frontend)
   - Designed and implemented a responsive UI using the project's frontend framework (components, layout, navigation).
   - Improved accessibility (keyboard navigation, semantic markup, ARIA where appropriate) to make the interface more usable and inclusive.
   - Added client-side validation and user-friendly error handling for forms and inputs.
   - Implemented automated UI tests and basic end-to-end checks to help ensure regressions are caught early.
   - Optimized rendering and resource loading to improve perceived performance and responsiveness.

2. Chatbot / Conversational AI
   - Integrated a local language model (Ollama) with the application, ensuring the chatbot runs 100% offline when required.
   - Designed the dialog architecture: intents, dialog flows, slot filling and fallback strategies to make interactions reliable and predictable.
   - Implemented the client-side chat UI and connected it to backend messaging/session APIs for real-time interaction.
   - Added logging and basic monitoring for chatbot interactions to collect usage data and evaluate model responses and safety.
   - Collaborated with backend/infrastructure contributors to ensure secure handling of session data and sensible defaults for privacy.

## Tech & tools (examples — replace with exact tech you used if you want)

- Frontend: Streamlit (app interface), React/TypeScript (if used), CSS/Tailwind or plain CSS
- AI: Ollama local model, custom model defined in `models/Modelfile`
- Testing: pytest, playwrigh t/selenium (for e2e) — adjust to actual tools used
- Others: Git, Docker (if used), environment configuration via `.env`

## Metrics / Impact (optional — add numbers if available)

- Reduced UI load time by X% (replace X with measured improvement)
- Increased chatbot success rate / reduced fallbacks by Y% after dialog architecture changes
- Implemented N automated UI tests and M end-to-end scenarios

## How to use / link from README

To reference this file from the main README, add a link in the Contributors or Documentation section:

- English: [My Contributions](horizon2080-main/my_contributions.md)
- French: see the French section below

---

## Mes contributions — Lise No (français)

Ce fichier décrit mes contributions personnelles au projet Medical Box — Horizon 2080.

### Résumé court

- Rôle : développeuse frontend & intégration IA conversationnelle
- Contributions principales : développement de l'interface utilisateur et implémentation/intégration du chatbot (modèle local avec Ollama).

### Détails des contributions

1. Interface (Frontend)
   - Conception et implémentation d'une interface responsive (composants, mise en page, navigation).
   - Améliorations d'accessibilité (navigation au clavier, balisage sémantique, ARIA) pour une meilleure utilisabilité.
   - Validation côté client et gestion conviviale des erreurs pour les formulaires et entrées utilisateur.
   - Mise en place de tests automatisés UI et de vérifications end-to-end pour prévenir les régressions.
   - Optimisation du rendu et du chargement des ressources pour améliorer la performance perçue.

2. Chatbot / IA conversationnelle
   - Intégration d'un modèle de langage local (Ollama) avec l'application pour permettre un fonctionnement hors ligne.
   - Définition de l'architecture des dialogues : intents, flux de conversation, remplissage de slots et stratégies de repli.
   - Implémentation de l'UI de chat côté client et connexion aux APIs backend pour la messagerie et la gestion des sessions.
   - Ajout de journalisation et de monitoring pour analyser les interactions et la sécurité des réponses.
   - Collaboration avec l'équipe backend/infrastructure pour assurer la confidentialité et la gestion sécurisée des données.

### Technologies & outils (exemples — remplacez par les outils exacts utilisés)

- Frontend : Streamlit, React/TypeScript, CSS/Tailwind
- IA : Ollama, modèle personnalisé dans `models/Modelfile`
- Tests : pytest, Playwright/Selenium

### Mesures / Impact (optionnel)

Ajoutez ici des chiffres concrets si vous en avez (ex. réduction du temps de chargement, amélioration du taux de succès du chatbot, nombre de tests automatisés).


---

If you'd like, I can:
- Update the main README to link to this file, or
- Customize the tech/tools and metrics with exact values you provide, or
- Create a short contributors badge or a one-line summary for the README instead.
