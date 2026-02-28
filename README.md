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
- **AI** — Google Gemini (`google-genai`) via AI Studio — task recommendations

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
    ├── mail.py                  # Flask-Mail: send_task_created() + send_task_completed()
    ├── blueprints/
    │   ├── tasks.py             # /tasks CRUD + /tasks/archived + /tasks/ai-suggest
    │   ├── reminders.py         # /reminders list route
    │   └── subscribers.py       # /subscribers CRUD routes
    ├── sql/
    │   └── schema.sql           # Idempotent schema + updated_at triggers
    ├── static/
    │   └── assets/img/
    │       ├── logo_raw.png     # Logo embedded in notification emails
    │       └── giphy.gif        # Loading gif shown in the AI modal
    └── templates/
        ├── base.html
        ├── tasks/
        │   ├── list.html
        │   ├── archived.html
        │   ├── detail.html
        │   └── form.html        # Includes AI recommendation modal + JS
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

# AI (optional — skip to disable AI recommendations)
GEMINI_API_KEY=your-gemini-api-key
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
| POST | `/tasks/new` | Create task + send creation email to active subscribers |
| GET | `/tasks/<id>` | Task detail |
| GET | `/tasks/<id>/edit` | Edit form |
| POST | `/tasks/<id>/edit` | Update task |
| POST | `/tasks/<id>/toggle` | Toggle completed + send completion email if marked done |
| POST | `/tasks/ai-suggest` | Call Gemini and return AI recommendation (JSON) |
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

Two types of HTML emails are sent to all **active subscribers**:

| Trigger | Subject |
|---|---|
| Task created | `[TaskFlow] New task: <title>` |
| Task marked complete | `[TaskFlow] Task completed: <title>` |

Both emails include the app logo embedded inline (CID attachment), relevant task fields, and the AI recommendation if one was generated. A plain-text fallback is always included.

Recipients are managed entirely from the `/subscribers` interface — no hardcoded addresses in `.env`.

**Gmail setup:**
1. Enable 2-Step Verification on your Google Account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create an App Password for "Mail"
4. Use that 16-character password as `MAIL_PASSWORD` in `.env`

> Email is **optional** — if `MAIL_USERNAME` is empty, all notifications are silently skipped.

---

## AI Recommendations

When creating a task, a modal asks whether to get an AI recommendation from **Gemini 2.0 Flash**. While the model responds, a loading gif is shown. The recommendation is:

- Stored in the `ai_recommendation` column of the `tasks` table
- Displayed in the task detail view
- Included in the creation email sent to subscribers

> AI is **optional** — if `GEMINI_API_KEY` is not set, the modal shows an error state and lets the user save the task without a recommendation.

Get a free API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id                SERIAL PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    body              TEXT,
    completed         BOOLEAN NOT NULL DEFAULT FALSE,
    archived          BOOLEAN NOT NULL DEFAULT FALSE,
    reminder_at       TIMESTAMPTZ,
    reminder_note     TEXT,
    ai_recommendation TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
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

Both tables have an `updated_at` trigger. The `ai_recommendation` column is added via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` so existing databases migrate automatically on next startup.

---

## Key Design Decisions

- **Archive over delete** — tasks are never deleted; `archived = TRUE` hides them from the main list. Restorable from the Archived panel.
- **No ORM** — raw SQL via psycopg2 with `RealDictCursor` (rows come back as dicts).
- **Schema auto-init** — `init_db()` runs `schema.sql` on every startup; safe because the schema is idempotent. If the DB is unreachable at startup, logs a warning and continues.
- **DB error handling** — `psycopg2.OperationalError` is caught globally and renders a friendly 503 page instead of crashing.
- **Subscribers over hardcoded recipients** — notification targets are stored in the `subscribers` table and managed from the UI. No email addresses in `.env`.
- **Shared mail helper** — `_send()` centralizes subscriber querying, logo attachment, and error handling. `send_task_created` and `send_task_completed` each only build their own content.
- **AI recommendation modal** — JS intercepts the new-task form submit, shows a modal with a loading gif (`giphy.gif`), calls `POST /tasks/ai-suggest`, and lets the user accept or skip before the form is actually submitted.
- **Everything optional** — email and AI features degrade gracefully if their respective env vars are missing.

---

## Useful Commands

```bash
# Stop PostgreSQL
docker compose down

# Stop and wipe the database volume (fresh start)
docker compose down -v
```
