import requests
import streamlit as st
from functools import lru_cache
import time
import re

@lru_cache(maxsize=100)
def get_steam_id_from_vanity(api_key, vanity_url):
    """Converte un vanity URL (custom URL) in Steam ID"""
    # Pulisci l'input - rimuovi URL completo se presente
    if "steamcommunity.com/id/" in vanity_url:
        vanity_url = vanity_url.split("/id/")[-1].rstrip("/")
    
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {
        "key": api_key,
        "vanityurl": vanity_url
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("response", {}).get("success") == 1:
            return str(data["response"]["steamid"])
    return None


def parse_steam_input(api_key, user_input):
    # Rimuoviamo eventuali spazi vuoti invisibili prima e dopo
    user_input = str(user_input).strip()
    
    # Se è già un ID numerico di 17 cifre, lo restituiamo subito senza chiamare Steam!
    if user_input.isdigit() and len(user_input) == 17:
        return user_input
    
    # Altrimenti, proviamo a risolverlo come Vanity URL
    url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={user_input}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('response', {}).get('success') == 1:
            return data['response']['steamid']
    except Exception as e:
        print(f"Errore nella risoluzione del profilo: {e}")
        
    return None

@lru_cache(maxsize=100)
def get_owned_games(api_key, steam_id):
    """Recupera la lista di giochi posseduti con statistiche di gioco"""
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("response", {})
    return None

@lru_cache(maxsize=100)
def get_recently_played(api_key, steam_id):
    """Recupera i giochi giocati recentemente (ultime 2 settimane)"""
    url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("response", {}).get("games", [])
    return None

@lru_cache(maxsize=100)
def get_player_achievements(api_key, steam_id, app_id):
    """Recupera gli achievement di un gioco specifico"""
    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        "key": api_key,
        "steamid": steam_id,
        "appid": app_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("playerstats", {}).get("achievements"):
            return data["playerstats"]
    return None

def get_common_games(api_key, steam_id_1, steam_id_2):
    """Trova i giochi in comune tra due giocatori"""
    with st.spinner("Recupero giochi del giocatore 1..."):
        games_1 = get_owned_games(api_key, steam_id_1)
    
    with st.spinner("Recupero giochi del giocatore 2..."):
        games_2 = get_owned_games(api_key, steam_id_2)
    
    if not games_1 or not games_2:
        return None, None, None
    
    # Estrai app_id
    apps_1 = {g["appid"] for g in games_1.get("games", [])}
    apps_2 = {g["appid"] for g in games_2.get("games", [])}
    
    common_apps = apps_1 & apps_2
    only_player_1 = apps_1 - apps_2
    only_player_2 = apps_2 - apps_1
    
    # Ricostruisci i dati dei giochi in comune
    common_games = [g for g in games_1.get("games", []) if g["appid"] in common_apps]
    player1_only = [g for g in games_1.get("games", []) if g["appid"] in only_player_1]
    
    return common_games, player1_only, games_1.get("games", [])

def calculate_total_playtime(games):
    """Calcola il tempo totale di gioco in ore"""
    total_minutes = sum(game.get("playtime_forever", 0) for game in games)
    total_hours = total_minutes / 60
    return total_hours

def get_owned_vs_played_ratio(games):
    """Calcola il rapporto giochi posseduti vs giocati"""
    total_games = len(games)
    played_games = sum(1 for g in games if g.get("playtime_forever", 0) > 0)
    return played_games, total_games

def get_top_games_by_playtime(games, limit=10):
    """Ordina i giochi per tempo di gioco totale"""
    sorted_games = sorted(games, key=lambda x: x.get("playtime_forever", 0), reverse=True)
    return sorted_games[:limit]

def get_top_games_by_recent_playtime(games, limit=10):
    """Ordina i giochi per tempo di gioco recente (ultime 2 settimane)"""
    sorted_games = sorted(games, key=lambda x: x.get("playtime_2weeks", 0), reverse=True)
    return [g for g in sorted_games if g.get("playtime_2weeks", 0) > 0][:limit]

def format_hours(minutes):
    """Converte minuti in ore formattate"""
    hours = minutes / 60
    return round(hours, 1)

def validate_steam_id(steam_id):
    """Valida il formato dello Steam ID"""
    return steam_id.strip().isdigit() and len(steam_id.strip()) >= 17


def get_unplayed_games(games):
    """
    Restituisce la lista dei giochi posseduti ma mai avviati
    (playtime_forever uguale a 0).
    """
    # Filtriamo la lista tenendo solo i giochi con 0 minuti registrati
    unplayed_games = [g for g in games if g.get("playtime_forever", 0) == 0]
    
    return unplayed_games

@lru_cache(maxsize=100)
def get_player_name(api_key, steam_id):
    """Interroga l'API di Steam per ottenere il vero nickname del giocatore"""
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": api_key, "steamids": steam_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            players = response.json().get("response", {}).get("players", [])
            if players:
                return players[0].get("personaname")
    except Exception:
        pass
    
    # Fallback nel caso in cui fallisse o il profilo non esista
    return str(steam_id)

@lru_cache(maxsize=100)
def get_game_schema(api_key, app_id, language="italian"):
    """
    Recupera il 'dizionario' del gioco: nomi reali, descrizioni e icone degli achievement.
    Il parametro 'language' traduce automaticamente i testi dove disponibile.
    """
    url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    params = {
        "key": api_key,
        "appid": app_id,
        "l": language  # Chiediamo a Steam la localizzazione in italiano
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Navighiamo l'albero del JSON fino agli achievement
            achievements = data.get("game", {}).get("availableGameStats", {}).get("achievements", [])
            
            # Creiamo un dizionario super veloce da consultare
            # Chiave: nome interno (apiname) -> Valore: tutti i dettagli (titolo, descr, icone)
            schema_dict = {}
            for ach in achievements:
                schema_dict[ach["name"]] = {
                    "titolo": ach.get("displayName", "Senza Titolo"),
                    "descrizione": ach.get("description", "Nessuna descrizione disponibile."),
                    "icona_sbloccata": ach.get("icon"),
                    "icona_bloccata": ach.get("icongray"),
                    "nascosto": ach.get("hidden", 0) # 1 se è un achievement segreto
                }
            return schema_dict
    except Exception:
        pass
        
    return {}

@lru_cache(maxsize=100)
def get_achievement_percentages(app_id):
    """Recupera le percentuali globali di rarità degli achievement per un gioco"""
    url = "https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/"
    params = {"gameid": app_id}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            achievements = data.get("achievementpercentages", {}).get("achievements", [])
            
            # Creiamo un dizionario veloce da leggere: { "codice_trofeo": 45.2 }
            return {ach["name"]: ach["percent"] for ach in achievements}
    except Exception:
        pass
        
    return {}

@lru_cache(maxsize=1000)
def get_game_features(app_id):
    """
    Usa le API del Negozio di Steam per capire se il gioco supporta 
    il Multiplayer, la Co-op o il Remote Play Together.
    """
    url = f"https://store.steampowered.com/api/appdetails"
    params = {"appids": app_id}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        # Se Steam ci sta bloccando per le troppe richieste (Errore 429)
        if response.status_code == 429:
            time.sleep(1) # Pausa tattica di 1 secondo
            response = requests.get(url, params=params, timeout=5)
            
        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(app_id), {})
            
            if app_data.get("success"):
                categories = app_data["data"].get("categories", [])
                
                # Estraiamo solo gli ID numerici delle categorie
                cat_ids = [cat["id"] for cat in categories]
                
                return {
                    "is_multiplayer": (1 in cat_ids) or (9 in cat_ids) or (38 in cat_ids),
                    "has_remote_play": 44 in cat_ids
                }
    except Exception:
        pass
        
    # Se il gioco è stato rimosso dallo store o fallisce la chiamata
    return {"is_multiplayer": False, "has_remote_play": False}


def get_game_details(api_key, appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&language=it"
    response = requests.get(url)
    data = response.json()
    if data and str(appid) in data and data[str(appid)]["success"]:
        return data[str(appid)]["data"]
    return None

    import streamlit as st
