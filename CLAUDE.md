# TasksManagerApp

Flask + PostgreSQL task manager with CRUD and soft-delete (archive).

## Stack

- **Python**: 3.11+, managed with `uv`
- **Web**: Flask with Blueprints (`tasks`, `reminders`)
- **DB**: PostgreSQL via Docker, `psycopg2-binary` with raw SQL (no ORM)
- **Config**: `python-dotenv` — credentials loaded from `.env`
- **Frontend**: Jinja2 templates + Tailwind CSS CDN

## Project Structure

```
TasksManagerApp/
├── main.py                  # Entrypoint: imports create_app from src/app.py
├── docker-compose.yml       # PostgreSQL service
├── .env                     # Local credentials (DO NOT commit)
├── .env.example             # Template for .env
├── pyproject.toml           # Dependencies (uv)
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

## Development Commands

```bash
# Install dependencies
uv sync

# Start PostgreSQL
docker compose up -d

# Run the app (schema auto-initializes on startup)
uv run flask --app src/app:create_app run --debug

# Stop PostgreSQL
docker compose down

# Stop + remove volumes (fresh DB)
docker compose down -v
```

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

## Key Decisions

- **Archive over delete**: tasks are never deleted; `archived=TRUE` hides them
- **No ORM**: raw SQL via `psycopg2` with `RealDictCursor` (rows as dicts)
- **Schema init at startup**: `init_db()` runs `schema.sql` every time (idempotent)
- **`.env` must not be committed**: add to `.gitignore`
