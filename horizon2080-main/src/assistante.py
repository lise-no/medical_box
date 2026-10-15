
import json
import httpx

from data_capteurs import get_raw_readings
from rules import find_candidate_causes
import streamlit as st
from tools import KNOWLEDGE_SHEET, build_vitals_context  

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "medical_box"

def show_assistant(vitals):
    st.title("🤖 Assistant Medical Box")

    st.write(
        "Posez une question concernant les mesures recueillies "
        "par la Medical Box."
    )

# --------------------------------------------------------
# CONTEXTE ACTUEL
# --------------------------------------------------------

    with st.expander(
        "📋 Voir les données transmises à l'IA"
    ):

        if vitals:

            st.code(
                build_vitals_context(vitals),
                language="text"
            )

        else:

            st.info(
                "Aucune mesure disponible."
            )

    st.divider()

    # --------------------------------------------------------
    # HISTORIQUE
    # --------------------------------------------------------

    for msg in st.session_state.messages:

        with st.chat_message(
            msg["role"]
        ):

            st.markdown(
                msg["content"]
            )

    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    user_input = st.chat_input(
        "Pose ta question..."
    )

    if user_input:

        # Ajouter la question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):

            st.markdown(
                user_input
            )

        # ----------------------------------------------------
        # CONSTRUCTION DU CONTEXTE
        # ----------------------------------------------------

        vitals_context = build_vitals_context(
            vitals
        )

        # --- AJOUT : causes candidates déterministes (rules.py), affichées en plus du LLM ---
        current_readings = get_raw_readings(st.session_state.session_id)
        candidate_causes = find_candidate_causes(current_readings, symptoms_text=user_input)
        if candidate_causes:
            with st.expander("🧭 Pistes déterministes (moteur de règles, indépendant du LLM)"):
                for cause in candidate_causes[:3]:
                    st.write(
                        f"- **{cause['cause']}** — signes concordants : "
                        f"{', '.join(cause['matched_signs'])} (couverture {cause['coverage']:.0%})"
                    )

        prompt = f"""
Tu es l'assistant IA intégré à une Medical Box.

Ton rôle est d'aider l'utilisateur à comprendre les données
vitales actuellement disponibles.

IMPORTANT :
- Les mesures ci-dessous proviennent automatiquement des capteurs.
- Il s'agit de données venant du patient, valeurs mesurées = ses mesures réelles.
- L'utilisateur n'a pas besoin de les fournir.
- Utilise ces mesures pour répondre à sa question.
- N'invente jamais une mesure qui n'est pas présente.
- Si une donnée est absente, indique qu'elle n'est pas disponible.
- Explique les informations avec un langage simple.
- Ne présente pas ton analyse comme un diagnostic médical définitif.
- Si la situation décrite semble nécessiter une prise en charge
  urgente, recommande de contacter rapidement un professionnel
  de santé ou les services d'urgence appropriés.
- Lit attentivement la fiche de connaissances ci-dessous et utilise-la pour répondre à la question.

========================
FICHE DE CONNAISSANCES (référence)
========================

{KNOWLEDGE_SHEET}

========================
DONNÉES DES CAPTEURS
========================

{vitals_context}

========================
QUESTION DE L'UTILISATEUR
========================

{user_input}

========================
RÉPONSE
========================
"""

        # ----------------------------------------------------
        # RÉPONSE OLLAMA
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            placeholder = st.empty()

            full_response = ""

            try:

                with httpx.Client(
                    timeout=None
                ) as client:

                    response = client.post(
                        f"{OLLAMA_URL}/api/generate",

                        json={
                            "model": OLLAMA_MODEL,
                            "prompt": prompt,
                            "stream": True
                        }
                    )

                    response.raise_for_status()

                    # Lecture du streaming Ollama
                    for line in response.iter_lines():

                        if not line:
                            continue

                        if isinstance(
                            line,
                            bytes
                        ):
                            line = line.decode(
                                "utf-8"
                            )

                        try:

                            data = json.loads(
                                line
                            )

                            token = data.get(
                                "response",
                                ""
                            )

                            full_response += token

                            placeholder.markdown(
                                full_response
                            )

                            if data.get(
                                "done",
                                False
                            ):
                                break

                        except json.JSONDecodeError:

                            continue

            except httpx.ConnectError:

                full_response = (
                    "❌ Impossible de contacter Ollama.\n\n"
                    "Vérifie qu'Ollama est démarré et "
                    "écoute sur `localhost:11434`."
                )

                placeholder.markdown(
                    full_response
                )

            except httpx.HTTPStatusError as e:

                full_response = (
                    f"❌ Ollama a retourné une erreur HTTP : "
                    f"{e.response.status_code}\n\n"
                    f"{e.response.text}"
                )

                placeholder.markdown(
                    full_response
                )

            except Exception as e:

                full_response = (
                    f"❌ Erreur : {e}"
                )

                placeholder.markdown(
                    full_response
                )

            # --- AJOUT : si le LLM a échoué (Ollama injoignable/erreur), montrer quand
            # même les pistes déterministes plutôt que de laisser l'utilisateur sans rien ---
            if full_response.startswith("❌") and candidate_causes:
                fallback_text = "\n\n**Plan B (moteur de règles, sans le LLM) :**\n" + "\n".join(
                    f"- {c['cause']} (couverture {c['coverage']:.0%})" for c in candidate_causes[:3]
                )
                full_response += fallback_text
                placeholder.markdown(full_response)

        # Ajouter la réponse à l'historique
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response
            }
        )
