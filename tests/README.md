# Test-Versionierung für Jahresdienstplan

Dieses Verzeichnis verwaltet versionierte Test-Snapshots (Eingaben/Outputs) für den Jahresdienstplan.

Struktur:
- v<name>/
  - Testdaten.csv
  - Jahresdienstplan_2026.csv (optional)
  - metadata.json (Zeitstempel, Kommentar)

Schnappschuss erstellen:

```bash
python3 ../manage_tests.py snapshot --version v1 --note "Erster Snapshot"
# Ohne --version wird automatisch ein Zeitstempel verwendet (z. B. v2025-08-27_1423)
```

Hinweise:
- Nutze sprechende Versionsnamen (z. B. vweights-rotation, vfavorites-tuned).
- Pflege Änderungen zusätzlich in CHANGELOG.md in diesem Verzeichnis.
