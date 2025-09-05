# Development Notes - Jahresdienstplan Generator

## Projekt-Überblick
Clientseitige HTML-Anwendung zur Erstellung von Jahresdienstplänen für 2026 (Berlin) mit Python-Validator und Test-Versionierung.

## Bekannte Probleme (Kritisch)

### 1. "Ende-Jahr-Problem"
**Symptom:** Abteilungen mit hohem Pensum (100%) werden zum Jahresende überproportional eingeteilt.
**Belege:** 
- Test v5: Abteilung mit 100% Pensum ausschließlich zum Jahresende
- Test v4: Abteilungen mit geringeren Pensen eher zum Jahresende

**Ursache:** Aktueller Algorithmus priorisiert Lieblingstage und Bedarf, aber verteilt nicht gleichmäßig über das Jahr.

### 2. Ungleiche zeitliche Verteilung
**Symptom:** Abteilungen werden nicht gleichmäßig über das Jahr verteilt.
**Auswirkung:** Unfaire Arbeitsbelastung, besonders bei hohen Pensen.

### 3. Rotations-Logik unzureichend
**Problem:** Rotation funktioniert nur innerhalb eines Tages, nicht über das gesamte Jahr.
**Folge:** Systematische Bevorzugung bestimmter Abteilungen.

## Aktuelle Algorithmus-Logik

### Zuweisungsprozess (dienstplan_generator.html)
1. **Quotenberechnung:** Largest-Remainder (Hare-Niemeyer) basierend auf Pensen
2. **Tägliche Zuweisung:**
   - Pass 1: Lieblingstage + nicht verhindert + nicht aufeinanderfolgend
   - Pass 2: ohne Lieblingstage + nicht verhindert + nicht aufeinanderfolgend  
   - Pass 3: ohne Lieblingstage + nicht verhindert (Folgetage erlaubt)
3. **Rotation:** Start-Index rotiert nach letzter Zuweisung

### Validierung (validate_plan.py)
- Wochenende/Feiertag-Checks
- Verhinderungs-Checks
- Proportionalität (Ziel vs. Ist)
- Folgetage-Zählung
- Lieblingstage-Treffer
- Monatsweise Auswertung

## Test-Erkenntnisse

### Test v4 (40 Abteilungen)
- **Daten:** Verschiedene Pensen (40%-100%), gemischte Lieblingstage/Verhinderungen
- **Problem:** Ungleiche Verteilung über das Jahr
- **Dateien:** `tests/v4/` (vollständig mit Validierungsberichten)

### Test v5 (Wenige Abteilungen)
- **Daten:** Reduzierte Testdaten
- **Problem:** 100%-Abteilung nur zum Jahresende
- **Dateien:** `tests/v5/` (Validierungsbericht zeigt extreme Ungleichheit)

## Geplante Verbesserungen

### Kurzfristig (TODO.md)
- [ ] scheduler-deterministic-seed: Deterministische Rotation
- [ ] scheduler-min-gap-between-assignments: Mindestabstand konfigurierbar
- [ ] validator-thresholds-exitcodes: Schwellwerte für Abweichungen

### Mittelfristig
- **Zeitliche Fairness:** Monatliche Quoten statt nur Jahresquoten
- **Anti-Folgetag:** Stärkere Logik gegen aufeinanderfolgende Einsätze
- **Gini-Koeffizient:** Fairness-Metrik implementieren

### Langfristig
- **Machine Learning:** Lernen aus optimalen Verteilungen
- **Constraint-Solving:** Mathematische Optimierung statt heuristischer Ansatz

## Technische Details

### Dateistruktur
```
Dienstplan_Tagesdienste/
├── docs/index.html          # Web-App (GitHub Pages)
├── validate_plan.py         # Python-Validator
├── manage_tests.py          # Snapshot-Management
├── tests/                   # Versionierte Tests
│   ├── v4/                  # 40 Abteilungen, Verteilungsprobleme
│   └── v5/                  # Wenige Abteilungen, Ende-Jahr-Problem
└── TODO.md                  # Offene Aufgaben
```

### Wichtige Funktionen
- `generatePlan()`: Haupt-Algorithmus in HTML
- `largest_remainder_targets()`: Quotenberechnung
- `run_validator()`: Automatische Validierung bei Snapshots

## Nächste Schritte

1. **Sofort:** Zeitliche Fairness-Checker implementieren
2. **Kurz:** Monatliche Quoten statt nur Jahresquoten
3. **Mittel:** Erweiterte Testsuite mit automatisierten Szenarien
4. **Lang:** Algorithmus-Überarbeitung mit mathematischer Optimierung

## Kontakt-Info für neue Chats
- Hauptproblem: Ende-Jahr-Problem bei hohen Pensen
- Testdaten: `tests/v4/` und `tests/v5/` zeigen Probleme
- Validator: Bereits implementiert, zeigt Ungleichheiten
- Ziel: Gleichmäßige Verteilung über das gesamte Jahr
