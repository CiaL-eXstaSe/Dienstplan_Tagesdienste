# Known Issues - Jahresdienstplan Generator

## Kritische Probleme

### 1. Ende-Jahr-Problem (Hoch)
**Beschreibung:** Abteilungen mit hohem Pensum (100%) werden zum Jahresende überproportional eingeteilt.

**Belege:**
- Test v5: Abteilung mit 100% Pensum ausschließlich in den letzten Monaten
- Test v4: Abteilungen mit geringeren Pensen werden eher zum Jahresende eingeteilt

**Auswirkung:** Unfaire Arbeitsbelastung, besonders bei Vollzeit-Abteilungen

**Status:** Nicht behoben

### 2. Ungleiche zeitliche Verteilung (Hoch)
**Beschreibung:** Abteilungen werden nicht gleichmäßig über das Jahr verteilt.

**Symptome:**
- Konzentration von Einsätzen in bestimmten Monaten
- Lange Pausen zwischen Einsätzen
- Unvorhersehbare Arbeitsbelastung

**Status:** Nicht behoben

### 3. Rotations-Logik unzureichend (Mittel)
**Beschreibung:** Rotation funktioniert nur innerhalb eines Tages, nicht über das gesamte Jahr.

**Auswirkung:** Systematische Bevorzugung bestimmter Abteilungen

**Status:** Teilweise behoben (tägliche Rotation implementiert)

## Mittlere Probleme

### 4. Fehlende monatliche Quoten (Mittel)
**Beschreibung:** Algorithmus arbeitet nur mit Jahresquoten, nicht mit monatlichen Zielen.

**Auswirkung:** Monatliche Ungleichheiten werden nicht verhindert

**Status:** Geplant (TODO.md)

### 5. Anti-Folgetag-Logik schwach (Niedrig)
**Beschreibung:** Minimale Logik gegen aufeinanderfolgende Einsätze.

**Auswirkung:** Abteilungen können mehrere Tage hintereinander eingeteilt werden

**Status:** Teilweise implementiert

## Geringe Probleme

### 6. Fehlende Fairness-Metriken (Niedrig)
**Beschreibung:** Keine quantitativen Maßzahlen für Verteilungsgerechtigkeit.

**Status:** Geplant

### 7. Deterministische vs. zufällige Rotation (Niedrig)
**Beschreibung:** Rotation ist nicht vollständig deterministisch reproduzierbar.

**Status:** Geplant (TODO.md)

## Test-Cases für Reproduktion

### Ende-Jahr-Problem reproduzieren:
```bash
# Test v5 verwenden
python3 manage_tests.py snapshot --version v5-repro --note "Ende-Jahr-Problem"
python3 validate_plan.py tests/v5-repro/Jahresdienstplan_2026.csv tests/v5-repro/Testdaten.csv
```

### Ungleiche Verteilung testen:
```bash
# Test v4 verwenden  
python3 manage_tests.py snapshot --version v4-repro --note "Ungleiche Verteilung"
python3 validate_plan.py tests/v4-repro/Jahresdienstplan_2026.csv tests/v4-repro/Testdaten.csv
```

## Workarounds

### Für Ende-Jahr-Problem:
- Manuelle Nachbearbeitung der letzten Monate
- Mehrfache Generierung und Auswahl des besten Ergebnisses

### Für ungleiche Verteilung:
- Monatliche Überprüfung der Validierungsberichte
- Anpassung der Testdaten (Verhinderungen, Lieblingstage)

## Prioritäten für Fixes

1. **Sofort:** Zeitliche Fairness-Checker implementieren
2. **Kurz:** Monatliche Quoten statt nur Jahresquoten  
3. **Mittel:** Stärkere Anti-Folgetag-Logik
4. **Lang:** Algorithmus-Überarbeitung mit mathematischer Optimierung

