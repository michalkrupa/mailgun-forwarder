import logging
import smtplib

from mailgun.config import SMTP_HOST, SMTP_PORT
from mailgun.celery_tasks.celery import celery

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=2)
def send_email_task(self, sender, recipient, raw_mime):
    try:
        logger.debug(f"Sending email from {sender} to {recipient}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=600) as smtp:
            smtp.sendmail(sender, [recipient], raw_mime)
        logger.info(f"Email successfully sent from {sender} to {recipient}")
        return {"status": "sent"}
    except Exception as exc:
        retry_delay = 2 ** self.request.retries
        logger.warning(f"Failed to send email to {recipient} (attempt {self.request.retries + 1}/3). Retrying in {retry_delay}s: {str(exc)}")
        raise self.retry(exc=exc, countdown=retry_delay)

