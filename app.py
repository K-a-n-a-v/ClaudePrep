import io
import re
import sqlite3

import openpyxl
from openpyxl.styles import Font
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, get_user_by_id, get_user_expenses

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("register.html", error="", name="", email="")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    def fail(msg):
        return render_template("register.html", error=msg, name=name, email=email)

    if not name:
        return fail("Name is required.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return fail("Enter a valid email address.")
    if len(password) < 8:
        return fail("Password must be at least 8 characters.")
    if password != confirm_password:
        return fail("Passwords do not match.")
    if get_user_by_email(email) is not None:
        return fail("An account with that email already exists.")

    password_hash = generate_password_hash(password)
    try:
        create_user(name, email, password_hash)
    except sqlite3.IntegrityError:
        return fail("An account with that email already exists.")

    flash("Account created! Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("login.html", error="", email="")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password", email=email)

    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    expenses = get_user_expenses(session["user_id"])

    total_spent = sum(e["amount"] for e in expenses)
    expense_count = len(expenses)

    category_breakdown = {}
    for e in expenses:
        cat = e["category"]
        if cat not in category_breakdown:
            category_breakdown[cat] = {"count": 0, "amount": 0.0}
        category_breakdown[cat]["count"] += 1
        category_breakdown[cat]["amount"] += e["amount"]

    categories_used = len(category_breakdown)
    recent_expenses = expenses[:5]

    return render_template(
        "profile.html",
        user=user,
        total_spent=total_spent,
        expense_count=expense_count,
        category_breakdown=category_breakdown,
        categories_used=categories_used,
        recent_expenses=recent_expenses,
    )


@app.route("/expenses/export")
def export_expenses():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expenses = get_user_expenses(session["user_id"])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses"

    headers = ["Date", "Category", "Description", "Amount (INR)"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for e in expenses:
        ws.append([e["date"], e["category"], e["description"] or "", e["amount"]])

    for col in ws.columns:
        width = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = width + 4

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="expenses.xlsx",
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
