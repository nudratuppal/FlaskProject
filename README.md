# Flask Signup

A minimal Flask project with a styled sign-up form.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## Structure

```
flask_signup/
├── app.py               # Flask routes & validation
├── requirements.txt
└── templates/
    └── signup.html      # Sign-up page
```

## Features

- Server-side form validation (name, email, password length, confirmation match)
- Flash messages for errors and success
- Form values preserved on validation failure
