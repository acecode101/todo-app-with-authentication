from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'  # Add a secret key for session encryption

# Example hardcoded user credentials
USER_CREDENTIALS = {'username': 'admin', 'password': 'password123'}

tasks = []  # List to store tasks

@app.route('/')
def home():
    # Redirect to login page if the user is not logged in
    if 'username' not in session:
        return redirect('/login')
    return render_template("index.html", tasks=tasks)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the credentials are correct
        if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
            session['username'] = username  # Store username in the session
            return redirect('/')
        else:
            flash("Incorrect username or password!", 'error')
    
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user from session
    return redirect('/login')

@app.route('/add', methods=["POST"])
def add_task():
    task = request.form.get("task")
    if task:
        tasks.append({"task": task, "done": False})
    return redirect('/')

@app.route('/complete/<int:index>')
def complete_task(index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
    return redirect('/')

@app.route('/delete/<int:index>')
def delete_task(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
