# Algorithm Design - Jahresdienstplan Generator

## Aktuelle Architektur

### 1. Quotenberechnung (Largest-Remainder)
```javascript
// Berechnung der Zielanzahl pro Abteilung
const totalWeight = abteilungen.reduce((sum, a) => sum + a.pensum, 0);
const exactQuota = (a.pensum / totalWeight) * totalWorkingDays;
const zielAnzahl = Math.floor(exactQuota);
const rest = exactQuota - zielAnzahl;

// Verteilung der Rest-Tage nach größtem Rest
const order = [...abteilungen].sort((a, b) => b.rest - a.rest);
```

### 2. Tägliche Zuweisungslogik
```javascript
// Drei-Pass-System
// Pass 1: Lieblingstage + nicht verhindert + nicht aufeinanderfolgend
// Pass 2: ohne Lieblingstage + nicht verhindert + nicht aufeinanderfolgend  
// Pass 3: ohne Lieblingstage + nicht verhindert (Folgetage erlaubt)

const pickFrom = (candidates) => {
    const need = (a) => a.zielAnzahl - a.zugewieseneTage;
    const rotated = [...abteilungen].slice(startIndex).concat([...abteilungen].slice(0, startIndex));
    return rotated.filter(a => candidates.includes(a))
        .sort((a, b) => need(b) - need(a) || b.pensum - a.pensum);
};
```

### 3. Rotation-System
```javascript
// Nach jeder Zuweisung: Start-Index rotiert
const chosenIdx = abteilungen.findIndex(a => a === chosen);
startIndex = (chosenIdx + 1) % abteilungen.length;
```

## Identifizierte Schwachstellen

### 1. Fehlende zeitliche Fairness
**Problem:** Algorithmus arbeitet nur mit Jahresquoten, nicht mit monatlichen Zielen.

**Aktuell:**
- Quoten werden einmal für das ganze Jahr berechnet
- Keine Kontrolle über monatliche Verteilung

**Gewünscht:**
- Monatliche Quoten: `(pensum / 100) * arbeitstage_pro_monat`
- Monatliche Überprüfung der Verteilung

### 2. Unzureichende Anti-Folgetag-Logik
**Problem:** Minimale Logik gegen aufeinanderfolgende Einsätze.

**Aktuell:**
```javascript
const notConsecutive = (a) => !isPreviousWorkingDayIndex(a.lastAssignedIndex, dayIdx);
```

**Gewünscht:**
- Konfigurierbarer Mindestabstand (z.B. 3 Arbeitstage)
- Stärkere Gewichtung gegen Folgetage

### 3. Rotations-Logik zu simpel
**Problem:** Rotation funktioniert nur innerhalb eines Tages.

**Aktuell:**
- Start-Index rotiert nach letzter Zuweisung
- Keine Berücksichtigung der Gesamtverteilung

**Gewünscht:**
- Globale Rotation über das gesamte Jahr
- Berücksichtigung der bisherigen Verteilung

## Geplante Verbesserungen

### 1. Zeitliche Fairness (Hoch)
```javascript
// Monatliche Quoten berechnen
const monthlyQuotas = {};
for (let month = 0; month < 12; month++) {
    const daysInMonth = getWorkingDaysInMonth(month);
    monthlyQuotas[month] = abteilungen.map(a => ({
        nummer: a.nummer,
        ziel: Math.round((a.pensum / 100) * daysInMonth),
        ist: 0
    }));
}

// Monatliche Überprüfung
const monthlyCheck = (abteilung, month) => {
    const quota = monthlyQuotas[month].find(q => q.nummer === abteilung.nummer);
    return abteilung.zugewieseneTage < quota.ziel;
};
```

### 2. Stärkere Anti-Folgetag-Logik (Mittel)
```javascript
// Konfigurierbarer Mindestabstand
const MIN_GAP_DAYS = 3; // Konfigurierbar

const notConsecutive = (a, currentDayIdx) => {
    const lastAssigned = a.lastAssignedIndex;
    if (lastAssigned === -9999) return true; // Erste Zuweisung
    
    const gap = currentDayIdx - lastAssigned;
    return gap >= MIN_GAP_DAYS;
};
```

### 3. Globale Rotation (Mittel)
```javascript
// Rotation basierend auf Gesamtverteilung
const globalRotation = (abteilungen, currentDayIdx) => {
    const totalDays = getTotalWorkingDays();
    const progress = currentDayIdx / totalDays;
    
    // Abteilungen mit geringerem Fortschritt bevorzugen
    return abteilungen.sort((a, b) => {
        const aProgress = a.zugewieseneTage / a.zielAnzahl;
        const bProgress = b.zugewieseneTage / b.zielAnzahl;
        return aProgress - bProgress;
    });
};
```

### 4. Gini-Koeffizient für Fairness (Niedrig)
```javascript
// Fairness-Metrik implementieren
const calculateGiniCoefficient = (assignments) => {
    // Mathematische Berechnung der Ungleichheit
    // Sollte nahe 0 sein für perfekte Gleichverteilung
};
```

## Alternative Ansätze

### 1. Constraint-Solving
- Mathematische Optimierung statt heuristischer Ansatz
- Bibliothek: OR-Tools, CP-SAT Solver
- Vorteil: Garantierte optimale Lösung
- Nachteil: Komplexität, Performance

### 2. Machine Learning
- Lernen aus optimalen Verteilungen
- Reinforcement Learning für Zuweisungsstrategien
- Vorteil: Anpassungsfähigkeit
- Nachteil: Komplexität, Datenbedarf

### 3. Genetische Algorithmen
- Evolutionäre Optimierung der Zuweisungen
- Fitness-Funktion: Fairness + Lieblingstage + Verhinderungen
- Vorteil: Flexible Optimierung
- Nachteil: Performance, Determinismus

## Implementierungsreihenfolge

1. **Sofort:** Zeitliche Fairness-Checker (monatliche Quoten)
2. **Kurz:** Stärkere Anti-Folgetag-Logik
3. **Mittel:** Globale Rotation über das Jahr
4. **Lang:** Gini-Koeffizient und erweiterte Metriken
5. **Zukunft:** Constraint-Solving oder Machine Learning
