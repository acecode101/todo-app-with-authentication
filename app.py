from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# SQLite Database (Change this if using PostgreSQL)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Create Tables
with app.app_context():
    db.create_all()

# Home Page (Show Tasks)
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    return render_template("index.html", tasks=user.tasks)

# Signup Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Try a different one.", "error")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Try again.", "error")

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# Add Task
@app.route("/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect(url_for("login"))

    task_text = request.form.get("task")
    if task_text:
        new_task = Task(task=task_text, user_id=session["user_id"])
        db.session.add(new_task)
        db.session.commit()
    
    return redirect(url_for("home"))

# Complete Task
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    task = Task.query.get(task_id)
    if task and task.user_id == session["user_id"]:
        task.done = True
        db.session.commit()
    
    return redirect(url_for("home"))

# Delete Task
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    task = Task.query.get(task_id)
    if task and task.user_id == session["user_id"]:
        db.session.delete(task)
        db.session.commit()
    
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
