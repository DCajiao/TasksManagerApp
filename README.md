# TasksManagerApp
Yes, another useless application for managing tasks just to implement a CRUD to a database.

---

## Stack

- **Python** 3.11+ — managed with [uv](https://docs.astral.sh/uv/)
- **Web** — Flask 3.x with Blueprints
- **Database** — PostgreSQL via Docker Compose
- **DB connector** — psycopg2-binary + raw SQL (no ORM)
- **Config** — python-dotenv (`.env` file)
- **Frontend** — Jinja2 templates + Tailwind CSS CDN (dark mode)

---

## Project Structure

```
TasksManagerApp/
├── main.py                  # Entrypoint
├── docker-compose.yml       # PostgreSQL service
├── .env                     # Local credentials (DO NOT commit)
├── .env.example             # Template for .env
├── pyproject.toml           # Dependencies
└── src/
    ├── app.py               # Flask app factory (create_app)
    ├── db.py                # psycopg2 helpers: get_db, close_db, init_db
    ├── blueprints/
    │   ├── tasks.py         # /tasks CRUD routes
    │   └── reminders.py     # /reminders list route
    ├── sql/
    │   └── schema.sql       # Idempotent schema + updated_at trigger
    └── templates/
        ├── base.html
        ├── tasks/
        │   ├── list.html
        │   ├── detail.html
        │   └── form.html
        └── reminders/
            └── list.html
```

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

The `.env` file expects:

```env
DATABASE_URL=postgresql://tasksuser:taskspass@localhost:5432/tasksdb
FLASK_SECRET_KEY=your-secret-key
POSTGRES_USER=tasksuser
POSTGRES_PASSWORD=taskspass
POSTGRES_DB=tasksdb
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Run the app

```bash
uv run flask --app src/app:create_app run --debug
```

The database schema initializes automatically on startup. Open `http://localhost:5000`.

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Redirects to `/tasks` |
| GET | `/tasks` | List active tasks |
| GET | `/tasks/new` | New task form |
| POST | `/tasks/new` | Create task |
| GET | `/tasks/<id>` | Task detail |
| GET | `/tasks/<id>/edit` | Edit form |
| POST | `/tasks/<id>/edit` | Update task |
| POST | `/tasks/<id>/toggle` | Toggle completed |
| POST | `/tasks/<id>/archive` | Soft-delete (archive) |
| GET | `/reminders` | List tasks with reminders |

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    body        TEXT,
    completed   BOOLEAN NOT NULL DEFAULT FALSE,
    archived    BOOLEAN NOT NULL DEFAULT FALSE,
    reminder_at TIMESTAMPTZ,
    reminder_note TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

An `updated_at` trigger updates the timestamp automatically on every row update.

---

## Key Design Decisions

- **Archive over delete** — tasks are never deleted; `archived = TRUE` hides them from all views.
- **No ORM** — raw SQL via psycopg2 with `RealDictCursor` (rows come back as dicts).
- **Schema auto-init** — `init_db()` runs `schema.sql` on every startup; safe because the schema is idempotent.
- **Blueprints** — `tasks` and `reminders` are registered as Flask Blueprints for modularity.

---

## Useful Commands

```bash
# Stop PostgreSQL
docker compose down

# Stop and wipe the database volume (fresh start)
docker compose down -v
```
