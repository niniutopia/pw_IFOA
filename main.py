import streamlit as st
import requests

# Configurazione della pagina
st.set_page_config(
    page_title="Steam Buddies",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stile CSS personalizzato
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1b1c1d;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Titolo principale
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown('<div class="main-header">🎮 Steam Buddies</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Una panoramica del tuo account di steam, confrontala con quella dei tuoi amici!</div>', unsafe_allow_html=True)

st.markdown("""
    **Benvenuto!** 👋
    
    Questa app ti aiuta a:
    - 📊 Analizzare le tue statistiche di gioco
    - 🎯 Scoprire a cosa giochi di più
    - 👥 Confrontare i tuoi gusti con i tuoi amici
    - 🎁 Trovare giochi che i tuoi amici dovrebbero provare
    
    Naviga usando le pagine nel menu a sinistra.
    """)


# Sidebar con info
with st.sidebar:
    st.title("Steam Buddies")
    st.markdown("---")
    st.caption("Alimentato da Steam Web API")