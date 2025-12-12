# 💰 Expense Tracker

A modern, user-friendly web application for tracking personal expenses. Built with Flask and featuring a clean, intuitive interface with interactive charts and multi-currency support.

## ✨ Features

- **User Authentication**: Secure registration and login system with password hashing
- **Expense Management**: Add, view, and delete expenses with detailed information
- **Category System**: Create and manage custom expense categories
- **Interactive Dashboard**: Visual representation of spending with Chart.js bar charts
- **Multi-Currency Support**: Choose from 8 different currencies (USD, EUR, GBP, IQD, JPY, AED, SAR, INR)
- **Monthly Overview**: View expenses filtered by current month
- **Responsive Design**: Modern UI built with Bootstrap 5 and Bootstrap Icons
- **Session Management**: Secure server-side sessions using Flask-Session
- **Data Visualization**: Real-time spending breakdown by category



## 🛠 Technologies Used

- **Backend**: Python 3.8+, Flask 3.0.0
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js
- **Security**: Werkzeug (password hashing), Flask-Session
- **Session Management**: Flask-Session (filesystem-based)


## 🚀 Usage

### Getting Started

1. **Register a new account**
   - Click on "Register" from the login page
   - Enter a username, password, and select your preferred currency
   - Default categories (Food, Transport, Entertainment, Bills, Shopping, Other) will be created automatically

2. **Login**
   - Use your credentials to log in
   - You'll be redirected to your personal dashboard

3. **Add Expenses**
   - Select a category from the dropdown
   - Enter the amount, description (optional), and date
   - Click "Add Expense" to save

4. **View Statistics**
   - Dashboard displays:
     - Total spending for the current month
     - Number of expenses
     - Number of categories
     - Interactive bar chart showing spending by category
     - Recent expenses list

5. **Manage Categories**
   - Navigate to "Categories" from the navigation menu
   - Add new categories or delete unused ones
   - Note: Categories with associated expenses cannot be deleted

6. **Delete Expenses**
   - Click the trash icon next to any expense in the recent expenses table
   - Confirm deletion in the popup dialog

## 📁 Project Structure

```
cs50-final-project/
│
├── app.py                 # Main Flask application
├── expenses.db            # SQLite database (auto-generated)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── flask_session/        # Flask session files
│   └── [session files]
│
└── templates/            # HTML templates
    ├── layout.html       # Base template with navigation
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── index.html        # Dashboard (main page)
    └── categories.html   # Category management page
```

## 🗄 Database Schema

The application uses SQLite with three main tables:

### Users Table
```sql
- id (INTEGER, PRIMARY KEY)
- username (TEXT, UNIQUE, NOT NULL)
- password (TEXT, NOT NULL)  -- Hashed using Werkzeug
- currency (TEXT, DEFAULT 'USD')
```

### Categories Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY → users.id)
- name (TEXT, NOT NULL)
```

### Expenses Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY → users.id)
- category_id (INTEGER, FOREIGN KEY → categories.id)
- amount (REAL, NOT NULL)
- description (TEXT)
- date (TEXT, NOT NULL)  -- Format: YYYY-MM-DD
```

### Dashboard
The main dashboard displays your spending overview with interactive charts and recent expenses.

### Category Management
Easily organize your expenses by creating and managing custom categories.

### Expense Entry
Quick and intuitive form for adding new expenses with category, amount, description, and date.

## 🔮 Future Enhancements

Potential features for future versions:

- [ ] Export expenses to CSV/PDF
- [ ] Budget setting and tracking
- [ ] Expense filtering by date range
- [ ] Recurring expenses
- [ ] Expense editing functionality
- [ ] Email notifications for budget alerts
- [ ] Dark mode toggle
- [ ] Mobile app version
- [ ] Data backup and restore
- [ ] Advanced analytics and reports

## 🔒 Security Features

- Password hashing using Werkzeug's secure password hashing
- Server-side session management
- SQL injection prevention through parameterized queries
- User data isolation (users can only access their own data)
- Input validation on all forms

## 📝 Notes

- The application runs in debug mode by default (`debug=True`). For production, set `debug=False` in `app.py`
- Session files are stored in the `flask_session/` directory
- The database file (`expenses.db`) is created automatically on first run
- All dates are stored in ISO format (YYYY-MM-DD)

## 🤝 Contributing

This is a CS50 final project. Contributions and suggestions are welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

Ahmed Waleed
- CS50 Final Project
- Harvard University

---

**Note**: This project was developed as part of the CS50 Introduction to Computer Science course final project requirements.

