from flask import Blueprint, render_template
from src.db import get_db

reminders_bp = Blueprint("reminders", __name__)


@reminders_bp.route("/")
def list_reminders():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT * FROM tasks
               WHERE reminder_at IS NOT NULL AND archived = FALSE
               ORDER BY reminder_at ASC"""
        )
        reminders = cur.fetchall()
    return render_template("reminders/list.html", reminders=reminders)
