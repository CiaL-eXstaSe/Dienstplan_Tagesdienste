#!/usr/bin/env python3
import argparse
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

sns.set_theme(style="whitegrid")

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]


def ensure_out(out_dir: str) -> None:
	os.makedirs(out_dir, exist_ok=True)


def save_fig(path: str) -> None:
	plt.tight_layout()
	plt.savefig(path, dpi=160)
	plt.close()
	print(f"Saved: {path}")


def plot_monthly_counts_heatmap(monthly_summary_csv: str, out_dir: str) -> None:
	if not os.path.exists(monthly_summary_csv):
		print(f"Skip monthly heatmap; file not found: {monthly_summary_csv}")
		return
	df = pd.read_csv(monthly_summary_csv, sep=';')
	# Erwartete Spalten: Monat;Abteilung;Ist;Favoriten
	pivot = df.pivot_table(index='Abteilung', columns='Monat', values='Ist', aggfunc='sum', fill_value=0)
	plt.figure(figsize=(14, max(6, len(pivot) * 0.3)))
	sns.heatmap(pivot, cmap='Blues', annot=False)
	plt.title('Heatmap: Einsätze pro Abteilung und Monat (Ist)')
	plt.xlabel('Monat')
	plt.ylabel('Abteilung')
	save_fig(os.path.join(out_dir, 'heatmap_monthly_counts.png'))


def plot_monthly_quota_deviation_heatmap(monthly_quota_csv: str, out_dir: str) -> None:
	if not os.path.exists(monthly_quota_csv):
		print(f"Skip quota deviation heatmap; file not found: {monthly_quota_csv}")
		return
	df = pd.read_csv(monthly_quota_csv, sep=';')
	# Spalten: Monat;Abteilung;Soll;Ist;Diff
	pivot = df.pivot_table(index='Abteilung', columns='Monat', values='Diff', aggfunc='sum', fill_value=0)
	plt.figure(figsize=(14, max(6, len(pivot) * 0.3)))
	sns.heatmap(pivot, cmap='coolwarm', center=0, annot=False)
	plt.title('Heatmap: Soll/Ist-Abweichung pro Abteilung und Monat (Diff)')
	plt.xlabel('Monat')
	plt.ylabel('Abteilung')
	save_fig(os.path.join(out_dir, 'heatmap_monthly_quota_diff.png'))


def plot_weekday_distribution(plan_csv: str, out_dir: str) -> None:
	if not os.path.exists(plan_csv):
		print(f"Skip weekday distribution; plan CSV not found: {plan_csv}")
		return
	df = pd.read_csv(plan_csv, sep=';')
	# Erwartete Spalten: Datum;Wochentag;Abteilungsnummer
	# Filter nur Montag-Freitag
	df = df[df['Wochentag'].isin(WEEKDAYS_DE)].copy()
	# Pivot: Abteilung x Wochentag → count
	pivot = df.pivot_table(index='Abteilungsnummer', columns='Wochentag', values='Datum', aggfunc='count', fill_value=0)
	# Spalten sortieren nach Wochentag-Ordnung
	present_days = [d for d in WEEKDAYS_DE if d in pivot.columns]
	pivot = pivot[present_days]
	plt.figure(figsize=(10, max(6, len(pivot) * 0.3)))
	sns.heatmap(pivot, cmap='Greens', annot=False)
	plt.title('Heatmap: Wochentags-Verteilung je Abteilung')
	plt.xlabel('Wochentag')
	plt.ylabel('Abteilung')
	save_fig(os.path.join(out_dir, 'heatmap_weekday_distribution.png'))


def plot_consecutive_bars(consecutive_csv: str, out_dir: str) -> None:
	if not os.path.exists(consecutive_csv):
		print(f"Skip consecutive bars; file not found: {consecutive_csv}")
		return
	df = pd.read_csv(consecutive_csv, sep=';')
	# Spalten: Abteilung;Folgetage
	df = df.sort_values('Folgetage', ascending=False)
	plt.figure(figsize=(12, max(5, len(df) * 0.3)))
	# Verwendung von einheitlicher Farbe statt palette ohne hue, um FutureWarning zu vermeiden
	sns.barplot(data=df, x='Folgetage', y='Abteilung', color='#d62728')
	plt.title('Folgetage je Abteilung (benachbarte Arbeitstage)')
	plt.xlabel('Anzahl Folgetage')
	plt.ylabel('Abteilung')
	save_fig(os.path.join(out_dir, 'bars_consecutive_by_department.png'))


def plot_q4_skew(q4_csv: str, out_dir: str) -> None:
	if not os.path.exists(q4_csv):
		print(f"Skip Q4 skew; file not found: {q4_csv}")
		return
	df = pd.read_csv(q4_csv, sep=';')
	# Spalten: Abteilung;Q4_Ist;Q4_Soll;Diff
	df = df.sort_values('Diff', key=lambda s: s.abs(), ascending=False)
	plt.figure(figsize=(12, max(5, len(df) * 0.3)))
	# Eigene Farbliste je nach Vorzeichen statt palette ohne hue
	colors = df['Diff'].apply(lambda v: '#d62728' if v > 0 else '#1f77b4').tolist()
	plt.barh(df['Abteilung'], df['Diff'], color=colors)
	plt.axvline(0, color='black', linewidth=0.8)
	plt.title('Q4-Skew: Abweichung Okt–Dez (Ist - Soll) je Abteilung')
	plt.xlabel('Diff (Ist - Soll)')
	plt.ylabel('Abteilung')
	save_fig(os.path.join(out_dir, 'bars_q4_skew.png'))


def main() -> int:
	parser = argparse.ArgumentParser(description='Visualisiere Validator-Reports (Heatmaps/Diagramme).')
	parser.add_argument('--dir', required=True, help='Verzeichnis mit Reports (z. B. tests/vX)')
	parser.add_argument('--plan', default=None, help='Pfad zu Plan-CSV (überschreibt auto-Suche)')
	parser.add_argument('--out-dir', default=None, help='Zielordner für Bilder (Default: gleich wie --dir)')
	args = parser.parse_args()

	reports_dir = os.path.abspath(args.dir)
	out_dir = os.path.abspath(args.out_dir or reports_dir)
	ensure_out(out_dir)

	monthly_summary_csv = os.path.join(reports_dir, 'validation_monthly_summary.csv')
	monthly_quota_csv = os.path.join(reports_dir, 'validation_monthly_quota_deviation.csv')
	consecutive_csv = os.path.join(reports_dir, 'validation_consecutive.csv')
	q4_csv = os.path.join(reports_dir, 'validation_q4_skew.csv')
	plan_csv = args.plan or os.path.join(reports_dir, 'Jahresdienstplan_2026.csv')

	plot_monthly_counts_heatmap(monthly_summary_csv, out_dir)
	plot_monthly_quota_deviation_heatmap(monthly_quota_csv, out_dir)
	plot_weekday_distribution(plan_csv, out_dir)
	plot_consecutive_bars(consecutive_csv, out_dir)
	plot_q4_skew(q4_csv, out_dir)

	print('Visualisierung abgeschlossen.')
	return 0


if __name__ == '__main__':
	sys.exit(main())
