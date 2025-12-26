import os

BROKER_URL = os.environ.get("BROKER_URL", 'redis://localhost:6379')
SMTP_HOST = os.environ.get("SMTP_HOST", "0.0.0.0")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
FORWARD_FOR = os.environ.get("FORWARD_FOR", 'forwarder@domain.com')
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", None)
