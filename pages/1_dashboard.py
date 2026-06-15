import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from utils import (
    get_owned_games, 
    get_top_games_by_playtime,
    get_top_games_by_recent_playtime,
    calculate_total_playtime,
    get_owned_vs_played_ratio,
    format_hours,
    validate_steam_id,
    parse_steam_input,
    get_unplayed_games,
)

st.set_page_config(page_title="Dashboard", page_icon="📊")

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

st.title("📊 Dashboard Personale")
st.write("Analizza le tue statistiche di gioco Steam")

# Sidebar con info
with st.sidebar:
    st.markdown("### 🎮 Steam Buddy")
    st.caption("Alimentato da Steam Web API")
    st.divider()
    
    st.write("Navigazione:")
    
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/1_dashboard.py", label="Dashboard Personale", icon="📊")
    st.page_link("pages/2_confronta_giocatori.py", label="Confronta Giocatori", icon="👥")
    st.page_link("pages/3_platinum_hunter.py", label="Platinum Hunter", icon="🏆")

# Richiamo la API key
API_KEY = st.secrets["STEAM_API_KEY"]

# ==========================================
# 🟢 INIZIALIZZAZIONE MEMORIA (DEVE STARE QUI!)
# ==========================================
if "my_games" not in st.session_state: 
    st.session_state.my_games = []
    
if "active_sid" not in st.session_state: 
    st.session_state.active_sid = None

# --- 1. CARICAMENTO PROFILO ---
with st.form("form_profilo"):
    steam_id = st.text_input(
        "🔍 Inserisci Steam ID, Vanity URL o Link del profilo:", 
        placeholder="Es. 76561198... oppure https://steamcommunity.com/id/tuonome"
    )
    
    # Il bottone ora si trova sotto l'input
    submit_profilo = st.form_submit_button("Cerca", use_container_width=True)
    
    if submit_profilo:
        if steam_id:
            # --- 1. PULIZIA E REGEX (Tutto dentro il form!) ---
            clean_input = steam_id.strip().strip("/")
            
            match_profiles = re.search(r'steamcommunity\.com/profiles/(\d+)', clean_input)
            if match_profiles:
                clean_input = match_profiles.group(1)
            else:
                match_id = re.search(r'steamcommunity\.com/id/([^/]+)', clean_input)
                if match_id:
                    clean_input = match_id.group(1)
            
            # --- 2. CHIAMATA API ---
            with st.spinner("🔄 Risoluzione profilo e recupero dati..."):
                sid = parse_steam_input(API_KEY, clean_input)
                
                if sid:
                    st.session_state.active_sid = sid
                    data = get_owned_games(API_KEY, sid)
                    st.session_state.my_games = data.get("games", [])
                    # Ricarica la pagina per mostrare i dati nella dashboard sottostante
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

# ==========================================
# 🟢 LETTURA DATI E STATISTICHE (Scatta solo se c'è un ID in memoria)
# ==========================================
if st.session_state.active_sid:
    # Recuperiamo la lista giochi dalla memoria
    games = st.session_state.my_games
    
    st.success(f"✅ Dati del profilo caricati! Trovati {len(games)} giochi.")
    st.divider()
    
    # --- CALCOLO MEDIA GIORNALIERA RECENTE ---
    # Sommiamo tutti i minuti giocati nelle ultime 2 settimane
    minuti_totali_2_settimane = sum(g.get("playtime_2weeks", 0) for g in games)

    # Convertiamo in ore e dividiamo per 14 giorni
    media_ore_giornaliere = (minuti_totali_2_settimane / 60) / 14

    # --- STAMPA DELLE METRICHE GLOBALI ---
    col1, col2 = st.columns(2)

    with col1:
        st.metric("🎮 Giochi Totali", len(games))
        
    with col2:
        st.metric("⏱️ Media di gioco attuale", f"{media_ore_giornaliere:.1f} ore / giorno", help="Calcolata sugli ultimi 14 giorni")
        
    st.divider()
    
    # [Da qui in poi puoi inserire il resto della tua dashboard: Top 10, Grafici, ecc.]    
    
    
    # ==========================================
    # 🛑 BLOCCO DI SICUREZZA
    # ==========================================
    # Se non c'è nessun ID in memoria, fermiamo la pagina qui e aspettiamo
    if not st.session_state.active_sid:
        st.info("👆 Inserisci un ID, un Vanity URL o un Link qui sopra per avviare l'analisi!")
        st.stop() # <-- Questo comando dice a Streamlit: "Non leggere il resto del file!"

        
    # SEZIONE 1: METRICHE PRINCIPALI

    
    st.subheader("📈 Statistiche Generali")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Metrica 1: Giochi posseduti
    with col1:
        st.metric(
            label="🎮 Giochi Posseduti",
            value=len(games)
        )
    
    # Metrica 2: Giochi giocati
    played_games, total_games = get_owned_vs_played_ratio(games)
    with col2:
        st.metric(
            label="🎯 Giochi Giocati",
            value=played_games
        )
    
    # Metrica 3: Tempo totale di gioco
    total_hours = calculate_total_playtime(games)
    with col3:
        st.metric(
            label="⏱️ Tempo Totale",
            value=f"{total_hours:.0f} ore"
        )
    
    # Metrica 4: Percentuale giocati
    with col4:
        percentage = (played_games / total_games * 100) if total_games > 0 else 0
        st.metric(
            label="📊 % Giocati",
            value=f"{percentage:.1f}%"
        )
    
    st.divider()
    
    # SEZIONE 2: GRAFICO CIAMBELLA
    st.subheader("🍩 Rapporto Giochi Posseduti vs Giocati")
    
    col_chart, col_info = st.columns([2, 1])
    
    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=["Giocati", "Non Giocati"],
            values=[played_games, total_games - played_games],
            hole=.3,
            marker=dict(colors=["#1f77b4", "#ff7f0e"]),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Quantità: %{value}<br>Percentuale: %{percent}<extra></extra>"
        )])
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(x=1.1, y=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_info:
        st.info(f"""
        **Analisi:**
        - 🎯 {played_games} giochi giocati
        - 📦 {total_games - played_games} giochi non toccati
        - 📊 {percentage:.1f}% del tuo catalogo usato
        """)
    
    with st.expander("📦 Pile of Shame:"):
        giochi_vergini = get_unplayed_games(games) 

        st.write(f"Hai **{len(giochi_vergini)}** giochi che non hai mai aperto. Ecco quali sono:")
        
        for gioco in giochi_vergini:
            # Nota: ricordati che get_owned_games deve avere "include_appinfo": True
            # altrimenti Steam non ti restituisce il "name" ma solo l'"appid"
            nome_gioco = gioco.get("name", f"App ID sconosciuto ({gioco.get('appid')})")
            st.write(f"- 👻 {nome_gioco}")
            

    st.divider()

    # SEZIONE 3: TOP 10 GIOCHI DI SEMPRE
    st.subheader("🏆 Top 10 Giochi di Sempre")
    
    top_games_all_time = get_top_games_by_playtime(games, limit=10)
    
    if top_games_all_time:
        # Aggiungiamo l'appid al DataFrame per poter recuperare le immagini!
        df_all_time = pd.DataFrame([
            {
                "appid": g.get("appid"),
                "🎮 Gioco": g.get("name", "Sconosciuto"),
                "⏱️ Ore": format_hours(g.get("playtime_forever", 0)),
                "Minuti": g.get("playtime_forever", 0)
            }
            for g in top_games_all_time
        ])
        
        # --- CREAZIONE COLONNA IMMAGINI ---
        if "appid" in df_all_time.columns:
            df_all_time["Icona"] = df_all_time["appid"].apply(
                lambda x: f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{x}/capsule_231x87.jpg"
            )
        else:
            df_all_time["Icona"] = ""
        
        # --- VISUALIZZAZIONE A TABS ---
        col_tab1, col_tab2 = st.tabs(["🔥 Top 10", "📊 Grafico"])
        
        with col_tab1:
            st.write("**I tuoi 10 giochi più giocati di sempre:**")
            
            for idx, row in df_all_time.iterrows():
                # Abbiamo 3 colonne: Immagine (1.5), Titolo (3) e Ore (1.5)
                col_img, col1, col2 = st.columns([1.5, 3, 1.5]) 
                
                with col_img:
                    if row["Icona"]:
                        st.image(row["Icona"], use_container_width=True)
                with col1:
                    st.write(f"**{idx+1}. {row['🎮 Gioco']}**")
                with col2:
                    st.metric("Ore di gioco", row["⏱️ Ore"])
                
                st.divider() # Linea di separazione tra un gioco e l'altro
                
        with col_tab2:
            # Grafico a barre
            fig_bar = go.Figure(data=[
                go.Bar(
                    y=df_all_time["🎮 Gioco"],
                    x=df_all_time["⏱️ Ore"],
                    orientation='h',
                    marker=dict(color='#1f77b4'),
                    text=df_all_time["⏱️ Ore"],
                    textposition='auto',
                    hovertemplate="<b>%{y}</b><br>Ore: %{x}<extra></extra>"
                )
            ])
            
            fig_bar.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Ore di gioco",
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
    else:
        st.info("Nessun gioco giocato ancora")
    
    st.divider()
    
    # SEZIONE 4: TOP GIOCHI ULTIME 2 SETTIMANE
    st.subheader("🔥 Ultimi Giochi (Ultime 2 Settimane)")
    
    # Filtra i dati per aggiungere playtime_2weeks
    for game in games:
        if game.get("playtime_2weeks", 0) > 0:
            continue
        game["playtime_2weeks"] = 0
    
    top_games_recent = get_top_games_by_recent_playtime(games, limit=10)
    
    if top_games_recent:
        # Aggiungiamo l'appid al DataFrame per recuperare le immagini!
        df_recent = pd.DataFrame([
            {
                "appid": g.get("appid"),
                "🎮 Gioco": g.get("name", "Sconosciuto"),
                "⏱️ Ore (2 sett.)": format_hours(g.get("playtime_2weeks", 0))
            }
            for g in top_games_recent
        ])
        
        # --- CREAZIONE COLONNA IMMAGINI ---
        if "appid" in df_recent.columns:
            df_recent["Icona"] = df_recent["appid"].apply(
                lambda x: f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{x}/capsule_231x87.jpg"
            )
        else:
            df_recent["Icona"] = ""
            
        # --- VISUALIZZAZIONE A TABS ---
        col_tab1, col_tab2 = st.tabs(["🔥 Più Giocati di Recente", "📊 Grafico"])
        
        with col_tab1:
            st.write("**I titoli a cui hai dedicato più tempo negli ultimi 14 giorni:**")
            
            for idx, row in df_recent.iterrows():
                # Stesso layout a 3 colonne pulito della sezione precedente
                col_img, col1, col2 = st.columns([1.5, 3, 1.5]) 
                
                with col_img:
                    if row["Icona"]:
                        st.image(row["Icona"], use_container_width=True)
                with col1:
                    st.write(f"**{idx+1}. {row['🎮 Gioco']}**")
                with col2:
                    st.metric("Ore (Ultime 2 sett.)", row["⏱️ Ore (2 sett.)"])
                
                st.divider() # Linea di separazione
                
        with col_tab2:
            # Grafico a barre
            fig_recent = go.Figure(data=[
                go.Bar(
                    y=df_recent["🎮 Gioco"],
                    x=df_recent["⏱️ Ore (2 sett.)"],
                    orientation='h',
                    marker=dict(color='#ff7f0e'),
                    text=df_recent["⏱️ Ore (2 sett.)"],
                    textposition='auto',
                    hovertemplate="<b>%{y}</b><br>Ore: %{x}<extra></extra>"
                )
            ])
            
            fig_recent.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Ore di gioco",
                showlegend=False
            )
            
            st.plotly_chart(fig_recent, use_container_width=True)
            
    else:
        st.info("Non hai giocato negli ultimi 14 giorni a nessuno dei tuoi giochi")
    
    # --- CALCOLO MEDIA GIORNALIERA RECENTE ---
    # Sommiamo tutti i minuti giocati nelle ultime 2 settimane
    minuti_totali_2_settimane = sum(g.get("playtime_2weeks", 0) for g in games)

    # Convertiamo in ore e dividiamo per 14 giorni
    media_ore_giornaliere = (minuti_totali_2_settimane / 60) / 14

    st.info(f"""
            💡 La tua media giornaliera nelle ultime settimane:
            {media_ore_giornaliere:.1f} ore al giorno!
            """)

    