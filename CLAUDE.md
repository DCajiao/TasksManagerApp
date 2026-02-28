# TasksManagerApp

Flask + PostgreSQL task manager with CRUD, soft-delete (archive), email notifications, subscriber management, and AI-powered task recommendations.

## Stack

- **Python**: 3.11+, managed with `uv`
- **Web**: Flask with Blueprints (`tasks`, `reminders`, `subscribers`)
- **DB**: PostgreSQL via Docker, `psycopg2-binary` with raw SQL (no ORM)
- **Config**: `python-dotenv` — credentials loaded from `.env`
- **Frontend**: Jinja2 templates + Tailwind CSS CDN (dark mode)
- **Email**: Flask-Mail via Gmail SMTP — HTML email with embedded logo
- **AI**: Google Gemini (`google-genai`) via AI Studio — task recommendations

## Project Structure

```
TasksManagerApp/
├── main.py                      # Entrypoint: imports create_app from src/app.py
├── docker-compose.yml           # PostgreSQL service
├── .env                         # Local credentials (DO NOT commit)
├── .env.example                 # Template for .env
├── pyproject.toml               # Dependencies (uv)
└── src/
    ├── app.py                   # Flask app factory (create_app)
    ├── db.py                    # psycopg2 helpers: get_db, close_db, init_db
    ├── mail.py                  # Flask-Mail setup + send_task_created() + send_task_completed()
    ├── blueprints/
    │   ├── tasks.py             # /tasks CRUD + /tasks/archived + /tasks/ai-suggest
    │   ├── reminders.py         # /reminders list route
    │   └── subscribers.py       # /subscribers CRUD routes
    ├── sql/
    │   └── schema.sql           # Idempotent schema + updated_at triggers
    ├── static/
    │   └── assets/img/
    │       ├── logo_raw.png     # Logo embedded in emails
    │       └── giphy.gif        # Loading gif shown in AI modal
    └── templates/
        ├── base.html            # Sidebar layout, flash messages
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

## Key Decisions

- **Archive over delete**: tasks are never deleted; `archived=TRUE` hides them. Restorable from `/tasks/archived`.
- **No ORM**: raw SQL via `psycopg2` with `RealDictCursor` (rows as dicts).
- **Schema init at startup**: `init_db()` runs `schema.sql` every time (idempotent). If DB is unreachable, logs a warning and continues.
- **DB error handling**: `psycopg2.OperationalError` is caught globally and renders a 503 page instead of crashing.
- **Subscribers over hardcoded recipients**: notification targets live in the `subscribers` table, managed from the UI. No emails in `.env`.
- **Two email triggers**: creation (`send_task_created`) and completion (`send_task_completed`). Both use a shared `_send()` helper. HTML + plain-text fallback with CID-embedded logo.
- **Email is optional**: if `MAIL_USERNAME` is not set, all notification functions return early without errors.
- **AI recommendation flow**: on new task submission, a JS modal intercepts and asks whether to fetch a Gemini recommendation. The result is stored in `ai_recommendation` (TEXT column), shown in the detail view and included in the creation email. The modal shows `giphy.gif` while waiting for the model response.
- **AI is optional**: if `GEMINI_API_KEY` is not set, the `/tasks/ai-suggest` endpoint returns 503; the modal handles it with an error state and lets the user save anyway.
- **`.env` must not be committed**: already in `.gitignore`.
