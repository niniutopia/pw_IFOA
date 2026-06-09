# 🎮 Steam Buddies - Multi-Page Dashboard

Una dashboard Streamlit per analizzare le tue statistiche di gioco Steam e confrontare i gusti di gioco con i tuoi amici.

## ✨ Funzionalità

### 📊 Pagina 1: Dashboard Personale
- **Statistiche Generali**: Numero giochi posseduti, giocati, tempo totale
- **Grafico Ciambella**: Rapporto visivo tra giochi posseduti e giocati
- **Top 10 Giochi di Sempre**: Classifica dei giochi più giocati con grafico interattivo
- **Top Giochi Ultime 2 Settimane**: Attività di gioco recente
- **Statistiche Avanzate**: Media ore per gioco, gioco più giocato

### 👥 Pagina 2: Confronta Giocatori
- **Giochi in Comune**: Vedi quali giochi condividete con gli amici
- **Grafico di Confronto**: Confronto visivo delle ore giocate per ogni gioco in comune
- **Analisi Achievement**: Confronto degli achievement sbloccati nei giochi comuni
- **Convincilo a Comprarlo**: Lista dei tuoi giochi migliori che il tuo amico non ha ancora
- **Giochi Esclusivi**: Vedi cosa ha il tuo amico che tu non hai

## 🚀 Come Iniziare

### Prerequisiti
- Python 3.8+
- pip

### 1. Installa le Dipendenze
```bash
pip install streamlit pandas plotly requests
```

### 2. Configura la Steam API Key
1. Vai su https://steamcommunity.com/dev/apikey
2. Accedi con il tuo account Steam
3. Copia la tua API Key
4. Apri `.streamlit/secrets.toml` e sostituisci `YOUR_STEAM_API_KEY_HERE` con la tua chiave

```toml
STEAM_API_KEY = "tua_chiave_api_qui"
```

### 3. Avvia l'App
```bash
streamlit run app.py
```

L'app si aprirà automaticamente nel tuo browser a `http://localhost:8501`

## 📍 Come Trovare lo Steam ID o Vanity URL

L'app accetta entrambi i formati:

### Formato 1: Steam ID Numerico (32-bit)
- **Esempio**: `76561198123456789` (17 cifre)
- Puoi trovarlo su https://steamid.io/ cercando il tuo profilo
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

## 📊 Struttura del Progetto

```
agents-streamlit-multi-page-dashboard/
├── app.py                          # Entry point (homepage)
├── utils.py                        # Funzioni utility per API Steam
├── pages/
│   ├── 1_dashboard.py             # Dashboard personale
│   └── 2_confronta_giocatori.py   # Confronto tra due giocatori
├── .streamlit/
│   └── secrets.toml               # Configurazione API Key
└── README.md                       # Questo file
```

## 🔌 API Utilizzate

- **GetOwnedGames**: Recupera la lista di giochi posseduti e ore giocate
- **GetRecentlyPlayedGames**: Giochi giocati recentemente
- **GetPlayerAchievements**: Achievement sbloccati per un gioco

## 📈 Performance

L'app utilizza cache (LRU) per ottimizzare le chiamate API e migliorare la velocità di risposta.

## 🐛 Troubleshooting

### "Profilo privato o Steam ID non valido"
- Verifica che il tuo Steam ID sia corretto
- Assicurati che il tuo profilo sia impostato su **Public**
- Attendi qualche minuto se hai appena reso pubblico il profilo

### "API Key non configurata"
- Aggiungi la tua API Key nel file `.streamlit/secrets.toml`
- Restarta l'app dopo aver salvato il file

### L'app è lenta
- La prima volta che cerchi un giocatore, potrebbe impiegare più tempo
- Le ricerche successive sono più veloci grazie alla cache
- L'app rispetta i rate limits di Steam API

## 🎯 Idee per Miglioramenti Futuri

- [ ] Statistiche avanzate di gioco (genere, developer, etc.)
- [ ] Suggerimenti di giochi basati sui gusti comuni
- [ ] Cronologia storica delle statistiche
- [ ] Integrazione con più piattaforme gaming

## 📝 Licenza

Questo progetto è fornito così com'è per scopi educativi e personali.

## 🤝 Contributi

Se hai suggerimenti o trovati bug, sentiti libero di contribuire!

---

**Sviluppato con ❤️ usando Streamlit**