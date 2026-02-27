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
- **Email** — Flask-Mail via Gmail SMTP — HTML email with embedded logo

---

## Project Structure

```
TasksManagerApp/
├── main.py                      # Entrypoint
├── docker-compose.yml           # PostgreSQL service
├── .env                         # Local credentials (DO NOT commit)
├── .env.example                 # Template for .env
├── pyproject.toml               # Dependencies
└── src/
    ├── app.py                   # Flask app factory (create_app)
    ├── db.py                    # psycopg2 helpers: get_db, close_db, init_db
    ├── mail.py                  # Flask-Mail setup + send_task_created()
    ├── blueprints/
    │   ├── tasks.py             # /tasks CRUD routes + /tasks/archived
    │   ├── reminders.py         # /reminders list route
    │   └── subscribers.py       # /subscribers CRUD routes
    ├── sql/
    │   └── schema.sql           # Idempotent schema + updated_at triggers
    ├── static/
    │   └── assets/img/
    │       └── logo_raw.png     # Logo embedded in notification emails
    └── templates/
        ├── base.html
        ├── tasks/
        │   ├── list.html
        │   ├── archived.html
        │   ├── detail.html
        │   └── form.html
        ├── reminders/
        │   └── list.html
        ├── subscribers/
        │   ├── list.html
        │   └── form.html
        └── errors/
            └── db_down.html     # 503 page when PostgreSQL is unreachable
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
| POST | `/tasks/new` | Create task + send email to active subscribers |
| GET | `/tasks/<id>` | Task detail |
| GET | `/tasks/<id>/edit` | Edit form |
| POST | `/tasks/<id>/edit` | Update task |
| POST | `/tasks/<id>/toggle` | Toggle completed |
| POST | `/tasks/<id>/archive` | Soft-delete (archive) |
| GET | `/tasks/archived` | List archived tasks |
| POST | `/tasks/<id>/unarchive` | Restore archived task |
| GET | `/reminders` | List tasks with reminders |
| GET | `/subscribers` | List subscribers |
| GET | `/subscribers/new` | New subscriber form |
| POST | `/subscribers/new` | Create subscriber |
| GET | `/subscribers/<id>/edit` | Edit subscriber |
| POST | `/subscribers/<id>/edit` | Update subscriber |
| POST | `/subscribers/<id>/toggle` | Activate / deactivate subscriber |

---

## Email Notifications

When a task is created, an HTML email is sent to all **active subscribers**. The email includes the app logo (embedded inline), task title, status, description, and reminder if set. It also includes a plain-text fallback for clients that don't render HTML.

Recipients are managed entirely from the `/subscribers` interface — no hardcoded addresses needed.

This uses **Flask-Mail** over Gmail SMTP (free).

**Gmail setup:**
1. Enable 2-Step Verification on your Google Account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create an App Password for "Mail"
4. Use that 16-character password as `MAIL_PASSWORD` in `.env`

> Email is **optional** — if `MAIL_USERNAME` is empty, notifications are silently skipped and the app works normally.

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

```sql
CREATE TABLE IF NOT EXISTS subscribers (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Both tables have an `updated_at` trigger that updates the timestamp automatically on every row update.

---

## Key Design Decisions

- **Archive over delete** — tasks are never deleted; `archived = TRUE` hides them from the main list. Restorable from the Archived panel.
- **No ORM** — raw SQL via psycopg2 with `RealDictCursor` (rows come back as dicts).
- **Schema auto-init** — `init_db()` runs `schema.sql` on every startup; safe because the schema is idempotent. If the DB is unreachable at startup, logs a warning and continues.
- **DB error handling** — `psycopg2.OperationalError` is caught globally and renders a friendly 503 page instead of crashing.
- **Subscribers over hardcoded recipients** — notification targets are stored in the `subscribers` table and managed from the UI. No email addresses in `.env`.
- **HTML email with embedded logo** — `send_task_created()` sends a styled HTML email with the app logo attached inline (CID), plus a plain-text fallback.
- **Email is optional** — if `MAIL_USERNAME` is missing from `.env`, `send_task_created()` returns early without errors.

---

## Useful Commands

```bash
# Stop PostgreSQL
docker compose down

# Stop and wipe the database volume (fresh start)
docker compose down -v
```
