from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.db import get_db
from src.mail import send_task_created

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
def list_tasks():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM tasks WHERE archived = FALSE ORDER BY created_at DESC"
        )
        tasks = cur.fetchall()
    return render_template("tasks/list.html", tasks=tasks)


@tasks_bp.route("/<int:task_id>")
def detail(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cur.fetchone()
    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.list_tasks"))
    return render_template("tasks/detail.html", task=task)


@tasks_bp.route("/new", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip() or None
        reminder_at = request.form.get("reminder_at", "").strip() or None
        reminder_note = request.form.get("reminder_note", "").strip() or None

        if not title:
            flash("Title is required.", "error")
            return render_template("tasks/form.html", task=None)

        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO tasks (title, body, reminder_at, reminder_note)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (title, body, reminder_at, reminder_note),
            )
            task_id = cur.fetchone()["id"]
        db.commit()

        with db.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            new_task = cur.fetchone()
        send_task_created(new_task)

        flash("Task created.", "success")
        return redirect(url_for("tasks.detail", task_id=task_id))

    return render_template("tasks/form.html", task=None)


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cur.fetchone()

    if task is None:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.list_tasks"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip() or None
        reminder_at = request.form.get("reminder_at", "").strip() or None
        reminder_note = request.form.get("reminder_note", "").strip() or None

        if not title:
            flash("Title is required.", "error")
            return render_template("tasks/form.html", task=task)

        with db.cursor() as cur:
            cur.execute(
                """UPDATE tasks
                   SET title = %s, body = %s, reminder_at = %s, reminder_note = %s
                   WHERE id = %s""",
                (title, body, reminder_at, reminder_note, task_id),
            )
        db.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks.detail", task_id=task_id))

    return render_template("tasks/form.html", task=task)


@tasks_bp.route("/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s", (task_id,)
        )
    db.commit()
    return redirect(request.referrer or url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/archive", methods=["POST"])
def archive_task(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("UPDATE tasks SET archived = TRUE WHERE id = %s", (task_id,))
    db.commit()
    flash("Task archived.", "success")
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/archived")
def archived_tasks():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM tasks WHERE archived = TRUE ORDER BY updated_at DESC"
        )
        tasks = cur.fetchall()
    return render_template("tasks/archived.html", tasks=tasks)


@tasks_bp.route("/<int:task_id>/unarchive", methods=["POST"])
def unarchive_task(task_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("UPDATE tasks SET archived = FALSE WHERE id = %s", (task_id,))
    db.commit()
    flash("Task restored.", "success")
    return redirect(url_for("tasks.archived_tasks"))
