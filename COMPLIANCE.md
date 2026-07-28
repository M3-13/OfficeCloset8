VERDICT: BLOCKED

## Rechtliche Prüfung des Gesamtprodukts „OfficeCloset8“

### 1. DSGVO (Datenschutz)

Die Anwendung verarbeitet E-Mail-Adresse, Passwort-Hash, hochgeladene Bilder (ggf. mit Metadaten) sowie Session-Cookies. Für die Teilnahme am Dienst ist die Verarbeitung erforderlich (Art. 6 Abs. 1 lit. b DSGVO). Gleichwohl bestehen gravierende, rechtswidrige Lücken:

*   **Keine Datenschutzerklärung / kein Impressum** (KRITISCH)
    *   **Befund:** Im gesamten Frontend sind weder Links noch Seiten für Datenschutzbestimmungen oder ein Impressum vorhanden. Die Verarbeitung personenbezogener Daten ohne transparente Information des Nutzers ist rechtswidrig.
    *   **Abhilfe:**  
        *   Erstelle eine statische Seite `frontend/public/datenschutz.html` mit vollständigen Informationen gem. Art. 13 DSGVO (u.a. Verantwortlicher, Zwecke, Rechtsgrundlage, Löschfristen, Betroffenenrechte).
        *   Ergänze die `RegisterPage.tsx` und die Login-Seite um einen gut sichtbaren Link zu dieser Seite (Text: „Datenschutzerklärung“), z. B. unter dem Formular.
        *   Stelle das Impressum bereit (falls kein rein privater Dienst vorliegt).

*   **Fehlende verbindliche Privacy-Checkbox bei der Registrierung** (HOCH)
    *   **Befund:** Die bindende Teamkonvention verlangt eine `privacy_accepted`-Checkbox, die vor Absendung der Registrierung bestätigt werden muss. Diese fehlt vollständig.
    *   **Abhilfe:**  
        *   Erweitere das Pydantic-Modell `UserCreate` in `backend/schemas.py` um das Feld `privacy_accepted: bool = Field(alias="privacyAccepted")`.
        *   Füge in `backend/routers/auth.py` in der `register`-Funktion eine Validierung hinzu: `if not body.privacy_accepted: raise HTTPException(status_code=400, detail="Bitte Datenschutzerklärung akzeptieren.")`
        *   Ergänze im Frontend (`RegisterPage.tsx`) eine Checkbox mit Link zur Datenschutzerklärung. Blockiere den Submit-Button, wenn sie nicht gesetzt ist.

*   **Bild-Upload & Kleidungsstück-Anlage nicht implementiert** (KRITISCH – BLOCKER)
    *   **Befund:** Die gesamte Backend-Logik für das Anlegen von Kleidungsstücken mit Bild ist nur als Platzhalter (`upload.py` mit `raise NotImplementedError`) vorhanden. Es gibt keinen POST-Endpunkt in `routers/clothing.py`. Die vom Sprint spezifizierten Sicherheits- und Datenschutzmaßnahmen (EXIF-Stripping, Magic-Byte-Validierung, Größengrenze, Path-Traversal-Schutz) sind überhaupt nicht realisiert. Das Produkt kann seine Kernfunktion nicht erfüllen.
    *   **Abhilfe:**  
        *   Implementiere in `backend/upload.py` die Funktionen `save_upload`, `validate_image` und `strip_exif` gemäß den Acceptance Criteria:
            *   **Validierung:** Maximal 5 MB (Content-Length und Dateigröße prüfen), erlaubte MIME‑Typen (image/jpeg, image/png, image/webp) anhand der Magic Bytes prüfen.
            *   **Dateiname:** Bereinigung via `werkzeug.utils.secure_filename` oder eigenem Regex (Steuerzeichen, Umlaute, Pfadtrenner entfernen). Zielpfad außerhalb des Web‑Roots.
            *   **EXIF‑Stripping:** Vor dem Speichern mittels `PIL.Image.open` und `.save()` Metadaten entfernen.
        *   Erstelle in `routers/clothing.py` einen vollständigen Router mit `POST /` (für Upload), `GET /`, `DELETE /{item_id}`.
        *   Stelle sicher, dass die Route in `backend/main.py` mittels `app.include_router` bereits eingebunden ist (ist sie), aber nun auch tatsächlich funktioniert.

*   **Personenbezogene Daten in Logs** (HOCH)
    *   **Befund:**  
        *   In `backend/main.py` wird bei unbehandelten Ausnahmen `logger.exception("Unhandled exception: %s", exc)` geloggt. Der Exception-String kann sensible Inhalte (z. B. die E-Mail aus einem Validierungsfehler) enthalten. Dies verstößt gegen das Verbot, personenbezogene Daten in Logs zu schreiben.
        *   Der Server (z. B. uvicorn) loggt standardmäßig IP-Adressen. Dies ist nicht unterbunden.
    *   **Abhilfe:**  
        *   Ändere den globalen Exception-Handler so, dass er nur `exc.__class__.__name__` oder eine eindeutige Fehler-ID loggt, niemals den Exception-String. Beispiel: `logger.exception("Unhandled exception (%s) for request %s", type(exc).__name__, request.headers.get("x-request-id"))`
        *   Stelle in der Deployment-Konfiguration (z.B. docker-compose oder Startscript) sicher, dass der Access‑Log von uvicorn deaktiviert wird (`UVICORN_ACCESS_LOG=False` oder `--no-access-log`), oder konfiguriere einen angepassten Logger ohne IP. Ergänze dazu die `README.md` oder die `RUN.json`.

*   **Session- und Datenbereinigung** (MITTEL)
    *   **Befund:** Sessions werden bei `DELETE /account` und beim Logout gelöscht, aber abgelaufene Sessions (Cookie max\_age 30 Tage) verbleiben dauerhaft in der Datenbank. Das widerspricht dem Grundsatz der Speicherbegrenzung.
    *   **Abhilfe:** Füge eine periodische Bereinigung hinzu, z. B. einen `@repeat_every(seconds=60*60*24)`-Task in der FastAPI-App, der Sessions mit `created_at` älter als 30 Tage löscht. Alternativ kann bei jedem Login eine Aufräumfunktion aufgerufen werden.

### 2. Mandatory Texts & UI

Neben der ohnehin erforderlichen Datenschutzerklärung sind folgende Punkte offen:

*   **Cookie‑Information (NIEDRIG)**
    *   Es wird ausschließlich ein technisch notwendiges Session‑Cookie gesetzt, das keine Einwilligung erfordert. Dennoch muss die Datenschutzerklärung einen Hinweis auf dieses Cookie enthalten. Da diese Seite noch fehlt, ist das mit der oben geforderten Erstellung der Datenschutzerklärung abzudecken.

### 3. Accessibility (Barrierefreiheit)

*   **Grundlegende Mängel** (HOCH)
    *   **Befund:** Die öffentliche Web‑UI muss gemäß WCAG 2.1 AA / BITV 2.0 zugänglich sein. Derzeit fehlen:
        *   Skiplinks für Screenreader.
        *   Korrekte, programmatisch verknüpfte Labels für alle Formulareingaben (aktuell nur visuell über `<span class="field-label">`; ein `aria-labelledby` oder `<label for="...">` wäre nötig).
        *   Ausreichender Mindestkontrast (z. B. `color-fg-muted` auf `bg-elevated`)? Der festgelegte Farbwert `#A0988C` auf `#141414` erfüllt möglicherweise nicht den Kontrast von 4.5:1. Dies ist zu prüfen.
        *   Fehlermeldungen sind nicht mit den Feldern assoziiert, um die Screenreader-Nutzung zu unterstützen.
    *   **Abhilfe:**  
        *   In `frontend/src/components/` ein `<SkipLink>`-Component einführen und im `Layout.tsx` rendern.
        *   In allen Formularen (`LoginPage.tsx`, `RegisterPage.tsx`, `OutfitCreatorPage.tsx`) konsequent das `<label>`-Element mit dem `for`-Attribut verwenden oder mit `aria-labelledby` verknüpfen. Beispiel: `<label htmlFor="email" className="field-label">E-Mail</label>` und `id="email"` auf dem Input.
        *   Fehlermeldungen mit `aria-describedby` an das entsprechende Eingabefeld binden.
        *   Die Farbkontraste prüfen und ggf. anpassen. Für normalen Text muss das Verhältnis mindestens 4.5:1 sein; für den aktuellen Grauwert auf dem Hintergrund könnte ein dunklerer Text verwendet werden. Ein Accessibility-Tool (z. B. axe DevTools) sollte final validieren.

### 4. EU Cyber Resilience Act (CRA)

*   **Vorbemerkung:** Die Verordnung ist noch nicht vollständig anwendbar, aber Security by Design ist ohnehin Bestandteil der DSGVO. Die vorhandenen Sicherheitsvorkehrungen (bcrypt, sichere Cookies) sind gut.
*   **Empfehlung (NIEDRIG):** In einer `SECURITY.md` sollten die grundlegenden Sicherheitsannahmen und das geplante Patch‑Management dokumentiert werden. Dies ist kein Blocker, aber zur Vorbereitung sinnvoll.

### 5. EU AI Act

*   **Entfällt.** Es sind keine KI‑basierten Features erkennbar.

### Gesamtbewertung

Das Produkt ist in seinem aktuellen Zustand **nicht marktreif**. Die grundlegende Funktion „Kleidungsstück mit Bild anlegen“ ist nicht implementiert, sodass die zentralen Datenschutz- und Sicherheitsanforderungen ungeprüft und unerfüllt bleiben. Parallel dazu fehlen essentielle Pflichttexte (Datenschutzerklärung, Impressum) für die rechtmäßige Verarbeitung personenbezogener Daten. Diese Mängel sind nicht durch kleine Anpassungen heilbar, sondern erfordern substantielle Nacharbeit. Daher **BLOCKED**.