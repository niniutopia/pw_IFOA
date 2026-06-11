import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils import (
    get_owned_games,
    get_player_achievements,
    format_hours,
    validate_steam_id,
    parse_steam_input,
    get_player_name,
    get_game_schema,              # 👈 Dizionario Testi
    get_achievement_percentages
)

st.set_page_config(page_title="Confronta Giocatori", page_icon="👥")

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

with st.expander("📍 Come Trovare lo Steam ID o Vanity URL"):
    st.markdown("""
    L'app accetta due formati:

    ### Formato 1: Steam ID Numerico (32-bit)
    - **Esempio**: `76561197960434622` (17 cifre)
    - Puoi trovarlo sul tuo profilo, sono le cifre alla fine dell'url `https://steamcommunity.com/profiles/76561197960434622`
    - **Più affidabile**, funziona sempre se il profilo è pubblico
    - **Non funziona se incolli tutto il link per intero**

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
    
    ## 🐛 Troubleshooting

    ##### "Profilo privato o Steam ID non valido"
    - Verifica che il tuo Steam ID sia corretto
    - Assicurati che il tuo profilo sia impostato su **Public**
    - Attendi qualche minuto se hai appena reso pubblico il profilo
                """)

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
    
    # Recupera i dati (e i veri nomi)
    with st.spinner("📥 Sto recuperando i dati e i nomi utente..."):
        # Prende i veri nickname da usare in tutta la UI
        name_1 = get_player_name(API_KEY, steam_id_1)
        name_2 = get_player_name(API_KEY, steam_id_2)
        
        games_data_1 = get_owned_games(API_KEY, steam_id_1)
        games_data_2 = get_owned_games(API_KEY, steam_id_2)
    
    if not games_data_1 or "games" not in games_data_1:
        st.error(f"❌ Profilo di {name_1} privato o non valido")
        st.stop()
    
    if not games_data_2 or "games" not in games_data_2:
        st.error(f"❌ Profilo di {name_2} privato o non valido")
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
    
    st.success(f"✅ Dati caricati per **{name_1}** e **{name_2}**!")
    st.divider()
    
    # SEZIONE 1: STATISTICHE GENERALI
    st.subheader("📊 Statistiche Generali")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(name_1, f"{len(games_1)} giochi")
    
    with col2:
        st.metric("🤝 Giochi in Comune", len(common_apps))
    
    with col3:
        st.metric(name_2, f"{len(games_2)} giochi")
    
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
                f"Ore {name_1}": format_hours(g1.get("playtime_forever", 0)),
                f"Ore {name_2}": format_hours(g2.get("playtime_forever", 0)),
                f"Minuti {name_1}": g1.get("playtime_forever", 0),
                f"Minuti {name_2}": g2.get("playtime_forever", 0),
            })
        
        # Ordina per tempo di gioco combinato
        common_games_data.sort(key=lambda x: x[f"Minuti {name_1}"] + x[f"Minuti {name_2}"], reverse=True)
        
        df_common = pd.DataFrame(common_games_data)
        
        # Visualizzazione
        col_tab1, col_tab2, col_tab3 = st.tabs(["📋 Tabella", "📊 Grafico Confronto", "🔥 Top 10"])
        
        with col_tab1:
            st.dataframe(
                df_common[["nome", f"Ore {name_1}", f"Ore {name_2}"]],
                use_container_width=True,
                hide_index=True
            )
        
        with col_tab2:
            # Grafico a barre affiancate
            top_common = df_common.head(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    name=name_1,
                    y=top_common["nome"],
                    x=top_common[f"Ore {name_1}"],
                    orientation='h',
                    marker=dict(color='#1f77b4')
                ),
                go.Bar(
                    name=name_2,
                    y=top_common["nome"],
                    x=top_common[f"Ore {name_2}"],
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
                    st.metric(name_1, row[f"Ore {name_1}"])
                with col3:
                    st.metric(name_2, row[f"Ore {name_2}"])
        
        st.divider()
        
        # SEZIONE 3: ANALISI ACHIEVEMENTS
        st.subheader("🏅 Analisi Achievements")
        
        st.info("Seleziona un gioco dalla lista dei giochi comuni per confrontare gli achievement")
        
        selected_game = st.selectbox(
            "Scegli un gioco:",
            options=[f"{row['nome']} (AppID: {row['appid']})" for _, row in df_common.iterrows()],
            key="game_selector"
        )
        
        if selected_game:
            # Estrai l'app_id dal testo della selectbox
            app_id = int(selected_game.split("(AppID: ")[1].rstrip(")"))
            game_name = selected_game.split(" (AppID:")[0]
            
            with st.spinner("📥 Recupero achievement, testi e rarità..."):
                # Dati sbloccati grezzi
                ach_1 = get_player_achievements(API_KEY, steam_id_1, app_id)
                ach_2 = get_player_achievements(API_KEY, steam_id_2, app_id)
                
                # I "Dizionari" che ci servono per tradurre i codici
                schema = get_game_schema(API_KEY, app_id) 
                rarity = get_achievement_percentages(app_id)
            
            if ach_1 and ach_2:
                # 1. Estraiamo la lista dei codici effettivamente sbloccati
                ach_unlocked_1 = [ach["apiname"] for ach in ach_1.get("achievements", []) if ach.get("achieved") == 1]
                ach_unlocked_2 = [ach["apiname"] for ach in ach_2.get("achievements", []) if ach.get("achieved") == 1]
                
                achievements_1 = set(ach_unlocked_1)
                achievements_2 = set(ach_unlocked_2)
                
                total_achievements = len(ach_1.get("achievements", []))
                common_achievements = achievements_1 & achievements_2
                
                # --- STATISTICHE BASE ---
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(f"{name_1}: Sbloccati", len(achievements_1))
                with col2:
                    st.metric(f"{name_2}: Sbloccati", len(achievements_2))
                with col3:
                    st.metric("🤝 In Comune", len(common_achievements))
                with col4:
                    pct_sync = (len(common_achievements) / total_achievements * 100) if total_achievements > 0 else 0
                    st.metric("Sincronismo", f"{pct_sync:.0f}%")
                
            
                # --- CALCOLO DEI TROFEI PIÙ RARI ---
                
                # Piccola funzione interna per trovare il più raro in una lista
                def find_rarest(unlocked_list, rarity_dict):
                    rarest_code = None
                    rarest_pct = 101.0 # Partiamo oltre il 100%
                    
                    for code in unlocked_list:
                        # 🔴 FIX: Forziamo la conversione in numero (float)
                        try:
                            pct = float(rarity_dict.get(code, 100.0))
                        except (ValueError, TypeError):
                            pct = 100.0
                            
                        if pct < rarest_pct:
                            rarest_pct = pct
                            rarest_code = code
                    return rarest_code, rarest_pct

                # Troviamo il vanto di ciascun giocatore
                rarest_1, pct_1 = find_rarest(ach_unlocked_1, rarity)
                rarest_2, pct_2 = find_rarest(ach_unlocked_2, rarity)
                
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    st.write(f"**🏆 Il vanto di {name_1}:**")
                    if rarest_1:
                        titolo = schema.get(rarest_1, {}).get("titolo", rarest_1)
                        descrizione = schema.get(rarest_1, {}).get("descrizione", "")
                        st.info(f"**{titolo}**\n\n*{descrizione}*\n\n📈 Sbloccato dal **{pct_1:.1f}%** dei giocatori")
                    else:
                        st.info("Nessun achievement sbloccato.")
                        
                with col_r2:
                    st.write(f"**🏆 Il vanto di {name_2}:**")
                    if rarest_2:
                        titolo = schema.get(rarest_2, {}).get("titolo", rarest_2)
                        descrizione = schema.get(rarest_2, {}).get("descrizione", "")
                        st.info(f"**{titolo}**\n\n*{descrizione}*\n\n📈 Sbloccato dal **{pct_2:.1f}%** dei giocatori")
                    else:
                        st.info("Nessun achievement sbloccato.")
                        
                # --- LISTA ACHIEVEMENT IN COMUNE ---
                if common_achievements:
                                        
                    # Creiamo una lista arricchita per poterli mettere in ordine di rarità
                    common_list = []
                    for ach in common_achievements:
                        # 🔴 FIX: Anche qui forziamo il numero per permettere un ordinamento corretto
                        try:
                            rarity_val = float(rarity.get(ach, 100.0))
                        except (ValueError, TypeError):
                            rarity_val = 100.0
                            
                        common_list.append({
                            "titolo": schema.get(ach, {}).get("titolo", ach),
                            "descrizione": schema.get(ach, {}).get("descrizione", ""),
                            "rarita": rarity_val
                        })
                    
                    # Ordiniamo la lista dal più difficile (percentuale più bassa) al più facile
                    common_list.sort(key=lambda x: x["rarita"])
                    
                    with st.expander(f"Visualizza i {len(common_achievements)} trofei che avete sbloccato entrambi"):
                        for ach_data in common_list:
                            st.write(f"- **{ach_data['titolo']}** (Sbloccato dal {ach_data['rarita']:.1f}%): *{ach_data['descrizione']}*")          
                st.success(f"✅ Achievement di {game_name} analizzati con successo!")
            else:
                st.warning(f"❌ Impossibile recuperare gli achievement per {game_name}. I profili potrebbero non essere pubblici o il gioco non ha trofei.")
    
    # SEZIONE 4: CONVINCILO A COMPRARLO
    st.subheader(f"🎁 Convincilo a Comprarlo!")
    st.write(f"Giochi che ha **{name_1}** ma non **{name_2}**")
    
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
                    marker=dict(color='#2ca02c'),
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
        {name_1} ha {len(only_player_1)} giochi che {name_2} non possiede.
        Il suo preferito è **{df_player_1_only.iloc[0]['nome']}** con ben **{df_player_1_only.iloc[0]['Ore']} ore** di gioco!
        """)
    
    else:
        st.success(f"✅ **{name_2}** ha TUTTI i giochi di **{name_1}**!")
    
    st.divider()
    
    # SEZIONE 5: GIOCHI ESCLUSIVI GIOCATORE 2
    st.subheader(f"🎮 Giochi Esclusivi di {name_2}")
    st.write(f"Giochi che ha **{name_2}** ma non **{name_1}**")
    
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
                    marker=dict(color='#d62728'),
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
        {name_2} ha {len(only_player_2)} giochi che potresti scroccare con il Family Sharing!
        Il suo titolo più giocato che tu non hai è **{df_player_2_only.iloc[0]['nome']}** con **{df_player_2_only.iloc[0]['Ore']} ore**.
        """)
        
    else:
        st.success(f"✅ **{name_1}** ha TUTTI i giochi di **{name_2}**!")

# Sidebar con info
with st.sidebar:
    st.markdown("### 🎮 Steam Buddy")
    st.caption("Alimentato da Steam Web API")
    st.divider()
    
    st.write("Navigazione:")
    
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/1_dashboard.py", label="Dashboard Personale", icon="📊")
    st.page_link("pages/2_confronta_giocatori.py", label="Confronta Giocatori", icon="👥")