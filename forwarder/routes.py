import logging
from flask import Blueprint, request, abort
from mailgun.queue.tasks import send_email_task
from mailgun.config import WEBHOOK_SECRET

logger = logging.getLogger(__name__)
bp = Blueprint('forwarder', __name__)

@bp.route("/mailgun-inbound-mime", methods=["POST"])
def mailgun_inbound():
    raw_mime = request.form.get("body-mime")
    recipient = request.form.get("recipient")
    sender = request.form.get("sender")
    
    logger.info(f"Received inbound email from {sender} to {recipient}")
    
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret")
        if token != WEBHOOK_SECRET:
            logger.warning(f"Authentication failed for request from {request.remote_addr}")
            abort(403)

    if not raw_mime or not recipient:
        logger.error(f"Missing required fields - MIME: {bool(raw_mime)}, recipient: {bool(recipient)}")
        abort(400, "Missing MIME body or recipient")

    send_email_task.delay(sender, recipient, raw_mime)
    logger.info(f"Queued email task for {recipient}")
    return "Queued", 202