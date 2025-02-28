from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# Initialize Database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Create tasks table (linked to users)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        task TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        FOREIGN KEY (username) REFERENCES users(username)
    )
    """)

    conn.commit()
    conn.close()

init_db()  # Run the function to ensure tables exist

# Register Route
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists! Choose another.", "error")
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))

        conn.close()

    return render_template("signup.html")

# Login Route
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")

# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# Home Route
@app.route('/')
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Fetch tasks for logged-in user
    cursor.execute("SELECT id, task, done FROM tasks WHERE username = ?", (username,))
    tasks = [{"id": row[0], "task": row[1], "done": bool(row[2])} for row in cursor.fetchall()]

    conn.close()

    return render_template("index.html", tasks=tasks)

# Add Task Route
@app.route('/add', methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    task = request.form.get("task")

    if task:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (username, task) VALUES (?, ?)", (username, task))
        conn.commit()
        conn.close()

    return redirect(url_for("home"))

# Complete Task Route
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ? AND username = ?", (task_id, username))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

# Delete Task Route
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, username))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
