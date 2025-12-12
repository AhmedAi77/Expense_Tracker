from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database setup
def get_db():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            currency TEXT DEFAULT 'USD'
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            @app.route("/")
            @login_required
            def index():
                conn = get_db()

                # Get user info including username
                user = conn.execute("SELECT username, currency FROM users WHERE id = ?", 
                                   (session["user_id"],)).fetchone()
                username = user['username']
                currency = user['currency']
                symbol = CURRENCIES.get(currency, currency)

                # Get categories
                categories = conn.execute(
                    "SELECT * FROM categories WHERE user_id = ?", 
                    (session["user_id"],)
                ).fetchall()

                # This month's period and data for totals / chart
                current_month = datetime.now().strftime('%Y-%m')
                month_expenses = conn.execute('''
                    SELECT e.*, c.name as category_name 
                    FROM expenses e
                    JOIN categories c ON e.category_id = c.id
                    WHERE e.user_id = ? AND e.date LIKE ?
                    ORDER BY e.date DESC
                ''', (session["user_id"], f"{current_month}%")).fetchall()

                # Calculate total for this month
                total = sum(expense['amount'] for expense in month_expenses)

                # Get spending by category for chart (this month only)
                category_totals = conn.execute('''
                    SELECT e.category_id, c.name, SUM(e.amount) as total
                    FROM expenses e
                    JOIN categories c ON e.category_id = c.id
                    WHERE e.user_id = ? AND e.date LIKE ?
                    GROUP BY e.category_id
                ''', (session["user_id"], f"{current_month}%")).fetchall()

                # Prepare arrays for chart data and log them for debugging
                # Cast totals to floats explicitly to avoid JSON sending strings.
                category_names = [r['name'] for r in category_totals]
                category_amounts = [float(r['total']) for r in category_totals]
                print(f"DEBUG - category_names: {category_names}")
                print(f"DEBUG - category_amounts: {category_amounts}")

                # Recent expenses - show the most recent 20 expenses across all dates so past-dated entries are visible
                expenses = conn.execute('''
                    SELECT e.*, c.name as category_name
                    FROM expenses e
                    JOIN categories c ON e.category_id = c.id
                    WHERE e.user_id = ?
                    ORDER BY e.date DESC
                    LIMIT 20
                ''', (session["user_id"],)).fetchall()

                conn.close()

                # Today's date for the date picker default
                today_date = datetime.now().strftime('%Y-%m-%d')

                return render_template("index.html", 
                                     username=username,
                                     categories=categories,
                                     expenses=expenses,
                                     total=total,
                                     category_totals=category_totals,
                                     category_names=category_names,
                                     category_amounts=category_amounts,
                                     currency=currency,
                                     symbol=symbol,
                                     today_date=today_date)
    # Get categories
    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?", 
        (session["user_id"],)
    ).fetchall()
    
<<<<<<< HEAD
    # Get this month's expenses
    current_month = datetime.now().strftime('%Y-%m')
    expenses = conn.execute('''
=======
    # This month's period and data for totals / chart
    current_month = datetime.now().strftime('%Y-%m')
    month_expenses = conn.execute('''
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
        SELECT e.*, c.name as category_name 
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND e.date LIKE ?
        ORDER BY e.date DESC
    ''', (session["user_id"], f"{current_month}%")).fetchall()
<<<<<<< HEAD
    
    # Calculate total
    total = sum(expense['amount'] for expense in expenses)
    
    # Get spending by category for chart
    category_totals = conn.execute('''
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND e.date LIKE ?
        GROUP BY c.name
    ''', (session["user_id"], f"{current_month}%")).fetchall()
=======

    # Calculate total for this month
    total = sum(expense['amount'] for expense in month_expenses)

    # Get spending by category for chart (this month only)
    category_totals = conn.execute('''
        SELECT e.category_id, c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND e.date LIKE ?
        GROUP BY e.category_id
    ''', (session["user_id"], f"{current_month}%")).fetchall()

    # Prepare arrays for chart data and log them for debugging
    # Cast totals to floats explicitly to avoid JSON sending strings.
    category_names = [r['name'] for r in category_totals]
    category_amounts = [float(r['total']) for r in category_totals]
    print(f"DEBUG - category_names: {category_names}")
    print(f"DEBUG - category_amounts: {category_amounts}")

    # Recent expenses - show the most recent 20 expenses across all dates so past-dated entries are visible
    expenses = conn.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
        ORDER BY e.date DESC
        LIMIT 20
    ''', (session["user_id"],)).fetchall()
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
    
    conn.close()
    
    return render_template("index.html", 
                         username=username,
                         categories=categories,
                         expenses=expenses,
                         total=total,
                         category_totals=category_totals,
<<<<<<< HEAD
                         currency=currency,
                         symbol=symbol)
=======
                            category_names=category_names,
                            category_amounts=category_amounts,
                         currency=currency,
                         symbol=symbol,
                         )
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        currency = request.form.get("currency")
        
        # Validation
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
        
        # Check if username exists
        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE username = ?", 
                               (username,)).fetchone()
        
        if existing:
            flash("Username already exists", "error")
            conn.close()
            return render_template("register.html", currencies=CURRENCIES)
        
        # Create user
        hashed = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, password, currency) VALUES (?, ?, ?)",
            (username, hashed, currency)
        )
        user_id = cursor.lastrowid
        
        # Create default categories
        default_categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Other']
        for category in default_categories:
            conn.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)",
                (user_id, category)
            )
        
        conn.commit()
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
        
        # Validation
        if not username:
            flash("Username is required", "error")
            return render_template("login.html")
        
        if not password:
            flash("Password is required", "error")
            return render_template("login.html")
        
        # Check credentials
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", 
                          (username,)).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password", "error")
            return render_template("login.html")
<<<<<<< HEAD
        
=======
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
        # Login successful
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
    
<<<<<<< HEAD
=======
    # Debug: Print form data to console
    print(f"DEBUG - Form Data:")
    print(f"  category_id: {category_id}")
    print(f"  amount: {amount}")
    print(f"  description: {description}")
    print(f"  date: {date}")
    
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
    # Validation
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
    
<<<<<<< HEAD
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Add expense
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], category_id, amount, description, date)
    )
    conn.commit()
    conn.close()
    
    flash("Expense added successfully", "success")
    return redirect("/")

=======
    # If no date provided, use today's date
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
        print(f"DEBUG - No date provided, using today: {date}")
    else:
        print(f"DEBUG - Date received: {date}")
        # Validate date format
        try:
            # this will raise ValueError if format is wrong
            datetime.strptime(date, '%Y-%m-%d')
        except Exception as ex:
            print(f"DEBUG - Invalid date format: {date}")
            flash("Invalid date format. Please select a valid date (YYYY-MM-DD).", "error")
            return redirect("/")
    
    # Add expense (respect 'exclude from reports' flag)
    try:
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], category_id, amount, description, date)
        )
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"DEBUG - Expense added successfully with ID: {expense_id}")
        flash("Expense added successfully", "success")
    except Exception as e:
        print(f"DEBUG - Error adding expense: {str(e)}")
        flash(f"Error adding expense: {str(e)}", "error")
    
    return redirect("/")
    
>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
@app.route("/delete_expense/<int:expense_id>")
@login_required
def delete_expense(expense_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    
    flash("Expense deleted", "success")
    return redirect("/")

<<<<<<< HEAD
=======

@app.route("/debug_category_totals")
@login_required
def debug_category_totals():
    """Debug endpoint that returns the current month's category totals and recent expenses as JSON.
    Useful to inspect what the app is sending to the chart.
    """
    from flask import jsonify
    conn = get_db()
    current_month = datetime.now().strftime('%Y-%m')
    category_totals = conn.execute('''
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND e.date LIKE ?
        GROUP BY c.name
    ''', (session["user_id"], f"{current_month}%")).fetchall()

    month_expenses = conn.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ? AND e.date LIKE ?
        ORDER BY e.date DESC
    ''', (session["user_id"], f"{current_month}%")).fetchall()

    conn.close()

    return jsonify({
        'category_totals': [{ 'name': r['name'], 'total': r['total'] } for r in category_totals],
        'month_expenses': [{ 'date': r['date'], 'category_name': r['category_name'], 'amount': r['amount'] } for r in month_expenses]
    })

>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
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
            conn.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)",
                (session["user_id"], name)
            )
            conn.commit()
            conn.close()
            
            flash("Category added", "success")
            return redirect("/categories")
        
        elif action == "delete":
            category_id = request.form.get("category_id")
            
            conn = get_db()
            # Check if category has expenses
            expenses = conn.execute(
                "SELECT COUNT(*) as count FROM expenses WHERE category_id = ?",
                (category_id,)
            ).fetchone()
            
            if expenses['count'] > 0:
                flash("Cannot delete category with existing expenses", "error")
            else:
                conn.execute(
                    "DELETE FROM categories WHERE id = ? AND user_id = ?",
                    (category_id, session["user_id"])
                )
                conn.commit()
                flash("Category deleted", "success")
            
            conn.close()
            return redirect("/categories")
    
    conn = get_db()
    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    
    return render_template("categories.html", categories=categories)

<<<<<<< HEAD
=======
# No custom 500 handler here; let Flask show tracebacks in debug mode

>>>>>>> e46a841 (Fix: category aggregation, chart data types, add debug endpoint, restore date behavior)
if __name__ == "__main__":
    init_db()
    app.run(debug=True)