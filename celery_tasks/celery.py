from celery import Celery

from mailgun.config import BROKER_URL

celery = Celery(__name__, broker=BROKER_URL)
