"""Tests for the Flask signup app."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import app, init_db


@pytest.fixture
def client():
    """Create a test client with a fresh database for each test."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"

    # Initialize the database before each test
    init_db()

    with app.test_client() as client:
        yield client

    # Clean up after each test
    if os.path.exists("users.db"):
        os.remove("users.db")


# ── GET request ───────────────────────────────────────────────────────────────

def test_signup_page_loads(client):
    """Home page should return 200."""
    response = client.get("/")
    assert response.status_code == 200

def test_signup_page_contains_form(client):
    """Page should contain the form fields."""
    response = client.get("/")
    assert b"name" in response.data
    assert b"email" in response.data
    assert b"password" in response.data


# ── Successful signup ─────────────────────────────────────────────────────────

def test_valid_signup_redirects(client):
    """Valid form submission should redirect."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepass123",
        "confirm": "securepass123",
    })
    assert response.status_code == 302

def test_valid_signup_shows_success_message(client):
    """After redirect, success message should appear on signin page."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepass123",
        "confirm": "securepass123",
    }, follow_redirects=True)
    assert b"successfully" in response.data


# ── Validation errors ─────────────────────────────────────────────────────────

def test_missing_name_shows_error(client):
    """Empty name should show validation error."""
    response = client.post("/", data={
        "name": "",
        "email": "jane@example.com",
        "password": "securepass123",
        "confirm": "securepass123",
    }, follow_redirects=True)
    assert b"Full name is required" in response.data

def test_invalid_email_shows_error(client):
    """Email without @ should show validation error."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "not-an-email",
        "password": "securepass123",
        "confirm": "securepass123",
    }, follow_redirects=True)
    assert b"valid email" in response.data

def test_short_password_shows_error(client):
    """Password under 8 characters should show validation error."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "short",
        "confirm": "short",
    }, follow_redirects=True)
    assert b"8 characters" in response.data

def test_password_mismatch_shows_error(client):
    """Mismatched passwords should show validation error."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepass123",
        "confirm": "differentpass",
    }, follow_redirects=True)
    assert b"do not match" in response.data

def test_multiple_errors_at_once(client):
    """Submitting empty form should show multiple errors."""
    response = client.post("/", data={
        "name": "",
        "email": "",
        "password": "",
        "confirm": "",
    }, follow_redirects=True)
    assert b"Full name is required" in response.data
    assert b"valid email" in response.data
    assert b"8 characters" in response.data


# ── Form value preservation ───────────────────────────────────────────────────

def test_name_preserved_on_error(client):
    """Name value should be kept in the form after a validation error."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "short",
        "confirm": "short",
    }, follow_redirects=True)
    assert b"Jane Doe" in response.data

def test_email_preserved_on_error(client):
    """Email value should be kept in the form after a validation error."""
    response = client.post("/", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "short",
        "confirm": "short",
    }, follow_redirects=True)
    assert b"jane@example.com" in response.data


# ── Signin ────────────────────────────────────────────────────────────────────

def test_signin_page_loads(client):
    """Signin page should return 200."""
    response = client.get("/signin")
    assert response.status_code == 200

def test_signin_invalid_credentials(client):
    """Wrong credentials should show error."""
    response = client.post("/signin", data={
        "email": "nobody@example.com",
        "password": "wrongpass",
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data


# ── Dashboard ─────────────────────────────────────────────────────────────────

def test_dashboard_accessible_without_login(client):
    """Dashboard has no auth check - should still return 200 (known flaw)."""
    response = client.get("/dashboard")
    assert response.status_code == 200

def test_logout_redirects(client):
    """Logout should redirect to signin."""
    response = client.get("/logout")
    assert response.status_code == 302