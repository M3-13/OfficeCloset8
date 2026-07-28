VERDICT: BUGS_FOUND

- **Titel**: Frontend‑API‑Anfragen werden vom Produktiv‑Server nicht an das Backend weitergeleitet und führen zu einem JSON‑Syntaxfehler
- **Symptom**: Die gesamte Web‑App lädt nicht. Im Browser erscheint sofort der Laufzeitfehler `Uncaught (in promise) SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`. Die Oberfläche bleibt funktionslos; Nutzer können sich weder registrieren noch einloggen noch Kleidungsstücke verwalten.
- **Repro**:
  1. Backend starten (z. B. mit `uvicorn main:app`)
  2. Frontend bauen (`npm run build`)
  3. Frontend über einen statischen Webserver ausliefern (nicht den Vite‑Dev‑Server)
  4. Die Seite im Browser öffnen
  → Der statische Server liefert für alle `/api/*`‑Zugriffe die `index.html` aus, da kein Reverse‑Proxy und keine konfigurierbare Backend‑URL vorhanden ist. Das `fetch` im Client versucht, dieses HTML als JSON zu parsen, und wirft den Syntax‑Error.
- **Evidence**: Aus dem Playwright‑Smoke‑Test:
  `Error: runtime errors during load: pageerror: Uncaught (in promise) SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`
- **Suspected file(s)**:
  * `frontend/vite.config.ts` – definiert nur einen Dev‑Proxy, der im Produktions‑Build nicht greift
  * `frontend/src/api/*.ts` – alle Fetch‑Aufrufe verwenden relative Pfade (`/api/...`) ohne einen konfigurierbaren Base‑URL‑Fallback
  * `backend/main.py` – die `StaticFiles`‑Mount‑Option wird im Test‑Setup nicht genutzt, weil das Backend und die statischen Dateien auf unterschiedlichen Ports laufen; die fehlende Trennung in der Standard‑Konfiguration hilft dem externen Deployment nicht
- **Severity**: critical – die produktiv gebaute Anwendung ist ohne manuelles Einrichten eines Reverse‑Proxy oder Starten über den Dev‑Server nicht nutzbar.