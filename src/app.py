import os
from flask import Flask
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

    init_db(app)

    return app
