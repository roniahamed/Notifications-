# Notification System Product Guide

Welcome to the Background Job-Based Notification System. This platform allows you to schedule notifications for any specific time in the future, automatically delivering them to users via Email, in-app WebSocket, and Firebase Cloud Messaging (FCM).

Live docs: https://notification.roniahamed.com/api/schema/swagger-ui/

## Product Overview and Features

* Multi-Channel Delivery: Send notifications through Email, real-time WebSocket, and mobile push notifications (FCM) simultaneously.
* Smart Scheduling: Leveraging Celery and Redis, the system accurately processes background jobs to send notifications at the exact scheduled time.
* Automatic Retry Mechanism: In the event of a delivery failure, the system automatically retries up to 3 times before updating the status to permanently failed.
* Secure Authentication: The system utilizes JSON Web Tokens (JWT) and Email OTP verification to ensure secure user registration and login.
* Advanced Tracking and History: A complete notification history is available, featuring pagination, search functionality, and status-based filtering.

## User Guide

### 1. Account Creation and Verification
To use the system, you must first create an account and verify your identity.
* Registration: Make a POST request to `https://notification.roniahamed.com/api/auth/register/` with your email and password.
* OTP Verification: A 6-digit OTP will be sent to your registered email. Submit it to `https://notification.roniahamed.com/api/auth/verify-otp/` to activate the account.
* Login: Login at `https://notification.roniahamed.com/api/auth/login/` to receive your Access Token. This token is required for all subsequent API requests.

### 2. Scheduling a Notification
To schedule a new notification, send a POST request with the required details.
URL: `https://notification.roniahamed.com/api/notifications/`

Request Body (JSON):
```json
{
  "title": "Welcome to our platform!",
  "message": "We are very glad to have you here.",
  "scheduled_time": "2026-10-15T10:30:00Z"
}
```
Note: The `scheduled_time` must be in the future. Past times will be rejected by the system.

### 3. Viewing Notification History
You can retrieve a list of all your scheduled notifications and their current statuses using a GET request.
URL: `https://notification.roniahamed.com/api/notifications/history/`

Query Parameters for Filtering and Searching:
* View specific statuses: `?status=PENDING`, `SENT`, or `FAILED`
* Search by title or message: `?search=Welcome`
* Pagination and sorting: `?page=1&ordering=-created_at`

### 4. Manual Retry for Failed Jobs
If a notification fails automatically 3 times (status: PERMANENTLY_FAILED), users have the option to manually retry sending it.
URL: `POST https://notification.roniahamed.com/api/notifications/<id>/retry/`

## Integration Guide for Frontend Developers

### In-App Real-Time Notifications (WebSocket)
To receive live notifications on a website or application, connect to the WebSocket endpoint:

```javascript
const accessToken = "your_login_access_token";
const socket = new WebSocket(`wss://notification.roniahamed.com/ws/notifications/?token=${accessToken}`);

socket.onopen = function(e) {
  console.log("Connected to Notification Server");
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(`New Notification Alert! Title: ${data.title}, Message: ${data.message}`);
};

socket.onclose = function(event) {
  console.log(event.wasClean ? "Connection closed gracefully" : "Connection died");
};
```

### Mobile Push Notifications (FCM)
To receive Firebase push notifications on a mobile device or browser, the user's FCM token must be saved to the system.
URL: `PATCH https://notification.roniahamed.com/api/auth/fcm-token/`
```json
{
  "fcm_token": "your_device_fcm_token_here"
}
```

## Setup and Deployment

### Technology Stack
* Django 5 + Django REST Framework
* Celery + Redis for background task scheduling
* PostgreSQL Database
* Django Channels for WebSockets
* Firebase Admin SDK for FCM push notifications
* Docker Compose for deployment

### Local Development Quick Start

```bash
cp .env.example .env
# Fill in EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, SECRET_KEY in the .env file.
# Place your Firebase serviceAccountKey.json in the project root directory.

chmod +x docker-up.sh entrypoint.sh
./docker-up.sh
```

## API Documentation
The system provides a comprehensive API dashboard for testing all endpoints directly from the browser.
Swagger API Documentation: https://notification.roniahamed.com/api/schema/swagger-ui/

Note: Ensure you authenticate in Swagger UI by clicking the Authorize button and providing your JWT token in the format `Bearer <token>`.
