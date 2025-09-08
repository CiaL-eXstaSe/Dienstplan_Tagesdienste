# Test-Versionierung für Jahresdienstplan

Dieses Verzeichnis verwaltet versionierte Test-Snapshots (Eingaben/Outputs) für den Jahresdienstplan.

Struktur:
- v<name>/
  - Testdaten.csv
  - Jahresdienstplan_2026.csv (optional)
  - metadata.json (Zeitstempel, Kommentar)
  - validation_report.txt (Konsolen-Output des Validators)
  - validation_summary.md (Markdown-Zusammenfassung)
  - validation_proportionality.csv (Ziel/Ist/Diff gesamt)
  - validation_consecutive.csv (Folgetage je Abteilung)
  - validation_favorites.csv (Lieblingstage-Treffer)
  - validation_monthly_summary.csv (Ist & Favoriten je Monat)
  - validation_monthly_quota_deviation.csv (Soll/Ist je Monat & Abteilung)
  - validation_q4_skew.csv (Ende-Jahr-Skew: Okt–Dez Soll/Ist)

Schnappschuss erstellen:

```bash
python3 ../manage_tests.py snapshot --version v1 --note "Erster Snapshot"
# Ohne --version wird automatisch ein Zeitstempel verwendet (z. B. v2025-08-27_1423)
```

Visualisierung (Heatmaps/Charts) direkt aus einem Versionsordner erzeugen:
```bash
pip install -r ../requirements.txt
python3 ../visualize_reports.py --dir ./v1
```

Hinweise:
- Nutze sprechende Versionsnamen (z. B. vweights-rotation, vfavorites-tuned).
- Pflege Änderungen zusätzlich in CHANGELOG.md in diesem Verzeichnis.
