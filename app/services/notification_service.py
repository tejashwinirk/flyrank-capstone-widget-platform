import logging

logger = logging.getLogger(__name__)


def send_submission_notification(
    submission_id: str,
    widget_id: str,
    email: str,
):
    """
    Placeholder notification service.

    In production this can be replaced with an email provider
    or webhook integration without changing the submission flow.
    """

    logger.info(
        "Submission notification queued: submission=%s widget=%s email=%s",
        submission_id,
        widget_id,
        email,
    )

    return True