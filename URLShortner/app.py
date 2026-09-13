import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models.database import close_db, get_db, init_db


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "shortener.sqlite3"))

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
    DATABASE=DATABASE_PATH,
)
app.teardown_appcontext(close_db)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please sign in to shorten and manage your links.", "info")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username FROM user WHERE id = ?", (user_id,)
        ).fetchone()


@app.route("/", methods=("GET", "POST"))
@login_required
def index():
    if request.method == "POST":
        long_url = request.form.get("longurl", "").strip()
        parsed_url = urlparse(long_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            flash("Enter a complete URL beginning with http:// or https://.", "error")
            return render_template("home.html", long_url=long_url), 400

        token = secrets.token_urlsafe(5).replace("-", "").replace("_", "")[:7]
        db = get_db()
        db.execute(
            "INSERT INTO url (user_id, token, long_url) VALUES (?, ?, ?)",
            (g.user["id"], token, long_url),
        )
        db.commit()
        short_url = url_for("redirect_to_url", token=token, _external=True)
        return render_template("resulturl.html", short_url=short_url, long_url=long_url)

    links = get_db().execute(
        "SELECT token, long_url, created_at FROM url "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("home.html", links=links)


@app.route("/<token>")
def redirect_to_url(token):
    link = get_db().execute("SELECT long_url FROM url WHERE token = ?", (token,)).fetchone()
    if link is None:
        return render_template("error404.html"), 404
    return redirect(link["long_url"])


@app.route("/register", methods=("GET", "POST"))
def register():
    if g.user is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        error = None
        if not username:
            error = "Username is required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."

        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = "That username is already taken."
            else:
                flash("Account created. You can now sign in.", "success")
                return redirect(url_for("login"))
        flash(error, "error")
    return render_template("auth/register.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if g.user is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, username, password FROM user WHERE username = ?", (username,)
        ).fetchone()
        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            next_page = request.args.get("next")
            safe_next = next_page and next_page.startswith("/") and not next_page.startswith("//")
            return redirect(next_page if safe_next else url_for("index"))
    return render_template("auth/login.html")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("error404.html"), 404


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "8080")), debug=os.environ.get("FLASK_DEBUG") == "1")
