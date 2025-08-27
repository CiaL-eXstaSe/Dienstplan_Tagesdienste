# TODO

Diese Datei hält die aktuellen Aufgaben rund um den Jahresdienstplan fest. Bitte hier ändern/ergänzen; ich halte sie mit meinem internen Aufgabenstand synchron.

## Offen / Geplant
- [ ] validator-monthly-breakdown: Monatsweise Auswertung (Quoten, Lieblingstage, Folgetage)
- [ ] validator-export-reports: Validierungsbericht zusätzlich als CSV/Markdown speichern
- [ ] validator-thresholds-exitcodes: Schwellwerte/Regeln und Exit-Codes bei Abweichungen
- [ ] scheduler-deterministic-seed: Deterministische Rotation per konfigurierbarem Seed
- [ ] scheduler-min-gap-between-assignments: Mindestabstand N Arbeitstage konfigurierbar
- [ ] holidays-dynamic-berlin: Berliner Feiertage dynamisch für ein Jahr berechnen
- [ ] input-validation-enhanced: Strengere Eingabevalidierung (Datum, Wochentage, Zeiträume)
- [ ] export-xlsx-support: Echten XLSX-Export zusätzlich zum CSV
- [ ] favorites-weighting-score: Optionale, score-basierte Gewichtung für Lieblingstage
- [ ] testing-suite-core: Unit-/Integrationstests (Parser, Quoten, Zuweiser)

## Erledigt
- [x] tests-versioning: Versionierung der Tests (Ordner, Schema, Changelog)
- [x] snapshot-run-validator: Validator beim Snapshot ausführen und Bericht speichern

Hinweis:
- Snapshots: `python3 manage_tests.py snapshot --version <name> --note "Kommentar"`
- Versionen: `python3 manage_tests.py list`
