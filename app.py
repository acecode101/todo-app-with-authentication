from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# To-Do List Data (Temporary Storage)
tasks = []

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", tasks=tasks)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Try another one!", "danger")
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))
    
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Incorrect password!", "danger")
        else:
            flash("Username does not exist!", "danger")
    
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route('/add', methods=["POST"])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    task = request.form.get("task")
    if task:
        tasks.append({"task": task, "done": False})
    return redirect(url_for('home'))

@app.route('/complete/<int:index>')
def complete_task(index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index]["done"]  # ✅ Fix: Toggle task completion
    return redirect(url_for('home'))

@app.route('/delete/<int:index>')
def delete_task(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Fix: Ensure DB is created before running
    app.run(debug=True)
