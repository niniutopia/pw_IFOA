 # ==========================================
 # Import
 # ==========================================

import streamlit as st
import requests

 # ==========================================
 # Configurazione della pagina
 # ==========================================

st.set_page_config(
    page_title="Steam Buddy",
    page_icon="🎮",
)

 # ==========================================
 # Menù
 # ==========================================
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

# Sidebar con menù
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
    

 # ==========================================
 # Body
 # ==========================================
# Titolo principale
st.title("🎮 Steam Buddy")
st.markdown('<div class="subtitle">Una panoramica del tuo account di steam, confrontala con quella dei tuoi amici!</div>', unsafe_allow_html=True)

# Testo
st.markdown("""
### **Benvenuto!** 👋            
Una dashboard Streamlit per analizzare le tue statistiche di gioco Steam  in modo visivo, confrontarle con i tuoi amici e scoprire cosa manca per "platinare" un gioco.
           
### 🧩 **Funzionalità**

##### Dashboard Personale
- **Statistiche Generali**: Numero giochi posseduti, giocati, tempo totale
- **Grafico Ciambella**: Rapporto visivo tra giochi posseduti e giocati
- **Top 10 Giochi di Sempre**: Classifica dei giochi più giocati con grafico interattivo
- **Top Giochi Ultime 2 Settimane**: Attività di gioco recente

##### Confronta Giocatori
- **Giochi in Comune**: Vedi quali giochi condividete con gli amici
- **Grafico di Confronto**: Confronto visivo delle ore giocate per ogni gioco in comune
- **Analisi Achievement**: Confronto degli achievement sbloccati nei giochi comuni
- **Convincilo a Comprarlo**: Lista dei tuoi giochi migliori che il tuo amico non ha ancora
- **Giochi Esclusivi**: Vedi cosa ha il tuo amico che tu non hai

##### Platinum Hunter
- **Analisi achievements**: Vedi quanti achievements ti mancano per platinare un gioco
- **Obiettivi chieri**: Lista degli achievements in chiaro con i relativi testi
- **Obiettivi segreti**: Lista degli obiettivi senza descrizione

### 🔌 API Utilizzate

- **GetOwnedGames**: Recupera la lista di giochi posseduti e ore giocate
- **GetRecentlyPlayedGames**: Giochi giocati recentemente
- **GetPlayerAchievements**: Achievement sbloccati per un gioco

""")


    