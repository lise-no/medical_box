"""
Point d'entrée de l'application. Lancer avec : streamlit run src/app.py
"""

from assistante import show_assistant
from dashboard import show_dashboard
from data_capteurs import get_vital_data, get_raw_readings
from guide import show_guide
from measures import show_measures
import streamlit as st
import httpx
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

from styles import apply_custom_styles
from tools import KNOWLEDGE_SHEET, build_vitals_context, display_vital_card

# --- AJOUT : rendre importables config/sensors/rules/storage (voisins dans src/) ---
sys.path.insert(0, str(Path(__file__).parent))
import config
import storage
from sensors import get_sensor
from rules import detect_alerts, find_candidate_causes, compute_concordance_index  # noqa: F401
# compute_concordance_index importé mais pas encore utilisé ici : voir la remarque en bas
# de fichier sur l'indice de concordance, pas encore affiché dans cette version.

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Medical Box",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

apply_custom_styles()

# --- AJOUT : bandeau d'avertissement obligatoire (config.WARNING_BANNER), sur toutes les pages ---
st.warning(config.WARNING_BANNER)


# --- AJOUT : session_id (pour retrouver les mesures de CETTE session dans storage.py) ---
storage.initialize()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ============================================================
# DONNÉES DES CAPTEURS
# ============================================================
vitals = get_vital_data()

# ============================================================
# HISTORIQUE DU CHAT
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🩺 Medical Box")

    st.caption(
        "Interface de surveillance et assistant IA"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            # "📊 Mesures",
            "🤖 Assistant IA",
            "📚 Guide"
        ]
    )

    st.divider()

    # --------------------------------------------------------
    # ÉTAT DE LA BOX
    # --------------------------------------------------------

    st.markdown("### 📡 État de la box")

    if vitals:
        st.success("🟢 Données reçues")
    else:
        st.warning("🟠 En attente des capteurs")

    st.caption(
        f"Dernière vérification : "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    # --------------------------------------------------------
    # RAFRAÎCHISSEMENT
    # --------------------------------------------------------

    if st.button(
        "🔄 Actualiser les mesures",
        use_container_width=True
    ):
        st.rerun()


# --- AJOUT : alertes critiques (rules.detect_alerts), affichées quelle que soit la page ---
_raw_readings = get_raw_readings(st.session_state.session_id)
_last_user_text = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
_alerts = detect_alerts(_raw_readings, symptoms_text=_last_user_text)
for _alert in _alerts:
    st.error(_alert)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    show_dashboard(vitals)


# ============================================================
# PAGE MESURES
# ============================================================

elif page == "📊 Mesures":
    show_measures(vitals)


# ============================================================
# ASSISTANT IA
# ============================================================

elif page == "🤖 Assistant IA":
    show_assistant(vitals)
    

# ============================================================
# GUIDE
# ============================================================

elif page == "📚 Guide":

    show_guide()
