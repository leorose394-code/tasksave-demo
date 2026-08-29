from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_DEMO_SECRET"

UPLOAD_FOLDER = "receipts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DEMO PAYMENT DETAILS —  USE REAL PAYMENTS
DEMO_BANK = "Opay bank"
DEMO_ACCOUNT_NUMBER = "9059426017"
DEMO_ACCOUNT_NAME = "Babatunde rashidat opeyemi"

# DEMO ADMIN LOGIN
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

users = {}
payments = []
withdrawals = []

payment_counter = 1
withdrawal_counter = 1

TASKS = [
    {"id": 1, "title": "Task 1", "description": "Read today's learning tip.", "reward": 100},
    {"id": 2, "title": "Task 2", "description": "Answer a practice question.", "reward": 100},
    {"id": 3, "title": "Task 3", "description": "Check your progress.", "reward": 100},
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
    max-width: 600px;
    margin: 25px auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 4px 15px #0002;
}

h1 {
    text-align: center;
}

input {
    width: 100%;
    box-sizing: border-box;
    padding: 13px;
    margin: 7px 0;
    border: 1px solid #ddd;
    border-radius: 9px;
    font-size: 15px;
}

button {
    width: 100%;
    padding: 13px;
    margin-top: 8px;
    border: 0;
    border-radius: 9px;
    background: #2563eb;
    color: white;
    font-size: 16px;
}

.success {
    background: #16a34a;
}

.danger {
    background: #dc2626;
}

.box {
    background: #f2f5f9;
    padding: 15px;
    border-radius: 12px;
    margin: 15px 0;
}

.balance {
    font-size: 34px;
    font-weight: bold;
    text-align: center;
}

.status {
    padding: 9px;
    border-radius: 8px;
    font-weight: bold;
    text-align: center;
}

.pending {
    background: #fff3cd;
}

.verified,
.approved {
    background: #d1fae5;
}

.rejected {
    background: #fee2e2;
}

.error {
    color: #c00;
}

.small {
    text-align: center;
    color: #777;
    font-size: 13px;
}

a {
    color: #2563eb;
}
</style>
</head>

<body>
<div class="card">

{% if page == "login" %}

<h1>TaskSave 💰</h1>
<p class="small">DEMO ONLY — real money only.</p>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>

<p style="text-align:center">
<a href="/register">Create demo account</a>
</p>

{% elif page == "register" %}

<h1>Create Demo Account</h1>
<p class="small">DEMO ONLY — No real money only.</p>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">
<input name="username" placeholder="Choose username" required>
<input type="password" name="password" placeholder="Choose password" required>
<button>Create Account</button>
</form>

<p style="text-align:center">
<a href="/login">Back to login</a>
</p>

{% elif page == "dashboard" %}

<h1>TaskSave 💰</h1>

<p>Welcome, <b>{{ username }}</b> 👋</p>

<div class="box">
<p>Virtual balance</p>
<div class="balance">₦{{ balance }}</div>
</div>

<h2>Demo Payment</h2>

<div class="box">
<b>Payment details</b>
<p>Bank: {{ bank }}</p>
<p>Account Number: {{ account }}</p>
<p>Account Name: {{ account_name }}</p>
</div>

<p class="small">
DEMO ONLY. send real money to these details.
</p>

<form method="POST" action="/submit-payment" enctype="multipart/form-data">
<input
    type="number"
    name="amount"
    min="1"
    placeholder="Demo amount"
    required
>

<input
    type="file"
    name="receipt"
    accept="image/*"
    required
>

<button>Submit Receipt for Review</button>
</form>

<h2>My Payments</h2>

{% for p in payments %}

<div class="box">
<b>₦{{ p.amount }}</b>
<p>{{ p.date }}</p>

<div class="status
{% if p.status == 'PENDING' %}
pending
{% elif p.status == 'VERIFIED' %}
verified
{% else %}
rejected
{% endif %}
">
{{ p.status }}
</div>

{% if p.status == "REJECTED" %}
<p>Reason: {{ p.reason }}</p>
{% endif %}
</div>

{% else %}

<p>No payment submissions yet.</p>

{% endfor %}

<hr>

<h2>Withdraw Virtual Balance 💸</h2>

<p class="small">
Demo withdrawal only.  real bank transfer only.
</p>

<form method="POST" action="/withdraw">

<input
    type="number"
    name="amount"
    min="1"
    placeholder="Withdrawal amount"
    required
>

<input
    name="bank_name"
    placeholder="Bank name"
    required
>

<input
    name="account_number"
    placeholder="Account number"
    required
>

<input
    name="account_name"
    placeholder="Account name"
    required
>

<button>Request Withdrawal</button>

</form>

<h2>My Withdrawals</h2>

{% for w in withdrawals %}

<div class="box">

<b>₦{{ w.amount }}</b>

<p>Bank: {{ w.bank_name }}</p>
<p>Account: {{ w.account_number }}</p>
<p>Name: {{ w.account_name }}</p>
<p>{{ w.date }}</p>

<div class="status
{% if w.status == 'PENDING' %}
pending
{% elif w.status == 'APPROVED' %}
approved
{% else %}
rejected
{% endif %}
">
{{ w.status }}
</div>

{% if w.status == "REJECTED" %}
<p>Reason: {{ w.reason }}</p>
{% endif %}

</div>

{% else %}

<p>No withdrawal requests yet.</p>

{% endfor %}

<hr>

<h2>Tasks 📋</h2>

{% for task in tasks %}

<div class="box">

<h3>{{ task.title }}</h3>

<p>{{ task.description }}</p>

{% if task.id in completed %}

<div class="status verified">
Completed ✅ +₦{{ task.reward }}
</div>

{% else %}

<form method="POST" action="/complete-task/{{ task.id }}">
<button>Complete Task</button>
</form>

{% endif %}

</div>

{% endfor %}

<p style="text-align:center">
<a href="/logout">Logout</a>
</p>

{% elif page == "admin_login" %}

<h1>Admin Login 🔐</h1>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">

<input
    name="username"
    placeholder="Admin username"
    required
>

<input
    type="password"
    name="password"
    placeholder="Admin password"
    required
>

<button>Admin Login</button>

</form>

<p class="small">
Demo admin area.
</p>

{% elif page == "admin" %}

<h1>Admin Dashboard 🔐</h1>

<h2>Payment Submissions</h2>

{% for p in payments %}

<div class="box">

<h3>Payment #{{ p.id }}</h3>

<p>User: <b>{{ p.username }}</b></p>
<p>Amount: <b>₦{{ p.amount }}</b></p>
<p>Date: {{ p.date }}</p>

<div class="status
{% if p.status == 'PENDING' %}
pending
{% elif p.status == 'VERIFIED' %}
verified
{% else %}
rejected
{% endif %}
">
{{ p.status }}
</div>

{% if p.receipt %}
<p>
<a href="/receipt/{{ p.id }}" target="_blank">
View receipt
</a>
</p>
{% endif %}

{% if p.status == "PENDING" %}

<form method="POST" action="/verify/{{ p.id }}">
<button class="success">
Verify Payment
</button>
</form>

<form method="POST" action="/reject/{{ p.id }}">
<button class="danger">
Reject Payment
</button>
</form>

{% endif %}

</div>

{% else %}

<p>No payment submissions.</p>

{% endfor %}

<hr>

<h2>Withdrawal Requests 💸</h2>

{% for w in withdrawals %}

<div class="box">

<h3>Withdrawal #{{ w.id }}</h3>

<p>User: <b>{{ w.username }}</b></p>
<p>Amount: <b>₦{{ w.amount }}</b></p>

<p>Bank: {{ w.bank_name }}</p>
<p>Account: {{ w.account_number }}</p>
<p>Name: {{ w.account_name }}</p>

<p>Date: {{ w.date }}</p>

<div class="status
{% if w.status == 'PENDING' %}
pending
{% elif w.status == 'APPROVED' %}
approved
{% else %}
rejected
{% endif %}
">
{{ w.status }}
</div>

{% if w.status == "PENDING" %}

<form method="POST" action="/approve-withdrawal/{{ w.id }}">
<button class="success">
Approve Withdrawal
</button>
</form>

<form method="POST" action="/reject-withdrawal/{{ w.id }}">
<button class="danger">
Reject Withdrawal
</button>
</form>

{% endif %}

</div>

{% else %}

<p>No withdrawal requests.</p>

{% endfor %}

<p style="text-align:center">
<a href="/admin/logout">Admin Logout</a>
</p>

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

    user_payments = [
        p for p in payments
        if p["username"] == username
    ]

    user_withdrawals = [
        w for w in withdrawals
        if w["username"] == username
    ]

    return render_template_string(
        PAGE,
        page="dashboard",
        username=username,
        balance=users[username]["balance"],
        tasks=TASKS,
        completed=users[username]["completed"],
        payments=user_payments,
        withdrawals=user_withdrawals,
        bank=DEMO_BANK,
        account=DEMO_ACCOUNT_NUMBER,
        account_name=DEMO_ACCOUNT_NAME
    )


@app.route("/submit-payment", methods=["POST"])
def submit_payment():

    global payment_counter

    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    amount = request.form.get("amount")
    receipt = request.files.get("receipt")

    if not amount or not receipt:
        return redirect(url_for("dashboard"))

    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for("dashboard"))

    filename = secure_filename(receipt.filename)

    if not filename:
        return redirect(url_for("dashboard"))

    filename = f"{payment_counter}_{username}_{filename}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    receipt.save(filepath)

    payments.append({
        "id": payment_counter,
        "username": username,
        "amount": amount,
        "receipt": filename,
        "status": "PENDING",
        "reason": "",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    payment_counter += 1

    return redirect(url_for("dashboard"))


@app.route("/withdraw", methods=["POST"])
def withdraw():

    global withdrawal_counter

    username = session.get("username")

    if not username or username not in users:
        return redirect(url_for("login"))

    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        return redirect(url_for("dashboard"))

    bank_name = request.form.get("bank_name", "").strip()
    account_number = request.form.get("account_number", "").strip()
    account_name = request.form.get("account_name", "").strip()

    user = users[username]

    if amount <= 0:
        return redirect(url_for("dashboard"))

    if amount > user["balance"]:
        return redirect(url_for("dashboard"))

    if not bank_name or not account_number or not account_name:
        return redirect(url_for("dashboard"))

    # Reserve the amount while the request is pending.
    user["balance"] -= amount

    withdrawals.append({
        "id": withdrawal_counter,
        "username": username,
        "amount": amount,
        "bank_name": bank_name,
        "account_number": account_number,
        "account_name": account_name,
        "status": "PENDING",
        "reason": "",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    withdrawal_counter += 1

    return redirect(url_for("dashboard"))


@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))

    error = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(url_for("admin_dashboard"))

        error = "Incorrect admin username or password."

    return render_template_string(
        PAGE,
        page="admin_login",
        error=error
    )


@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template_string(
        PAGE,
        page="admin",
        payments=payments,
        withdrawals=withdrawals
    )


@app.route("/verify/<int:payment_id>", methods=["POST"])
def verify(payment_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    for payment in payments:

        if payment["id"] == payment_id:

            if payment["status"] == "PENDING":

                payment["status"] = "VERIFIED"

                username = payment["username"]

                if username in users:
                    users[username]["balance"] += payment["amount"]

            break

    return redirect(url_for("admin_dashboard"))


@app.route("/reject/<int:payment_id>", methods=["POST"])
def reject(payment_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    for payment in payments:

        if payment["id"] == payment_id:

            if payment["status"] == "PENDING":

                payment["status"] = "REJECTED"
                payment["reason"] = "Receipt could not be verified."

            break

    return redirect(url_for("admin_dashboard"))


@app.route("/receipt/<int:payment_id>")
def receipt(payment_id):

    if not session.get("admin"):
        return "Unauthorized", 403

    for payment in payments:

        if payment["id"] == payment_id:

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                payment["receipt"]
            )

            if os.path.exists(filepath):

                from flask import send_file

                return send_file(filepath)

    return "Receipt not found", 404


@app.route("/approve-withdrawal/<int:withdrawal_id>", methods=["POST"])
def approve_withdrawal(withdrawal_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    for withdrawal in withdrawals:

        if withdrawal["id"] == withdrawal_id:

            if withdrawal["status"] == "PENDING":

                withdrawal["status"] = "APPROVED"

            break

    return redirect(url_for("admin_dashboard"))


@app.route("/reject-withdrawal/<int:withdrawal_id>", methods=["POST"])
def reject_withdrawal(withdrawal_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    for withdrawal in withdrawals:

        if withdrawal["id"] == withdrawal_id:

            if withdrawal["status"] == "PENDING":

                withdrawal["status"] = "REJECTED"
                withdrawal["reason"] = "Withdrawal request rejected."

                username = withdrawal["username"]

                if username in users:
                    users[username]["balance"] += withdrawal["amount"]

            break

    return redirect(url_for("admin_dashboard"))


@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id):

    username = session.get("username")

    if not username or username not in users:
        return redirect(url_for("login"))

    user = users[username]

    if task_id not in user["completed"]:

        task = next(
            (t for t in TASKS if t["id"] == task_id),
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


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )