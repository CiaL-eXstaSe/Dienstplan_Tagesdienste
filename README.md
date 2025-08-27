## Jahresdienstplan 2026 – Clientseitiger Generator und Tests

### Überblick
- Einfache, clientseitige HTML-Anwendung zur Erstellung eines Jahres-Dienstplans für 2026 (Berlin)
- Verteilung nach Pensen (als Gewichte), Berücksichtigung von Lieblingstagen und Verhinderungen
- Export als CSV (Excel-kompatibel)
- Separater Python-Validator zur automatischen Prüfung der Ergebnisse
- Versionierung von Testeingaben/-ausgaben mit Snapshots

### Nutzung der Web-App
1. `dienstplan_generator.html` im Browser öffnen (Doppelklick genügt)
2. Abteilungsdaten im Format eingeben:
```
<Nummer>; <Pensum in %>; <Lieblingstage>; <Verhinderungen>
1; 50%; Montag, Mittwoch; 01.02.2026-15.02.2026, 03.03.2026
2; 100%; Freitag; 10.03.2026
3; 75%; Dienstag, Mittwoch; 01.12.2026-31.12.2026
```
3. „Dienstplan generieren“ klicken
4. „Als Excel exportieren“ erstellt `Jahresdienstplan_2026.csv`

Hinweise:
- Es werden nur Wochentage geplant; Berliner Feiertage 2026 sind berücksichtigt (inkl. 08.03.)
- Pensen werden proportional auf Arbeitstage verteilt (Largest-Remainder)

### Python-Validator (optional)
Prüft den erzeugten Plan gegen Regeln und erstellt Berichte.

Voraussetzungen:
- Python 3

Ausführung:
```bash
python3 validate_plan.py /Pfad/zu/Jahresdienstplan_2026.csv /Pfad/zu/Testdaten.csv --out-dir ./reports
```
Ergebnisse:
- Konsolenbericht (Regelverstöße, Proportionalität, Folgetage, Lieblingstage)
- In `--out-dir`: CSVs und `validation_summary.md` (monatsweise Übersicht)

### Test-Snapshots (Versionierung)
Automatisches Archivieren der aktuell im Hauptordner liegenden Dateien `Testdaten.csv` und `Jahresdienstplan_2026.csv` inkl. Validatorlauf.

Snapshot erstellen:
```bash
python3 manage_tests.py snapshot --version v1 --note "Kommentar zur Version"
# oder ohne Namen (Zeitstempel):
python3 manage_tests.py snapshot
```
Versionen auflisten:
```bash
python3 manage_tests.py list
```
Ergebnis pro Version (z. B. `tests/v1/`):
- `Testdaten.csv`
- `Jahresdienstplan_2026.csv`
- `metadata.json` (Zeitstempel/Kommentar)
- `validation_report.txt`
- CSV-Exporte und `validation_summary.md`

### Projektstruktur (Auszug)
```
Dienstplan_Tagesdienste/
  ├─ dienstplan_generator.html   # Web-App (HTML/CSS/JS)
  ├─ Testdaten.csv               # Aktuelle Eingaben
  ├─ Jahresdienstplan_2026.csv   # Aktueller Export
  ├─ validate_plan.py            # Validator (Python)
  ├─ manage_tests.py             # Snapshots + Validatorlauf
  ├─ tests/                      # Versionierte Tests
  │   ├─ README.md, CHANGELOG.md
  │   └─ v*/ (Snapshots mit Reports)
  └─ TODO.md                     # Roadmap/Offene Punkte
```

### Roadmap / Offenes
Siehe `TODO.md` für geplante Verbesserungen (z. B. dynamische Feiertage, XLSX-Export, strengere Validierung, deterministische Rotation, Mindestabstände).