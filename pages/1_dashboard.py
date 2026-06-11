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


# Richiamo la API key
API_KEY = st.secrets["STEAM_API_KEY"]


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

# bottone
if submit_profilo or steam_id:
    if not steam_id:
        st.warning("Per favore, inserisci uno Steam ID, un Vanity URL o il link del profilo")
        st.stop()
    
    # --- ESTRAZIONE DA URL ---
    # Puliamo l'input da spazi e slash finali accidentali
    clean_input = steam_id.strip().strip("/")
    
    # 1. Controlla se è un URL /profiles/ (ID Numerico)
    match_profiles = re.search(r'steamcommunity\.com/profiles/(\d+)', clean_input)
    if match_profiles:
        clean_input = match_profiles.group(1)
    else:
        # 2. Controlla se è un URL /id/ (Vanity Name)
        match_id = re.search(r'steamcommunity\.com/id/([^/]+)', clean_input)
        if match_id:
            clean_input = match_id.group(1)
    # -------------------------

    # Prova a risolvere l'input pulito (ora supporta ID, Vanity e URL completi)
    with st.spinner("🔄 Sto risolvendo il tuo profilo..."):
        resolved_steam_id = parse_steam_input(API_KEY, clean_input)
    
    if not resolved_steam_id:
        st.error("❌ Steam ID, Vanity URL o Link non valido. Assicurati che:\n- L'ID o il link sia corretto\n- Il profilo sia pubblico")
        st.stop()
    
    steam_id = resolved_steam_id


    # Recupera i dati
    with st.spinner("📥 Sto recuperando i tuoi dati da Steam..."):
        games_data = get_owned_games(API_KEY, steam_id)
    
    if not games_data or "games" not in games_data:
        st.error("❌ Profilo privato o Steam ID non valido. Assicurati che il tuo profilo sia pubblico.")
        st.stop()
    
    games = games_data.get("games", [])
    
    if not games:
        st.info("📭 Non hai giochi nel tuo account")
        st.stop()
    
    st.success(f"✅ Dati caricati! {len(games)} giochi trovati")
    st.divider()
    
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
        df_all_time = pd.DataFrame([
            {
                "🎮 Gioco": g.get("name", "Sconosciuto"),
                "⏱️ Ore": format_hours(g.get("playtime_forever", 0)),
                "Minuti": g.get("playtime_forever", 0)
            }
            for g in top_games_all_time
        ])
        
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
        
        with st.expander("📋 Dettagli tabella"):
            st.dataframe(
                df_all_time[["🎮 Gioco", "⏱️ Ore"]],
                use_container_width=True,
                hide_index=True
            )
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
        df_recent = pd.DataFrame([
            {
                "🎮 Gioco": g.get("name", "Sconosciuto"),
                "⏱️ Ore (2 sett.)": format_hours(g.get("playtime_2weeks", 0))
            }
            for g in top_games_recent
        ])
        
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
        
        with st.expander("📋 Dettagli tabella"):
            st.dataframe(
                df_recent,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Non hai giocato negli ultimi 14 giorni a nessuno dei tuoi giochi")
    
    st.divider()
    
    # SEZIONE 5: STATISTICHE EXTRA
    with st.expander("📊 Statistiche Avanzate"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Media ore per gioco (giocati):**")
            if played_games > 0:
                avg_hours = total_hours / played_games
                st.info(f"{avg_hours:.1f} ore")
            else:
                st.info("N/A")
        
        with col2:
            st.write("**Gioco più giocato:**")
            if top_games_all_time:
                most_played = top_games_all_time[0]
                st.success(f"{most_played.get('name', 'Sconosciuto')}: {format_hours(most_played.get('playtime_forever', 0))} ore")

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
    

    