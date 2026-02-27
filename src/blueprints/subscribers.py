from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.db import get_db

subscribers_bp = Blueprint("subscribers", __name__)


@subscribers_bp.route("/")
def list_subscribers():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM subscribers ORDER BY created_at DESC")
        subscribers = cur.fetchall()
    return render_template("subscribers/list.html", subscribers=subscribers)


@subscribers_bp.route("/new", methods=["GET", "POST"])
def new_subscriber():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            flash("Name and email are required.", "error")
            return render_template("subscribers/form.html", subscriber=None)

        db = get_db()
        try:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO subscribers (name, email) VALUES (%s, %s)",
                    (name, email),
                )
            db.commit()
            flash("Subscriber added.", "success")
            return redirect(url_for("subscribers.list_subscribers"))
        except Exception:
            db.rollback()
            flash("That email is already registered.", "error")
            return render_template("subscribers/form.html", subscriber=None)

    return render_template("subscribers/form.html", subscriber=None)


@subscribers_bp.route("/<int:sub_id>/edit", methods=["GET", "POST"])
def edit_subscriber(sub_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM subscribers WHERE id = %s", (sub_id,))
        subscriber = cur.fetchone()

    if subscriber is None:
        flash("Subscriber not found.", "error")
        return redirect(url_for("subscribers.list_subscribers"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            flash("Name and email are required.", "error")
            return render_template("subscribers/form.html", subscriber=subscriber)

        try:
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE subscribers SET name = %s, email = %s WHERE id = %s",
                    (name, email, sub_id),
                )
            db.commit()
            flash("Subscriber updated.", "success")
            return redirect(url_for("subscribers.list_subscribers"))
        except Exception:
            db.rollback()
            flash("That email is already in use.", "error")
            return render_template("subscribers/form.html", subscriber=subscriber)

    return render_template("subscribers/form.html", subscriber=subscriber)


@subscribers_bp.route("/<int:sub_id>/toggle", methods=["POST"])
def toggle_subscriber(sub_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE subscribers SET active = NOT active WHERE id = %s RETURNING active",
            (sub_id,),
        )
        result = cur.fetchone()
    db.commit()
    status = "activated" if result and result["active"] else "deactivated"
    flash(f"Subscriber {status}.", "success")
    return redirect(url_for("subscribers.list_subscribers"))
