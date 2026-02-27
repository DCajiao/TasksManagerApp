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
- **Email** — Flask-Mail via Gmail SMTP (free)

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
    ├── mail.py              # Flask-Mail setup + send_task_created()
    ├── blueprints/
    │   ├── tasks.py         # /tasks CRUD routes + /tasks/archived
    │   └── reminders.py     # /reminders list route
    ├── sql/
    │   └── schema.sql       # Idempotent schema + updated_at trigger
    └── templates/
        ├── base.html
        ├── tasks/
        │   ├── list.html
        │   ├── archived.html
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

Edit `.env` with your values:

```env
DATABASE_URL=postgresql://tasksuser:taskspass@localhost:5432/tasksdb
FLASK_SECRET_KEY=your-secret-key
POSTGRES_USER=tasksuser
POSTGRES_PASSWORD=taskspass
POSTGRES_DB=tasksdb

# Email (optional — skip to disable notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your@gmail.com
NOTIFICATION_EMAIL=recipient@example.com
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
| POST | `/tasks/new` | Create task (sends email if configured) |
| GET | `/tasks/<id>` | Task detail |
| GET | `/tasks/<id>/edit` | Edit form |
| POST | `/tasks/<id>/edit` | Update task |
| POST | `/tasks/<id>/toggle` | Toggle completed |
| POST | `/tasks/<id>/archive` | Soft-delete (archive) |
| GET | `/tasks/archived` | List archived tasks |
| POST | `/tasks/<id>/unarchive` | Restore archived task |
| GET | `/reminders` | List tasks with reminders |

---

## Email Notifications

An email is sent to `NOTIFICATION_EMAIL` every time a task is created. This uses **Flask-Mail** over Gmail SMTP (free).

**Gmail setup:**
1. Enable 2-Step Verification on your Google Account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create an App Password for "Mail"
4. Use that 16-character password as `MAIL_PASSWORD` in `.env`

> Email is **optional** — if `MAIL_USERNAME` or `NOTIFICATION_EMAIL` are empty, notifications are silently skipped and the app works normally.

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

- **Archive over delete** — tasks are never deleted; `archived = TRUE` hides them from the main list. They can be restored from the Archived panel.
- **No ORM** — raw SQL via psycopg2 with `RealDictCursor` (rows come back as dicts).
- **Schema auto-init** — `init_db()` runs `schema.sql` on every startup; safe because the schema is idempotent.
- **Blueprints** — `tasks` and `reminders` are registered as Flask Blueprints for modularity.
- **Email is optional** — if mail vars are missing from `.env`, `send_task_created()` returns early without errors.

---

## Useful Commands

```bash
# Stop PostgreSQL
docker compose down

# Stop and wipe the database volume (fresh start)
docker compose down -v
```
