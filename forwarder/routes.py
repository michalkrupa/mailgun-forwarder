import logging
from flask import Blueprint, request, abort
from mailgun.queue.tasks import send_email_task
from mailgun.config import WEBHOOK_SECRET

logger = logging.getLogger(__name__)
bp = Blueprint('forwarder', __name__)

@bp.route("/mailgun-inbound-mime", methods=["POST"])
def mailgun_inbound():
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret")
        if token != WEBHOOK_SECRET:
            logger.warning(f"Authentication failed for request from {request.remote_addr}")
            abort(403)

    raw_mime = request.form.get("body-mime")
    recipient = request.form.get("recipient")
    sender = request.form.get("sender")
    mime_body = None

    try:
        if isinstance(raw_mime, str):
            mime_body = raw_mime.encode('utf-8')
        else:
            mime_body = raw_mime
    except Exception as e:
        print(f"Encoding error: {e}")

    if not mime_body:
        logger.error(f"Failed to process MIME body")
        abort(400, "Invalid MIME body")

    logger.info(f"Received inbound email from {sender} to {recipient}")

    if not recipient:
        logger.error(f"Missing required fields - recipient: {bool(recipient)}")
        abort(400, "Missing recipient")

    send_email_task.delay(sender, recipient, mime_body)
    logger.info(f"Queued email task for {recipient}")
    return "Queued", 202