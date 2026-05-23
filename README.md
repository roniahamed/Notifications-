# Background Job Notification System

A Django REST Framework backend for scheduling notifications delivered via **Email**, **WebSocket**, and **Firebase Cloud Messaging**.

## Stack

- Django 5 + DRF
- Celery + Redis (background job scheduling)
- PostgreSQL
- Django Channels (WebSocket)
- Firebase Admin SDK (FCM push)
- Docker Compose

## Quick Start

```bash
cp .env.example .env
# Fill in EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, SECRET_KEY
# Place your Firebase serviceAccountKey.json in the project root

chmod +x docker-up.sh entrypoint.sh
./docker-up.sh
```

## API Endpoints

### Auth — `/api/auth/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/register/` | Register new user |
| POST | `/verify-otp/` | Verify email OTP |
| POST | `/resend-otp/` | Resend OTP |
| POST | `/login/` | Login → JWT tokens |
| POST | `/logout/` | Blacklist refresh token |
| POST | `/token/refresh/` | Refresh access token |
| POST | `/forgot-password/` | Send reset token via email |
| POST | `/reset-password/` | Reset password with token |
| PATCH | `/fcm-token/` | Update FCM device token |

### Notifications — `/api/notifications/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/` | Create & schedule notification |
| GET | `/history/` | List my notifications (paginated, filterable) |
| GET | `/<id>/` | Get notification detail |
| POST | `/<id>/retry/` | Manually retry failed notification |

#### List query params
- `?status=PENDING|SENT|FAILED|PERMANENTLY_FAILED`
- `?search=<query>` — searches title & message
- `?ordering=scheduled_time|-created_at`
- `?page=1&page_size=10`

### WebSocket

```
ws://localhost:8000/ws/notifications/?token=<access_token>
```

Receives real-time JSON messages:
```json
{"type": "notification", "notification_id": 1, "title": "...", "message": "..."}
```

## Notification Flow

```
POST /api/notifications/
  → validated (future time only)
  → Celery task scheduled with eta
  → At scheduled time:
      → Email sent (SMTP)
      → WebSocket push to user group
      → FCM push notification
  → Status: PENDING → SENT
  
On failure:
  → Retry up to 3× (60s, 120s, 240s backoff)
  → After 3 failures: PERMANENTLY_FAILED
```

## Environment Variables

See `.env.example` for all required variables.

## Firebase Setup

1. Go to Firebase Console → Project Settings → Service Accounts
2. Generate new private key → download `serviceAccountKey.json`
3. Place in project root (mounted into container as `/app/serviceAccountKey.json`)
# Notifications-
