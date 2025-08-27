#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from datetime import datetime
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')

INPUT_FILE = os.path.join(BASE_DIR, 'Testdaten.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'Jahresdienstplan_2026.csv')
VALIDATOR = os.path.join(BASE_DIR, 'validate_plan.py')


def ensure_tests_dir():
	os.makedirs(TESTS_DIR, exist_ok=True)


def timestamp_version() -> str:
	return 'v' + datetime.now().strftime('%Y-%m-%d_%H%M%S')


def run_validator(plan_path: str, test_path: str, report_path: str) -> None:
	"""Runs the validator and writes stdout to report_path."""
	try:
		with open(report_path, 'w', encoding='utf-8') as fout:
			proc = subprocess.run(
				['python3', VALIDATOR, plan_path, test_path],
				stdout=fout,
				stderr=subprocess.STDOUT,
				cwd=BASE_DIR,
				check=False,
			)
			# append exit code for traceability
			with open(report_path, 'a', encoding='utf-8') as fappend:
				fappend.write(f"\n\n[validator-exit-code]: {proc.returncode}\n")
	except FileNotFoundError:
		# validator missing
		with open(report_path, 'w', encoding='utf-8') as fout:
			fout.write('Validator-Skript nicht gefunden. Übersprungen.\n')


def create_snapshot(version: str = None, note: str = '') -> str:
	ensure_tests_dir()
	if not version:
		version = timestamp_version()
	version_dir = os.path.join(TESTS_DIR, version)
	if os.path.exists(version_dir):
		raise SystemExit(f"Version existiert bereits: {version}")
	os.makedirs(version_dir)

	# Kopiere vorhandene Dateien
	copied_input = False
	copied_output = False
	if os.path.exists(INPUT_FILE):
		shutil.copy2(INPUT_FILE, os.path.join(version_dir, 'Testdaten.csv'))
		copied_input = True
	else:
		print('Warnung: Testdaten.csv nicht gefunden, Snapshot ohne Eingabedatei.')
	if os.path.exists(OUTPUT_FILE):
		shutil.copy2(OUTPUT_FILE, os.path.join(version_dir, 'Jahresdienstplan_2026.csv'))
		copied_output = True
	else:
		print('Hinweis: Jahresdienstplan_2026.csv nicht gefunden, Snapshot ohne Output-Datei.')

	# Metadata schreiben
	metadata = {
		'version': version,
		'timestamp': datetime.now().isoformat(timespec='seconds'),
		'note': note,
	}
	with open(os.path.join(version_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
		json.dump(metadata, f, ensure_ascii=False, indent=2)

	# Validator ausführen, wenn beide Dateien vorhanden sind
	if copied_input and copied_output:
		report_path = os.path.join(version_dir, 'validation_report.txt')
		run_validator(
			plan_path=os.path.join(version_dir, 'Jahresdienstplan_2026.csv'),
			test_path=os.path.join(version_dir, 'Testdaten.csv'),
			report_path=report_path,
		)
		print(f'Validator-Bericht gespeichert: {report_path}')
	else:
		print('Validator übersprungen (benötigt sowohl Testdaten.csv als auch Jahresdienstplan_2026.csv).')

	print(f'Snapshot erstellt: {version_dir}')
	return version


def list_versions():
	ensure_tests_dir()
	entries = [d for d in os.listdir(TESTS_DIR) if d.startswith('v') and os.path.isdir(os.path.join(TESTS_DIR, d))]
	for d in sorted(entries):
		print(d)


def main():
	parser = argparse.ArgumentParser(description='Verwalte versionierte Test-Snapshots')
	sub = parser.add_subparsers(dest='cmd', required=True)

	p_snap = sub.add_parser('snapshot', help='Erzeuge einen Snapshot (Version)')
	p_snap.add_argument('--version', help='Versionsname (Default: Zeitstempel)')
	p_snap.add_argument('--note', default='', help='Kommentar zur Version')

	sub.add_parser('list', help='Liste vorhandene Test-Versionen')

	args = parser.parse_args()
	if args.cmd == 'snapshot':
		create_snapshot(args.version, args.note)
	elif args.cmd == 'list':
		list_versions()


if __name__ == '__main__':
	main()
