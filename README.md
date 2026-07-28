# OfficeCloset8 — Glamouroeser Kleiderschrank-Manager

Ein glamouroeser Kleiderschrank-Manager mit Web-GUI im Hollywood-Stil. Benutzer
registrieren sich, legen Kleidungsstuecke mit Bildern und Kategorien an,
durchstoebern ihre Garderobe und kombinieren im Outfit-Creator Einzelteile zu
gespeicherten Outfits – alles in einer eleganten Red-Carpet-Optik.

## Tech Stack

- **Backend**: Python, FastAPI, SQLite (SQLAlchemy)
- **Frontend**: React (TypeScript), Vite
- **Bildspeicherung**: Lokales Dateisystem (upload/)

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Entwicklung

### Backend starten

```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend starten

```bash
cd frontend && npm run dev
```

Das Frontend laeuft unter `http://localhost:5173`, das Backend unter `http://localhost:8000`.

### Tests

```bash
cd backend && PYTHONPATH=. python -m pytest
```

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/health` | Health-Check |
| * | `/api/auth/*` | Authentifizierung (Stub) |
| * | `/api/clothing/*` | Kleidungsstuecke (Stub) |
| * | `/api/outfits/*` | Outfits (Stub) |

## Features

- Benutzerregistrierung und Login
- Kleidungsstuecke mit Bildern und Kategorien anlegen
- Garderoben-Galerie mit Kategoriefilter
- Outfit-Creator zum Kombinieren von Kleidungsstuecken
- Gespeicherte Outfits verwalten
- Konto selbststaendig loeschen (inkl. aller Daten)
- Sicherheit: bcrypt-Passwort-Hashing, Session-Cookies mit Secure/HttpOnly/SameSite
- Datenschutz: EXIF-Stripping vor Upload, keine personenbezogenen Daten in Logs
