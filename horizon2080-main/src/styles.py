import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>

    /* Fond général */
    .stApp {
        background-color: #f5f7fa;
    }

    /* Contenu principal */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    /* Cartes */
    .vital-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        min-height: 150px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .vital-title {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 8px;
    }

    .vital-value {
        color: #111827;
        font-size: 30px;
        font-weight: 700;
    }

    .vital-status {
        margin-top: 8px;
        font-size: 13px;
    }

    .status-waiting {
        color: #6b7280;
    }

    .status-normal {
        color: #16a34a;
    }

    .status-warning {
        color: #d97706;
    }

    .status-danger {
        color: #dc2626;
    }

    /* Box information */
    .info-box {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e5e7eb;
    }

    /* Header */
    .main-header {
        background-color: white;
        border-radius: 15px;
        padding: 20px 25px;
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }

    </style>
    """, unsafe_allow_html=True)
