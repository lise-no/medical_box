import streamlit as st
from tools import display_vital_card

def show_dashboard(vitals):
    """
    Affiche le tableau de bord avec les mesures vitales.
    """
    st.title("🩺 Medical Box")

    st.subheader("📊 Constantes vitales")

    st.write(
        "Les valeurs affichées proviennent des données "
        "actuellement reçues par les capteurs."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        display_vital_card(
            "🌡️",
            "Température",
            vitals.get("temperature"),
            "°C"
        )

    with col2:
        display_vital_card(
            "❤️",
            "Fréquence cardiaque",
            vitals.get("heart_rate"),
            "bpm"
        )

    with col3:
        display_vital_card(
            "🫁",
            "Saturation SpO₂",
            vitals.get("spo2"),
            "%"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        display_vital_card(
            "🩸",
            "Pression systolique",
            vitals.get("systolic"),
            "mmHg"
        )

    with col2:
        display_vital_card(
            "🩸",
            "Pression diastolique",
            vitals.get("diastolic"),
            "mmHg"
        )

    with col3:
        display_vital_card(
            "🌬️",
            "Fréquence respiratoire",
            vitals.get("respiratory_rate"),
            "resp/min"
        )

    # --------------------------------------------------------
    # INFORMATIONS
    # --------------------------------------------------------



    st.markdown(
            """
            <div class="info-box">

            ### 🤖 Assistant IA

            L'assistant IA utilise automatiquement les dernières
            données reçues par la Medical Box pour répondre
            aux questions de l'utilisateur.

            Il n'est donc pas nécessaire de recopier les mesures
            dans le chatbot.

            </div>
            """,
            unsafe_allow_html=True
    )

    st.write("")