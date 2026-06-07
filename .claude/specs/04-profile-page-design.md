# Spec: Profile Page Design

## Overview

Replace the `GET /profile` stub with a real, access-guarded profile page. The
page shows the logged-in user's account info (name, email, member since) alongside
a spending summary (total amount spent, expense count, per-category breakdown) and
a short list of their most recent expenses. This is the first page in Spendly that
is restricted to authenticated users — visiting `/profile` while logged out
redirects to `/login`. It also anchors the nav by adding a "Profile" link visible
to logged-in users.

## Depends on

- Step 1 — Database (`get_db()`, `init_db()`, `users` and `expenses` tables must exist)
- Step 2 — Registration (users must exist in the DB)
- Step 3 — Login/Logout (`session["user_id"]` must be set after login)

## Routes

- `GET /profile` — fetch user record + expenses, render profile page — **logged-in only** (redirect to `/login` if `session["user_id"]` is absent)

## Database changes

No new tables or columns. Two new helpers are needed in `database/db.py`:

- `get_user_by_id(user_id)` — returns the `users` row for the given id, or `None`
- `get_user_expenses(user_id)` — returns all `expenses` rows for the given user,
  ordered by `date DESC`, as a list of `sqlite3.Row` objects

## Templates

- **Create:** `templates/profile.html`
  - Extends `base.html`
  - Header section: user avatar placeholder (initials-based, CSS only), name, email, "Member since" date
  - Stats row: three stat cards — Total Spent (sum of all expense amounts), Expenses Logged (count), Categories Used (distinct category count)
  - Per-category breakdown: a simple list showing each category name, expense count, and total amount
  - Recent activity: last 5 expenses as a table/list (date, category, description, amount)
  - Empty state: if the user has no expenses, show a friendly message with a link to add one (the add route is still a stub — link to it anyway using `url_for('add_expense')`)

- **Modify:** `templates/base.html`
  - Add a "Profile" `<a>` link in `.nav-links` for logged-in users, between the brand and "Log out"

## Files to change

- `app.py`
  - Import `get_user_by_id`, `get_user_expenses` from `database.db`
  - Replace the `/profile` stub with a real route:
    - If `session.get("user_id")` is falsy → `redirect(url_for("login"))`
    - Call `get_user_by_id(session["user_id"])`; if `None` → `session.clear()` then redirect to login
    - Call `get_user_expenses(session["user_id"])`
    - Compute `total_spent`, `expense_count`, `category_breakdown` (dict of category → {count, amount}) in the route function
    - Pass all computed values to `render_template("profile.html", ...)`
- `database/db.py`
  - Add `get_user_by_id(user_id)`
  - Add `get_user_expenses(user_id)`
- `templates/base.html`
  - Add `<a href="{{ url_for('profile') }}">Profile</a>` inside the `{% if session.get("user_id") %}` block

## Files to create

- `templates/profile.html` — profile page template
- `static/css/profile.css` — page-specific styles (linked via `{% block head %}`)

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never f-strings in SQL
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Access guard must be the very first thing in the route — before any DB call
- `get_user_by_id` and `get_user_expenses` must live in `database/db.py`, not inline in the route
- Category breakdown and totals must be computed in the route function (Python), not in the Jinja2 template
- Amount values should be formatted to 2 decimal places in the template using `"%.2f"|format(value)` or passed pre-formatted
- The "add expense" empty-state link must use `url_for('add_expense')` — no hardcoded URLs
- The nav "Profile" link must use `url_for('profile')` — no hardcoded URLs
- `profile.css` must only use CSS variables from `style.css` — no new hex values

## Definition of done

- [ ] Visiting `GET /profile` while logged out redirects to `/login`
- [ ] Visiting `GET /profile` while logged in renders `profile.html` without errors
- [ ] The page displays the logged-in user's name, email, and formatted `created_at` date
- [ ] The stats row shows correct Total Spent, Expenses Logged, and Categories Used values
- [ ] The per-category breakdown lists every category the user has expenses in
- [ ] The recent activity section shows the 5 most recent expenses (date, category, description, amount)
- [ ] If the user has no expenses, an empty state message appears with a link to add one
- [ ] The nav shows a "Profile" link when logged in, and it is absent when logged out
- [ ] `profile.css` is linked and all styles use CSS variables only
- [ ] App starts without errors and existing seed data is unaffected
- [ ] No raw string is returned from the `/profile` route under any code path
