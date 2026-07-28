VERDICT: BLOCKED

## Strukturierter Sicherheitsbericht

### 1. Fehlerhafte CORS‑Konfiguration mit Credentials (Hoch)

**Betroffene Datei:** `backend/main.py` (Zeilen 27–33)

**Beschreibung:**  
Die Middleware `CORSMiddleware` ist mit `allow_origins=["*"]` und gleichzeitig `allow_credentials=True` konfiguriert. Gemäß CORS‑Spezifikation darf `Access-Control-Allow-Origin` nicht `*` sein, wenn Zugangsdaten erlaubt sind (`Access-Control-Allow-Credentials: true`). Zwar blockieren moderne Browser diese Kombination in der Regel, jedoch kann die Fehlkonfiguration in bestimmten Bereitstellungstopologien (z. B. mit Proxies, die CORS‑Header überschreiben) zu einer gravierenden Sicherheitslücke führen: Eine bösartige Website könnte Anfragen im Namen des angemeldeten Nutzers ausführen, da das Session‑Cookie automatisch mitgesendet wird. Das untergräbt den Same‑Origin‑Schutz und ermöglicht CSRF‑Angriffe sowie potenziellen Session‑Diebstahl.

**Empfehlung:**  
`allow_origins` auf die tatsächliche(n) Frontend‑Domain(s) beschränken, z. B. `["http://localhost:5173"]` für die Entwicklung oder die Produktiv‑URL. Nur so ist die Kombination mit `allow_credentials=True` sicher und standardkonform.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # konkret auflisten
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

---

### 2. Unzureichende Eingabevalidierung für Outfit‑Namen (Mittel)

**Betroffene Datei:** `backend/routers/outfits.py` (erstellen/aktualisieren)  
**Beschreibung:**  
Der Outfit‑Name wird nur auf Maximallänge (100 Zeichen) geprüft und mit `strip()` bereinigt. Es fehlt eine Prüfung auf Steuerzeichen oder potenziell gefährliche HTML‑Entitäten, wie sie für Kleidungsnamen in `routers/clothing.py` existiert. Obwohl das React‑Frontend durch JSX automatisch escaped, sollte die Serverseite einen strikten Eingabefilter anwenden, um Angriffe über andere Clients oder zukünftige Erweiterungen (z. B. E‑Mail‑Benachrichtigungen mit Outfit‑Namen) auszuschließen. Die Acceptance Criteria verlangen explizit das Escapen aller Texteingaben gegen XSS.

**Empfehlung:**  
Die für Kleidungsnamen definierte `validate_clothing_name()` (oder eine äquivalente Helfer‑Funktion) auch auf Outfit‑Namen anwenden.

```python
# in outfits.py nach dem Import von clothing
from .clothing import validate_clothing_name

# vor der Speicherung
name = validate_clothing_name(body.name)
```

---

### 3. Path‑Traversal‑Risiko bei Konto‑Löschung (Mittel)

**Betroffene Datei:** `backend/routers/auth.py` (Endpunkt `DELETE /api/auth/account`)

**Beschreibung:**  
Bei der Löschung aller Bilddateien eines Benutzers wird der Pfad wie folgt zusammengesetzt:

```python
full_path = UPLOAD_DIR / path if not os.path.isabs(path) else path
```

Da derzeit kein Upload‑Endpunkt existiert, können keine bösartigen Pfade in die Datenbank geschrieben werden. Sobald die Bild‑Upload‑Funktion implementiert ist, könnte ein Angreifer jedoch einen absoluten Pfad oder einen relativen Pfad mit `..` in der Datenbank ablegen und so das Löschen beliebiger Dateien im Dateisystem erreichen, wenn die Konto‑Löschung ausgelöst wird.

**Empfehlung:**  
Den Pfad vor der Dateioperation harten:  
- Keine absoluten Pfade zulassen (`os.path.isabs` sollte nicht blind verwendet werden, sondern zu einem Fehler führen).  
- Den normalisierten Pfad unterhalb von `UPLOAD_DIR` erzwingen (z. B. mit `resolve()` und Prüfung auf Präfix).  
- Bereits beim Upload (sobald implementiert) einen bereinigten Dateinamen erzeugen und jegliche Sonderzeichen entfernen.

---

### 4. Scanner‑Ergebnisse

- `bandit` – nicht ausgeführt (`[skipped]`)  
- `semgrep` – nicht ausgeführt (`[skipped]`)

Keine maschinell gefundenen Schwachstellen zusätzlich zu den manuell identifizierten.

---

**Begründung für BLOCKED:**  
Die CORS‑Fehlkonfiguration (`*` mit Credentials) stellt ein hohes Risiko dar, da sie den Session‑Mechanismus untergraben kann. Sie muss vor dem Deployment behoben werden. Die weiteren Funde sind in der aktuellen Implementierung nicht unmittelbar ausnutzbar, erhöhen aber die Sicherheit, wenn sie behoben werden.