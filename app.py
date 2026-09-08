import os
import secrets
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE"] = os.getenv("DATABASE", "shadownet.db")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0") == "1"

from data import LANGUAGES

def db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_premium INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]

@app.context_processor
def inject_globals():
    return {"csrf_token": csrf_token(), "user": current_user()}

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return user

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def check_csrf():
    if request.form.get("csrf") != session.get("csrf"):
        abort(400, "Invalid CSRF token")

@app.after_request
def headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

@app.route("/")
def index():
    return render_template("index.html", languages=list(LANGUAGES.keys()))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(name) < 2 or len(email) < 5 or len(password) < 8:
            return render_template("auth.html", mode="register", error="Use a valid name, email, and password of at least 8 characters.")
        conn = db()
        try:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            session.clear()
            session["user_id"] = cur.lastrowid
            session["csrf"] = secrets.token_urlsafe(32)
            return redirect(url_for("welcome"))
        except sqlite3.IntegrityError:
            return render_template("auth.html", mode="register", error="That email is already registered.")
        finally:
            conn.close()
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("auth.html", mode="login", error="Invalid email or password.")
        session.clear()
        session["user_id"] = user["id"]
        session["csrf"] = secrets.token_urlsafe(32)
        return redirect(url_for("welcome"))
    return render_template("auth.html", mode="login")

@app.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html")

@app.route("/app")
@login_required
def dashboard():
    return render_template("dashboard.html", languages=list(LANGUAGES.keys()))

@app.route("/language/<path:name>")
@login_required
def language(name):
    if name not in LANGUAGES:
        abort(404)
    return render_template("language.html", name=name, topics=LANGUAGES[name])

@app.route("/premium")
@login_required
def premium():
    return render_template("premium.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("index"))

@app.route("/api/ai", methods=["POST"])
@login_required
def ai():
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "AI is not configured. Add OPENAI_API_KEY to the server .env file."}), 503

    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()
    language = str(body.get("language", "Programming"))
    if not message or len(message) > 6000:
        return jsonify({"error": "Message must contain 1 to 6000 characters."}), 400

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    system = (
        "You are ShadowNet AI Assistant. Teach programming clearly and safely. "
        "The learner is using the ShadowNet Master Class. "
        f"Current language: {language}. "
        "Give concise explanations, runnable examples, debugging steps, and practical tips. "
        "For cybersecurity topics, stay within authorized defensive and educational use."
    )
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            instructions=system,
            input=message,
        )
        return jsonify({"answer": response.output_text})
    except Exception as exc:
        app.logger.exception("OpenAI request failed")
        return jsonify({"error": "The AI service could not complete the request."}), 502

@app.route("/privacy")
def privacy():
    return render_template("legal.html", page="Privacy Policy")

@app.route("/terms")
def terms():
    return render_template("legal.html", page="Terms & Conditions")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "0") == "1")
