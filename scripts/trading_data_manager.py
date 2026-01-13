#!/usr/bin/env python3
"""
Trading data file management utility.

Goals:
- Keep a clean, predictable folder structure for logs/exports/reports
- Convert CSV exports to XLSX (analysis-ready)
- Apply retention rules with a reversible "trash" quarantine
- Write an audit log for every action (JSONL)

Safe defaults are intentionally conservative (trash quarantine instead of hard-delete).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional, Tuple


try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore


SAFE_STEM_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _safe_stem(value: str) -> str:
    value = value.strip().replace(" ", "_")
    value = SAFE_STEM_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "report"


def _is_symlink(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return True


def _ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def _file_mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _older_than(path: Path, cutoff_utc: datetime) -> bool:
    return _file_mtime_utc(path) < cutoff_utc


def _within_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _iter_files(base: Path, suffixes: Tuple[str, ...]) -> Iterable[Path]:
    if not base.exists():
        return []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if _is_symlink(p):
            continue
        if p.suffix.lower() in suffixes:
            yield p


def _unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    for i in range(1, 10_000):
        candidate = parent / f"{stem}__{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique destination for {dest}")


@dataclass(frozen=True)
class RetentionPolicy:
    txt_days: int
    xlsx_archive_after_days: int
    trash_purge_after_days: int
    csv_post_convert_trash_days: int


@dataclass
class RunStats:
    converted_csv: int = 0
    trashed_txt: int = 0
    trashed_csv: int = 0
    archived_xlsx: int = 0
    purged_trash: int = 0
    skipped: int = 0
    errors: int = 0


class AuditLog:
    def __init__(self, log_path: Path, dry_run: bool):
        self.log_path = log_path
        self.dry_run = dry_run
        self._fh = None

    def __enter__(self) -> "AuditLog":
        if self.dry_run:
            return self
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.log_path.open("a", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fh:
            self._fh.close()

    def write(self, event: dict) -> None:
        event = {
            "ts_utc": _utcnow().isoformat(timespec="seconds").replace("+00:00", "Z"),
            **event,
        }
        line = json.dumps(event, ensure_ascii=False)
        if self.dry_run:
            # Still show what would be written.
            print(line)
            return
        assert self._fh is not None
        self._fh.write(line + "\n")
        self._fh.flush()


def _move_to_trash(
    *,
    src: Path,
    trash_dir: Path,
    root: Path,
    dry_run: bool,
    audit: AuditLog,
    reason: str,
) -> Path:
    if not _within_root(src, root):
        raise ValueError(f"Refusing to move file outside root: {src}")
    _ensure_dir(trash_dir, dry_run=dry_run)
    # Preserve relative structure inside trash for easier recovery.
    rel = src.resolve().relative_to(root.resolve())
    dest = trash_dir / rel
    _ensure_dir(dest.parent, dry_run=dry_run)
    dest = _unique_destination(dest)
    audit.write(
        {
            "action": "trash",
            "src": str(src),
            "dest": str(dest),
            "reason": reason,
            "size_bytes": src.stat().st_size,
            "mtime_utc": _file_mtime_utc(src)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "dry_run": dry_run,
        }
    )
    if not dry_run:
        shutil.move(str(src), str(dest))
    return dest


def _purge_old_files(
    *,
    base: Path,
    older_than_days: int,
    root: Path,
    dry_run: bool,
    audit: AuditLog,
) -> int:
    if older_than_days < 0:
        return 0
    cutoff = _utcnow() - timedelta(days=older_than_days)
    purged = 0
    for p in _iter_files(base, suffixes=(".txt", ".csv", ".xlsx", ".json", ".log")):
        if not _older_than(p, cutoff):
            continue
        if not _within_root(p, root):
            continue
        audit.write(
            {
                "action": "purge",
                "src": str(p),
                "reason": f"older_than_{older_than_days}_days",
                "size_bytes": p.stat().st_size,
                "mtime_utc": _file_mtime_utc(p)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
                "dry_run": dry_run,
            }
        )
        purged += 1
        if not dry_run:
            p.unlink(missing_ok=True)
    return purged


def _convert_csv_to_xlsx(
    *,
    csv_path: Path,
    reports_dir: Path,
    root: Path,
    dry_run: bool,
    audit: AuditLog,
) -> Optional[Path]:
    if pd is None:
        raise RuntimeError(
            "pandas is required for CSV→XLSX conversion but is not installed."
        )
    if not _within_root(csv_path, root):
        raise ValueError(f"Refusing to convert file outside root: {csv_path}")

    # Partition by month of the CSV mtime to keep reports tidy.
    mtime = _file_mtime_utc(csv_path)
    month_dir = reports_dir / mtime.strftime("%Y-%m")
    _ensure_dir(month_dir, dry_run=dry_run)

    safe = _safe_stem(csv_path.stem)
    out_name = f"{mtime.strftime('%Y-%m-%d')}_{safe}.xlsx"
    out_path = _unique_destination(month_dir / out_name)

    audit.write(
        {
            "action": "convert_csv_to_xlsx",
            "src": str(csv_path),
            "dest": str(out_path),
            "size_bytes": csv_path.stat().st_size,
            "mtime_utc": mtime.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "dry_run": dry_run,
        }
    )
    if dry_run:
        return out_path

    # Conservative parsing: keep strings to avoid accidental type coercion.
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    df.to_excel(tmp_path, index=False, engine="openpyxl")
    tmp_path.replace(out_path)
    return out_path


def _archive_old_reports(
    *,
    reports_dir: Path,
    archive_dir: Path,
    archive_after_days: int,
    root: Path,
    dry_run: bool,
    audit: AuditLog,
) -> int:
    if archive_after_days < 0:
        return 0
    cutoff = _utcnow() - timedelta(days=archive_after_days)
    moved = 0
    for xlsx in _iter_files(reports_dir, suffixes=(".xlsx",)):
        if not _older_than(xlsx, cutoff):
            continue
        if not _within_root(xlsx, root):
            continue
        mtime = _file_mtime_utc(xlsx)
        dest_dir = archive_dir / mtime.strftime("%Y") / mtime.strftime("%m")
        _ensure_dir(dest_dir, dry_run=dry_run)
        dest = _unique_destination(dest_dir / xlsx.name)
        audit.write(
            {
                "action": "archive_xlsx",
                "src": str(xlsx),
                "dest": str(dest),
                "reason": f"older_than_{archive_after_days}_days",
                "size_bytes": xlsx.stat().st_size,
                "mtime_utc": mtime.isoformat(timespec="seconds").replace("+00:00", "Z"),
                "dry_run": dry_run,
            }
        )
        moved += 1
        if not dry_run:
            shutil.move(str(xlsx), str(dest))
    return moved


def run_daily(*, root: Path, policy: RetentionPolicy, dry_run: bool) -> RunStats:
    stats = RunStats()

    logs_dir = root / "logs"
    raw_csv_dir = root / "raw_csv"
    reports_dir = root / "reports"
    archive_dir = root / "archive"
    trash_dir = root / "trash"
    maintenance_logs_dir = root / "maintenance_logs"

    for d in (logs_dir, raw_csv_dir, reports_dir, archive_dir, trash_dir, maintenance_logs_dir):
        _ensure_dir(d, dry_run=dry_run)

    log_path = maintenance_logs_dir / f"{_utcnow().strftime('%Y-%m-%d')}.jsonl"
    with AuditLog(log_path, dry_run=dry_run) as audit:
        # 1) TXT retention -> trash
        if policy.txt_days >= 0:
            cutoff = _utcnow() - timedelta(days=policy.txt_days)
            for txt in _iter_files(logs_dir, suffixes=(".txt", ".log")):
                try:
                    if not _older_than(txt, cutoff):
                        continue
                    _move_to_trash(
                        src=txt,
                        trash_dir=trash_dir,
                        root=root,
                        dry_run=dry_run,
                        audit=audit,
                        reason=f"txt_older_than_{policy.txt_days}_days",
                    )
                    stats.trashed_txt += 1
                except Exception as e:
                    stats.errors += 1
                    audit.write({"action": "error", "src": str(txt), "error": str(e)})

        # 2) CSV -> XLSX, then trash CSV
        for csv_path in _iter_files(raw_csv_dir, suffixes=(".csv",)):
            try:
                xlsx_path = _convert_csv_to_xlsx(
                    csv_path=csv_path,
                    reports_dir=reports_dir,
                    root=root,
                    dry_run=dry_run,
                    audit=audit,
                )
                if xlsx_path is not None:
                    stats.converted_csv += 1

                # Move CSV to trash after conversion (reversible by default)
                _move_to_trash(
                    src=csv_path,
                    trash_dir=trash_dir,
                    root=root,
                    dry_run=dry_run,
                    audit=audit,
                    reason="csv_converted_to_xlsx",
                )
                stats.trashed_csv += 1
            except Exception as e:
                stats.errors += 1
                audit.write({"action": "error", "src": str(csv_path), "error": str(e)})

        # 3) Archive old XLSX reports
        try:
            stats.archived_xlsx += _archive_old_reports(
                reports_dir=reports_dir,
                archive_dir=archive_dir,
                archive_after_days=policy.xlsx_archive_after_days,
                root=root,
                dry_run=dry_run,
                audit=audit,
            )
        except Exception as e:
            stats.errors += 1
            audit.write({"action": "error", "src": str(reports_dir), "error": str(e)})

        # 4) Purge trash after retention window
        try:
            stats.purged_trash += _purge_old_files(
                base=trash_dir,
                older_than_days=policy.trash_purge_after_days,
                root=root,
                dry_run=dry_run,
                audit=audit,
            )
        except Exception as e:
            stats.errors += 1
            audit.write({"action": "error", "src": str(trash_dir), "error": str(e)})

    return stats


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Trading data file management utility")
    p.add_argument(
        "--root",
        default="data/trading_data",
        help="Root directory for trading data folders (default: data/trading_data)",
    )
    p.add_argument(
        "--mode",
        choices=("daily",),
        default="daily",
        help="Run mode (default: daily)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without modifying files",
    )
    p.add_argument(
        "--txt-retention-days",
        type=int,
        default=14,
        help="Move .txt/.log from logs/ to trash/ after N days (default: 14). Set -1 to disable.",
    )
    p.add_argument(
        "--xlsx-archive-after-days",
        type=int,
        default=90,
        help="Move .xlsx from reports/ to archive/ after N days (default: 90). Set -1 to disable.",
    )
    p.add_argument(
        "--trash-purge-after-days",
        type=int,
        default=30,
        help="Hard-delete files in trash/ after N days (default: 30). Set -1 to disable.",
    )
    p.add_argument(
        "--csv-post-convert-trash-days",
        type=int,
        default=30,
        help=(
            "How long converted CSVs live in trash/ before purge (default: 30). "
            "Note: this is controlled by trash purge; this flag is informational for future expansion."
        ),
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    root = Path(args.root).expanduser()

    # Ensure we don't accidentally manage '/' or a home dir without intention.
    if str(root).strip() in ("/", str(Path.home())):
        print(f"Refusing to run with unsafe --root: {root}", file=sys.stderr)
        return 2

    policy = RetentionPolicy(
        txt_days=args.txt_retention_days,
        xlsx_archive_after_days=args.xlsx_archive_after_days,
        trash_purge_after_days=args.trash_purge_after_days,
        csv_post_convert_trash_days=args.csv_post_convert_trash_days,
    )

    if args.mode == "daily":
        stats = run_daily(root=root, policy=policy, dry_run=args.dry_run)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        return 2

    summary = {
        "root": str(root),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "converted_csv": stats.converted_csv,
        "trashed_txt": stats.trashed_txt,
        "trashed_csv": stats.trashed_csv,
        "archived_xlsx": stats.archived_xlsx,
        "purged_trash": stats.purged_trash,
        "errors": stats.errors,
    }
    print(json.dumps(summary, indent=2))
    return 0 if stats.errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

