# Steam Buddies - Multi-Page Dashboard
Una dashboard Streamlit per analizzare le tue statistiche di gioco Steam  in modo visivo e confrontare i gusti di gioco con i tuoi amici.

## Funzionalità

### Dashboard Personale
- **Statistiche Generali**: Numero giochi posseduti, giocati, tempo totale
- **Grafico Ciambella**: Rapporto visivo tra giochi posseduti e giocati
- **Top 10 Giochi di Sempre**: Classifica dei giochi più giocati con grafico interattivo
- **Top Giochi Ultime 2 Settimane**: Attività di gioco recente
- **Statistiche Avanzate**: Media ore per gioco, gioco più giocato

### Confronta Giocatori
- **Giochi in Comune**: Vedi quali giochi condividete con gli amici
- **Grafico di Confronto**: Confronto visivo delle ore giocate per ogni gioco in comune
- **Analisi Achievement**: Confronto degli achievement sbloccati nei giochi comuni
- **Convincilo a Comprarlo**: Lista dei tuoi giochi migliori che il tuo amico non ha ancora
- **Giochi Esclusivi**: Vedi cosa ha il tuo amico che tu non hai

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

## 🔌 API Utilizzate

- **GetOwnedGames**: Recupera la lista di giochi posseduti e ore giocate
- **GetRecentlyPlayedGames**: Giochi giocati recentemente
- **GetPlayerAchievements**: Achievement sbloccati per un gioco

## 🐛 Troubleshooting

### "Profilo privato o Steam ID non valido"
- Verifica che il tuo Steam ID sia corretto
- Assicurati che il tuo profilo sia impostato su **Public**
- Attendi qualche minuto se hai appena reso pubblico il profilo

## 🎯 Idee per Miglioramenti Futuri

- [ ] Statistiche avanzate di gioco (genere, developer, etc.)
- [ ] Suggerimenti di giochi basati sui gusti comuni