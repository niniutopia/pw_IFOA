import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    get_owned_games,
    get_player_achievements,
    format_hours,
    validate_steam_id,
    parse_steam_input
)

st.set_page_config(page_title="Confronta Giocatori", page_icon="👥")

st.title("👥 Confronta Giocatori")
st.write("Scopri i giochi in comune e i gusti di gioco con i tuoi amici")

# Inizializza la API key
if "STEAM_API_KEY" not in st.secrets:
    st.error("⚠️ API Key non configurata. Aggiungi STEAM_API_KEY nel file secrets.toml")
    st.stop()

API_KEY = st.secrets["STEAM_API_KEY"]

# INIZIALIZZAZIONE MEMORIA DI STREAMLIT
if "ricerca_avviata" not in st.session_state:
    st.session_state.ricerca_avviata = False

# Input Steam IDs
col1, col2 = st.columns(2)

with col1:
    steam_id_1 = st.text_input("🎮 Steam ID/Vanity URL Giocatore 1:", placeholder="Username oppure 76561198...")

with col2:
    steam_id_2 = st.text_input("🎮 Steam ID/Vanity URL Giocatore 2:", placeholder="Username oppure 76561198...")

search_button = st.button("Confronta", use_container_width=True)

# SE IL BOTTONE VIENE CLICCATO, SALVIAMO NELLA MEMORIA CHE LA RICERCA È PARTITA
if search_button:
    st.session_state.ricerca_avviata = True

# ORA USIAMO LA MEMORIA INVECE DEL BOTTONE PER TENERE APERTA LA PAGINA
if st.session_state.ricerca_avviata:
    
    # Validazione
    if not steam_id_1 or not steam_id_2:
        st.warning("Per favore, inserisci entrambi gli Steam ID o Vanity URL")
        st.stop()
    
    # Risolvi gli input
    with st.spinner("🔄 Sto risolvendo i profili..."):
        resolved_steam_id_1 = parse_steam_input(API_KEY, steam_id_1)
        resolved_steam_id_2 = parse_steam_input(API_KEY, steam_id_2)
    
    if not resolved_steam_id_1 or not resolved_steam_id_2:
        st.error("❌ Uno o entrambi gli Steam ID/Vanity URL non sono validi. Assicurati che i profili siano pubblici.")
        st.stop()
    
    steam_id_1 = resolved_steam_id_1
    steam_id_2 = resolved_steam_id_2
    
    # Recupera i dati
    with st.spinner("📥 Sto recuperando i dati..."):
        games_data_1 = get_owned_games(API_KEY, steam_id_1)
        games_data_2 = get_owned_games(API_KEY, steam_id_2)
    
    if not games_data_1 or "games" not in games_data_1:
        st.error("❌ Profilo 1 privato o Steam ID non valido")
        st.stop()
    
    if not games_data_2 or "games" not in games_data_2:
        st.error("❌ Profilo 2 privato o Steam ID non valido")
        st.stop()
    
    games_1 = games_data_1.get("games", [])
    games_2 = games_data_2.get("games", [])
    
    # Crea dizionari per accesso rapido
    games_dict_1 = {g["appid"]: g for g in games_1}
    games_dict_2 = {g["appid"]: g for g in games_2}
    
    # Calcola insiemi di app IDs
    apps_1 = set(games_dict_1.keys())
    apps_2 = set(games_dict_2.keys())
    
    common_apps = apps_1 & apps_2
    only_player_1 = apps_1 - apps_2
    only_player_2 = apps_2 - apps_1
    
    st.success(f"✅ Dati caricati!")
    st.divider()
    
    # SEZIONE 1: STATISTICHE GENERALI
    st.subheader("📊 Statistiche Generali")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Giocatore 1", f"{len(games_1)} giochi")
    
    with col2:
        st.metric("🤝 Giochi in Comune", len(common_apps))
    
    with col3:
        st.metric("Giocatore 2", f"{len(games_2)} giochi")
    
    st.divider()
    
    # SEZIONE 2: GIOCHI IN COMUNE
    if common_apps:
        st.subheader("🤝 Giochi in Comune")
        
        common_games_data = []
        for app_id in common_apps:
            g1 = games_dict_1[app_id]
            g2 = games_dict_2[app_id]
            
            common_games_data.append({
                "appid": app_id,
                "nome": g1.get("name", "Sconosciuto"),
                "Ore G1": format_hours(g1.get("playtime_forever", 0)),
                "Ore G2": format_hours(g2.get("playtime_forever", 0)),
                "Minuti G1": g1.get("playtime_forever", 0),
                "Minuti G2": g2.get("playtime_forever", 0),
            })
        
        # Ordina per tempo di gioco combinato
        common_games_data.sort(key=lambda x: x["Minuti G1"] + x["Minuti G2"], reverse=True)
        
        df_common = pd.DataFrame(common_games_data)
        
        # Visualizzazione
        col_tab1, col_tab2, col_tab3 = st.tabs(["📋 Tabella", "📊 Grafico Confronto", "🔥 Top 10"])
        
        with col_tab1:
            st.dataframe(
                df_common[["nome", "Ore G1", "Ore G2"]],
                use_container_width=True,
                hide_index=True
            )
        
        with col_tab2:
            # Grafico a barre affiancate
            top_common = df_common.head(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    name="Giocatore 1",
                    y=top_common["nome"],
                    x=top_common["Ore G1"],
                    orientation='h',
                    marker=dict(color='#1f77b4')
                ),
                go.Bar(
                    name="Giocatore 2",
                    y=top_common["nome"],
                    x=top_common["Ore G2"],
                    orientation='h',
                    marker=dict(color='#ff7f0e')
                )
            ])
            
            fig.update_layout(
                barmode='group',
                height=500,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Ore di gioco",
                hovermode='y unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_tab3:
            top_10_common = df_common.head(10)
            st.write("**Top 10 Giochi Comuni (per ore combinate):**")
            
            for idx, row in top_10_common.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{idx+1}. {row['nome']}**")
                with col2:
                    st.metric("G1", row["Ore G1"])
                with col3:
                    st.metric("G2", row["Ore G2"])
        
        st.divider()
        
        # SEZIONE 3: ANALISI ACHIEVEMENT
        st.subheader("🏅 Analisi Achievement")
        
        st.info("Seleziona un gioco dalla lista dei giochi comuni per confrontare gli achievement")
        
        selected_game = st.selectbox(
            "Scegli un gioco:",
            options=[f"{row['nome']} (AppID: {row['appid']})" for _, row in df_common.iterrows()],
            key="game_selector"
        )
        
        if selected_game:
            # Estrai l'app_id
            app_id = int(selected_game.split("(AppID: ")[1].rstrip(")"))
            game_name = selected_game.split(" (AppID:")[0]
            
            with st.spinner("📥 Recupero achievement..."):
                ach_1 = get_player_achievements(API_KEY, steam_id_1, app_id)
                ach_2 = get_player_achievements(API_KEY, steam_id_2, app_id)
            
            if ach_1 and ach_2:
                achievements_1 = {ach["apiname"] for ach in ach_1.get("achievements", []) if ach.get("achieved") == 1}
                achievements_2 = {ach["apiname"] for ach in ach_2.get("achievements", []) if ach.get("achieved") == 1}
                
                total_achievements = len([ach for ach in ach_1.get("achievements", [])])
                common_achievements = achievements_1 & achievements_2
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("G1: Sbloccati", len(achievements_1))
                
                with col2:
                    st.metric("G2: Sbloccati", len(achievements_2))
                
                with col3:
                    st.metric("🤝 In Comune", len(common_achievements))
                
                with col4:
                    # Manteniamo il calcolo del totale solo in background per la percentuale
                    pct = (len(common_achievements) / total_achievements * 100) if total_achievements > 0 else 0
                    st.metric("Sincronismo", f"{pct:.0f}%")
                
                st.success(f"✅ {game_name}: Achievement caricati!")
            else:
                st.warning(f"❌ Impossibile recuperare gli achievement per {game_name}. Il gioco potrebbe non avere achievement o i profili non sono pubblici.")
    
    else:
        st.warning("❌ Nessun gioco in comune! I due giocatori hanno gusti completamente diversi.")
    
    st.divider()
    
    # SEZIONE 4: CONVINCILO A COMPRARLO
    st.subheader("🎁 Convincilo a Comprarlo!")
    st.write("Giochi che ha il Giocatore 1 ma non il Giocatore 2")
    
    if only_player_1:
        player_1_only_data = []
        for app_id in only_player_1:
            g = games_dict_1[app_id]
            player_1_only_data.append({
                "nome": g.get("name", "Sconosciuto"),
                "Ore": format_hours(g.get("playtime_forever", 0)),
                "Minuti": g.get("playtime_forever", 0)
            })
        
        # Ordina per ore giocate
        player_1_only_data.sort(key=lambda x: x["Minuti"], reverse=True)
        
        df_player_1_only = pd.DataFrame(player_1_only_data)
        
        # Visualizzazione
        col_tab1, col_tab2 = st.tabs(["📋 Tabella", "📊 Top 20"])
        
        with col_tab1:
            st.dataframe(
                df_player_1_only[["nome", "Ore"]],
                use_container_width=True,
                hide_index=True
            )
        
        with col_tab2:
            top_20 = df_player_1_only.head(20)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=top_20["nome"],
                    x=top_20["Ore"],
                    orientation='h',
                    marker=dict(color='#2ca02c'), # Verde per il G1
                    text=top_20["Ore"],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Ore di gioco",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"""
        **💡 Consiglio:**
        Il Giocatore 1 ha {len(only_player_1)} giochi che il Giocatore 2 non possiede.
        Il top è **{df_player_1_only.iloc[0]['nome']}** con **{df_player_1_only.iloc[0]['Ore']} ore** di gioco!
        """)
    
    else:
        st.success("✅ Il Giocatore 2 ha TUTTI i giochi del Giocatore 1!")
    
    st.divider()
    
    # SEZIONE 5: GIOCHI ESCLUSIVI GIOCATORE 2 (BUG FIXATO)
    st.subheader("🎮 Giochi Esclusivi del Giocatore 2")
    st.write("Giochi che ha il Giocatore 2 ma non il Giocatore 1")
    
    if only_player_2:
        player_2_only_data = []
        for app_id in only_player_2:
            g = games_dict_2[app_id]
            player_2_only_data.append({
                "nome": g.get("name", "Sconosciuto"),
                "Ore": format_hours(g.get("playtime_forever", 0)),
                "Minuti": g.get("playtime_forever", 0)
            })
        
        # Ordina per ore giocate
        player_2_only_data.sort(key=lambda x: x["Minuti"], reverse=True)
        
        df_player_2_only = pd.DataFrame(player_2_only_data)
        
        # Visualizzazione
        col_tab1, col_tab2 = st.tabs(["📋 Tabella", "📊 Top 20"])
        
        with col_tab1:
            st.dataframe(
                df_player_2_only[["nome", "Ore"]],
                use_container_width=True,
                hide_index=True
            )
        
        with col_tab2:
            top_20_p2 = df_player_2_only.head(20)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=top_20_p2["nome"],
                    x=top_20_p2["Ore"],
                    orientation='h',
                    marker=dict(color='#d62728'), # Rosso/Arancio scuro per distinguerlo
                    text=top_20_p2["Ore"],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Ore di gioco",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        st.info(f"""
        **💡 Scoperta:**
        Il Giocatore 2 ha {len(only_player_2)} giochi che potresti scroccare con il Family Sharing!
        Il suo titolo più giocato che tu non hai è **{df_player_2_only.iloc[0]['nome']}** con **{df_player_2_only.iloc[0]['Ore']} ore**.
        """)
        
    else:
        st.success("✅ Il Giocatore 1 ha TUTTI i giochi del Giocatore 2!")