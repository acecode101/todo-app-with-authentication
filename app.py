from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template("index.html", tasks=user_tasks)

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
    
    task_text = request.form.get("task")
    if task_text:
        new_task = Task(user_id=session['user_id'], task=task_text)
        db.session.add(new_task)
        db.session.commit()
    
    return redirect(url_for('home'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == session.get('user_id'):
        task.done = not task.done
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == session.get('user_id'):
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Ensures database is created
    app.run(debug=True)
