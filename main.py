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
    
    Steam Buddy è un'app per analizare le tue statistiche di gioco Steam in modo visivo e confrontarti con i tuoi amici.
    Cosa puoi vedere:
    - Quanti giochi ancora non toccati hai nel tuo account?
    - A cosa giochi di più?
    - Che giochi avete in comune tu ed i tuoi amici?
    - Cosa potresti consigliargli?
    
    Naviga usando le pagine nel menu a sinistra.
    """)

st.markdown("""
    ## 📍 Come Trovare lo Steam ID o Vanity URL

    L'app accetta due formati:

    ### Formato 1: Steam ID Numerico (32-bit)
    - **Esempio**: `76561198123456666` (17 cifre)
    - Puoi trovarlo sul tuo profilo, sono le cifre alla fine dell'url `https://steamcommunity.com/profiles/76561198123456666`
    - **Più affidabile**, funziona sempre se il profilo è pubblico

    ### Formato 2: Vanity URL (Custom URL)
    - **Esempio**: `https://steamcommunity.com/id/username` oppure solo `username`
    - Se hai impostato un custom URL su Steam, puoi usarlo direttamente
    - **Più comodo**, basta inserire il tuo nome utente Steam
    - Se non hai un Vanity URL personalizzato, usa lo Steam ID numerico

    #### Come impostare un Vanity URL:
    1. Vai a https://steamcommunity.com/my/edit/settings
    2. Clicca su "Custom URL"
    3. Scegli un nome univoco
    4. Ora puoi usare `https://steamcommunity.com/id/tuonome`

    ## 🔐 Privacy & Profili Pubblici

    **⚠️ Importante:** Affinché l'app funzioni correttamente, il tuo profilo Steam deve essere **pubblico**.

    Per rendere il profilo pubblico:
    1. Vai a https://steamcommunity.com/my/edit/settings
    2. Vai a "Privacy settings"
    3. Assicurati che "Game details", "Playtime statistics" e "Library visibility" siano impostati su **Public**
    """)

# Sidebar con info
with st.sidebar:
    st.title("Steam Buddies")
    st.markdown("---")
    st.caption("Alimentato da Steam Web API")