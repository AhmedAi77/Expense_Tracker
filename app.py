from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import psycopg2.extras
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            currency TEXT DEFAULT 'USD'
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            name TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            category_id INTEGER NOT NULL REFERENCES categories(id),
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

if DATABASE_URL:
    init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

CURRENCIES = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'IQD': 'IQD',
    'JPY': '¥', 'AED': 'AED', 'SAR': 'SAR', 'INR': '₹'
}


@app.route("/")
@login_required
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT username, currency FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    username = user['username']
    currency = user['currency']
    symbol = CURRENCIES.get(currency, currency)

    cur.execute("SELECT * FROM categories WHERE user_id = %s", (session["user_id"],))
    categories = cur.fetchall()

    current_month = datetime.now().strftime('%Y-%m')
    cur.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s AND e.date LIKE %s
        ORDER BY e.date DESC
    ''', (session["user_id"], f"{current_month}%"))
    expenses = cur.fetchall()

    total = sum(expense['amount'] for expense in expenses)

    cur.execute('''
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s AND e.date LIKE %s
        GROUP BY c.name
    ''', (session["user_id"], f"{current_month}%"))
    category_totals = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html",
                           username=username,
                           categories=categories,
                           expenses=expenses,
                           total=total,
                           category_totals=category_totals,
                           currency=currency,
                           symbol=symbol,
                           today=datetime.now().strftime('%Y-%m-%d'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        currency = request.form.get("currency")

        if not username:
            flash("Username is required", "error")
            return render_template("register.html", currencies=CURRENCIES)

        if not password:
            flash("Password is required", "error")
            return render_template("register.html", currencies=CURRENCIES)

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("register.html", currencies=CURRENCIES)

        if password != confirmation:
            flash("Passwords do not match", "error")
            return render_template("register.html", currencies=CURRENCIES)

        if not currency or currency not in CURRENCIES:
            flash("Please select a valid currency", "error")
            return render_template("register.html", currencies=CURRENCIES)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing = cur.fetchone()

        if existing:
            flash("Username already exists", "error")
            cur.close()
            conn.close()
            return render_template("register.html", currencies=CURRENCIES)

        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, password, currency) VALUES (%s, %s, %s) RETURNING id",
            (username, hashed, currency)
        )
        user_id = cur.fetchone()['id']

        default_categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Other']
        for category in default_categories:
            cur.execute(
                "INSERT INTO categories (user_id, name) VALUES (%s, %s)",
                (user_id, category)
            )

        conn.commit()
        cur.close()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect("/login")

    return render_template("register.html", currencies=CURRENCIES)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required", "error")
            return render_template("login.html")

        if not password:
            flash("Password is required", "error")
            return render_template("login.html")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        flash("Welcome back!", "success")
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect("/login")


@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    category_id = request.form.get("category_id")
    amount = request.form.get("amount")
    description = request.form.get("description")
    date = request.form.get("date")

    if not category_id:
        flash("Please select a category", "error")
        return redirect("/")

    if not amount:
        flash("Amount is required", "error")
        return redirect("/")

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be positive", "error")
            return redirect("/")
    except ValueError:
        flash("Invalid amount", "error")
        return redirect("/")

    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (%s, %s, %s, %s, %s)",
        (session["user_id"], category_id, amount, description, date)
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Expense added successfully", "success")
    return redirect("/")


@app.route("/delete_expense/<int:expense_id>")
@login_required
def delete_expense(expense_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM expenses WHERE id = %s AND user_id = %s",
        (expense_id, session["user_id"])
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Expense deleted", "success")
    return redirect("/")


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            name = request.form.get("name")

            if not name:
                flash("Category name is required", "error")
                return redirect("/categories")

            if len(name) > 50:
                flash("Category name too long", "error")
                return redirect("/categories")

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO categories (user_id, name) VALUES (%s, %s)",
                (session["user_id"], name)
            )
            conn.commit()
            cur.close()
            conn.close()

            flash("Category added", "success")
            return redirect("/categories")

        elif action == "delete":
            category_id = request.form.get("category_id")

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) as count FROM expenses WHERE category_id = %s",
                (category_id,)
            )
            expenses = cur.fetchone()

            if expenses['count'] > 0:
                flash("Cannot delete category with existing expenses", "error")
            else:
                cur.execute(
                    "DELETE FROM categories WHERE id = %s AND user_id = %s",
                    (category_id, session["user_id"])
                )
                conn.commit()
                flash("Category deleted", "success")

            cur.close()
            conn.close()
            return redirect("/categories")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories WHERE user_id = %s", (session["user_id"],))
    categories = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("categories.html", categories=categories)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
