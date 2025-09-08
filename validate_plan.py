#!/usr/bin/env python3
import csv
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Tuple, Optional
import sys
import os
import argparse

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


def working_days_by_month_2026() -> Dict[int, List[date]]:
	"""Gibt für 2026 eine Map {1..12: [arbeitstage im Monat]} zurück."""
	holidays = set(berlin_holidays_2026())
	monthly: Dict[int, List[date]] = {m: [] for m in range(1, 13)}
	for month in range(1, 13):
		# Tage im Monat
		if month == 12:
			days_in_month = 31
		else:
			days_in_month = (date(2026, month + 1, 1) - date(2026, month, 1)).days
		for day in range(1, days_in_month + 1):
			d = date(2026, month, day)
			if is_weekday(d) and d not in holidays:
				monthly[month].append(d)
	return monthly


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


def write_csv(path: str, header: List[str], rows: List[List]):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, 'w', newline='', encoding='utf-8') as f:
		w = csv.writer(f, delimiter=';')
		w.writerow(header)
		for r in rows:
			w.writerow(r)


def write_markdown_summary(path: str, total_days: int, violations: List[str], deviations: List[Tuple[int,int,int,int]], consecutive_counts: Dict[int,int], favorite_hits: Dict[int,int], counts: Dict[int,int], monthly: Dict[str, Dict[int, Dict[str,int]]], monthly_quota_dev: List[List], q4_skew: List[List]):
	lines: List[str] = []
	lines.append('# Validierungsbericht')
	lines.append('')
	lines.append(f'- Plan-Tage: {total_days}')
	lines.append('')
	lines.append('## Regelverstöße')
	if not violations:
		lines.append('Keine harten Regelverstöße gefunden.')
	else:
		for v in violations:
			lines.append(f'- {v}')
	lines.append('')
	lines.append('## Proportionalität (Ziel vs. Ist)')
	lines.append('Nummer | Ziel | Ist | Diff')
	lines.append('---|---:|---:|---:')
	for num, ziel, ist, diff in deviations:
		lines.append(f'{num} | {ziel} | {ist} | {diff:+d}')
	lines.append('')
	lines.append('## Folgetage je Abteilung')
	lines.append('Nummer | Folgetage')
	lines.append('---|---:')
	for num in sorted(counts.keys()):
		lines.append(f'{num} | {consecutive_counts.get(num, 0)}')
	lines.append('')
	lines.append('## Lieblingstage-Treffer')
	lines.append('Nummer | Treffer | Gesamt')
	lines.append('---|---:|---:')
	for num in sorted(counts.keys()):
		lines.append(f'{num} | {favorite_hits.get(num, 0)} | {counts.get(num, 0)}')
	lines.append('')
	lines.append('## Monatsweise Auswertung (Ist & Lieblings-Treffer)')
	lines.append('Monat | Abteilung | Ist | Favoriten')
	lines.append('---|---:|---:|---:')
	for month in sorted(monthly.keys()):
		for num in sorted(monthly[month].keys()):
			m = monthly[month][num]
			lines.append(f'{month} | {num} | {m.get("ist",0)} | {m.get("fav",0)}')
	lines.append('')
	lines.append('## Monatsweise Soll/Ist-Quoten-Abweichung')
	lines.append('Monat | Abteilung | Soll | Ist | Diff')
	lines.append('---|---:|---:|---:|---:')
	for row in monthly_quota_dev:
		lines.append(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]:+d}')
	lines.append('')
	lines.append('## Q4-Skew (Ende-Jahr-Verteilung)')
	lines.append('Abteilung | Q4 Ist | Q4 Soll | Diff')
	lines.append('---|---:|---:|---:')
	for row in q4_skew:
		lines.append(f'{row[0]} | {row[1]} | {row[2]} | {row[3]:+d}')
	with open(path, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines))


def main(plan_csv: str, testdaten_csv: str, out_dir: Optional[str] = None) -> int:
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

	# 5) Monatsweise Auswertung (Ist & Favoriten)
	monthly: Dict[str, Dict[int, Dict[str, int]]] = {}
	for d, weekday_name, abt_num in parsed_plan:
		month_key = f"{d.year}-{d.month:02d}"
		monthly.setdefault(month_key, {})
		monthly[month_key].setdefault(abt_num, {"ist": 0, "fav": 0})
		monthly[month_key][abt_num]["ist"] += 1
		a = abt_by_num.get(abt_num)
		if a and weekday_name in a.lieblingstage:
			monthly[month_key][abt_num]["fav"] += 1

	# 6) Monatsweise Soll/Ist-Quoten (Checker)
	monthly_days = working_days_by_month_2026()
	monthly_quota_dev_rows: List[List] = []  # [Monat, Abteilung, Soll, Ist, Diff]
	for month in range(1, 13):
		mon_key = f"2026-{month:02d}"
		days_in_month = len(monthly_days[month])
		mon_targets = largest_remainder_targets(abteilungen, days_in_month)
		for a in abteilungen:
			ist = monthly.get(mon_key, {}).get(a.nummer, {}).get('ist', 0)
			soll = mon_targets.get(a.nummer, 0)
			diff = ist - soll
			monthly_quota_dev_rows.append([mon_key, a.nummer, soll, ist, diff])

	# 7) Q4-Skew (Ende-Jahr-Verteilung)
	q4_months = {10, 11, 12}
	q4_total_days = sum(len(monthly_days[m]) for m in q4_months)
	q4_targets = largest_remainder_targets(abteilungen, q4_total_days)
	q4_counts: Dict[int, int] = {}
	for d, _, abt_num in parsed_plan:
		if d.month in q4_months:
			q4_counts[abt_num] = q4_counts.get(abt_num, 0) + 1
	q4_skew_rows: List[List] = []  # [Abteilung, Q4 Ist, Q4 Soll, Diff]
	for a in abteilungen:
		ist = q4_counts.get(a.nummer, 0)
		soll = q4_targets.get(a.nummer, 0)
		diff = ist - soll
		q4_skew_rows.append([a.nummer, ist, soll, diff])
	# Sortiere zur besseren Sichtbarkeit nach größter Abweichung
	q4_skew_rows.sort(key=lambda r: abs(r[3]), reverse=True)

	# Bericht (stdout)
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
	print()

	print("Monatliche Soll/Ist-Abweichungen (Top 10 nach |Diff|):")
	for row in sorted(monthly_quota_dev_rows, key=lambda r: abs(r[4]), reverse=True)[:10]:
		print(f"- {row[0]} Abt {row[1]}: Soll {row[2]}, Ist {row[3]}, Diff {row[4]:+d}")
	print()

	print("Q4-Skew (Top 10 nach |Diff|):")
	for row in q4_skew_rows[:10]:
		print(f"- Abt {row[0]}: Q4 Soll {row[2]}, Ist {row[1]}, Diff {row[3]:+d}")

	# Exporte
	if out_dir:
		os.makedirs(out_dir, exist_ok=True)
		# Proportionalität CSV
		write_csv(os.path.join(out_dir, 'validation_proportionality.csv'), ['Abteilung', 'Ziel', 'Ist', 'Diff'], [[n, z, i, d] for (n, z, i, d) in deviations])
		# Folgetage CSV
		write_csv(os.path.join(out_dir, 'validation_consecutive.csv'), ['Abteilung', 'Folgetage'], [[a.nummer, consecutive_counts.get(a.nummer, 0)] for a in abteilungen])
		# Favoriten CSV
		write_csv(os.path.join(out_dir, 'validation_favorites.csv'), ['Abteilung', 'Treffer', 'Gesamt'], [[a.nummer, favorite_hits.get(a.nummer, 0), counts.get(a.nummer, 0)] for a in abteilungen])
		# Monatsweise CSV (Ist & Favoriten)
		monthly_rows: List[List] = []
		for month in sorted(monthly.keys()):
			for num in sorted(monthly[month].keys()):
				m = monthly[month][num]
				monthly_rows.append([month, num, m.get('ist', 0), m.get('fav', 0)])
		write_csv(os.path.join(out_dir, 'validation_monthly_summary.csv'), ['Monat', 'Abteilung', 'Ist', 'Favoriten'], monthly_rows)
		# Monatsweise Soll/Ist-Quoten CSV
		write_csv(os.path.join(out_dir, 'validation_monthly_quota_deviation.csv'), ['Monat', 'Abteilung', 'Soll', 'Ist', 'Diff'], monthly_quota_dev_rows)
		# Q4-Skew CSV
		write_csv(os.path.join(out_dir, 'validation_q4_skew.csv'), ['Abteilung', 'Q4_Ist', 'Q4_Soll', 'Diff'], q4_skew_rows)
		# Markdown Summary
		write_markdown_summary(os.path.join(out_dir, 'validation_summary.md'), total_days, violations, deviations, consecutive_counts, favorite_hits, counts, monthly, monthly_quota_dev_rows, q4_skew_rows)

	# Rückgabecode: 0 wenn keine harten Regelverstöße
	return 0 if not violations else 2


if __name__ == "__main__":
	# CLI
	parser = argparse.ArgumentParser(description='Validiere Dienstplan-CSV gegen Regeln')
	parser.add_argument('plan_csv', help='Pfad zur Plan-CSV (Jahresdienstplan_2026.csv)')
	parser.add_argument('testdaten_csv', help='Pfad zu Testdaten.csv')
	parser.add_argument('--out-dir', help='Ordner für CSV/Markdown-Exporte', default=None)
	args = parser.parse_args()
	sys.exit(main(args.plan_csv, args.testdaten_csv, args.out_dir))


