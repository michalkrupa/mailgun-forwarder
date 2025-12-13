#!/usr/bin/env python3
from flask import Flask, request, abort, Request
import smtplib
from time import sleep
import os

from .tasks import send_email_task

class LargeRequest(Request):
    max_form_memory_size = 50 * 1024 * 1024   # 50MB field limit
    max_content_length = 300 * 1024 * 1024   # 300MB total

app = Flask(__name__)
app.request_class = LargeRequest
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
app.config['ENV'] = "production"
app.config['DEBUG'] = False

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", None)


@app.route("/mailgun-inbound-mime", methods=["POST"])
def mailgun_inbound():
    raw_mime = request.form.get("body-mime")
    recipient = request.form.get("recipient")
    sender = request.form.get("sender")
    
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret")
        if token != WEBHOOK_SECRET:
            abort(403)

    if not raw_mime or not recipient:
        abort(400, "Missing MIME body or recipient")

    send_email_task.delay(sender, recipient, raw_mime)
    return "Queued", 202

# ⚠️ REMOVE app.run() in production
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)


