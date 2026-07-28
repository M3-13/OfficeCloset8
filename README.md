# OfficeCloset8 – Glamouröser Kleiderschrank-Manager

Ein glamouröser Kleiderschrank-Manager mit Web-GUI im Hollywood-Stil. Benutzer registrieren sich, legen Kleidungsstücke mit Bildern und Kategorien an, durchstöbern ihre Garderobe und kombinieren im Outfit-Creator Einzelteile zu gespeicherten Outfits – alles in einer eleganten Red-Carpet-Optik.

## Tech Stack

- **Backend**: Python, FastAPI, SQLite (SQLAlchemy)
- **Frontend**: React (TypeScript), Vite
- **Bildspeicherung**: Lokales Dateisystem (upload/)

## How to run

```bash
cd frontend
npm install
npm run build
```

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

Die Anwendung ist unter `http://localhost:8000` vollständig nutzbar – Frontend und API laufen auf demselben Port.

### Entwicklung

Für die Entwicklung mit Hot Module Replacement:

```bash
cd frontend
npm run dev
```

Das Dev-Frontend läuft unter `http://localhost:5173` und leitet `/api`-Anfragen per Proxy ans Backend (`http://localhost:8000`) weiter.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Der API-Server startet unter `http://localhost:8000`.

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/health` | Health-Check → `{"status": "ok"}` |
| POST | `/api/auth/register` | Registrierung |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Aktueller Benutzer |
| DELETE | `/api/auth/account` | Konto löschen |
| GET | `/api/clothing` | Alle Kleidungsstücke |
| POST | `/api/clothing` | Kleidungsstück anlegen |
| DELETE | `/api/clothing/{id}` | Kleidungsstück löschen |
| GET | `/api/outfits` | Alle Outfits |
| POST | `/api/outfits` | Outfit erstellen |
| PUT | `/api/outfits/{id}` | Outfit aktualisieren |
| DELETE | `/api/outfits/{id}` | Outfit löschen |

## Features

- Benutzerregistrierung und Login mit Sessions
- Kleidungsstücke mit Bildern und Kategorien anlegen
- Garderoben-Galerie mit Kategorie-Filter
- Outfit-Creator zum Kombinieren von Kleidungsstücken
- Gespeicherte Outfits verwalten (öffnen, bearbeiten, löschen)
- Konto löschen mit allen zugehörigen Daten

