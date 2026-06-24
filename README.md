# 📷 Fuji X-T2 Film Simulation Rezepte

Persönliche Datenbank für Fujifilm X-T2 Film Simulation Rezepte — gebaut mit Streamlit.

## Features
- 🌐 **Bilingual** — Deutsch / English (umschaltbar in der App)
- ✅ Rezepte speichern (alle Kameraparameter)
- 🎞️ **Multiselect** für Film Simulation (mehrere Simulationen pro Rezept)
- 🔗 **Auto-Import** von [FujiXWeekly](https://fujixweekly.com) — Rezeptdaten per URL auslesen
- 🔍 Filtern nach Kategorie & Film Simulation (Sidebar)
- 📝 Eigene Notizen pro Rezept
- 🗑️ Rezepte löschen

## Tech-Stack
| Komponente | Technologie |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| Datenbank | Google Sheets (via `gspread`) |
| Scraping | `requests` + `BeautifulSoup4` |
| Auth | Google Service Account |

## Deploy auf Streamlit Cloud

1. Gehe zu [share.streamlit.io](https://share.streamlit.io)
2. Mit GitHub anmelden
3. Repository `fuji-xt2-rezepte` auswählen
4. `app.py` als Hauptdatei auswählen
5. **Secrets konfigurieren** — füge deinen Google Service Account Key unter `gcp_service_account` hinzu:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "..."
   client_email = "..."
   # ... etc.
   ```
6. Deploy klicken ✅

## Lokale Entwicklung

```bash
pip install -r requirements.txt
streamlit run app.py
```

> **Hinweis:** Für lokale Entwicklung muss eine `.streamlit/secrets.toml` Datei mit dem Service Account Key vorhanden sein.
