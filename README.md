# Fuji X-T2 Rezepte

React + TypeScript App für Fujifilm Filmrezepte, gespeichert in Google Sheets.

## Architektur

```
Browser (React) → Vercel API Function (/api/rezepte) → Google Sheets
```

## Setup

### 1. Google Sheets vorbereiten

1. Öffne dein bestehendes Google Sheet
2. Stelle sicher, dass das Sheet den Namen **`Rezepte`** hat
3. Kopiere die Sheet-ID aus der URL: `https://docs.google.com/spreadsheets/d/**SHEET_ID**/edit`

### 2. Google Service Account erstellen

1. [console.cloud.google.com](https://console.cloud.google.com) → APIs & Dienste → Anmeldedaten
2. **Service Account** erstellen
3. **Google Sheets API** aktivieren
4. JSON-Key herunterladen
5. Den Service Account als **Editor** zum Google Sheet hinzufügen

### 3. Vercel Deployment

1. Repo bei Vercel importieren
2. Folgende **Environment Variables** eintragen:
   - `GOOGLE_SHEET_ID` — die Sheet-ID aus Schritt 1
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — den gesamten Inhalt der JSON-Key-Datei
3. Deploy klicken ✅

## Lokale Entwicklung

```bash
npm install
# .env.local erstellen mit den obigen Variablen
npm run dev
```

<!-- redeploy: 3 -->
