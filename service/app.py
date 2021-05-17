import os

from psycopg2 import pool
from flask import Flask, g, jsonify
from service import get_covid_articles_count


PG_SERVER = os.getenv("POSTGRES_HOST")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT")

app = Flask(__name__)

app.config["postgreSQL_pool"] = pool.SimpleConnectionPool(
    2,
    8,
    database="postgres",
    user=PG_USER,
    password=PG_PASSWORD,
    host=PG_SERVER,
    port=PG_PORT,
)


def get_db():
    if "db" not in g:
        g.db = app.config["postgreSQL_pool"].getconn()
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        app.config["postgreSQL_pool"].putconn(db)


@app.route("/", methods=["GET"])
def check_health():
    return jsonify(status="OK")


@app.route("/<string:year>/<string:month>/<string:day>", methods=["GET"])
def article_covid(year, month, day):
    conn = get_db()
    covid_articles = get_covid_articles_count(
        f"{year}-{month.zfill(0)}-{day.zfill(0)}", conn
    )
    return jsonify(number=covid_articles, text="Number of covid related articles")
