
import subprocess
import time
import logging
import csv
from pathlib import Path
from datetime import datetime, timezone

import requests

# Configuration
PROMETHEUS_URL = "http://localhost:9090"
TARGET_CONTAINER = "demo-app"

CHECK_INTERVAL = 15
FAILURE_THRESHOLD = 3
RECOVERY_COOLDOWN = 120
RECOVERY_VERIFY_TIMEOUT = 60

LOG_FILE = (
    Path(__file__).resolve().parent
    / "logs"
    / "recovery_history.csv"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

failures = 0
last_recovery = 0


def save_recovery_event(event, status, details):
    """Save recovery activity to a CSV file."""

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    new_file = (
        not LOG_FILE.exists()
        or LOG_FILE.stat().st_size == 0
    )

    with LOG_FILE.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if new_file:
            writer.writerow([
                "timestamp",
                "container",
                "event",
                "status",
                "details"
            ])

        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            TARGET_CONTAINER,
            event,
            status,
            details
        ])


def check_application():
    """Check application availability through Prometheus."""

    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={
                "query": 'up{job="fastapi-app"}'
            },
            timeout=5
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") != "success":
            return None

        results = payload["data"]["result"]

        if len(results) != 1:
            logging.warning(
                "Unexpected Prometheus target count: %d",
                len(results)
            )
            return None

        return results[0]["value"][1] == "1"

    except (
        requests.RequestException,
        KeyError,
        ValueError,
        TypeError
    ) as error:
        logging.warning(
            "Monitoring query failed: %s",
            error
        )
        return None


def verify_recovery():
    """Check the application health endpoint after recovery."""

    deadline = (
        time.monotonic()
        + RECOVERY_VERIFY_TIMEOUT
    )

    while time.monotonic() < deadline:
        try:
            response = requests.get(
                "http://localhost:8000/health",
                timeout=5
            )

            if (
                response.status_code == 200
                and response.json().get("status") == "healthy"
            ):
                logging.info(
                    "Application recovery verified successfully"
                )

                save_recovery_event(
                    event="recovery_verification",
                    status="healthy",
                    details="Application health endpoint responded"
                )

                return True

        except (
            requests.RequestException,
            ValueError
        ):
            pass

        time.sleep(5)

    logging.error(
        "Application did not become healthy after recovery"
    )

    save_recovery_event(
        event="recovery_verification",
        status="unhealthy",
        details="Health check verification timed out"
    )

    return False


def recover_container():
    """Start or restart the allowlisted Docker container."""

    logging.warning(
        "Attempting recovery: %s",
        TARGET_CONTAINER
    )

    try:
        inspect = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Running}}",
                TARGET_CONTAINER
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        if inspect.returncode != 0:
            logging.error(
                "Container not found: %s",
                TARGET_CONTAINER
            )

            save_recovery_event(
                event="recovery_attempt",
                status="container_not_found",
                details=inspect.stderr.strip()
            )

            return False

        running = (
            inspect.stdout.strip().lower()
            == "true"
        )

        action = "restart" if running else "start"

        result = subprocess.run(
            [
                "docker",
                action,
                TARGET_CONTAINER
            ],
            capture_output=True,
            text=True,
            timeout=45
        )

        if result.returncode == 0:
            logging.info(
                "Recovery action completed: docker %s %s",
                action,
                TARGET_CONTAINER
            )

            save_recovery_event(
                event="recovery_attempt",
                status="command_succeeded",
                details=f"docker {action} {TARGET_CONTAINER}"
            )

            return verify_recovery()

        logging.error(
            "Recovery failed: %s",
            result.stderr.strip()
        )

        save_recovery_event(
            event="recovery_attempt",
            status="command_failed",
            details=result.stderr.strip()
        )

        return False

    except (
        subprocess.SubprocessError,
        OSError
    ) as error:
        logging.error(
            "Recovery error: %s",
            error
        )

        save_recovery_event(
            event="recovery_attempt",
            status="error",
            details=str(error)
        )

        return False


def main():
    global failures, last_recovery

    logging.info(
        "Auto-Healing Engine started"
    )

    logging.info(
        "Monitoring container: %s",
        TARGET_CONTAINER
    )

    while True:
        healthy = check_application()

        if healthy is True:
            failures = 0

            logging.info(
                "Application is healthy"
            )

        elif healthy is False:
            failures += 1

            logging.warning(
                "Application failure detected (%d/%d)",
                failures,
                FAILURE_THRESHOLD
            )

            if failures >= FAILURE_THRESHOLD:
                now = time.monotonic()

                if (
                    now - last_recovery
                    >= RECOVERY_COOLDOWN
                ):
                    last_recovery = now
                    recover_container()

                else:
                    remaining = (
                        RECOVERY_COOLDOWN
                        - (now - last_recovery)
                    )

                    logging.warning(
                        "Recovery cooldown active: %.0f seconds remaining",
                        remaining
                    )

                failures = 0

        else:
            logging.warning(
                "Monitoring unavailable; skipping recovery"
            )

            failures = 0

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        logging.info(
            "Auto-Healing Engine stopped by user"
        )
