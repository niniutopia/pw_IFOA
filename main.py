import streamlit as st
import requests

# Configurazione della pagina
st.set_page_config(
    page_title="Steam Buddy",
    page_icon="🎮",
)
# Stile CSS personalizzato
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Nasconde il menu di navigazione automatico */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar con info
with st.sidebar:
    # Titolo
    st.markdown("### 🎮 Steam Buddy")
    st.caption("Alimentato da Steam Web API")

    st.divider() # separazione
    
    # Menù di navigazione
    st.write("Navigazione:")

    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/1_dashboard.py", label="Dashboard Personale", icon="📊")
    st.page_link("pages/2_confronta_giocatori.py", label="Confronta Giocatori", icon="👥")
    st.page_link("pages/3_platinum_hunter.py", label="Platinum Hunter", icon="🏆")
    


# Titolo principale
st.title("🎮 Steam Buddy")
st.markdown('<div class="subtitle">Una panoramica del tuo account di steam, confrontala con quella dei tuoi amici!</div>', unsafe_allow_html=True)

# Testo/body
st.markdown("""
    **Benvenuto!** 👋
            
    Steam Buddy è un'app per analizare le tue statistiche di gioco Steam in modo visivo e confrontarti con i tuoi amici.
    Cosa puoi vedere:
    - Quanti giochi ancora non toccati hai nel tuo account?
    - A cosa giochi di più?
    - Che giochi avete in comune tu ed i tuoi amici?
    - Chi ha sbloccato più achievements?
    - Quali achievements ti mancano per platinare un gioco?
    
    Naviga usando le pagine nel menu a sinistra.
    """)


    