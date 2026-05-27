import streamlit as st
import requests

# Titolo dell'app
st.title("Steam Buddies")
st.write("A cosa hai giocato nelle ultime due settimane?")

API_KEY = st.secrets["STEAM_API_KEY"]

# INPUT
steam_id_input = st.text_input("Inserisci lo SteamID:")

if st.button("Cerca tra i miei giochi"):
    
    if steam_id_input:

        url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
        parametri = {
            "key": API_KEY,
            "steamid": steam_id_input.strip()
        }
        
        # spinner di caricamento mentre Steam risponde
        with st.spinner('Sto interrogando i server di Steam...'):
            risposta = requests.get(url, params=parametri)
        
        # PRINT
        if risposta.status_code == 200:
            dati = risposta.json()
            giochi = dati.get("response", {}).get("games", [])
            
            if len(giochi) > 0:
                st.success("Dati recuperati con successo!")
                st.subheader("Ecco a cosa hai giocato nelle ultime due settimane:")
                
                # Lista dei giochi
                for gioco in giochi:
                    nome = gioco.get("name", "Gioco Sconosciuto")
                    ore_giocate = round(gioco.get("playtime_2weeks", 0) / 60, 1)
                    
                    st.write(f"- **{nome}**: {ore_giocate} ore di gioco")
                    
            else:
                # Se l'array "games" è vuoto
                st.info("Non risulta nessuna ora di gioco nelle ultime due settimane su questo account.")
                
        else:
            # Se la chiamata API fallisce (es. ID sbagliato o profilo privato)
            st.error(f"Errore nella chiamata! Codice di stato: {risposta.status_code}")
            
    else:
        st.warning("Per favore, inserisci uno SteamID prima di cliccare su Cerca.")