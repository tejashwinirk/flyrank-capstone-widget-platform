# Build Log

## Project

FlyRank Lead Capture Platform

Author: Tejashwini R.K.

## Phase 1 — Project Setup

- Created a new public GitHub repository.
- Created the FastAPI application structure.
- Added application, API, service, database, migration, test, and documentation directories.
- Added `.gitignore`.
- Added `.env.example`.
- Added Python dependencies.

## Phase 2 — PostgreSQL

- Started PostgreSQL using Docker.
- Created a dedicated `flyrank_capstone` database.
- Added the initial database migration.
- Created tenant, widget, and submission tables.
- Added indexes for common tenant, widget, and submission queries.

## Phase 3 — Authentication

- Added tenant registration.
- Added password hashing using Argon2.
- Added login endpoint.
- Added JWT access tokens.
- Added authentication dependencies for protected endpoints.

## Phase 4 — Widget Management

- Added authenticated widget creation.
- Added widget listing.
- Added individual widget retrieval.
- Added widget updates.
- Added widget deletion.
- Added widget type validation.
- Added widget status validation.
- Added widget version increments.
- Added tenant isolation.

## Phase 5 — Public Widget Delivery

- Added public widget configuration endpoint.
- Added versioned configuration.
- Added embed snippet generation.
- Added JavaScript embed endpoint.
- Added in-memory widget caching.
- Added cache invalidation after widget updates and deletion.

## Phase 6 — Public Lead Submission

- Added public submission endpoint.
- Added Pydantic request validation.
- Added 64 KB request-size protection.
- Added CORS support.
- Added honeypot protection.
- Added IP and widget-based rate limiting.
- Added database-backed idempotency.

## Phase 7 — Geo Enrichment

- Added primary IP geolocation provider.
- Added secondary provider fallback.
- Added graceful handling when both providers fail.
- Geo enrichment failure does not prevent lead storage.

## Phase 8 — Background Processing

- Added background notification job.
- Added retry handling.
- Added increasing retry delays.
- Added permanent failure logging and alerts.
- Kept notification processing outside the submission response path.

## Phase 9 — Dashboard

- Added authenticated submission listing.
- Added widget filtering.
- Added pagination.
- Added submission analytics.
- Added country aggregation.
- Added daily submission aggregation.

## Phase 10 — Evaluation

Manually verified:

- Health endpoint
- Authentication
- Widget CRUD
- Public widget delivery
- Embed snippet
- Valid submission
- Dashboard
- Idempotency
- Malformed request validation
- Honeypot protection
- Rate limiting

All listed manual evaluation flows passed.

## Phase 11 — Documentation

Added:

- `README.md`
- `capstone.yaml`
- `EVIDENCE.md`
- `BUILDLOG.md`
- `.env.example`

## Current Status

Core capstone functionality is implemented and manually evaluated.

The project runs locally using:

```bash
python -m uvicorn app.main:app --port 8001