from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from pathlib import Path
import sqlite3
import os
import base64
import uuid
import socket

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# ECO FUSION 360 WEB
# COMPLETE APP.PY
#
# THREE SEPARATE LOGIN PATHS
#
# 1. USER
# 2. COORDINATOR
# 3. ADMIN
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DB_PATH = DATABASE_DIR / "ecofusion.db"


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "ECO_FUSION_SECRET",
    "eco-fusion-360-secret-change-later"
)

# ============================================================
# PLASTIC CAMERA PHOTO STORAGE
# ============================================================

UPLOAD_FOLDER = BASE_DIR / "static" / "uploads" / "plastic_photos"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


# ============================================================
# ADMIN ACCOUNTS
# ============================================================

ADMIN_EMAILS = [
    "devaloki69@gmail.com",
    "pandathor69@gmail.com",
    "kotaironman69@gamil.com",
    "manishspiderman69@gamil.com"
]


# IMPORTANT:
# You can set your real admin password as an environment
# variable called ECO_ADMIN_PASSWORD.
#
# If you don't set it, this temporary default is used.
#
# Example PowerShell:
#
# $env:ECO_ADMIN_PASSWORD="YourPasswordHere"
#
ADMIN_PASSWORD = os.environ.get(
    "ECO_ADMIN_PASSWORD",
    "EcoFusionAdmin123"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    conn = sqlite3.connect(DB_PATH, timeout=20)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 20000")

    return conn


# ============================================================
# DATABASE COLUMN MIGRATION
# ============================================================

def add_column_if_missing(
    conn,
    table,
    column,
    definition
):

    cur = conn.cursor()

    cur.execute(
        f"PRAGMA table_info({table})"
    )

    columns = [
        row["name"]
        for row in cur.fetchall()
    ]

    if column not in columns:

        cur.execute(
            f"""
            ALTER TABLE {table}
            ADD COLUMN {column} {definition}
            """
        )

        print(
            f"✅ Added {column} to {table}"
        )


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    conn = get_connection()
    cur = conn.cursor()

    # ========================================================
    # USERS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'User',

            recycle_center_name TEXT,

            recycle_center_id TEXT,

            district TEXT,

            address TEXT,

            mobile TEXT,

            approved INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    add_column_if_missing(
        conn,
        "users",
        "role",
        "TEXT DEFAULT 'User'"
    )

    add_column_if_missing(
        conn,
        "users",
        "recycle_center_name",
        "TEXT"
    )

    add_column_if_missing(
        conn,
        "users",
        "recycle_center_id",
        "TEXT"
    )

    add_column_if_missing(
        conn,
        "users",
        "district",
        "TEXT"
    )

    add_column_if_missing(
        conn,
        "users",
        "address",
        "TEXT"
    )

    add_column_if_missing(
        conn,
        "users",
        "mobile",
        "TEXT"
    )

    add_column_if_missing(
        conn,
        "users",
        "approved",
        "INTEGER DEFAULT 1"
    )

    print("✅ Users table ready")

    # ========================================================
    # USER PROGRESS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            green_tokens INTEGER DEFAULT 0,

            plastic_kg REAL DEFAULT 0,

            trees_saved INTEGER DEFAULT 0,

            water_saved REAL DEFAULT 0,

            energy_saved REAL DEFAULT 0,

            co2_reduced REAL DEFAULT 0,

            badge TEXT DEFAULT 'Beginner Recycler',

            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(email)
            REFERENCES users(email)

        )
    """)

    add_column_if_missing(
        conn,
        "user_progress",
        "green_tokens",
        "INTEGER DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "plastic_kg",
        "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "trees_saved",
        "INTEGER DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "water_saved",
        "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "energy_saved",
        "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "co2_reduced",
        "REAL DEFAULT 0"
    )

    add_column_if_missing(
        conn,
        "user_progress",
        "badge",
        "TEXT DEFAULT 'Beginner Recycler'"
    )

    print("✅ User progress table ready")

    # ========================================================
    # TREE GAME
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tree_game (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            biome TEXT,

            tree_type TEXT,

            watering_count INTEGER DEFAULT 0,

            tree_height REAL DEFAULT 0,

            game_started INTEGER DEFAULT 0,

            completed INTEGER DEFAULT 0,

            biome_unlocked INTEGER DEFAULT 0,

            tree_unlocked INTEGER DEFAULT 0,

            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(email)
            REFERENCES users(email)

        )
    """)

    print("🌳 Tree Game table ready")

    # ========================================================
    # PLASTIC HISTORY
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plastic_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_email TEXT,

            plastic_type TEXT,

            process_used TEXT,

            result TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("♻️ Plastic history table ready")

    # ========================================================
    # REWARDS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rewards (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT,

            reward_name TEXT,

            reward_cost INTEGER DEFAULT 0,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("🎁 Rewards table ready")

    # ========================================================
    # REWARD CATALOGUE + GREEN TOKEN TRANSACTION HISTORY
    # ========================================================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reward_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reward_name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            reward_cost INTEGER NOT NULL DEFAULT 0,
            reward_type TEXT NOT NULL DEFAULT 'Physical',
            stock INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Extend the existing catalogue safely for digital anime/manga unlocks.
    add_column_if_missing(conn, "reward_catalog", "reward_url", "TEXT DEFAULT ''")
    add_column_if_missing(conn, "reward_catalog", "reward_category", "TEXT DEFAULT 'eco'")

    # Shared database, strictly separated unlock records per account.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reward_unlocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            reward_catalog_id INTEGER NOT NULL,
            reward_name TEXT NOT NULL,
            reward_cost INTEGER NOT NULL,
            reward_url TEXT DEFAULT '',
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email, reward_catalog_id),
            FOREIGN KEY(email) REFERENCES users(email),
            FOREIGN KEY(reward_catalog_id) REFERENCES reward_catalog(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS token_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            amount INTEGER NOT NULL,
            reason TEXT NOT NULL,
            reference_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add starter rewards only if the catalogue is empty.
    cur.execute("SELECT COUNT(*) AS total FROM reward_catalog")
    if cur.fetchone()["total"] == 0:
        starter_rewards = [
            ("Eco Stationery Kit", "Recycled-paper notebook and eco-friendly stationery.", 250, "Physical", 20),
            ("Seed Starter Pack", "Seeds for a small home or school planting activity.", 500, "Physical", 15),
            ("Nature Learning Book", "A book about nature, recycling, or the environment.", 750, "Physical", 10),
            ("Eco Champion Certificate", "A digital certificate recognising your contribution.", 300, "Digital", 0),
            ("Planet Guardian Certificate", "A digital milestone certificate for verified recycling.", 600, "Digital", 0),
        ]
        cur.executemany("""
            INSERT INTO reward_catalog
                (reward_name, description, reward_cost, reward_type, stock)
            VALUES (?, ?, ?, ?, ?)
        """, starter_rewards)


    digital_unlocks = [
        ("Digital Anime Book", "Unlock the digital anime book before starting your manga collection.", 250, "Digital", 0, "https://mangaplus.shueisha.co.jp/", "anime"),
        ("Haikyu!!", "Manga collection chapter 1. Unlock after the Digital Anime Book.", 300, "Digital", 0, "https://www.viz.com/shonenjump/haikyu-chapter-1/chapter/4118?action=read", "manga"),
        ("Demon Slayer", "Unlock after Haikyu!! in your personal manga collection.", 350, "Digital", 0, "https://www.viz.com/manga-books/manga/demon-slayer-kimetsu-no-yaiba-volume-1-0/product/5547", "manga"),
        ("Black Clover", "Unlock after Demon Slayer in your personal manga collection.", 400, "Digital", 0, "https://mangaplus.shueisha.co.jp/titles/100003", "manga"),
        ("Solo Leveling", "Unlock after Black Clover in your personal manga collection.", 450, "Digital", 0, "https://www.tappytoon.com/en/book/solo-leveling-official", "manga"),
        ("Jujutsu Kaisen", "Unlock after Solo Leveling in your personal manga collection.", 500, "Digital", 0, "https://www.viz.com/manga-books/manga/jujutsu-kaisen-volume-0-0/product/6537", "manga"),
        ("Eco Champion Certificate", "Personalise and print your Eco Fusion 360 achievement certificate.", 300, "Digital", 0, "", "certificate"),
        ("Planet Guardian Certificate", "A higher-tier printable certificate for your eco journey.", 600, "Digital", 0, "", "certificate"),
    ]
    for reward_name, description, cost, reward_type, stock, reward_url, reward_category in digital_unlocks:
        cur.execute("""
            INSERT OR IGNORE INTO reward_catalog
                (reward_name, description, reward_cost, reward_type, stock, active, reward_url, reward_category)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        """, (reward_name, description, cost, reward_type, stock, reward_url, reward_category))
        # Ensure links/category are correct for existing catalogue rows too.
        cur.execute("""
            UPDATE reward_catalog
            SET description = ?, reward_cost = ?, reward_type = ?, reward_url = ?, reward_category = ?, active = 1
            WHERE reward_name = ?
        """, (description, cost, reward_type, reward_url, reward_category, reward_name))

    # ========================================================
    # RECYCLING SUBMISSIONS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recycling_submissions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            plastic_type TEXT NOT NULL,

            process TEXT NOT NULL,

            weight_kg REAL NOT NULL,

            recycle_center TEXT NOT NULL,

            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            status TEXT DEFAULT 'Pending',

            coordinator_email TEXT,

            remarks TEXT

        )
    """)

    print("♻️ Recycling submissions table ready")

    # Camera photo columns (safe for existing databases)
    add_column_if_missing(conn, "recycling_submissions", "photo_path", "TEXT")
    add_column_if_missing(conn, "recycling_submissions", "camera_verified", "INTEGER DEFAULT 0")
    add_column_if_missing(conn, "recycling_submissions", "photo_captured_at", "TIMESTAMP")

    # ========================================================
    # ADMINS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # CREATE / UPDATE FOUR ADMINS
    # ========================================================

    admin_hash = generate_password_hash(
        ADMIN_PASSWORD
    )

    for admin_email in ADMIN_EMAILS:

        cur.execute("""
            SELECT id
            FROM admins
            WHERE email = ?
        """, (admin_email,))

        existing = cur.fetchone()

        if existing is None:

            cur.execute("""
                INSERT INTO admins
                (
                    email,
                    password_hash
                )
                VALUES (?, ?)
            """, (
                admin_email,
                admin_hash
            ))

        else:

            # Keep existing password if already present.
            pass

    print("🔐 Four admin accounts ready")

    # ========================================================
    # QUIZ QUESTIONS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            question TEXT NOT NULL,

            option_a TEXT NOT NULL,

            option_b TEXT NOT NULL,

            option_c TEXT NOT NULL,

            option_d TEXT NOT NULL,

            correct_answer TEXT NOT NULL,

            active INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("🧠 Quiz tables ready")

    # ========================================================
    # QUIZ ATTEMPTS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            quiz_week TEXT NOT NULL,

            score INTEGER DEFAULT 0,

            correct_answers INTEGER DEFAULT 0,

            wrong_answers INTEGER DEFAULT 0,

            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(email, quiz_week)

        )
    """)

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            achievement_type TEXT NOT NULL,

            achievement_name TEXT NOT NULL,

            description TEXT,

            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("🏅 Achievements table ready")

    # ========================================================
    # MESSAGES
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_email TEXT NOT NULL,

            subject TEXT,

            message TEXT NOT NULL,

            reply TEXT,

            status TEXT DEFAULT 'Unread',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            replied_at TIMESTAMP

        )
    """)

    print("💬 Messages table ready")

    # ========================================================
    # USER NOTIFICATIONS — coordinator review updates
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            submission_id INTEGER,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Unread',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        )
    """)

    print("🔔 User notifications table ready")

    # ========================================================
    # FEEDBACK
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            rating INTEGER,

            message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("❤️ Feedback table ready")

    # ========================================================
    # COORDINATOR REQUESTS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS coordinator_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            center_name TEXT,

            center_id TEXT,

            district TEXT,

            address TEXT,

            mobile TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    print("🏢 Coordinator requests table ready")

    # ========================================================
    # COMMIT
    # ========================================================

    conn.commit()
    conn.close()

    print()
    print("==============================================")
    print("🌍 ECO FUSION 360 DATABASE READY")
    print("==============================================")
    print(f"Database:")
    print(DB_PATH)
    print("==============================================")


# ============================================================
# SESSION HELPERS
# ============================================================

def logged_in():

    return session.get(
        "logged_in"
    ) is True


def is_user():

    return (
        logged_in()
        and session.get("role") == "User"
    )


def is_coordinator():

    return (
        logged_in()
        and session.get("role")
        == "Recycle Center Coordinator"
    )


def is_admin():

    return (
        logged_in()
        and session.get("role") == "Admin"
    )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# USER REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not full_name or not email or not password:

            return render_template(
                "register.html",
                error="Please fill in all fields."
            )

        if password != confirm_password:

            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        if len(password) < 6:

            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        conn = get_connection()
        cur = conn.cursor()

        try:

            password_hash = generate_password_hash(
                password
            )

            cur.execute("""
                INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    role,
                    approved
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    'User',
                    1
                )
            """, (
                full_name,
                email,
                password_hash
            ))

            cur.execute("""
                INSERT INTO user_progress
                (
                    email
                )
                VALUES (?)
            """, (email,))

            cur.execute("""
                INSERT INTO tree_game
                (
                    email
                )
                VALUES (?)
            """, (email,))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.rollback()
            conn.close()

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        except Exception as error:

            conn.rollback()
            conn.close()

            print(
                "USER REGISTRATION ERROR:",
                error
            )

            return render_template(
                "register.html",
                error="Could not create the account."
            )

        conn.close()

        return redirect(
            url_for("user_login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# USER LOGIN
# ============================================================

@app.route(
    "/user-login",
    methods=["GET", "POST"]
)
def user_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND role = 'User'
        """, (email,))

        user = cur.fetchone()

        conn.close()

        if user:

            if check_password_hash(
                user["password"],
                password
            ):

                if user["approved"] == 0:

                    return render_template(
                        "user_login.html",
                        error="Your account is currently disabled."
                    )

                session.clear()

                session["logged_in"] = True
                session["role"] = "User"
                session["user_id"] = user["id"]
                session["full_name"] = user["full_name"]
                session["email"] = user["email"]

                return redirect(
                    url_for("dashboard")
                )

        return render_template(
            "user_login.html",
            error="Incorrect user email or password."
        )

    return render_template(
        "user_login.html"
    )


# ============================================================
# COORDINATOR REGISTER
# ============================================================

@app.route(
    "/coordinator-register",
    methods=["GET", "POST"]
)
def coordinator_register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        center_name = request.form.get(
            "recycle_center_name",
            ""
        ).strip()

        center_id = request.form.get(
            "recycle_center_id",
            ""
        ).strip()

        district = request.form.get(
            "district",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        if not full_name or not email or not password:

            return render_template(
                "coordinator_register.html",
                error="Please fill in the required fields."
            )

        if password != confirm_password:

            return render_template(
                "coordinator_register.html",
                error="Passwords do not match."
            )

        if len(password) < 6:

            return render_template(
                "coordinator_register.html",
                error="Password must contain at least 6 characters."
            )

        conn = get_connection()
        cur = conn.cursor()

        try:

            password_hash = generate_password_hash(
                password
            )

            # ------------------------------------------------
            # CREATE COORDINATOR
            # ------------------------------------------------

            cur.execute("""
                INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    role,
                    recycle_center_name,
                    recycle_center_id,
                    district,
                    address,
                    mobile,
                    approved
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    'Recycle Center Coordinator',
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    0
                )
            """, (
                full_name,
                email,
                password_hash,
                center_name,
                center_id,
                district,
                address,
                mobile
            ))

            # ------------------------------------------------
            # CREATE APPROVAL REQUEST
            # ------------------------------------------------

            cur.execute("""
                INSERT OR REPLACE INTO coordinator_requests
                (
                    email,
                    center_name,
                    center_id,
                    district,
                    address,
                    mobile,
                    status
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    'Pending'
                )
            """, (
                email,
                center_name,
                center_id,
                district,
                address,
                mobile
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.rollback()
            conn.close()

            return render_template(
                "coordinator_register.html",
                error="This email is already registered."
            )

        except Exception as error:

            conn.rollback()
            conn.close()

            print(
                "COORDINATOR REGISTRATION ERROR:",
                error
            )

            return render_template(
                "coordinator_register.html",
                error="Could not create coordinator account."
            )

        conn.close()

        return render_template(
            "coordinator_login.html",
            message=(
                "Coordinator account created successfully. "
                "Please wait for Admin approval."
            )
        )

    return render_template(
        "coordinator_register.html"
    )


# ============================================================
# COORDINATOR LOGIN
# ============================================================

@app.route(
    "/coordinator-login",
    methods=["GET", "POST"]
)
def coordinator_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND role = 'Recycle Center Coordinator'
        """, (email,))

        coordinator = cur.fetchone()

        conn.close()

        if coordinator:

            if check_password_hash(
                coordinator["password"],
                password
            ):

                if coordinator["approved"] == 0:

                    return render_template(
                        "coordinator_login.html",
                        error=(
                            "Your coordinator account is "
                            "waiting for Admin approval."
                        )
                    )

                session.clear()

                session["logged_in"] = True
                session["role"] = (
                    "Recycle Center Coordinator"
                )
                session["user_id"] = coordinator["id"]
                session["full_name"] = coordinator["full_name"]
                session["email"] = coordinator["email"]

                return redirect(
                    url_for(
                        "coordinator_dashboard"
                    )
                )

        return render_template(
            "coordinator_login.html",
            error="Incorrect coordinator email or password."
        )

    return render_template(
        "coordinator_login.html"
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM admins
            WHERE email = ?
        """, (email,))

        admin = cur.fetchone()

        conn.close()

        if admin:

            if check_password_hash(
                admin["password_hash"],
                password
            ):

                session.clear()

                session["logged_in"] = True
                session["role"] = "Admin"
                session["email"] = admin["email"]
                session["full_name"] = "Eco Fusion 360 Admin"

                return redirect(
                    url_for(
                        "admin_dashboard"
                    )
                )

        return render_template(
            "admin_login.html",
            error="Incorrect admin email or password."
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# USER DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not logged_in():

        return redirect(
            url_for("home")
        )

    if is_admin():

        return redirect(
            url_for("admin_dashboard")
        )

    if is_coordinator():

        return redirect(
            url_for("coordinator_dashboard")
        )

    if not is_user():

        return redirect(
            url_for("home")
        )

    email = session["email"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cur.fetchone()

    cur.execute("""
        SELECT *
        FROM user_progress
        WHERE email = ?
    """, (email,))

    progress = cur.fetchone()

    cur.execute("""
        SELECT *
        FROM tree_game
        WHERE email = ?
    """, (email,))

    tree = cur.fetchone()

    cur.execute("""
        SELECT id, plastic_type, process, weight_kg, recycle_center,
               submitted_at, status, remarks
        FROM recycling_submissions
        WHERE lower(trim(email)) = lower(trim(?))
        ORDER BY submitted_at DESC
        LIMIT 10
    """, (email,))
    user_submissions = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE lower(trim(user_email)) = lower(trim(?))
          AND status = 'Unread'
    """, (email,))
    unread_notifications = cur.fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        progress=progress,
        tree=tree,
        user_submissions=user_submissions,
        unread_notifications=unread_notifications
    )


# ============================================================
# ECOSPHERE AI — SIGNED-IN USER CHATBOT
# ============================================================

@app.route("/ecosphere")
def ecosphere_ai():
    # Keep the chatbot inside the existing Flask app and require user login.
    if not is_user():
        if logged_in():
            return redirect(url_for("dashboard"))
        return redirect(url_for("user_login"))

    return render_template("ecosphere_ai.html")


# ============================================================
# USER NOTIFICATIONS
# ============================================================

@app.route("/notifications")
def user_notifications():

    if not is_user():
        return redirect(url_for("user_login"))

    email = session["email"]
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, submission_id, title, message, status, created_at
        FROM notifications
        WHERE lower(trim(user_email)) = lower(trim(?))
        ORDER BY created_at DESC, id DESC
    """, (email,))
    notifications = cur.fetchall()

    cur.execute("""
        UPDATE notifications
        SET status = 'Read', read_at = CURRENT_TIMESTAMP
        WHERE lower(trim(user_email)) = lower(trim(?))
          AND status = 'Unread'
    """, (email,))
    conn.commit()
    conn.close()

    return render_template(
        "user_notifications.html",
        notifications=notifications
    )


# ============================================================
# PLASTIC IDENTIFICATION
# ============================================================

@app.route("/plastic-identification")
def plastic_identification():

    if not is_user():

        return redirect(
            url_for("user_login")
        )

    return render_template(
        "plastic_identification.html"
    )


# ============================================================
# PLASTIC CAMERA
# ============================================================

@app.route("/plastic-camera")
def plastic_camera():

    if not is_user():
        return redirect(url_for("user_login"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT full_name, email, recycle_center_name, recycle_center_id,
                   district, address
            FROM users
            WHERE role = 'Recycle Center Coordinator'
              AND approved = 1
            ORDER BY recycle_center_name, full_name
        """)
        coordinators = cur.fetchall()
    finally:
        conn.close()

    message = session.pop("plastic_submission_message", "")
    return render_template(
        "plastic_camera.html",
        coordinators=coordinators,
        success_message=message
    )


# ============================================================
# CAMERA PLASTIC PHOTO CAPTURE
# ============================================================

@app.route("/capture-plastic-photo", methods=["POST"])
def capture_plastic_photo():

    if not is_user():
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    try:
        data = request.get_json(silent=True) or {}
        image_data = data.get("image", "")

        if not image_data:
            return jsonify({
                "success": False,
                "message": "Please capture a photo first."
            }), 400

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        if not image_bytes:
            raise ValueError("Empty image")

        filename = f"plastic_{session['user_id']}_{uuid.uuid4().hex}.jpg"
        file_path = UPLOAD_FOLDER / filename

        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)

        photo_path = f"uploads/plastic_photos/{filename}"

        # Keep the latest captured photo in the user's session until submission.
        session["plastic_photo_path"] = photo_path

        return jsonify({
            "success": True,
            "message": "Plastic photo captured successfully!",
            "photo_path": photo_path
        })

    except Exception as error:
        print("CAMERA CAPTURE ERROR:", error)
        return jsonify({
            "success": False,
            "message": "Could not save the captured photo."
        }), 500


# ============================================================
# SUBMIT PLASTIC TO A RECYCLING CENTRE
# ============================================================

@app.route("/submit-plastic", methods=["POST"])
def submit_plastic():

    if not is_user():
        return redirect(url_for("user_login"))

    # A submission must use the photo captured by this logged-in session.
    photo_path = (session.get("plastic_photo_path") or "").strip()
    if not photo_path:
        session["plastic_submission_message"] = (
            "Please capture and save a photo before submitting."
        )
        return redirect(url_for("plastic_camera"))

    plastic_type = (request.form.get("plastic_type") or "").strip()
    process = (request.form.get("process") or "").strip()
    weight_text = (request.form.get("weight_kg") or "").strip()
    coordinator_email = (request.form.get("coordinator_email") or "").strip().lower()

    allowed_plastics = {
        "PET", "HDPE", "PVC", "LDPE", "PP", "PS",
        "PC", "ABS", "PLA", "PC/ABS/PLA", "Mixed", "Unknown"
    }
    allowed_processes = {"Pyrolysis", "Cryolysis"}

    if plastic_type not in allowed_plastics:
        session["plastic_submission_message"] = "Please select a valid plastic type."
        return redirect(url_for("plastic_camera"))

    if process not in allowed_processes:
        session["plastic_submission_message"] = "Please select a processing method."
        return redirect(url_for("plastic_camera"))

    try:
        weight_kg = float(weight_text)
        if weight_kg <= 0 or weight_kg > 10000:
            raise ValueError
    except (TypeError, ValueError):
        session["plastic_submission_message"] = (
            "Enter a valid weight greater than 0 kg and no more than 10,000 kg."
        )
        return redirect(url_for("plastic_camera"))

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT email, full_name, recycle_center_name
            FROM users
            WHERE lower(email) = ?
              AND role = 'Recycle Center Coordinator'
              AND approved = 1
            LIMIT 1
        """, (coordinator_email,))
        coordinator = cur.fetchone()

        if coordinator is None:
            session["plastic_submission_message"] = (
                "Please choose an approved recycling centre coordinator."
            )
            return redirect(url_for("plastic_camera"))

        cur.execute("""
            INSERT INTO recycling_submissions (
                email, plastic_type, process, weight_kg, recycle_center,
                status, coordinator_email, photo_path, camera_verified,
                photo_captured_at
            )
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, 0, CURRENT_TIMESTAMP)
        """, (
            session["email"],
            plastic_type,
            process,
            weight_kg,
            coordinator["recycle_center_name"] or coordinator["full_name"],
            coordinator["email"],
            photo_path
        ))
        conn.commit()

        # Prevent the same captured photo from being submitted repeatedly
        # through the same session. A new submission requires a new capture.
        session.pop("plastic_photo_path", None)
        session["plastic_submission_message"] = (
            "Submission sent successfully! It is now Pending coordinator verification."
        )
    except sqlite3.Error as error:
        conn.rollback()
        print("PLASTIC SUBMISSION DATABASE ERROR:", error)
        session["plastic_submission_message"] = (
            "The submission could not be saved. Please try again."
        )
    finally:
        conn.close()

    return redirect(url_for("plastic_camera"))


# ============================================================
# REPAIR / SEED DIGITAL REWARD CATALOGUE
# This runs when the Reward Center is opened as well as at startup,
# so older databases receive the manga rows even if startup seeding
# was skipped or the catalogue already contained physical rewards.
# ============================================================

def ensure_digital_reward_catalog(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reward_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reward_name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            reward_cost INTEGER NOT NULL DEFAULT 0,
            reward_type TEXT NOT NULL DEFAULT 'Physical',
            stock INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    add_column_if_missing(conn, "reward_catalog", "reward_url", "TEXT DEFAULT ''")
    add_column_if_missing(conn, "reward_catalog", "reward_category", "TEXT DEFAULT 'eco'")

    digital_rewards = [
        ("Digital Anime Book", "Start your personal digital reading collection.", 250, "https://mangaplus.shueisha.co.jp/", "anime"),
        ("Haikyu!!", "Manga reward — unlock after Digital Anime Book.", 300, "https://www.viz.com/shonenjump/haikyu-chapter-1/chapter/4118?action=read", "manga"),
        ("Demon Slayer", "Manga reward — unlock after Haikyu!!.", 350, "https://www.viz.com/manga-books/manga/demon-slayer-kimetsu-no-yaiba-volume-1-0/product/5547", "manga"),
        ("Black Clover", "Manga reward — unlock after Demon Slayer.", 400, "https://mangaplus.shueisha.co.jp/titles/100003", "manga"),
        ("Solo Leveling", "Digital comic reward — unlock after Black Clover.", 450, "https://www.tappytoon.com/en/book/solo-leveling-official", "manga"),
        ("Jujutsu Kaisen", "Manga reward — unlock after Solo Leveling.", 500, "https://www.viz.com/manga-books/manga/jujutsu-kaisen-volume-0-0/product/6537", "manga"),
        ("Eco Champion Certificate", "Personalise and print your Eco Fusion 360 achievement certificate.", 300, "", "certificate"),
        ("Planet Guardian Certificate", "A higher-tier printable certificate for your eco journey.", 600, "", "certificate"),
    ]
    for name, description, cost, url, category in digital_rewards:
        cur.execute("""
            INSERT OR IGNORE INTO reward_catalog
                (reward_name, description, reward_cost, reward_type, stock, active, reward_url, reward_category)
            VALUES (?, ?, ?, 'Digital', 0, 1, ?, ?)
        """, (name, description, cost, url, category))
        cur.execute("""
            UPDATE reward_catalog
               SET description = ?, reward_cost = ?, reward_type = 'Digital',
                   active = 1, reward_url = ?, reward_category = ?
             WHERE reward_name = ?
        """, (description, cost, url, category, name))
    conn.commit()


# ============================================================
# REWARD CENTER
# ============================================================

@app.route("/reward-center")
def reward_center():
    """Show eco rewards plus per-user sequential anime/manga unlocks."""
    if not is_user():
        return redirect(url_for("user_login"))

    email = (session.get("email") or "").strip().lower()
    if not email:
        session.clear()
        return redirect(url_for("user_login"))

    conn = None
    try:
        conn = get_connection()
        # Repair/seed the digital catalogue on page load so existing databases
        # cannot silently hide the manga cards just because they lack seed rows.
        ensure_digital_reward_catalog(conn)
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM users WHERE lower(email) = ? AND role = 'User'", (email,))
        user = cur.fetchone()
        if user is None:
            session.clear()
            return redirect(url_for("user_login"))
        email = user["email"]
        session["email"] = email

        cur.execute("SELECT * FROM user_progress WHERE email = ?", (email,))
        progress = cur.fetchone()
        if progress is None:
            cur.execute("INSERT OR IGNORE INTO user_progress (email, green_tokens) VALUES (?, 0)", (email,))
            conn.commit()
            cur.execute("SELECT * FROM user_progress WHERE email = ?", (email,))
            progress = cur.fetchone()

        cur.execute("SELECT * FROM reward_catalog WHERE active = 1 ORDER BY reward_cost ASC, reward_name ASC")
        rows = cur.fetchall()
        cur.execute("SELECT reward_catalog_id, reward_name, reward_url, unlocked_at FROM reward_unlocks WHERE email = ?", (email,))
        unlock_rows = cur.fetchall()
        unlocked_ids = {int(row["reward_catalog_id"]) for row in unlock_rows}
        unlocked_names = {row["reward_name"] for row in unlock_rows}
        unlocked_by_id = {int(row["reward_catalog_id"]): dict(row) for row in unlock_rows}
        balance = int(progress["green_tokens"] or 0) if progress else 0
        sequence = ["Digital Anime Book", "Haikyu!!", "Demon Slayer", "Black Clover", "Solo Leveling", "Jujutsu Kaisen"]
        catalogue = []
        for row in rows:
            item = dict(row)
            item["unlocked"] = int(item["id"]) in unlocked_ids
            item["unlock_url"] = (unlocked_by_id.get(int(item["id"]), {}).get("reward_url") or item.get("reward_url") or "")
            item["affordable"] = balance >= int(item["reward_cost"] or 0)
            item["locked_reason"] = ""
            if item.get("reward_category") in ("anime", "manga"):
                if item["reward_name"] in sequence:
                    pos = sequence.index(item["reward_name"])
                    if pos > 0 and sequence[pos - 1] not in unlocked_names:
                        item["locked_reason"] = f"Unlock {sequence[pos - 1]} first."
                    elif not item["unlocked"] and not item["affordable"]:
                        item["locked_reason"] = f"You need {int(item['reward_cost']) - balance} more Green Tokens."
                item["can_unlock"] = (not item["unlocked"] and not item["locked_reason"] and item["affordable"])
            else:
                item["can_unlock"] = item["affordable"] and not (item["reward_type"] == "Physical" and int(item["stock"] or 0) <= 0)
            catalogue.append(item)

        cur.execute("SELECT * FROM rewards WHERE email = ? ORDER BY created_at DESC", (email,))
        rewards = cur.fetchall()
        cur.execute("SELECT * FROM achievements WHERE email = ? ORDER BY earned_at DESC", (email,))
        achievements = cur.fetchall()
        cur.execute("SELECT * FROM token_transactions WHERE email = ? ORDER BY created_at DESC LIMIT 15", (email,))
        transactions = cur.fetchall()
        return render_template("reward_center.html", progress=progress, rewards=rewards,
                               catalogue=catalogue, achievements=achievements,
                               transactions=transactions, unlocks=unlock_rows)
    except sqlite3.OperationalError:
        app.logger.exception("Reward Center database error")
        return "The Reward Center database is temporarily busy. Please wait a few seconds and refresh the page.", 503
    except Exception:
        app.logger.exception("Reward Center failed to load")
        return "The Reward Center could not load. Please try again.", 500
    finally:
        if conn is not None:
            conn.close()


@app.route("/reward/redeem/<int:reward_id>", methods=["POST"])
def redeem_reward(reward_id):
    if not is_user():
        return redirect(url_for("user_login"))

    email = (session.get("email") or "").strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Serialise balance checks so concurrent requests cannot double-spend tokens.
        cur.execute("BEGIN IMMEDIATE")
        cur.execute("SELECT * FROM reward_catalog WHERE id = ? AND active = 1", (reward_id,))
        item = cur.fetchone()
        if item is None:
            session["reward_notice"] = ("error", "That reward is no longer available.")
        else:
            category = item["reward_category"] if "reward_category" in item.keys() else "eco"
            cur.execute("SELECT green_tokens FROM user_progress WHERE email = ?", (email,))
            progress = cur.fetchone()
            balance = int(progress["green_tokens"] or 0) if progress else 0

            if category in ("anime", "manga", "certificate"):
                cur.execute("SELECT id FROM reward_unlocks WHERE email = ? AND reward_catalog_id = ?", (email, reward_id))
                if cur.fetchone():
                    session["reward_notice"] = ("success", f"{item['reward_name']} is already unlocked for your account.")
                else:
                    sequence = ["Digital Anime Book", "Haikyu!!", "Demon Slayer", "Black Clover", "Solo Leveling", "Jujutsu Kaisen"]
                    position = sequence.index(item["reward_name"]) if item["reward_name"] in sequence else -1
                    if category in ("anime", "manga") and position > 0:
                        cur.execute("SELECT 1 FROM reward_unlocks WHERE email = ? AND reward_name = ?", (email, sequence[position - 1]))
                        if cur.fetchone() is None:
                            session["reward_notice"] = ("error", f"Unlock {sequence[position - 1]} first.")
                            conn.commit()
                            return redirect(url_for("reward_center"))
                    cost = int(item["reward_cost"] or 0)
                    if balance < cost:
                        session["reward_notice"] = ("error", f"You need {cost - balance} more Green Tokens.")
                    else:
                        cur.execute("UPDATE user_progress SET green_tokens = green_tokens - ?, last_updated = CURRENT_TIMESTAMP WHERE email = ? AND green_tokens >= ?", (cost, email, cost))
                        if cur.rowcount != 1:
                            raise ValueError("Your token balance changed. Please refresh and try again.")
                        cur.execute("INSERT INTO reward_unlocks (email, reward_catalog_id, reward_name, reward_cost, reward_url) VALUES (?, ?, ?, ?, ?)", (email, reward_id, item["reward_name"], cost, item["reward_url"] or ""))
                        cur.execute("INSERT INTO token_transactions (email, amount, reason, reference_id) VALUES (?, ?, ?, ?)", (email, -cost, f"Digital unlock: {item['reward_name']}", reward_id))
                        session["reward_notice"] = ("success", f"{item['reward_name']} unlocked! It is saved to your account and will not be charged twice.")
            else:
                cost = int(item["reward_cost"] or 0)
                if item["reward_type"] == "Physical" and int(item["stock"] or 0) <= 0:
                    session["reward_notice"] = ("error", "This physical reward is out of stock.")
                elif balance < cost:
                    session["reward_notice"] = ("error", "You do not have enough Green Tokens yet.")
                else:
                    cur.execute("UPDATE user_progress SET green_tokens = green_tokens - ?, last_updated = CURRENT_TIMESTAMP WHERE email = ? AND green_tokens >= ?", (cost, email, cost))
                    if cur.rowcount != 1:
                        raise ValueError("Your token balance changed. Please try again.")
                    if item["reward_type"] == "Physical":
                        cur.execute("UPDATE reward_catalog SET stock = stock - 1 WHERE id = ? AND stock > 0", (reward_id,))
                        if cur.rowcount != 1:
                            raise ValueError("This reward just went out of stock. Please try again.")
                    cur.execute("INSERT INTO rewards (email, reward_name, reward_cost, status) VALUES (?, ?, ?, 'Pending')", (email, item["reward_name"], cost))
                    redemption_id = cur.lastrowid
                    cur.execute("INSERT INTO token_transactions (email, amount, reason, reference_id) VALUES (?, ?, ?, ?)", (email, -cost, f"Reward redemption: {item['reward_name']}", redemption_id))
                    session["reward_notice"] = ("success", "Redemption request submitted! Your request is now pending admin review.")
        conn.commit()
    except ValueError as exc:
        conn.rollback()
        session["reward_notice"] = ("error", str(exc))
    except Exception:
        conn.rollback()
        app.logger.exception("Reward redemption failed")
        session["reward_notice"] = ("error", "Could not process this redemption. Please try again.")
    finally:
        conn.close()
    return redirect(url_for("reward_center"))


@app.route("/admin/reward-management", methods=["GET", "POST"])
def admin_reward_management():
    if not is_admin():
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cur = conn.cursor()
    notice = None
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "add_reward":
            name = request.form.get("reward_name", "").strip()
            description = request.form.get("description", "").strip()
            reward_type = request.form.get("reward_type", "Physical")
            try:
                cost = int(request.form.get("reward_cost", "0"))
                stock = int(request.form.get("stock", "0"))
            except ValueError:
                cost, stock = -1, -1
            if not name or cost < 0 or stock < 0 or reward_type not in ("Physical", "Digital"):
                notice = ("error", "Enter a name, valid token cost, stock, and reward type.")
            else:
                try:
                    cur.execute("INSERT INTO reward_catalog (reward_name, description, reward_cost, reward_type, stock, active) VALUES (?, ?, ?, ?, ?, 1)",
                                (name, description, cost, reward_type, stock if reward_type == "Physical" else 0))
                    conn.commit()
                    notice = ("success", "Reward added to the catalogue.")
                except sqlite3.IntegrityError:
                    conn.rollback()
                    notice = ("error", "A reward with that name already exists.")
        elif action == "update_reward":
            try:
                reward_id = int(request.form.get("reward_id", "0"))
                cost = int(request.form.get("reward_cost", "0"))
                stock = int(request.form.get("stock", "0"))
                active = 1 if request.form.get("active") == "1" else 0
                if cost < 0 or stock < 0:
                    raise ValueError
                cur.execute("UPDATE reward_catalog SET reward_cost = ?, stock = ?, active = ? WHERE id = ?", (cost, stock, active, reward_id))
                conn.commit()
                notice = ("success", "Reward settings updated.")
            except (ValueError, TypeError):
                conn.rollback()
                notice = ("error", "Enter valid non-negative values.")
        elif action == "update_redemption":
            try:
                redemption_id = int(request.form.get("redemption_id", "0"))
                status = request.form.get("status", "Pending")
                if status not in ("Approved", "Rejected", "Completed"):
                    raise ValueError
                cur.execute("SELECT * FROM rewards WHERE id = ?", (redemption_id,))
                redemption = cur.fetchone()
                if redemption is None:
                    raise ValueError
                if redemption["status"] == "Pending" and status == "Rejected":
                    cur.execute("UPDATE user_progress SET green_tokens = green_tokens + ?, last_updated = CURRENT_TIMESTAMP WHERE email = ?", (redemption["reward_cost"], redemption["email"]))
                    cur.execute("INSERT INTO token_transactions (email, amount, reason, reference_id) VALUES (?, ?, ?, ?)",
                                (redemption["email"], redemption["reward_cost"], f"Refund: {redemption['reward_name']}", redemption_id))
                    cur.execute("SELECT id FROM reward_catalog WHERE reward_name = ? AND reward_type = 'Physical'", (redemption["reward_name"],))
                    catalog_item = cur.fetchone()
                    if catalog_item:
                        cur.execute("UPDATE reward_catalog SET stock = stock + 1 WHERE id = ?", (catalog_item["id"],))
                cur.execute("UPDATE rewards SET status = ? WHERE id = ?", (status, redemption_id))
                conn.commit()
                notice = ("success", "Redemption status updated.")
            except (ValueError, TypeError):
                conn.rollback()
                notice = ("error", "Invalid redemption request.")
        if notice:
            session["reward_admin_notice"] = notice
        conn.close()
        return redirect(url_for("admin_reward_management"))

    cur.execute("SELECT * FROM reward_catalog ORDER BY reward_type, reward_cost")
    catalogue = cur.fetchall()
    cur.execute("SELECT * FROM rewards ORDER BY created_at DESC")
    redemptions = cur.fetchall()
    conn.close()
    notice = session.pop("reward_admin_notice", notice)
    return render_template("admin_reward_management.html", catalogue=catalogue,
                           redemptions=redemptions, notice=notice)


# ============================================================
# TREE GAME
# ============================================================

@app.route("/tree-game")
def tree_game():

    if not is_user():

        return redirect(
            url_for("user_login")
        )

    return render_template(
        "tree_game.html"
    )


# ============================================================
# COORDINATOR DASHBOARD
# ============================================================

@app.route("/coordinator-dashboard")
def coordinator_dashboard():

    if not is_coordinator():

        return redirect(
            url_for("coordinator_login")
        )

    email = session["email"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            full_name,
            email,
            recycle_center_name,
            recycle_center_id,
            district,
            address,
            mobile,
            approved
        FROM users
        WHERE email = ?
        AND role = 'Recycle Center Coordinator'
    """, (email,))

    coordinator = cur.fetchone()

    cur.execute("""
        SELECT *
        FROM recycling_submissions
        WHERE lower(trim(coordinator_email)) = lower(trim(?))
        ORDER BY submitted_at DESC
    """, (email,))

    submissions = cur.fetchall()

    conn.close()

    return render_template(
        "coordinator_dashboard.html",
        coordinator=coordinator,
        submissions=submissions
    )


# ============================================================
# COORDINATOR UPDATE SUBMISSION
# ============================================================

@app.route(
    "/coordinator/submission/<int:submission_id>",
    methods=["POST"]
)
def coordinator_update_submission(
    submission_id
):

    if not is_coordinator():

        return redirect(
            url_for("coordinator_login")
        )

    status = request.form.get(
        "status",
        "Pending"
    )

    remarks = request.form.get(
        "remarks",
        ""
    ).strip()

    allowed_statuses = [
        "Pending",
        "Accepted",
        "Completed",
        "Rejected"
    ]

    if status not in allowed_statuses:

        status = "Pending"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE recycling_submissions
        SET
            status = ?,
            remarks = ?,
            camera_verified = CASE WHEN ? IN ('Accepted', 'Completed', 'Rejected') THEN 1 ELSE camera_verified END
        WHERE id = ?
        AND lower(trim(coordinator_email)) = lower(trim(?))
    """, (
        status,
        remarks,
        status,
        submission_id,
        session["email"]
    ))

    # Save a user-facing notification whenever the assigned coordinator
    # updates the submission review. The notification includes their remarks.
    if cur.rowcount > 0:
        cur.execute("""
            SELECT email, plastic_type, recycle_center
            FROM recycling_submissions
            WHERE id = ?
              AND lower(trim(coordinator_email)) = lower(trim(?))
            LIMIT 1
        """, (submission_id, session["email"]))
        reviewed_submission = cur.fetchone()

        cur.execute("""
            SELECT full_name, recycle_center_name
            FROM users
            WHERE lower(trim(email)) = lower(trim(?))
            LIMIT 1
        """, (session["email"],))
        coordinator_user = cur.fetchone()

        if reviewed_submission:
            coordinator_name = (
                (coordinator_user["recycle_center_name"] or coordinator_user["full_name"])
                if coordinator_user else "Your recycling coordinator"
            )
            review_text = remarks if remarks else "No additional remarks were provided."
            notification_message = (
                f"{coordinator_name} reviewed your {reviewed_submission['plastic_type']} "
                f"submission for {reviewed_submission['recycle_center']}. "
                f"Status: {status}. Coordinator's remarks: {review_text}"
            )
            cur.execute("""
                INSERT INTO notifications
                    (user_email, submission_id, title, message, status)
                VALUES (?, ?, ?, ?, 'Unread')
            """, (
                reviewed_submission["email"],
                submission_id,
                f"Plastic submission {status}",
                notification_message
            ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("coordinator_dashboard")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cur = conn.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM users
        ORDER BY created_at DESC
    """)

    users = cur.fetchall()

    # --------------------------------------------------------
    # COORDINATORS
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM users
        WHERE role = 'Recycle Center Coordinator'
        ORDER BY created_at DESC
    """)

    coordinators = cur.fetchall()

    # --------------------------------------------------------
    # COORDINATOR REQUESTS
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM coordinator_requests
        ORDER BY created_at DESC
    """)

    coordinator_requests = cur.fetchall()

    # --------------------------------------------------------
    # SUBMISSIONS
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM recycling_submissions
        ORDER BY submitted_at DESC
    """)

    submissions = cur.fetchall()

    # --------------------------------------------------------
    # MESSAGES
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM messages
        ORDER BY created_at DESC
    """)

    messages = cur.fetchall()

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM feedback
        ORDER BY created_at DESC
    """)

    feedback = cur.fetchall()

    # --------------------------------------------------------
    # QUIZ
    # --------------------------------------------------------

    cur.execute("""
        SELECT *
        FROM quiz_questions
        ORDER BY id
    """)

    quiz_questions = cur.fetchall()

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'User'
    """)

    total_users = cur.fetchone()["total"]

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'Recycle Center Coordinator'
    """)

    total_coordinators = cur.fetchone()["total"]

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM recycling_submissions
    """)

    total_submissions = cur.fetchone()["total"]

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM messages
        WHERE status = 'Unread'
    """)

    unread_messages = cur.fetchone()["total"]

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM feedback
    """)

    total_feedback = cur.fetchone()["total"]

    conn.close()

    return render_template(
        "admin_dashboard.html",

        users=users,

        coordinators=coordinators,

        coordinator_requests=coordinator_requests,

        submissions=submissions,

        messages=messages,

        feedback=feedback,

        quiz_questions=quiz_questions,

        total_users=total_users,

        total_coordinators=total_coordinators,

        total_submissions=total_submissions,

        unread_messages=unread_messages,

        total_feedback=total_feedback
    )


# ============================================================
# ADMIN APPROVE COORDINATOR
# ============================================================

@app.route(
    "/admin/approve-coordinator/<int:user_id>"
)
def approve_coordinator(user_id):

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET approved = 1
        WHERE id = ?
        AND role = 'Recycle Center Coordinator'
    """, (user_id,))

    cur.execute("""
        UPDATE coordinator_requests
        SET status = 'Approved'
        WHERE email = (
            SELECT email
            FROM users
            WHERE id = ?
        )
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# ADMIN REJECT COORDINATOR
# ============================================================

@app.route(
    "/admin/reject-coordinator/<int:user_id>"
)
def reject_coordinator(user_id):

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET approved = 0
        WHERE id = ?
        AND role = 'Recycle Center Coordinator'
    """, (user_id,))

    cur.execute("""
        UPDATE coordinator_requests
        SET status = 'Rejected'
        WHERE email = (
            SELECT email
            FROM users
            WHERE id = ?
        )
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# ADMIN CHANGE GREEN TOKENS
# ============================================================

@app.route(
    "/admin/tokens",
    methods=["POST"]
)
def admin_tokens():

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    amount_text = request.form.get(
        "amount",
        "0"
    )

    try:

        amount = int(amount_text)

    except ValueError:

        amount = 0

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO user_progress
        (
            email,
            green_tokens
        )
        VALUES
        (
            ?,
            ?
        )
        ON CONFLICT(email)
        DO UPDATE SET
            green_tokens =
                user_progress.green_tokens
                + excluded.green_tokens,

            last_updated =
                CURRENT_TIMESTAMP
    """, (
        email,
        amount
    ))

    if amount != 0:
        cur.execute("""
            INSERT INTO token_transactions (email, amount, reason)
            SELECT ?, ?, 'Admin token adjustment'
            WHERE EXISTS (SELECT 1 FROM users WHERE email = ? AND role = 'User')
        """, (email, amount, email))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# USER MESSAGE TO ADMIN
# ============================================================

@app.route(
    "/message-admin",
    methods=["POST"]
)
def message_admin():

    if not logged_in():

        return redirect(
            url_for("home")
        )

    message = request.form.get(
        "message",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    if message:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO messages
            (
                user_email,
                subject,
                message
            )
            VALUES (?, ?, ?)
        """, (
            session["email"],
            subject,
            message
        ))

        conn.commit()
        conn.close()

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# USER FEEDBACK
# ============================================================

@app.route(
    "/feedback",
    methods=["POST"]
)
def submit_feedback():

    if not logged_in():

        return redirect(
            url_for("home")
        )

    rating_text = request.form.get(
        "rating",
        "0"
    )

    message = request.form.get(
        "message",
        ""
    ).strip()

    try:

        rating = int(rating_text)

    except ValueError:

        rating = 0

    rating = max(
        0,
        min(
            5,
            rating
        )
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO feedback
        (
            email,
            rating,
            message
        )
        VALUES (?, ?, ?)
    """, (
        session["email"],
        rating,
        message
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# ADMIN REPLY
# ============================================================

@app.route(
    "/admin/reply",
    methods=["POST"]
)
def admin_reply():

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    message_id = request.form.get(
        "message_id"
    )

    reply = request.form.get(
        "reply",
        ""
    ).strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE messages
        SET
            reply = ?,
            status = 'Replied',
            replied_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        reply,
        message_id
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# ADMIN ADD QUIZ
# ============================================================

@app.route(
    "/admin/add-quiz",
    methods=["POST"]
)
def add_quiz():

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    question = request.form.get(
        "question",
        ""
    ).strip()

    option_a = request.form.get(
        "option_a",
        ""
    ).strip()

    option_b = request.form.get(
        "option_b",
        ""
    ).strip()

    option_c = request.form.get(
        "option_c",
        ""
    ).strip()

    option_d = request.form.get(
        "option_d",
        ""
    ).strip()

    correct_answer = request.form.get(
        "correct_answer",
        ""
    ).strip().upper()

    if not all([
        question,
        option_a,
        option_b,
        option_c,
        option_d
    ]):

        return redirect(
            url_for("admin_dashboard")
        )

    if correct_answer not in [
        "A",
        "B",
        "C",
        "D"
    ]:

        return redirect(
            url_for("admin_dashboard")
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO quiz_questions
        (
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        correct_answer
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# ADMIN DELETE QUIZ
# ============================================================

@app.route(
    "/admin/delete-quiz/<int:question_id>"
)
def delete_quiz(question_id):

    if not is_admin():

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM quiz_questions
        WHERE id = ?
    """, (question_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# QUIZ
# ============================================================

@app.route("/quiz")
def quiz():

    if not logged_in():

        return redirect(
            url_for("home")
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM quiz_questions
        WHERE active = 1
        ORDER BY RANDOM()
        LIMIT 10
    """)

    questions = cur.fetchall()

    conn.close()

    return render_template(
        "quiz.html",
        questions=questions
    )


# ============================================================
# QUIZ SUBMIT
# ============================================================

@app.route(
    "/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    if not logged_in():

        return redirect(
            url_for("home")
        )

    email = session["email"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM quiz_questions
        WHERE active = 1
        ORDER BY id
        LIMIT 10
    """)

    questions = cur.fetchall()

    score = 0
    correct = 0
    wrong = 0

    for question in questions:

        selected = request.form.get(
            f"question_{question['id']}",
            ""
        ).upper()

        if selected == question["correct_answer"]:

            score += 5
            correct += 1

        elif selected:

            score -= 2
            wrong += 1

    if score < 0:

        score = 0

    cur.execute("""
        INSERT INTO quiz_attempts
        (
            email,
            quiz_week,
            score,
            correct_answers,
            wrong_answers
        )
        VALUES
        (
            ?,
            strftime('%Y-%W', 'now'),
            ?,
            ?,
            ?
        )
        ON CONFLICT(email, quiz_week)
        DO UPDATE SET
            score = excluded.score,
            correct_answers =
                excluded.correct_answers,
            wrong_answers =
                excluded.wrong_answers
    """, (
        email,
        score,
        correct,
        wrong
    ))

    cur.execute("""
        INSERT INTO user_progress
        (
            email,
            green_tokens
        )
        VALUES (?, ?)

        ON CONFLICT(email)
        DO UPDATE SET

            green_tokens =
                user_progress.green_tokens
                + excluded.green_tokens,

            last_updated =
                CURRENT_TIMESTAMP
    """, (
        email,
        score
    ))

    conn.commit()
    conn.close()

    return render_template(
        "quiz_result.html",
        score=score,
        correct=correct,
        wrong=wrong
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# TEST PAGE
# ============================================================

@app.route("/test")
def test():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Eco Fusion 360 Test</title>
        <style>
            body {
                font-family: Arial;
                background: #071a12;
                color: white;
                text-align: center;
                padding: 100px;
            }

            h1 {
                color: #39ff88;
            }
        </style>
    </head>

    <body>

        <h1>🌍 Eco Fusion 360</h1>

        <h2>Flask server is working!</h2>

        <p>
            The three login system is ready.
        </p>

        <p>
            👤 User Login
            |
            ♻️ Coordinator Login
            |
            🔐 Admin Login
        </p>

    </body>
    </html>
    """


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    create_database()

    print()
    print("==============================================")
    print("🌍 ECO FUSION 360 WEB")
    print("==============================================")
    print()
    print("👤 USER LOGIN:")
    print("http://127.0.0.1:5001/user-login")
    print()
    print("♻️ COORDINATOR LOGIN:")
    print("http://127.0.0.1:5001/coordinator-login")
    print()
    print("📝 COORDINATOR REGISTER:")
    print("http://127.0.0.1:5001/coordinator-register")
    print()
    print("🔐 ADMIN LOGIN:")
    print("http://127.0.0.1:5001/admin-login")
    print()
    print("🏠 HOME:")
    print("http://127.0.0.1:5001/")
    print()
    # ------------------------------------------------------------
    # NETWORK / MOBILE ACCESS
    # ------------------------------------------------------------
    # 0.0.0.0 makes Flask listen on all network interfaces,
    # so another device on the same Wi-Fi can connect.
    PORT = 5001
    HOST = "0.0.0.0"

    try:
        # Get the laptop's local Wi-Fi/LAN IPv4 address.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
    except Exception:
        local_ip = "YOUR-LAPTOP-IP"

    print("🧪 TEST:")
    print(f"http://127.0.0.1:{PORT}/test")
    print()
    print("📱 MOBILE / OTHER DEVICES:")
    print(f"http://{local_ip}:{PORT}/")
    print()
    print("📱 MOBILE TEST:")
    print(f"http://{local_ip}:{PORT}/test")
    print()
    print("⚠️ IMPORTANT:")
    print("1. Connect the phone and laptop to the SAME Wi-Fi.")
    print("2. On the phone, use the MOBILE / OTHER DEVICES URL above.")
    print("3. Do NOT use localhost or 127.0.0.1 on the phone.")
    print("4. If Windows Firewall asks for access, allow Python on")
    print("   Private networks.")
    print()
    print("==============================================")
    print(f"Database: {DB_PATH}")
    print(f"Listening on: {HOST}:{PORT}")
    print(f"LAN address: http://{local_ip}:{PORT}")
    print("==============================================")

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )
