# Football DB

A production-style backend project built with **FastAPI** and **PostgreSQL**, using the [Kaggle European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer) as its data source. Built as a second full CRUD backend project (after [kpop-db-project](https://github.com/nmf-wasi)) to practice production patterns: auth, role-based access, rate limiting, migrations, testing, and containerization — end to end.

This is a CRUD API over the football data (players, teams, leagues, matches, countries), **not** a prediction/ML project — betting odds and player position coordinates from the raw dataset were deliberately left out of scope, as they're outside the core domain model.

## Features

- **FastAPI** REST API with routers for Countries, Leagues, Teams, Players, Matches, and Users
- **JWT authentication** (access + refresh tokens) with **role-based access control** (`user` / `admin`)
- **Rate limiting** middleware backed by Redis
- Centralized logging and a global exception handler
- **Alembic** migrations for schema versioning
- **Pytest** test suite (organized by resource via custom markers)
- Fully **Dockerized** (API + Postgres + Redis via Docker Compose)
- **CI pipeline** (GitHub Actions): runs the test suite against live Postgres/Redis services, then builds and smoke-tests the Docker image

## Tech Stack

| Layer | Tool |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL |
| ORM / migrations | SQLAlchemy + Alembic |
| Caching / rate limiting | Redis |
| Auth | JWT (python-jose), bcrypt password hashing |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |

## Project Structure

```
app/
├── config/         # Settings (pydantic-settings)
├── core/           # Logging setup
├── database/       # DB session/engine setup
├── middleware/     # Rate limiting, request logging
├── models/         # SQLAlchemy models (football.py, user.py)
├── routers/        # API endpoints (players, teams, matches, leagues, country, users)
├── schemas/        # Pydantic request/response schemas
├── scripts/        # Utility/data-loading scripts
├── security/       # Password hashing, JWT handling
├── src/            # App entrypoint (main.py)
└── test/           # Pytest test suite

alembic/             # Migration environment and versions
notebooks/           # EDA and data inspection notebooks
data/                # Cleaned dataset
```

## Getting Started (Docker — recommended)

**Requirements:** Docker and Docker Compose installed.

1. Clone the repo:
   ```bash
   git clone https://github.com/nmf-wasi/Football-DB.git
   cd Football-DB
   ```

2. Create a `.env` file in the project root with at least:
   ```
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ```

3. Build and start everything (API, Postgres, Redis):
   ```bash
   docker compose up --build
   ```

4. In a second terminal, run the database migrations (first run only, or after new migrations are added):
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. Open the interactive API docs:
   ```
   http://localhost:8000/docs
   ```

### Stopping / resetting

```bash
docker compose down       # stop containers
docker compose down -v    # also wipe the Postgres volume (fresh DB on next start)
```

## Running Tests

Tests run against `TEST_DATABASE_URL` (a separate `football_test` database, created automatically on first Postgres init via `init-test-db.sh`):

```bash
docker compose exec api pytest
```

Tests are organized with custom markers per resource (e.g. `-m players`, `-m user`) — see `pytest.ini` for the full list.

## Authentication & Roles

- `POST /api/users/create_user` — register a new user (default role: `user`)
- `POST /api/users/login` — returns access + refresh tokens
- `POST /api/users/refresh` — refresh an access token
- `GET /api/users/me` — current user info
- `PATCH /api/users/{user_id}/role` — promote/change a user's role (**admin only**)

Write access to core resources (e.g. creating players) is restricted to `admin` users. To bootstrap your first admin locally:

```bash
docker compose exec db psql -U postgres -d football_db
```
```sql
UPDATE users SET user_role = 'admin' WHERE username = 'your_username';
```

## CI

On every push/PR to `main`, GitHub Actions:
1. Spins up Postgres and Redis as service containers
2. Installs dependencies and runs Alembic migrations
3. Runs the full pytest suite
4. Builds the Docker image and runs a smoke test to confirm it starts cleanly

See `.github/workflows/ci.yml`.

## Data Source

[European Soccer Database (Kaggle)](https://www.kaggle.com/datasets/hugomathien/soccer) — ~25,000+ matches, player & team attributes across major European leagues. EDA and data-cleaning steps are documented in `notebooks/`.

---
Built by [Wasi](https://github.com/nmf-wasi)
