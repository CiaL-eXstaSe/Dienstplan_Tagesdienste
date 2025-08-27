# CHANGELOG (Tests)

Hier werden Änderungen an Test-Snapshots dokumentiert.

Format-Vorschlag:

## <Version> – <Datum>
- Motivation/Kommentar
- Relevante Unterschiede in Testdaten/Ergebnissen
- Verwendete App-/Validator-Version (optional)

## v3 – 2025-08-27
- Validator erweitert um monatsweise Auswertung (Ist & Lieblingstage je Monat)
- Validator-Exporte hinzugefügt: CSV (Proportionalität, Folgetage, Favoriten, monatliche Summary) und Markdown-Zusammenfassung
- manage_tests snapshot führt Validator automatisch aus und speichert Report sowie CSV/MD im Versionsordner
- README zu Testversionierung ergänzt

## v2 – 2025-08-27
- Erster Snapshot mit integrierter Validator-Ausführung (validation_report.txt)
- Validierung korrigiert (Wochentagsberechnung, BOM-tolerantes Parsing)

## v1 – 2025-08-27
- Baseline-Snapshot (Testdaten.csv + Jahresdienstplan_2026.csv) ohne automatischen Validatorlauf
