from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

tasks = []  # List to store tasks

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page (Only Accessible After Login)
@app.route('/')
@login_required
def home():
    return render_template("index.html", tasks=tasks)

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists! Try a different one.", "error")
            return redirect(url_for("signup"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("signup.html")

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "error")
    
    return render_template("login.html")

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Task Routes (Require Login)
@app.route('/add', methods=["POST"])
@login_required
def add_task():
    task = request.form.get("task")
    if task:
        tasks.append({"task": task, "done": False})
    return redirect('/')

@app.route('/complete/<int:index>')
@login_required
def complete_task(index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
    return redirect('/')

@app.route('/delete/<int:index>')
@login_required
def delete_task(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if not exists
    app.run(debug=True)
