import logging
import time
from concurrent.futures import ThreadPoolExecutor

from app.services.notification_service import (
    send_submission_notification,
)


logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


def queue_submission_notification(
    submission_id: str,
    widget_id: str,
    email: str,
):
    executor.submit(
        _run_submission_notification,
        submission_id,
        widget_id,
        email,
    )


def _run_submission_notification(
    submission_id: str,
    widget_id: str,
    email: str,
):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            send_submission_notification(
                submission_id=submission_id,
                widget_id=widget_id,
                email=email,
            )

            logger.info(
                "Submission notification succeeded: "
                "submission=%s attempt=%s",
                submission_id,
                attempt,
            )

            return

        except Exception:
            logger.exception(
                "Submission notification failed: "
                "submission=%s attempt=%s",
                submission_id,
                attempt,
            )

            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS * attempt)

    logger.error(
        "ALERT: submission notification permanently failed "
        "after %s attempts: submission=%s widget=%s email=%s",
        MAX_ATTEMPTS,
        submission_id,
        widget_id,
        email,
    )