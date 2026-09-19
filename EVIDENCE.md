# Evidence

## 1. Authentication

- Owner registration implemented.
- Owner login implemented.
- Passwords are hashed using Argon2.
- JWT access tokens are issued after successful login.
- Protected widget and dashboard endpoints require authentication.

## 2. Tenant Isolation

- Widgets are queried using both `widget_id` and authenticated `tenant_id`.
- Dashboard submissions are filtered by authenticated `tenant_id`.
- Owners cannot access widgets belonging to another tenant through protected endpoints.

## 3. Widget Management

Implemented authenticated CRUD operations:

- Create widget
- List widgets
- Get widget
- Update widget
- Delete widget

Supported widget types:

- signup
- contact
- cta
- popover

Supported statuses:

- active
- inactive

Widget versions increment when a widget is updated.

## 4. Public Widget Delivery

Implemented:

- Public widget configuration endpoint
- Versioned widget configuration
- Embed snippet generation
- JavaScript embed endpoint
- In-memory caching
- Cache invalidation after widget updates and deletion

## 5. Cross-Origin Submission

The platform supports public submissions from a separate origin.

The demo page is located at:

`docs/test-widget.html`

CORS is configured in the FastAPI application.

## 6. Request Validation

Pydantic validation is used for public submissions.

Tested malformed input:

- Empty name
- Invalid email

Result:

`422 Unprocessable Entity`

Request bodies are limited to 64 KB.

Oversized requests return:

`413 Request body too large`

## 7. Rate Limiting

Public submission requests are rate limited per IP address and widget.

Configured limit:

`5 requests per minute`

Repeated requests beyond the limit return:

`429 Too Many Requests`

## 8. Honeypot Protection

The public widget contains a hidden honeypot field named:

`website`

When the honeypot contains a value, the request is acknowledged but no lead record is created.

## 9. Idempotency

The submission endpoint supports the:

`Idempotency-Key`

header.

Repeated submissions using the same widget and idempotency key return the original submission instead of creating a duplicate record.

Verified manually using:

`capstone-test-001`

The first request created a submission and the second request returned:

`"idempotent": true`

## 10. Geo Enrichment

Submission IP addresses are passed to a primary geo provider.

If the primary provider fails, the platform attempts a secondary provider.

If both providers fail, the submission is still stored with empty geo fields.

## 11. Background Notifications

After a submission is stored successfully, a background notification job is queued.

The worker:

- runs outside the request-response path
- retries failed notification attempts
- uses increasing retry delays
- logs permanent failures as alerts

A notification failure does not cause an already-stored submission to fail.

## 12. Dashboard

Authenticated dashboard endpoints provide:

- Submission listing
- Widget filtering
- Pagination
- Total submissions
- Spam submission count
- Country-based submission counts
- Daily submission counts

## 13. Manual Evaluation Results

The following flows were manually verified against the running FastAPI application:

| Test | Result |
|---|---|
| Health check | Passed |
| Owner login | Passed |
| Authenticated widget creation | Passed |
| Public widget delivery | Passed |
| Embed snippet generation | Passed |
| Valid public submission | Passed |
| Dashboard submission listing | Passed |
| Idempotency | Passed |
| Malformed submission validation | Passed |
| Honeypot protection | Passed |
| Rate limiting | Passed |

## 14. API Response Evidence

### Valid Submission

HTTP status:

`201 Created`

The API returned a submission ID and creation timestamp.

### Idempotent Submission

The repeated request returned the same submission ID with:

```json
{
  "idempotent": true
}

## Invalid Submission

HTTP status:

422 Unprocessable Entity

## Honeypot Submission

HTTP status:

200 OK

The response acknowledged the request without returning a submission ID.

## Rate-Limited Submission

HTTP status:

429 Too Many Requests

## 15. Database

PostgreSQL is used as the primary database.

Database migrations create:

tenants
widgets
submissions

Indexes are defined for tenant, widget, and submission lookup paths.

Submission idempotency is protected with a unique database index.

## 16. Local Run

Start the API with:

python -m uvicorn app.main:app --port 8001

Swagger documentation:

http://127.0.0.1:8001/docs

Health endpoint:

http://127.0.0.1:8001/health