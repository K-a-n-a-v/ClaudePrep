# Spec: Login and Logout

## Overview

Implement the login and logout flows so registered users can authenticate into
Spendly and end their session. `GET /login` already renders the template and
`GET /logout` returns a stub string — this step wires up the `POST /login`
handler (validates credentials, starts a Flask session) and replaces the
`GET /logout` stub with a real session-clearing redirect. After login, the user
is sent to `/profile` (a stub until Step 4). After logout, they are sent to
`/`. No access-guarding of other routes happens in this step.

## Depends on

- Step 1 — Database (`get_db()`, `init_db()`, `users` table must exist)
- Step 2 — Registration (`get_user_by_email()` must exist, users must exist in DB)

## Routes

- `POST /login` — Receives email + password, validates credentials, sets `session["user_id"]`, redirects to `/profile` — public
- `GET /logout` — Clears the session, redirects to `/` — public (no guard needed)

`GET /login` already exists and only needs its template updated to render the
form correctly.

## Database changes

No new tables or columns. No new DB helpers are needed — `get_user_by_email(email)`
already exists in `database/db.py` and is sufficient to look up the user for
credential checking.

## Templates

- **Modify:** `templates/login.html`
  - Add a `<form method="POST" action="{{ url_for('login') }}">` with fields: `email`, `password`
  - Display flash messages (error on bad credentials, success from previous registration)
  - Link to `/register` for users without an account
- **Modify:** `templates/base.html`
  - Show a "Log out" nav link when `session.user_id` is set; show "Log in" when it is not

## Files to change

- `app.py`
  - Import `session`, `check_password_hash` (werkzeug already imported, add `check_password_hash`)
  - Change `GET /login` route to accept `GET` and `POST` methods
  - Add `POST /login` logic: look up user by email, verify password hash, set `session["user_id"]`, redirect to `/profile`; on failure re-render with error
  - Replace `GET /logout` stub with real handler: `session.clear()`, redirect to `/`
- `templates/login.html` — wire up the form and flash/error display
- `templates/base.html` — conditional nav links based on `session`

## Files to create

- `static/css/login.css` — page-specific styles for the login form

## New dependencies

No new dependencies. `werkzeug.security.check_password_hash` is already available
via `werkzeug` which is installed as a Flask dependency.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never f-strings in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Store only `user_id` (integer) in `session` — never store email or password
- On failed login show a generic error ("Invalid email or password") — do not reveal which field is wrong
- `session.permanent` should remain `False` (default) — session ends when browser closes
- Do not guard any other routes in this step — access control is a later step
- After successful login → `redirect(url_for('profile'))`
- After logout → `redirect(url_for('landing'))`

## Definition of done

- [ ] Visiting `GET /login` renders a form with `email` and `password` fields
- [ ] Submitting valid credentials sets `session["user_id"]` and redirects to `/profile`
- [ ] Submitting an unknown email shows "Invalid email or password" and does not crash
- [ ] Submitting a correct email with wrong password shows "Invalid email or password"
- [ ] The email field retains its value after a failed login attempt
- [ ] Visiting `/logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer set
- [ ] The nav in `base.html` shows "Log out" when logged in and "Log in" when logged out
- [ ] Flash message from a successful registration appears on the login page
- [ ] `login.css` is linked and styles use CSS variables only
- [ ] App starts without errors and existing seed data is unaffected
