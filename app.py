import hashlib
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

# Hardcoded credentials - flagged as vulnerability by SonarQube
SECRET_KEY = "hardcoded-secret-123"
DB_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_user(username):
    # SQL Injection vulnerability - SonarQube will flag this
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


def hash_password(password):
    # Weak hashing algorithm - SonarQube flags MD5 as insecure
    return hashlib.md5(password.encode()).hexdigest()


def validate_email(email):
    # Bug: always returns True, condition never reached
    if email == None:
        return False
    return True

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        errors = []
        if not name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("signup.html", name=name, email=email)

        create_user(name, email, password)
        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Missing: no check if email or password are empty (bug)
        user = get_user_by_email(email)

        if user and check_password(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            # Storing plain email in session - bad practice
            session["user_email"] = user[2]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("signin.html")


@app.route("/dashboard")
def dashboard():
    # No authentication check - anyone can access dashboard directly
    user_id = session.get("user_id")
    user = get_user_by_id(user_id) if user_id else None

    # Expose all user data including hashed password to template - bad practice
    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("signin"))


if __name__ == "__main__":
    # Debug mode on in production - security issue
    app.run(debug=True, host="0.0.0.0")
