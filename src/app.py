import os
import psycopg2
from flask import Flask, render_template
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

    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(reminders_bp, url_prefix="/reminders")

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("tasks.list_tasks"))

    @app.errorhandler(psycopg2.OperationalError)
    def handle_db_down(e):
        return render_template("errors/db_down.html"), 503

    init_db(app)

    return app
