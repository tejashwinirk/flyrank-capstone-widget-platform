# FlyRank Lead Capture Platform

An embeddable lead-capture widget platform built with FastAPI and PostgreSQL.

The platform allows authenticated owners to create and manage lead-capture widgets, generate embeddable JavaScript snippets, receive public submissions from other origins, protect endpoints against abuse, enrich submissions with IP-based geolocation, and view captured leads through dashboard APIs.

## Features

- JWT-based owner authentication
- Tenant-isolated widget management
- Widget CRUD operations
- Widget versioning
- Public widget configuration endpoint
- Embeddable JavaScript widget
- Cross-origin lead submission
- Pydantic request validation
- Request body size protection
- Per-IP/per-widget rate limiting
- Honeypot spam protection
- Idempotency keys for duplicate-submission protection
- IP geolocation with provider fallback
- Submission persistence in PostgreSQL
- Background notification job
- Notification retries and failure logging
- Dashboard submission listing
- Submission analytics
- Docker PostgreSQL support
- Migration-based database schema

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- psycopg
- JWT
- Argon2 password hashing
- SlowAPI
- HTTPX
- Docker

## Project Structure

```text
flyrank-capstone-widget-platform/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── public_widgets.py
│   │   ├── submissions.py
│   │   └── widgets.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── background_jobs.py
│   │   ├── geo_service.py
│   │   ├── notification_service.py
│   │   ├── public_widget_service.py
│   │   ├── rate_limit.py
│   │   └── widget_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── docs/
│   └── test-widget.html
│
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_auth_fields.sql
│   └── 003_submission_idempotency.sql
│
├── tests/
│
├── .env.example
├── .gitignore
├── BUILDLOG.md
├── EVIDENCE.md
├── LICENSE
├── capstone.yaml
└── requirements.txt

## Setup
1. Clone the repository
git clone https://github.com/tejashwinirk/flyrank-capstone-widget-platform.git
cd flyrank-capstone-widget-platform

2. Create a virtual environment

Windows:
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables

Create a .env file from .env.example.

Example:

DATABASE_URL=postgresql://postgres:dev@localhost:5432/flyrank_capstone
GEO_PROVIDER_A_URL=https://ip-api.com/json
GEO_PROVIDER_B_URL=https://ipapi.co
JWT_SECRET=change-this-secret

Never commit .env or production secrets.

## Database

The project uses PostgreSQL.

The migration files are located in:

migrations/

Run them in order:

psql "$DATABASE_URL" -f migrations/001_initial_schema.sql
psql "$DATABASE_URL" -f migrations/002_add_auth_fields.sql
psql "$DATABASE_URL" -f migrations/003_submission_idempotency.sql

For local development, PostgreSQL can also be run using Docker.

Example:

docker run --name flyrank-postgres \
  -e POSTGRES_PASSWORD=dev \
  -p 5432:5432 \
  -d postgres

Create the application database:

docker exec -it flyrank-postgres \
  psql -U postgres \
  -c "CREATE DATABASE flyrank_capstone;"

## Run the API

Start the FastAPI application with:

python -m uvicorn app.main:app --port 8001

The API will be available at:

http://127.0.0.1:8001

Swagger documentation:

http://127.0.0.1:8001/docs

Health check:

http://127.0.0.1:8001/health

Expected health response:

{
  "status": "ok"
}

## Authentication

Register an owner:

POST /auth/register

Example:

{
  "name": "Example Owner",
  "email": "owner@example.com",
  "password": "TestPass123"
}

Login:

POST /auth/login

The response contains a JWT access token.

Protected endpoints require:

Authorization: Bearer <access_token>

## Widget Management

Authenticated owners can:

POST   /widgets/
GET    /widgets/
GET    /widgets/{widget_id}
PATCH  /widgets/{widget_id}
DELETE /widgets/{widget_id}

Supported widget types:

signup
contact
cta
popover

Widget statuses:

active
inactive

Updating a widget increments its version number.

## Public Widget Delivery

Public widget configuration:

GET /public/widgets/{widget_id}

Embed snippet:

GET /public/widgets/{widget_id}/embed

JavaScript bundle:

GET /public/embed/{widget_id}.js

Example generated embed:

<script
  src="http://127.0.0.1:8001/public/embed/WIDGET_ID.js"
  data-widget-id="WIDGET_ID"
  async>
</script>

The public widget configuration is cached in memory for faster repeated delivery. Widget updates and deletion invalidate the corresponding cache entry.

## Public Submissions

Lead submissions are accepted through:

POST /public/widgets/{widget_id}/submissions

Example:

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "I would like more information",
  "website": ""
}

Successful submissions return:

201 Created

## Protection
Request validation

Invalid fields are rejected using Pydantic validation.

Example invalid email:

{
  "name": "Test",
  "email": "not-an-email"
}

returns a `422 Unprocessable Entity` validation response.

Request size limit

Requests larger than 64 KB are rejected with:

413 Request Entity Too Large
Rate limiting

Public submissions are limited to:

5 requests per minute per IP + widget

Excess requests receive:

429 Too Many Requests

## Honeypot

The public form contains a hidden website field.

A submission that fills this field is treated as a bot submission and acknowledged without creating a normal lead record.

## Idempotency

Clients can provide:

Idempotency-Key

When the same key is reused for the same widget, the existing submission is returned instead of creating a duplicate.

## Geolocation

Submission IP addresses are enriched using two providers.

Provider A is attempted first.

If it fails, Provider B is attempted.

If both providers fail, the submission is still stored with unknown geographic fields.

Geolocation failure therefore does not prevent lead capture.

## Background Notifications

After a submission is successfully stored, a background notification job is queued.

The worker:

- runs outside the request-response path
- retries failed notification attempts
- uses increasing retry delays
- logs permanent failures as alerts

Notification processing is isolated from the submission request, so a notification failure does not cause an already-stored submission to fail.

## Dashboard
Authenticated owners can access:

GET /dashboard/submissions
GET /dashboard/analytics

Submissions can optionally be filtered by widget.

Dashboard queries are tenant-scoped using the tenant ID from the authenticated JWT.

## Cross-Origin Test Page

A plain HTML page is provided at:

docs/test-widget.html

It represents a separate website origin and loads the public widget JavaScript from the API server.

Serve the docs directory with a simple HTTP server if required:

python -m http.server 5500 --directory docs

Then open:

http://127.0.0.1:5500/test-widget.html

Replace WIDGET_ID in the page with an active widget ID.

## Evaluation Checks

The implementation was manually verified for:

Authentication
Widget creation
Public widget delivery
Embed snippet generation
Valid lead submission
Dashboard submission retrieval
Idempotency
Malformed request validation
Honeypot handling
Rate limiting
Tenant-scoped dashboard access

## Security Notes

.env is ignored by Git.
.env.example contains no secrets.
Passwords are stored as Argon2 password hashes.
JWTs contain the authenticated tenant ID.
Widget management queries require tenant ownership.
Dashboard queries are tenant-scoped.
Public endpoints expose only the information required for widget delivery.
PostgreSQL parameterized queries are used for database operations.

## Author
Tejashwini R K

## License
This project is licensed under the MIT License.