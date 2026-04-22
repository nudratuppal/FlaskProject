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

        flash("Account created successfully! Welcome aboard.", "success")
        return redirect(url_for("signup"))

    return render_template("signup.html")


if __name__ == "__main__":
    # Debug mode on in production - security issue
    app.run(debug=True, host="0.0.0.0")
