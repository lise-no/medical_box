
import streamlit as st

def show_measures(vitals):
    """
    Affiche la barre latérale avec les mesures vitales.
    """
    st.title("📊 Mesures")

    st.write(
        "Toutes les données actuellement reçues par la Medical Box."
    )

    st.divider()

    if not vitals:

        st.info(
            "📡 Aucune mesure reçue pour le moment. "
            "Les données apparaîtront automatiquement "
            "lorsque la Medical Box transmettra les mesures."
        )

    else:

        labels = {
            "temperature": "🌡️ Température",
            "heart_rate": "❤️ Fréquence cardiaque",
            "spo2": "🫁 SpO₂",
            "systolic": "🩸 Pression systolique",
            "diastolic": "🩸 Pression diastolique",
            "respiratory_rate": "🌬️ Fréquence respiratoire"
        }

        units = {
            "temperature": "°C",
            "heart_rate": "bpm",
            "spo2": "%",
            "systolic": "mmHg",
            "diastolic": "mmHg",
            "respiratory_rate": "resp/min"
        }

        for key, value in vitals.items():

            label = labels.get(
                key,
                key.replace("_", " ").capitalize()
            )

            unit = units.get(
                key,
                ""
            )

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{label}**")

            with col2:
                st.write(
                    f"**{value} {unit}**"
                )

            st.divider()
    