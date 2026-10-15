import streamlit as st

def show_guide():
    """
    Affiche le guide d'utilisation de la Medical Box.
    """
    st.title("📚 Guide d'utilisation")

    st.write(
        "Cette section explique comment utiliser la Medical Box."
    )

    st.divider()

    st.subheader("1️⃣ Préparer la Medical Box")

    st.write(
        """
            Allumez la Medical Box et vérifiez que les capteurs
            sont correctement connectés.
            """
    )

    st.subheader("2️⃣ Effectuer une mesure")

    st.write(
        """
            Positionnez les capteurs conformément aux indications
            fournies avec la Medical Box.
            """
    )

    st.subheader("3️⃣ Consulter les résultats")

    st.write(
        """
            Les données transmises par les capteurs apparaissent
            automatiquement dans le dashboard.
            """
    )

    st.subheader("4️⃣ Utiliser l'assistant IA")

    st.write(
        """
            L'assistant dispose automatiquement des dernières
            données reçues par les capteurs.

            Vous pouvez par exemple lui demander :

            - « Que montrent mes mesures ? »
            - « Peux-tu m'expliquer ma saturation ? »
            - « Que signifie cette mesure ? »
            """
    )

    st.divider()

    st.warning(
        "⚠️ L'assistant IA fournit des informations à partir "
        "des données disponibles. Il ne remplace pas un "
        "professionnel de santé."
    )