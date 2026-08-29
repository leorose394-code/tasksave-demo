from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = "tasksave-demo-secret"

users = {}

TASKS = [
    {
        "id": 1,
        "title": "Task 1",
        "description": "Read today's learning tip.",
        "reward": 100
    },
    {
        "id": 2,
        "title": "Task 2",
        "description": "Answer a practice question.",
        "reward": 100
    },
    {
        "id": 3,
        "title": "Task 3",
        "description": "Check your progress.",
        "reward": 100
    }
]

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TaskSave Demo</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f5f9;
            margin: 0;
            padding: 20px;
        }

        .card {
            max-width: 520px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,.12);
        }

        h1 {
            text-align: center;
        }

        input {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 14px;
            margin-top: 10px;
            border: 0;
            border-radius: 10px;
            background: #2563eb;
            color: white;
            font-size: 16px;
        }

        .balance {
            font-size: 36px;
            font-weight: bold;
            margin: 25px 0;
        }

        .task {
            background: #f2f5f9;
            padding: 18px;
            border-radius: 14px;
            margin: 15px 0;
        }

        .completed {
            background: #dff7e5;
            color: #16803c;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }

        .error {
            color: #d00;
            text-align: center;
        }

        .demo {
            text-align: center;
            color: #777;
            font-size: 13px;
            margin-top: 20px;
        }

        .link {
            text-align: center;
            margin-top: 20px;
        }

        a {
            color: #2563eb;
        }
    </style>
</head>

<body>
<div class="card">

{% if page == "register" %}

    <h1>Create Account 💰</h1>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <form method="POST">
        <input name="username" placeholder="Choose username" required>
        <input type="password" name="password"
               placeholder="Choose password" required>
        <button type="submit">Create Demo Account</button>
    </form>

    <div class="link">
        Already registered?
        <a href="/login">Login</a>
    </div>

    <p class="demo">
        DEMO ONLY — no real money is involved.
    </p>

{% elif page == "login" %}

    <h1>TaskSave 💰</h1>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <form method="POST">
        <input name="username" placeholder="Username" required>
        <input type="password" name="password"
               placeholder="Password" required>
        <button type="submit">Login</button>
    </form>

    <div class="link">
        New user?
        <a href="/register">Create Account</a>
    </div>

    <p class="demo">
        DEMO ONLY — balance is virtual.
    </p>

{% else %}

    <h1>TaskSave 💰</h1>

    <p>Welcome, {{ username }} 👋</p>

    <p>Demo balance:</p>

    <div class="balance">
        ₦{{ balance }}
    </div>

    <h2>Today's Tasks 📋</h2>

    {% for task in tasks %}

        <div class="task">
            <h3>{{ task.title }}</h3>
            <p>{{ task.description }}</p>

            {% if task.id in completed %}

                <div class="completed">
                    Completed ✅ +₦{{ task.reward }}
                </div>

            {% else %}

                <form method="POST"
                      action="/complete-task/{{ task.id }}">
                    <button type="submit">
                        Complete Task
                    </button>
                </form>

            {% endif %}
        </div>

    {% endfor %}

    <p class="demo">
        DEMO ONLY — all money shown is virtual.
    </p>

    <div class="link">
        <a href="/logout">Logout</a>
    </div>

{% endif %}

</div>
</body>
</html>
"""


@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in users:
            return render_template_string(
                PAGE,
                page="register",
                error="Username already exists."
            )

        if len(username) < 3 or len(password) < 4:
            return render_template_string(
                PAGE,
                page="register",
                error="Username must be 3+ characters and password 4+ characters."
            )

        users[username] = {
            "password": password,
            "balance": 3000,
            "completed": []
        }

        session["username"] = username

        return redirect(url_for("dashboard"))

    return render_template_string(
        PAGE,
        page="register",
        error=""
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = users.get(username)

        if user and user["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))

        return render_template_string(
            PAGE,
            page="login",
            error="Incorrect username or password."
        )

    return render_template_string(
        PAGE,
        page="login",
        error=""
    )


@app.route("/dashboard")
def dashboard():

    username = session.get("username")

    if not username or username not in users:
        return redirect(url_for("login"))

    user = users[username]

    return render_template_string(
        PAGE,
        page="dashboard",
        username=username,
        balance=user["balance"],
        tasks=TASKS,
        completed=user["completed"]
    )


@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id):

    username = session.get("username")

    if not username or username not in users:
        return redirect(url_for("login"))

    user = users[username]

    if task_id not in user["completed"]:

        task = next(
            (task for task in TASKS if task["id"] == task_id),
            None
        )

        if task:
            user["completed"].append(task_id)
            user["balance"] += task["reward"]

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )