import streamlit as st
import re
from utils import (
    get_owned_games, 
    get_player_achievements, 
    get_game_schema, 
    parse_steam_input,
    get_game_details,
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
    

# 1. DEFINISCI LA CHIAVE SUBITO

st.set_page_config(page_title="Platinum Hunter", page_icon="🏆")
st.title("🏆 Platinum Hunter")
st.write("Sei un completazionista e vuoi vedere quanti achievements (e quali) ti mancano per platinare un gioco? Carica la tua libreria e scoprilo!")


API_KEY = st.secrets["STEAM_API_KEY"]

# Inizializziamo lo stato
if "my_games" not in st.session_state: st.session_state.my_games = []
if "active_sid" not in st.session_state: st.session_state.active_sid = None

# --- 1. CARICAMENTO PROFILO ---
st.subheader("1. Carica il tuo Profilo")

with st.form("form_profilo"):
    steam_id_input = st.text_input(
        "🔍 Inserisci Steam ID, Vanity URL o Link del profilo:", 
        placeholder="Es. 76561198... oppure https://steamcommunity.com/id/tuonome"
    )
    
    # Il bottone ora si trova sotto l'input, esteso per tutta la larghezza
    submit_profilo = st.form_submit_button("Carica Libreria", use_container_width=True)
    
    if submit_profilo:
        if steam_id_input:
            # --- PULIZIA E REGEX ---
            clean_input = steam_id_input.strip().strip("/")
            
            match_profiles = re.search(r'steamcommunity\.com/profiles/(\d+)', clean_input)
            if match_profiles:
                clean_input = match_profiles.group(1)
            else:
                match_id = re.search(r'steamcommunity\.com/id/([^/]+)', clean_input)
                if match_id:
                    clean_input = match_id.group(1)
            
            # --- CHIAMATA API ---
            with st.spinner("🔄 Risoluzione profilo e recupero dati..."):
                sid = parse_steam_input(API_KEY, clean_input)
                
                if sid:
                    st.session_state.active_sid = sid
                    data = get_owned_games(API_KEY, sid)
                    st.session_state.my_games = data.get("games", [])
                    st.rerun() 
                else:
                    st.error("❌ ID o Link non valido. Controlla e riprova.")
        else:
            st.warning("⚠️ Per favore, inserisci un ID o un link.")

# INFO STEAMID
with st.expander("📍 Cosa sono lo Steam ID o Vanity URL"):
    st.markdown("""
    L'app accetta i sequenti formati:

    ### L'url del tuo profilo
    - **Esempio**: `https://steamcommunity.com/profiles/76561197960434622`
                
    ### Steam ID Numerico (32-bit)
    - **Esempio**: `76561197960434622` (17 cifre)
    - **Più affidabile**, funziona sempre se il profilo è pubblico

    ### Vanity URL (Custom URL)
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
    
    ## 🐛 Troubleshooting

    ##### "Profilo privato o Steam ID non valido"
    - Verifica che il tuo Steam ID sia corretto
    - Assicurati che il tuo profilo sia impostato su **Public**
    - Attendi qualche minuto se hai appena reso pubblico il profilo

                            
    """)

# --- 2. SEZIONI DI RICERCA ---
st.subheader("2. Scegli il gioco")

tab1, tab2 = st.tabs(["🎮 Dalla mia Libreria", "🔗 Manuale (Family Share)"])

# Percorso A: Giochi con achievements
with tab1:
    st.write("Giochi avviati con sistema di achievement attivo:")
    if st.session_state.my_games:
        giochi_validi = [g for g in st.session_state.my_games if g.get("playtime_forever", 0) > 0]
        options = {f"{g.get('name', 'Gioco')} (ID: {g['appid']})": g['appid'] for g in giochi_validi}
        
        # Creiamo un form per la tendina
        with st.form("form_libreria"):
            sel_a = st.selectbox("Seleziona dalla libreria:", ["---"] + list(options.keys()), key="sel_auto")
            submit_auto = st.form_submit_button("Analizza Gioco Selezionato", use_container_width=True)
            
            if submit_auto:
                if sel_a != "---":
                    st.session_state.target_app_id = options[sel_a]
                    st.session_state.target_name = sel_a
                    st.rerun()
                else:
                    st.warning("Seleziona prima un gioco dalla tendina.")
    else:
        st.info("Carica il profilo per vedere i tuoi giochi.")

import re

# ... (resto del codice fino al Tab 1) ...

# Percorso B: Inserimento AppID o URL
with tab2:
    st.write("Hai giocato un titolo in Family Sharing? Incolla qui l'**AppID** o l'intero **link della pagina del negozio Steam**:")
    
    with st.form("form_manuale_url"):
        manual_input = st.text_input(
            "Inserisci AppID o URL Steam:", 
            placeholder="es. 105600 oppure https://store.steampowered.com/app/105600/Terraria/"
        )
        submit_manual = st.form_submit_button("Analizza Gioco", use_container_width=True)
        
        if submit_manual:
            if manual_input.strip():
                extracted_id = None
                clean_input = manual_input.strip()
                
                # Caso 1: L'utente ha inserito solo il numero (es. 105600)
                if clean_input.isdigit():
                    extracted_id = clean_input
                
                # Caso 2: L'utente ha incollato l'URL (estraiamo i numeri dopo "/app/")
                else:
                    match = re.search(r'/app/(\d+)', clean_input)
                    if match:
                        extracted_id = match.group(1)
                
                # Se abbiamo trovato un ID valido, procediamo
                if extracted_id:
                    st.session_state.target_app_id = int(extracted_id)
                    st.session_state.target_name = f"Gioco Manuale (ID: {extracted_id})"
                    st.rerun()
                else:
                    st.error("❌ Formato non riconosciuto. Inserisci un AppID numerico o un link valido dello store di Steam.")
            else:
                st.warning("⚠️ Per favore, inserisci un ID o un link.")

st.divider()



# --- 3. ANALISI (Comune) ---
if "target_app_id" in st.session_state and st.session_state.active_sid:
    app_id = st.session_state.target_app_id
    
    # Risolviamo nome e icona
    details = get_game_details(API_KEY, app_id)
    game_name = details.get("name", st.session_state.target_name) if details else st.session_state.target_name
    game_icon = details.get("header_image", "") if details else ""
    
    # Header del gioco
    c1, c2 = st.columns([1, 3])
    if game_icon: c1.image(game_icon, use_container_width=True)
    c2.subheader(f"{game_name}")
    
    with st.spinner("Recupero trofei..."):
        ach_data = get_player_achievements(API_KEY, st.session_state.active_sid, app_id)
        schema = get_game_schema(API_KEY, app_id)
        
        if ach_data and "achievements" in ach_data:
            all_ach = ach_data["achievements"]
            unlocked = [a for a in all_ach if a.get("achieved") == 1]
            locked = [a for a in all_ach if a.get("achieved") == 0]
            
            if len(all_ach) > 0:
                percent = (len(unlocked) / len(all_ach)) * 100
                st.progress(float(percent / 100))
                st.metric("Completamento", f"{len(unlocked)} / {len(all_ach)}")
                
                if percent >= 100:
                    st.success("🎉 Platinato!")
                else:
                    st.write(f"**Trofei mancanti:** {len(locked)}")
                    # ... (dentro la sezione analisi, dopo aver definito 'locked')
                    
                    with st.expander(f"Vedi i {len(locked)} trofei mancanti"):
                        # Dividiamo i trofei in due liste
                        con_descrizione = []
                        senza_descrizione = []
                        
                        for ach in locked:
                            a_info = schema.get(ach["apiname"], {})
                            desc = a_info.get("descrizione", "")
                            
                            if desc and desc != "Nessuna descrizione disponibile.":
                                con_descrizione.append((ach, a_info))
                            else:
                                senza_descrizione.append((ach, a_info))
                        
                        # STAMPA 1: Trofei con descrizione
                        if con_descrizione:
                            st.subheader("📋 Obiettivi chiari")
                            for ach, a_info in con_descrizione:
                                titolo = a_info.get("titolo", ach["apiname"])
                                desc = a_info.get("descrizione", "")
                                st.markdown(f"- **{titolo}** : *{desc}*")
                        
                        # STAMPA 2: Trofei senza descrizione (tutti insieme)
                        if senza_descrizione:
                            st.subheader("❓ Obiettivi segreti / Senza descrizione")
                            for ach, a_info in senza_descrizione:
                                titolo = a_info.get("titolo", ach["apiname"])
                                st.markdown(f"🔒 **{titolo}**")
            else:
                st.warning("Questo gioco non ha trofei.")
        else:
            st.error("Dati non disponibili o gioco senza achievements.")