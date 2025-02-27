from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            
            if not username or not password:
                flash("Please fill in all fields", "danger")
                return redirect(url_for("register"))
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already taken. Choose another one.", "warning")
                return redirect(url_for("register"))

            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Account created! You can now login.", "success")
            return redirect(url_for("login"))
        
        return render_template("register.html")
    
    except Exception as e:
        print(f"Error: {e}")
        flash("An unexpected error occurred. Try again.", "danger")
        return redirect(url_for("register"))

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password", "danger")

        return render_template("login.html")

    except Exception as e:
        print(f"Error: {e}")
        flash("An unexpected error occurred. Try again.", "danger")
        return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {current_user.username}! <a href='{url_for('logout')}'>Logout</a>"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database is created
    app.run(debug=True)
