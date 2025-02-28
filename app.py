from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# Sample user storage (Replace with a database in production)
users = {}
user_tasks = {}  # Store tasks separately for each user

@app.route('/')
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    tasks = user_tasks.get(username, [])  # Get tasks for logged-in user

    return render_template("index.html", tasks=tasks)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            flash("Username already exists! Choose another.", "error")
        else:
            users[username] = generate_password_hash(password)
            user_tasks[username] = []  # Create an empty task list for this user
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route('/add', methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    task = request.form.get("task")

    if task:
        user_tasks[username].append({"task": task, "done": False})  # Add task to this user's list

    return redirect(url_for("home"))

@app.route('/complete/<int:index>')
def complete_task(index):
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    if 0 <= index < len(user_tasks[username]):
        user_tasks[username][index]["done"] = True

    return redirect(url_for("home"))

@app.route('/delete/<int:index>')
def delete_task(index):
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    if 0 <= index < len(user_tasks[username]):
        user_tasks[username].pop(index)  # Remove task from this user's list

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
