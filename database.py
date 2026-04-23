print("🔥 LOADING DATABASE.PY")

import sqlite3
import hashlib
import os
import random
import re

# ---------------- CONNECT ----------------
def connect_db():
    return sqlite3.connect("users.db", check_same_thread=False)


# ---------------- CREATE TABLE ----------------
def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()

        # USERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            salt TEXT,
            otp TEXT,
            verified INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user'
        )
        """)

        # JOBS POSTED BY RECRUITER
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recruiter_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            description TEXT,
            posted_by TEXT
        )
        """)


# ---------------- PASSWORD VALIDATION ----------------
def validate_password(password):
    if len(password) < 6 or len(password) > 16:
        return False

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{6,16}$'
    return re.match(pattern, password)


# ---------------- HASH ----------------
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def generate_salt():
    return os.urandom(16).hex()


# ---------------- OTP ----------------
def generate_otp():
    return str(random.randint(100000, 999999))


def save_otp(email, otp):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET otp=? WHERE email=?",
            (otp.strip(), email.strip())
        )


# ---------------- VERIFY OTP ----------------
def verify_otp(email, otp):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT otp FROM users WHERE email=?",
            (email.strip(),)
        )

        data = cursor.fetchone()

        if not data:
            return "no_user"

        db_otp = (data[0] or "").strip()

        if db_otp == otp.strip():
            cursor.execute(
                "UPDATE users SET otp=NULL WHERE email=?",
                (email.strip(),)
            )
            return "success"

        return "invalid"


# ---------------- SIGNUP ----------------
def create_user(email, password):
    with connect_db() as conn:
        cursor = conn.cursor()

        email = email.strip()

        if not validate_password(password):
            return "weak_password"

        salt = generate_salt()
        hashed = hash_password(password, salt)

        try:
            cursor.execute(
                "INSERT INTO users (email, password, salt) VALUES (?, ?, ?)",
                (email, hashed, salt)
            )
            return "success"
        except sqlite3.IntegrityError:
            return "exists"


# ---------------- VERIFY ACCOUNT ----------------
def verify_user(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET verified=1 WHERE email=?",
            (email.strip(),)
        )


# ---------------- LOGIN ----------------
def login_user(email, password):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password, salt, verified FROM users WHERE email=?",
            (email.strip(),)
        )

        user = cursor.fetchone()

        if not user:
            return "no_user"

        stored_hash, salt, verified = user

        if not verified:
            return "not_verified"

        if hash_password(password, salt) == stored_hash:
            return "success"

        return "wrong_password"


# ---------------- RESET PASSWORD ----------------
def reset_password(email, new_password):
    with connect_db() as conn:
        cursor = conn.cursor()

        if not validate_password(new_password):
            return "weak_password"

        salt = generate_salt()
        hashed = hash_password(new_password, salt)

        cursor.execute(
            "UPDATE users SET password=?, salt=? WHERE email=?",
            (hashed, salt, email.strip())
        )

        return "success"


# ---------------- ROLE MANAGEMENT ----------------
def make_recruiter(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET role='recruiter' WHERE email=?",
            (email.strip(),)
        )


def get_user_role(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE email=?",
            (email.strip(),)
        )
        data = cursor.fetchone()
        return data[0] if data else "user"


# ---------------- RECRUITER JOBS ----------------
def post_job(title, company, description, email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO recruiter_jobs (title, company, description, posted_by)
        VALUES (?, ?, ?, ?)
        """, (title, company, description, email))


def get_recruiter_jobs(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT title, company, description FROM recruiter_jobs
        WHERE posted_by=?
        """, (email,))
        return cursor.fetchall()


# ✅ FIXED DELETE FUNCTION (IMPORTANT)
def delete_job(title, email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM recruiter_jobs WHERE title=? AND posted_by=?",
            (title, email)
        )
        conn.commit()
        # ---------------- ADMIN FEATURES ----------------

def make_admin(email):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET role='admin' WHERE email=?",
            (email.strip(),)
        )
        conn.commit()


def get_all_users():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, role FROM users")
        return cursor.fetchall()


def get_all_jobs():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT title, company, description, posted_by
        FROM recruiter_jobs
        """)
        return cursor.fetchall()


def delete_any_job(title):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM recruiter_jobs WHERE title=?",
            (title,)
        )
        conn.commit()
        def apply_job(email, title, company):
            with connect_db() as conn:
             cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            job_title TEXT,
            company TEXT
        )
        """)

        cursor.execute("""
        INSERT INTO applications (user_email, job_title, company)
        VALUES (?, ?, ?)
        """, (email, title, company))


def get_applications_for_recruiter(recruiter_email):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT a.user_email, a.job_title, a.company
        FROM applications a
        JOIN recruiter_jobs r
        ON a.job_title = r.title
        WHERE r.posted_by=?
        """, (recruiter_email,))

        return cursor.fetchall()