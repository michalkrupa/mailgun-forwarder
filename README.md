# Mailgun Forwarder

A Flask-based email forwarding service that leverages Mailgun webhooks to work around port 25 restrictions in hosting environments.

## Problem

Many hosting providers block outbound SMTP on port 25 to prevent spam. This makes it difficult to self-host email services that rely on direct SMTP access. Even if you have your own mail server, you often can't connect to it from the hosting environment.

## Solution

This application provides a workaround by:

1. **Receiving emails via Mailgun webhook** - Mailgun receives inbound emails on your behalf and sends them to this service
2. **Forwarding to internal mail server** - The service connects to your private mail server on an alternative port (e.g., 2525) that isn't blocked
3. **Handling large attachments** - Supports up to 300MB emails with async queue processing via Celery

This allows you to route incoming mail through Mailgun's infrastructure while maintaining control over final delivery.

## Architecture

- **Flask app** - Receives webhook POST requests from Mailgun
- **Celery worker** - Processes email delivery asynchronously with retries
- **Redis** - Message broker for task queue
- **Gunicorn** - Production WSGI server

## Setup

### 1. Configure Environment Variables

Create a `.env` file in the project root:

```env
BROKER_URL=redis://redis:6379
SMTP_HOST=192.168.1.65
SMTP_PORT=2525
WEBHOOK_SECRET=your-secret-webhook-token
```

**Variables:**
- `BROKER_URL` - Redis connection string (used by Celery)
- `SMTP_HOST` - Your internal mail server hostname/IP
- `SMTP_PORT` - SMTP port on your mail server (commonly 2525, 587, or 465)
- `WEBHOOK_SECRET` - Authentication token to protect the webhook (set a strong value)

### 2. Configure Mailgun Webhook

In your Mailgun dashboard:

1. Go to **Receiving > Routes**
2. Create a new route or edit existing one
3. Set the action to **forward** to your webhook URL:
   ```
   https://your-domain.com:8765/mailgun-inbound-mime
   ```
4. Add a custom header with your webhook secret:
   ```
   X-Webhook-Secret: your-secret-webhook-token
   ```

Mailgun will POST incoming emails as MIME data to this endpoint. The webhook is authenticated via the `X-Webhook-Secret` header to prevent unauthorized access.

### 3. Running the App

#### Option A: Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts three services:
- **app** (Flask + Gunicorn) on port 8765
- **worker** (Celery) for async task processing
- **redis** (message broker)

View logs:
```bash
docker-compose logs -f app
docker-compose logs -f worker
```

Stop services:
```bash
docker-compose down
```

#### Option B: Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis:
   ```bash
   redis-server
   ```

3. Start Celery worker (in a separate terminal):
   ```bash
   celery -A mailgun.queue.celery worker --loglevel=info
   ```

4. Run the app:
   ```bash
   python -m mailgun.app
   ```

## How It Works

1. Mailgun receives an inbound email
2. Mailgun's route forwards it as a POST request to `/mailgun-inbound-mime`
3. The endpoint validates the webhook secret
4. Email is queued for async delivery via Celery
5. Worker connects to your internal SMTP server on the configured port
6. Email is delivered with automatic retries (up to 3 attempts with exponential backoff)

## API

### POST /mailgun-inbound-mime

Receives inbound emails from Mailgun.

**Request:**
- Form data with fields: `body-mime`, `sender`, `recipient`
- Header: `X-Webhook-Secret` (if `WEBHOOK_SECRET` is configured)

**Response:**
- 202 Accepted - Email queued for delivery
- 400 Bad Request - Missing required fields
- 403 Forbidden - Invalid webhook secret

## Logging

The application logs key events:
- Incoming email receipts
- Authentication failures
- Queue status
- Delivery successes and failures with retry information

Logs are output to stdout (visible in container logs or console).

## Notes

- Large attachments (up to 300MB) are supported but require sufficient memory/resources
- Email delivery is retried up to 3 times with exponential backoff
- SMTP timeout is set to 600 seconds to handle slow connections
- All environment variables are required except `WEBHOOK_SECRET` (optional, but recommended for security)
