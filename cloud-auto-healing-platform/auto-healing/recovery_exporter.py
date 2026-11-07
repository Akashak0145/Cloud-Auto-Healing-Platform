
import csv
import time
from pathlib import Path
from datetime import datetime

from prometheus_client import Gauge, start_http_server

CSV_FILE = (
    Path(__file__).resolve().parent
    / "logs"
    / "recovery_history.csv"
)

attempts = Gauge(
    "auto_healing_recovery_attempts_total",
    "Recorded Docker recovery attempts"
)

success = Gauge(
    "auto_healing_recovery_success_total",
    "Verified successful application recoveries"
)

failures = Gauge(
    "auto_healing_recovery_failures_total",
    "Recorded unsuccessful recovery attempts or verifications"
)

last_recovery = Gauge(
    "auto_healing_last_recovery_timestamp_seconds",
    "Timestamp of last verified recovery"
)


def update_metrics():
    attempt_count = 0
    success_count = 0
    failure_count = 0
    latest_success = 0

    if CSV_FILE.exists():
        with CSV_FILE.open(
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            for row in csv.DictReader(file):
                event = row.get("event", "")
                status = row.get("status", "")

                if event == "recovery_attempt":
                    attempt_count += 1

                    if status != "command_succeeded":
                        failure_count += 1

                elif event == "recovery_verification":
                    if status == "healthy":
                        success_count += 1

                        try:
                            timestamp = datetime.fromisoformat(
                                row["timestamp"]
                            ).timestamp()

                            latest_success = max(
                                latest_success,
                                timestamp
                            )
                        except (ValueError, KeyError):
                            pass

                    else:
                        failure_count += 1

    attempts.set(attempt_count)
    success.set(success_count)
    failures.set(failure_count)
    last_recovery.set(latest_success)


if __name__ == "__main__":
    start_http_server(9102)

    print(
        "Recovery Metrics Exporter started on port 9102",
        flush=True
    )

    while True:
        try:
            update_metrics()
        except Exception as error:
            print(
                f"Metrics update error: {error}",
                flush=True
            )

        time.sleep(10)
