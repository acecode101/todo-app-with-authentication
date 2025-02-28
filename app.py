from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secret key for session handling
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

users = {}  # Dictionary to store user credentials
tasks = []  # List to store tasks

# Home Route - Redirects to Login if not authenticated
@app.route('/')
def home():
    if "user" not in session:
        return redirect('/login')
    return render_template("index.html", tasks=tasks, username=session["user"])

# Signup Route
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            flash("Username already exists!", "error")
            return redirect('/signup')

        users[username] = generate_password_hash(password)
        flash("Signup successful! Please login.", "success")
        return redirect('/login')

    return render_template("signup.html")

# Login Route
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect('/')
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")

# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/login')

# Add Task Route
@app.route('/add', methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect('/login')

    task = request.form.get("task")
    if task:
        tasks.append({"task": task, "done": False})
    return redirect('/')

# Complete Task Route
@app.route('/complete/<int:index>')
def complete_task(index):
    if "user" not in session:
        return redirect('/login')

    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
    return redirect('/')

# Delete Task Route
@app.route('/delete/<int:index>')
def delete_task(index):
    if "user" not in session:
        return redirect('/login')

    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
