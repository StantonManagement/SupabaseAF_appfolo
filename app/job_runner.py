"""
Job Runner for dataset syncs.

Usage examples:
  python -m app.job_runner --dataset unit_vacancy
  python -m app.job_runner --dataset rental_applications
  python -m app.job_runner --dataset unit_vacancy,rental_applications

Environment:
  JOB_DATASET           Optional default dataset if --dataset is omitted

Exit code is non-zero on failure so schedulers can retry.
Emits structured JSON logs per dataset with fields:
  event, dataset, run_id, status, count, duration_ms, error
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import traceback
from typing import List
from uuid import uuid4

from app.services.sync import sync_details
from app.helpers.constants import DETAILS

# Create logger for this module
logger = logging.getLogger(__name__)


def _log(payload: dict) -> None:
    """Emit a single JSON line to stdout."""
    try:
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
    except Exception:  # pragma: no cover - logging must not crash the job
        # Fallback to best-effort string output
        print(str(payload))


def run_dataset(dataset: str, run_id: str) -> int:
    start = time.time()
    try:
        results = sync_details(dataset)
        # sync_details now returns {"success": int, "failed": int, "total": int}
        count = results.get("total", 0) if isinstance(results, dict) else 0
        _log(
            {
                "event": "sync_complete",
                "dataset": dataset,
                "run_id": run_id,
                "status": "success",
                "count": count,
                "success": results.get("success", 0),
                "failed": results.get("failed", 0),
                "duration_ms": int((time.time() - start) * 1000),
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        _log(
            {
                "event": "sync_complete",
                "dataset": dataset,
                "run_id": run_id,
                "status": "error",
                "error": str(exc),
                "trace": traceback.format_exc(limit=5),
                "duration_ms": int((time.time() - start) * 1000),
            }
        )
        return 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AppFolio dataset sync job(s)")
    parser.add_argument(
        "--dataset",
        help="Dataset key from app.helpers.constants.DETAILS or comma-separated list",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first dataset failure (default: continue through all)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    datasets_arg = args.dataset or os.getenv("JOB_DATASET", "").strip()

    if not datasets_arg:
        valid = ", ".join(sorted(DETAILS.keys()))
        logger.error(
            "❌ No dataset provided. Use --dataset <name> or set JOB_DATASET.\n"
            f"Valid options: {valid}"
        )
        print(
            "Error: no dataset provided. Use --dataset <name> or set JOB_DATASET.\n"
            f"Valid options: {valid}",
            file=sys.stderr,
        )
        return 2

    datasets = [d.strip() for d in datasets_arg.split(",") if d.strip()]
    invalid = [d for d in datasets if d not in DETAILS]
    if invalid:
        logger.error(f"❌ Invalid dataset(s): {', '.join(invalid)}")
        print(
            f"Error: invalid dataset(s): {', '.join(invalid)}",
            file=sys.stderr,
        )
        print(
            "Hint: choose from: " + ", ".join(sorted(DETAILS.keys())),
            file=sys.stderr,
        )
        return 2

    overall_code = 0
    run_id = str(uuid4())
    _log({"event": "sync_start", "datasets": datasets, "run_id": run_id})
    for d in datasets:
        code = run_dataset(d, run_id)
        if code != 0:
            overall_code = code
            if args.fail_fast:
                break
    _log(
        {
            "event": "sync_end",
            "run_id": run_id,
            "status": "ok" if overall_code == 0 else "error",
        }
    )
    return overall_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
