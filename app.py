from flask import Flask, render_template, request, redirect

app = Flask(__name__)

tasks = []  # List to store tasks

@app.route('/')
def home():
    return render_template("index.html", tasks=tasks)

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
