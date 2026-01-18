## Trading data file management (logs, CSV exports, reports)

This repo generates/consumes multiple “trading output” files (signals, logs, exports). To keep disk usage predictable and avoid accidentally deleting useful data, use a simple lifecycle:

- **Ingest (raw)**: short-lived, easy-to regenerate (`.txt`, `.csv`)
- **Reports (analysis-ready)**: long-lived (`.xlsx`)
- **Archive**: cold storage for older reports
- **Trash (quarantine)**: reversible “delete” buffer

### Recommended folders

Use a single root folder (default: `data/trading_data/`):

```
data/trading_data/
  logs/                 # temporary .txt logs
  raw_csv/              # incoming CSV exports
  reports/              # current XLSX reports (kept “hot”)
  archive/              # older XLSX reports (cold storage)
  trash/                # quarantined deletes (safe rollback)
  maintenance_logs/     # JSONL audit logs per run
```

### Keep / clean rules (safe defaults)

- **`.txt` logs**
  - Keep for **14 days** (configurable).
  - Action: move to `trash/` once expired; trash is purged after **30 days**.

- **`.csv` exports**
  - Convert to `.xlsx` immediately (configurable).
  - After successful conversion, move the `.csv` to `trash/` (or delete if you set retention to 0).

- **`.xlsx` reports**
  - Keep “hot” in `reports/`.
  - Move to `archive/` after **90 days** (configurable).

### Naming & partitioning (prevents duplicates)

Converted CSV reports are written as:

- `reports/YYYY-MM/YYYY-MM-DD_<csv-stem>.xlsx`

This makes it easy to:

- find all reports by month,
- keep multiple report types per day (different `<csv-stem>`),
- avoid accidental overwrites (script writes atomically and uses a collision-safe name).

### Automation (daily)

Run once per day (cron example):

```bash
0 2 * * * cd /path/to/GenX_FX && /usr/bin/python3 scripts/trading_data_manager.py --root data/trading_data --mode daily >> logs/trading_data_manager.log 2>&1
```

First run it in dry-run mode to verify what it will do:

```bash
python3 scripts/trading_data_manager.py --root data/trading_data --mode daily --dry-run
```

### Safety features (why this is “clean”)

- **Dry-run**: shows actions without changing anything
- **Quarantine trash**: moves files instead of hard-deleting by default
- **Audit logs**: JSONL log per run in `maintenance_logs/`
- **Scope guard**: only operates inside the chosen `--root`

