#!/usr/bin/env python3
import csv
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Tuple
import sys


# Python date.weekday(): Montag=0 .. Sonntag=6
GERMAN_WEEKDAYS = [
    "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"
]


def parse_date_de(d: str) -> date:
    # dd.mm.yyyy
    day, month, year = d.strip().split(".")
    return date(int(year), int(month), int(day))


def format_date_de(d: date) -> str:
    return f"{d.day:02d}.{d.month:02d}.{d.year}"


def berlin_holidays_2026() -> List[date]:
    # Minimal feste Liste passend zur Web-App
    fixed = [
        date(2026, 1, 1),   # Neujahr
        date(2026, 3, 8),   # Internationaler Frauentag (Berlin)
        date(2026, 4, 3),   # Karfreitag
        date(2026, 4, 6),   # Ostermontag
        date(2026, 5, 1),   # Tag der Arbeit
        date(2026, 5, 14),  # Christi Himmelfahrt
        date(2026, 5, 25),  # Pfingstmontag
        date(2026, 10, 3),  # Tag der Deutschen Einheit
        date(2026, 12, 25), # 1. Weihnachtstag
        date(2026, 12, 26), # 2. Weihnachtstag
    ]
    return fixed


def is_weekday(d: date) -> bool:
    return d.weekday() < 5  # Mon-Fri = 0..4


@dataclass
class Verhinderung:
    type: str  # 'single' or 'range'
    start: date = None
    end: date = None


@dataclass
class Abteilung:
    nummer: int
    pensum: float
    lieblingstage: List[str]
    verhinderungen: List[Verhinderung]


def parse_abteilungen_csv(path: str) -> List[Abteilung]:
    abteilungen: List[Abteilung] = []
    with open(path, newline='', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip().lstrip('\ufeff')  # remove potential BOM
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) < 4:
                # toleranter: fehlende Felder auffüllen
                parts += [""] * (4 - len(parts))

            try:
                nummer = int(parts[0])
            except Exception:
                # Überschrift oder defekte Zeile überspringen (z. B. 'Abteilung', 'Nummer', ...)
                continue

            pensum_str = parts[1].replace('%', '').strip()
            pensum = float(pensum_str) if pensum_str else 0.0
            lieblingstage = [t.strip() for t in parts[2].split(',') if t.strip()]

            verhinderungen: List[Verhinderung] = []
            if parts[3].strip():
                for token in [t.strip() for t in parts[3].split(',') if t.strip()]:
                    if '-' in token:
                        start_s, end_s = [x.strip() for x in token.split('-', 1)]
                        verhinderungen.append(Verhinderung('range', parse_date_de(start_s), parse_date_de(end_s)))
                    else:
                        verhinderungen.append(Verhinderung('single', parse_date_de(token), parse_date_de(token)))

            abteilungen.append(Abteilung(nummer, pensum, lieblingstage, verhinderungen))
    return abteilungen


def parse_plan_csv(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for r in reader:
            # Normalize keys
            rows.append({
                'Datum': r.get('Datum', '').strip(),
                'Wochentag': r.get('Wochentag', '').strip(),
                'Abteilungsnummer': r.get('Abteilungsnummer', '').strip(),
            })
    return rows


def is_verhindert(a: Abteilung, d: date) -> bool:
    for v in a.verhinderungen:
        if v.type == 'single':
            if v.start == d:
                return True
        else:
            if v.start <= d <= v.end:
                return True
    return False


def largest_remainder_targets(abteilungen: List[Abteilung], total_days: int) -> Dict[int, int]:
    total_weight = sum(a.pensum for a in abteilungen)
    if total_weight <= 0:
        return {a.nummer: 0 for a in abteilungen}
    quotas = []
    for a in abteilungen:
        exact = (a.pensum / total_weight) * total_days
        floor_v = int(exact)
        quotas.append((a.nummer, floor_v, exact - floor_v, a.pensum))
    assigned = sum(q[1] for q in quotas)
    remaining = total_days - assigned
    quotas.sort(key=lambda x: (x[2], x[3], -x[0]), reverse=True)
    targets = {num: base for (num, base, _, _) in quotas}
    for i in range(max(0, remaining)):
        num = quotas[i % len(quotas)][0]
        targets[num] += 1
    return targets


def main(plan_csv: str, testdaten_csv: str) -> int:
    holidays = set(berlin_holidays_2026())
    abteilungen = parse_abteilungen_csv(testdaten_csv)
    plan = parse_plan_csv(plan_csv)

    # Indexe
    abt_by_num: Dict[int, Abteilung] = {a.nummer: a for a in abteilungen}

    # 1) Basischecks: Wochenende/Feiertag, Wochentag stimmt
    violations: List[str] = []
    parsed_plan: List[Tuple[date, str, int]] = []
    for row in plan:
        try:
            d = parse_date_de(row['Datum'])
        except Exception:
            violations.append(f"Ungültiges Datumsformat: {row['Datum']}")
            continue
        weekday_name = GERMAN_WEEKDAYS[d.weekday()]
        if row['Wochentag'] and row['Wochentag'] != weekday_name:
            violations.append(f"Wochentag stimmt nicht: {row['Datum']} (CSV: {row['Wochentag']}, berechnet: {weekday_name})")
        if not is_weekday(d):
            violations.append(f"Wochenend-Zuweisung gefunden: {row['Datum']}")
        if d in holidays:
            violations.append(f"Feiertags-Zuweisung gefunden: {row['Datum']}")
        try:
            abt = int(row['Abteilungsnummer'])
        except Exception:
            violations.append(f"Ungültige Abteilungsnummer in Plan: {row['Abteilungsnummer']}")
            continue
        parsed_plan.append((d, weekday_name, abt))

    parsed_plan.sort(key=lambda x: x[0])

    # 2) Verhinderungen
    for d, _, abt_num in parsed_plan:
        a = abt_by_num.get(abt_num)
        if a and is_verhindert(a, d):
            violations.append(f"Abteilung {abt_num} verhindert am {format_date_de(d)}")

    # 3) Proportionalität (Largest Remainder Ziel)
    total_days = len(parsed_plan)
    targets = largest_remainder_targets(abteilungen, total_days)
    counts: Dict[int, int] = {}
    favorite_hits: Dict[int, int] = {}
    for d, weekday_name, abt_num in parsed_plan:
        counts[abt_num] = counts.get(abt_num, 0) + 1
        a = abt_by_num.get(abt_num)
        if a and weekday_name in a.lieblingstage:
            favorite_hits[abt_num] = favorite_hits.get(abt_num, 0) + 1

    deviations: List[Tuple[int, int, int, int]] = []  # (num, ziel, ist, diff)
    for a in abteilungen:
        ist = counts.get(a.nummer, 0)
        ziel = targets.get(a.nummer, 0)
        deviations.append((a.nummer, ziel, ist, ist - ziel))
    deviations.sort(key=lambda x: abs(x[3]), reverse=True)

    # 4) Folgetage zählen (über Workingday-Sequenz)
    consecutive_counts: Dict[int, int] = {}
    for i in range(1, len(parsed_plan)):
        prev_d, _, prev_abt = parsed_plan[i - 1]
        cur_d, _, cur_abt = parsed_plan[i]
        if cur_abt == prev_abt:
            # Plan listet nur Arbeitstage; benachbarte Zeilen sind konsekutive Arbeitstage
            consecutive_counts[cur_abt] = consecutive_counts.get(cur_abt, 0) + 1

    # Bericht
    print("== Validierungsbericht ==")
    print(f"Plan-Tage: {total_days}")
    print(f"Abteilungen: {len(abteilungen)}")
    print()

    if violations:
        print("Regelverstöße:")
        for v in violations:
            print(f"- {v}")
    else:
        print("Keine harten Regelverstöße (Wochenende/Feiertag/Verhinderung/Wochentag) gefunden.")
    print()

    print("Proportionalität (Ziel vs. Ist, diff=Ist-Ziel):")
    for num, ziel, ist, diff in deviations:
        print(f"- Abt {num}: Ziel {ziel}, Ist {ist}, Diff {diff:+d}")
    print()

    print("Folgetage je Abteilung (Anzahl benachbarter Zuweisungen):")
    for a in abteilungen:
        print(f"- Abt {a.nummer}: {consecutive_counts.get(a.nummer, 0)}")
    print()

    print("Lieblingstage-Treffer:")
    for a in abteilungen:
        print(f"- Abt {a.nummer}: {favorite_hits.get(a.nummer, 0)}/{counts.get(a.nummer, 0)}")

    # Rückgabecode: 0 wenn keine harten Regelverstöße
    return 0 if not violations else 2


if __name__ == "__main__":
    # Standardpfade
    plan_path = "Jahresdienstplan_2026.csv"
    testdaten_path = "Testdaten.csv"
    if len(sys.argv) >= 2:
        plan_path = sys.argv[1]
    if len(sys.argv) >= 3:
        testdaten_path = sys.argv[2]
    sys.exit(main(plan_path, testdaten_path))


