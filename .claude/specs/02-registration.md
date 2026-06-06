# Spec: Registration

## Overview

Implement the user registration flow so new visitors can create a Spendly account.
The `GET /register` route already renders the template; this step wires up the
`POST /register` handler, writes the DB helper, and makes the form fully functional.
On success, the user is redirected to `/login` with a flash message. No session or
auto-login is created here — that belongs to Step 3.

## Depends on

- Step 1 — Database (`get_db()`, `init_db()`, `users` table must exist)

## Routes

- `POST /register` — Receives form data, validates, hashes password, inserts user, redirects — public

`GET /register` already exists; it only needs its template updated to render the form correctly.

## Database changes

No new tables or columns. Two new helpers are needed in `database/db.py`:

- `create_user(name, email, password_hash)` — inserts a row into `users`, returns the new `id`
- `get_user_by_email(email)` — returns the `users` row for the given email, or `None`

## Templates

- **Modify:** `templates/register.html`
  - Add a `<form method="POST" action="{{ url_for('register') }}">` with fields: `name`, `email`, `password`, `confirm_password`
  - Display flash messages (errors and success)
  - Link to `/login` for users who already have an account

## Files to change

- `app.py` — add `POST /register` route; add `secret_key`; import `create_user`, `get_user_by_email`; import `session`, `flash`, `redirect`, `url_for`, `request` from Flask
- `database/db.py` — add `create_user()` and `get_user_by_email()`
- `templates/register.html` — wire up the form and flash message display

## Files to create

- `static/css/register.css` — page-specific styles for the registration form

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` before insert
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `app.secret_key` must be set (use a hardcoded dev string for now — flagged for env var in a later step)
- Validate server-side: name non-empty, valid email format, password ≥ 8 chars, passwords match
- Duplicate email → flash an error, re-render the form (do not crash)
- Catch `sqlite3.IntegrityError` on insert as a safety net for the UNIQUE constraint
- After successful registration → `redirect(url_for('login'))` with a success flash
- Use `abort(400)` only for malformed requests, not validation failures — flash + re-render instead

## Definition of done

- [ ] Submitting the form with valid data creates a new row in `users` with a hashed password
- [ ] Submitting with a duplicate email shows an inline error and does not crash
- [ ] Submitting with mismatched passwords shows a validation error
- [ ] Submitting with a password shorter than 8 characters shows a validation error
- [ ] Successful registration redirects to `/login` and shows a success flash message
- [ ] The form retains `name` and `email` values after a failed submission
- [ ] Visiting `/register` while already having an account still works (no session guard needed yet)
- [ ] `register.css` is linked and styles are applied using CSS variables only
- [ ] App starts without errors and existing seed data is unaffected
