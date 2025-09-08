## Jahresdienstplan 2026 – Clientseitiger Generator und Tests

### Überblick
- Einfache, clientseitige HTML-Anwendung zur Erstellung eines Jahres-Dienstplans für 2026 (Berlin)
- Verteilung nach Pensen (als Gewichte), Berücksichtigung von Lieblingstagen und Verhinderungen
- Export als CSV (Excel-kompatibel)
- Separater Python-Validator zur automatischen Prüfung der Ergebnisse
- Versionierung von Testeingaben/-ausgaben mit Snapshots

### Nutzung der Web-App
1. `docs/index.html` im Browser öffnen (GitHub Pages) oder lokal öffnen
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
Ergebnisse (neu erweitert):
- Konsolenbericht (Regelverstöße, Proportionalität, Folgetage, Lieblingstage)
- Monatsweise Auswertung und zeitlicher Verteilungs-Checker:
  - `validation_monthly_quota_deviation.csv` (Soll/Ist je Monat & Abteilung)
  - `validation_q4_skew.csv` (Ende-Jahr-Skew: Okt–Dez Soll/Ist)
- Weitere Exporte:
  - `validation_proportionality.csv`, `validation_consecutive.csv`, `validation_favorites.csv`
  - `validation_monthly_summary.csv` (Ist & Favoriten je Monat)
  - `validation_summary.md` (Markdown-Zusammenfassung)

### Visualisierung (Heatmaps & Diagramme)
Zum schnellen Erkennen von Ungleichheiten aus den Validator-Reports.

Setup:
```bash
pip install -r requirements.txt
```
Nutzung (z. B. für einen Snapshot in `tests/v6`):
```bash
python3 visualize_reports.py --dir tests/v6
```
Erzeugte Grafiken (im gleichen Ordner):
- `heatmap_monthly_counts.png` (Ist-Einsätze je Monat/Abteilung)
- `heatmap_monthly_quota_diff.png` (Soll/Ist-Diff je Monat/Abteilung)
- `heatmap_weekday_distribution.png` (Wochentagsverteilung je Abteilung)
- `bars_consecutive_by_department.png` (Folgetage je Abteilung)
- `bars_q4_skew.png` (Ende-Jahr-Skew je Abteilung)

### Test-Snapshots (Versionierung)
Automatisches Archivieren der aktuellen Dateien `Testdaten.csv` und `Jahresdienstplan_2026.csv` inkl. Validatorlauf und Exporte.

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
- `Testdaten.csv`, `Jahresdienstplan_2026.csv`, `metadata.json`
- `validation_report.txt` (Konsolen-Output)
- CSV-/MD-Exporte inkl. monatlicher Quoten und Q4-Skew

### Projektstruktur (Auszug)
```
Dienstplan_Tagesdienste/
  ├─ docs/                    # Web-App & Projektdoku
  │   ├─ index.html           # App (für GitHub Pages)
  │   ├─ DEVELOPMENT_NOTES.md
  │   ├─ KNOWN_ISSUES.md
  │   └─ ALGORITHM_DESIGN.md
  ├─ Testdaten.csv            # Aktuelle Eingaben
  ├─ Jahresdienstplan_2026.csv# Aktueller Export
  ├─ validate_plan.py         # Validator (Python)
  ├─ visualize_reports.py     # Visualisierung (Heatmaps/Charts)
  ├─ manage_tests.py          # Snapshots + Validatorlauf
  ├─ tests/                   # Versionierte Tests (mit Reports)
  └─ TODO.md                  # Roadmap/Offene Punkte
```

### Roadmap / Offenes
Siehe `TODO.md` für geplante Verbesserungen (z. B. dynamische Feiertage, XLSX-Export, strengere Validierung, deterministische Rotation, Mindestabstände).