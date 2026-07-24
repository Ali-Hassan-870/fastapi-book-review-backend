# 📚 Bookly — Book Review REST API

A production-deployed backend for a book review platform, built with **FastAPI** and deployed on **Render** with a full CI/CD pipeline.

**Live API docs:** https://bookly-api-lwbf.onrender.com/docs
*(free-tier instance — the first request after idle takes ~30–50 s to wake up)*

## Features

- **JWT authentication** — signup, login, access + refresh tokens, and server-side token revocation via a Redis blocklist (logout actually invalidates the token)
- **Email verification & password reset** — tokenized email links rendered from HTML templates, sent as **Celery background tasks** through a Redis broker
- **Role-based access control** — `admin` / `user` roles enforced per-endpoint
- **Books CRUD** — create, list, detail, update, delete; books are owned by users
- **Reviews** — rate (1–5) and review any book
- **Tags** — tag books and browse by tag
- **Async SQLAlchemy/SQLModel** on PostgreSQL (asyncpg) with **Alembic** migrations, applied automatically on every deploy
- **Custom middleware & error handling** — request logging, trusted-host protection, CORS, and typed domain exceptions mapped to clean JSON error responses

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Database | PostgreSQL (Neon) via SQLModel/SQLAlchemy async + asyncpg |
| Migrations | Alembic |
| Auth | PyJWT, passlib/bcrypt |
| Background jobs | Celery + Redis (broker & result backend) |
| Email | fastapi-mail with Jinja2 HTML templates |
| Containerization | Docker |
| Hosting | Render (Docker web service + managed Redis), DB on Neon |
| CI/CD | GitHub Actions → Render deploy hook |

## Architecture

```
                        ┌────────────────────────────┐
 GitHub push → Actions  │  Render (Docker container) │
   CI: deps, import     │  ┌──────────┐ ┌──────────┐ │      ┌──────────┐
   check, image build   │  │ FastAPI  │ │  Celery  │ │ ───► │  Neon    │
   CD: deploy hook  ───►│  │ (uvicorn)│ │  worker  │ │      │ Postgres │
                        │  └────┬─────┘ └────┬─────┘ │      └──────────┘
                        └───────┼────────────┼───────┘
                                └────► Redis ◄┘
                              (Render Key Value)
```

The Celery worker runs inside the same container as the API (see `start.sh`) to fit Render's free tier; in a scaled production setup it would run as a separate worker service — the code requires no changes for that split.

## API Overview

All routes are prefixed with `/api/v1`. Interactive documentation with request/response schemas is available at [`/docs`](https://bookly-api-lwbf.onrender.com/docs).

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/signup`, `GET /auth/verify/{token}`, `POST /auth/login`, `GET /auth/refresh-token`, `GET /auth/me`, `GET /auth/logout`, `POST /auth/password-reset-request`, `POST /auth/password-reset-confirm/{token}` |
| Books | `GET/POST /books/`, `GET/PATCH/DELETE /books/{uid}`, `GET /books/user/{uid}` |
| Reviews | `POST /reviews/book/{book_uid}`, `GET /reviews/`, `GET /reviews/{uid}` |
| Tags | `GET /tags/`, `PUT /tags/{uid}` |

## Running Locally

**Prerequisites:** Python 3.12, Docker (for Redis), a PostgreSQL database.

```bash
# 1. Clone and install
git clone https://github.com/Ali-Hassan-870/fastapi-book-review-backend.git
cd fastapi-book-review-backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

# 2. Configure environment
#    Create a .env file (see the variable list below)

# 3. Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 4. Apply migrations
alembic upgrade head

# 5. Run the API
fastapi dev src

# 6. (optional) Run the Celery worker for emails
celery -A src.celery_tasks worker --loglevel=info --pool=solo
```

### Environment variables (`.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` |
| `REDIS_URL` | e.g. `redis://localhost:6379/0` |
| `JWT_SECRET`, `JWT_ALGORITHM` | Access/refresh token signing |
| `EMAIL_TOKEN_SECRET` | Signing secret for email verification / password reset links |
| `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_FROM`, `MAIL_FROM_NAME` | SMTP settings |
| `DOMAIN` | Public hostname used in emailed links |

### Run with Docker

```bash
docker build -t bookly .
docker run -p 8000:8000 --env-file .env bookly
```

## Deployment & CI/CD

- **`render.yaml`** is a Render Blueprint that provisions the web service and a managed Redis instance, wiring `REDIS_URL` automatically.
- **GitHub Actions** (`.github/workflows/ci-cd.yml`) runs on every push/PR: installs dependencies, sanity-checks the app, and builds the Docker image. On pushes to `main` that pass CI, it triggers a Render deploy via deploy hook — Render's own auto-deploy is disabled, so broken commits never ship.
- Database migrations run automatically at container startup (`alembic upgrade head` in `start.sh`).
