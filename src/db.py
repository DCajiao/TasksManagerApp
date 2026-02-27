import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
    with app.app_context():
        db = get_db()
        with open(schema_path) as f:
            with db.cursor() as cur:
                cur.execute(f.read())
        db.commit()
        close_db()
