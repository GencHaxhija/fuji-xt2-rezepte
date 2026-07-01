# 📷 Fuji X-T2 Rezepte

Persönliche Film Simulation Rezepte App für die Fujifilm X-T2.

## Tech Stack

- **Frontend:** React + TypeScript
- **Build:** Vite
- **Database:** Firebase Firestore
- **Hosting:** Vercel

## Setup

### 1. Dependencies installieren
```bash
npm install
```

### 2. Firebase Projekt erstellen
1. [Firebase Console](https://console.firebase.google.com/) → Neues Projekt
2. Firestore Database aktivieren
3. Web App registrieren → Config kopieren

### 3. Environment Variables setzen
Datei `.env.local` erstellen:
```env
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

### 4. Lokal starten
```bash
npm run dev
```

## Vercel Deployment

1. Repo auf [vercel.com](https://vercel.com) importieren
2. Environment Variables in Vercel Dashboard eintragen
3. Deploy!

## Legacy
Der alte Streamlit/Python Code ist im Branch `streamlit-legacy` erhalten.
