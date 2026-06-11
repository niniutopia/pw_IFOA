import streamlit as st
import requests

# Configurazione della pagina
st.set_page_config(
    page_title="Steam Buddy",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Titolo principale
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown('<div class="main-header">🎮 Steam Buddy</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Una panoramica del tuo account di steam, confrontala con quella dei tuoi amici!</div>', unsafe_allow_html=True)

st.markdown("""
    **Benvenuto!** 👋
    
    Steam Buddy è un'app per analizare le tue statistiche di gioco Steam in modo visivo e confrontarti con i tuoi amici.
    Cosa puoi vedere:
    - Quanti giochi ancora non toccati hai nel tuo account?
    - A cosa giochi di più?
    - Che giochi avete in comune tu ed i tuoi amici?
    - Cosa potresti consigliargli?
    
    Naviga usando le pagine nel menu a sinistra.
    """)

# Sidebar con info
with st.sidebar:
    # 1. Il tuo titolo svetta in cima
    st.markdown("### 🎮 Steam Buddy")
    st.caption("Alimentato da Steam Web API")
    st.divider() # Una bella linea di separazione
    
    # 2. I tuoi link di navigazione (nello stesso ordine in cui li vuoi tu)
    st.write("Navigazione:")
    
    # Sostituisci 'main.py' con il nome reale del tuo file principale se è diverso
    st.page_link("main.py", label="Home", icon="🏠")
    
    # Sostituisci il percorso e il nome con quelli reali della tua pagina 2
    st.page_link("pages/1_dashboard.py", label="Dashboard Personale", icon="📊")
    
    # Aggiungi qui eventuali altre pagine...
    st.page_link("pages/2_confronta_giocatori.py", label="Confronta Giocatori", icon="👥")