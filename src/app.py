import os
import psycopg2
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from src.db import close_db, init_db
from src.mail import init_mail


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    app.teardown_appcontext(close_db)

    init_mail(app)

    from src.blueprints.tasks import tasks_bp
    from src.blueprints.reminders import reminders_bp
    from src.blueprints.subscribers import subscribers_bp

    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(reminders_bp, url_prefix="/reminders")
    app.register_blueprint(subscribers_bp, url_prefix="/subscribers")

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("tasks.list_tasks"))

    @app.route("/health")
    def health():
        from src.db import get_db
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute("SELECT 1")
            return jsonify({"status": "ok"}), 200
        except Exception:
            return jsonify({"status": "db_unavailable"}), 503

    @app.errorhandler(psycopg2.OperationalError)
    def handle_db_down(e):
        return render_template("errors/db_down.html"), 503

    init_db(app)

    return app
