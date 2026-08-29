import os
import sqlite3
from datetime import datetime
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    render_template_string,
    flash
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

# Render provides the port through the PORT environment variable.
PORT = int(os.environ.get("PORT", "5000"))

DATABASE = "tasksave.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            amount REAL NOT NULL,
            receipt TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            amount REAL NOT NULL,
            account_name TEXT,
            account_number TEXT,
            bank TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def admin_required():
    return session.get("admin") is True


PAGE = """
<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TaskSave Demo</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f4f6f8;
            color: #222;
        }

        header {
            background: #111827;
            color: white;
            padding: 18px;
        }

        main {
            max-width: 900px;
            margin: 25px auto;
            padding: 15px;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 18px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,.08);
        }

        input, select, button {
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            margin: 7px 0;
            border-radius: 7px;
            border: 1px solid #ccc;
        }

        button {
            background: #111827;
            color: white;
            border: none;
            cursor: pointer;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            overflow-x: auto;
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }

        .pending {
            color: #b45309;
        }

        .approved {
            color: #15803d;
        }

        .rejected {
            color: #dc2626;
        }

        a {
            color: #2563eb;
        }

        .notice {
            padding: 12px;
            background: #fff7ed;
            border-radius: 8px;
            margin-bottom: 15px;
        }
    </style>
</head>

<body>

<header>
    <strong>TaskSave Demo</strong>
</header>

<main>

{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            <div class="notice">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}


{% if page == "home" %}

<div class="card">
    <h2>TaskSave</h2>
    <p>This is a demonstration of a payment and withdrawal workflow.</p>
    <p><strong>Demo only:</strong> no real money is processed by this application.</p>
</div>

<div class="card">
    <h3>Submit Payment Receipt</h3>

    <form method="POST"
          action="{{ url_for('submit_payment') }}"
          enctype="multipart/form-data">

        <input
            type="text"
            name="username"
            placeholder="Username"
            required
        >

        <input
            type="number"
            name="amount"
            step="0.01"
            min="0"
            placeholder="Amount"
            required
        >

        <input
            type="file"
            name="receipt"
            accept=".png,.jpg,.jpeg,.webp,.pdf"
            required
        >

        <button type="submit">
            Submit Receipt
        </button>

    </form>
</div>

<div class="card">
    <h3>Request Withdrawal</h3>

    <form method="POST"
          action="{{ url_for('request_withdrawal') }}">

        <input
            type="text"
            name="username"
            placeholder="Username"
            required
        >

        <input
            type="number"
            name="amount"
            step="0.01"
            min="0"
            placeholder="Withdrawal amount"
            required
        >

        <input
            type="text"
            name="account_name"
            placeholder="Account name"
            required
        >

        <input
            type="text"
            name="account_number"
            placeholder="Account number"
            required
        >

        <input
            type="text"
            name="bank"
            placeholder="Bank"
            required
        >

        <button type="submit">
            Submit Withdrawal Request
        </button>

    </form>
</div>

<div class="card">
    <a href="{{ url_for('admin_login') }}">
        Admin Login
    </a>
</div>


{% elif page == "admin_login" %}

<div class="card">

    <h2>Admin Login</h2>

    <form method="POST">

        <input
            type="text"
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

        <button type="submit">
            Login
        </button>

    </form>

</div>


{% elif page == "admin" %}

<div class="card">

    <h2>Admin Dashboard</h2>

    <p>
        <a href="{{ url_for('admin_logout') }}">
            Logout
        </a>
    </p>

</div>


<div class="card">

    <h3>Payment Receipts</h3>

    {% if payments %}

    <table>

        <tr>
            <th>User</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Receipt</th>
            <th>Action</th>
        </tr>

        {% for payment in payments %}

        <tr>

            <td>{{ payment["username"] }}</td>

            <td>{{ payment["amount"] }}</td>

            <td class="{{ payment['status'] }}">
                {{ payment["status"] }}
            </td>

            <td>
                {% if payment["receipt"] %}
                    <a href="{{ url_for('receipt', filename=payment['receipt']) }}"
                       target="_blank">
                        View
                    </a>
                {% endif %}
            </td>

            <td>

                <form method="POST"
                      action="{{ url_for('payment_action', payment_id=payment['id']) }}">

                    <select name="status">

                        <option value="pending"
                            {% if payment["status"] == "pending" %}selected{% endif %}>
                            Pending
                        </option>

                        <option value="approved"
                            {% if payment["status"] == "approved" %}selected{% endif %}>
                            Approved
                        </option>

                        <option value="rejected"
                            {% if payment["status"] == "rejected" %}selected{% endif %}>
                            Rejected
                        </option>

                    </select>

                    <button type="submit">
                        Update
                    </button>

                </form>

            </td>

        </tr>

        {% endfor %}

    </table>

    {% else %}

    <p>No payment receipts yet.</p>

    {% endif %}

</div>


<div class="card">

    <h3>Withdrawal Requests</h3>

    {% if withdrawals %}

    <table>

        <tr>
            <th>User</th>
            <th>Amount</th>
            <th>Bank</th>
            <th>Status</th>
            <th>Action</th>
        </tr>

        {% for withdrawal in withdrawals %}

        <tr>

            <td>{{ withdrawal["username"] }}</td>

            <td>{{ withdrawal["amount"] }}</td>

            <td>{{ withdrawal["bank"] }}</td>

            <td class="{{ withdrawal['status'] }}">
                {{ withdrawal["status"] }}
            </td>

            <td>

                <form method="POST"
                      action="{{ url_for('withdrawal_action', withdrawal_id=withdrawal['id']) }}">

                    <select name="status">

                        <option value="pending"
                            {% if withdrawal["status"] == "pending" %}selected{% endif %}>
                            Pending
                        </option>

                        <option value="approved"
                            {% if withdrawal["status"] == "approved" %}selected{% endif %}>
                            Approved
                        </option>

                        <option value="rejected"
                            {% if withdrawal["status"] == "rejected" %}selected{% endif %}>
                            Rejected
                        </option>

                    </select>

                    <button type="submit">
                        Update
                    </button>

                </form>

            </td>

        </tr>

        {% endfor %}

    </table>

    {% else %}

    <p>No withdrawal requests yet.</p>

    {% endif %}

</div>

{% endif %}

</main>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE, page="home")


@app.route("/payment", methods=["POST"])
def submit_payment():

    username = request.form.get("username", "").strip()
    amount = request.form.get("amount", "").strip()
    receipt_file = request.files.get("receipt")

    if not username or not amount or not receipt_file:
        flash("Please complete all payment fields.")
        return redirect(url_for("home"))

    try:
        amount_value = float(amount)
    except ValueError:
        flash("Invalid amount.")
        return redirect(url_for("home"))

    if amount_value <= 0:
        flash("Amount must be greater than zero.")
        return redirect(url_for("home"))

    if receipt_file.filename == "":
        flash("Please select a receipt.")
        return redirect(url_for("home"))

    if not allowed_file(receipt_file.filename):
        flash("Unsupported receipt file type.")
        return redirect(url_for("home"))

    filename = secure_filename(receipt_file.filename)

    unique_name = (
        datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        + "_"
        + filename
    )

    receipt_file.save(
        os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    )

    db = get_db()

    db.execute(
        """
        INSERT INTO payments
        (username, amount, receipt, status, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            amount_value,
            unique_name,
            "pending",
            datetime.utcnow().isoformat()
        )
    )

    db.commit()
    db.close()

    flash("Receipt submitted successfully. It is awaiting admin review.")

    return redirect(url_for("home"))


@app.route("/withdraw", methods=["POST"])
def request_withdrawal():

    username = request.form.get("username", "").strip()
    amount = request.form.get("amount", "").strip()
    account_name = request.form.get("account_name", "").strip()
    account_number = request.form.get("account_number", "").strip()
    bank = request.form.get("bank", "").strip()

    if not all([
        username,
        amount,
        account_name,
        account_number,
        bank
    ]):
        flash("Please complete all withdrawal fields.")
        return redirect(url_for("home"))

    try:
        amount_value = float(amount)
    except ValueError:
        flash("Invalid withdrawal amount.")
        return redirect(url_for("home"))

    if amount_value <= 0:
        flash("Withdrawal amount must be greater than zero.")
        return redirect(url_for("home"))

    db = get_db()

    db.execute(
        """
        INSERT INTO withdrawals
        (
            username,
            amount,
            account_name,
            account_number,
            bank,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            amount_value,
            account_name,
            account_number,
            bank,
            "pending",
            datetime.utcnow().isoformat()
        )
    )

    db.commit()
    db.close()

    flash("Withdrawal request submitted for review.")

    return redirect(url_for("home"))


@app.route("/receipt/<path:filename>")
def receipt(filename):

    from flask import send_from_directory

    if not admin_required():
        return "Unauthorized", 401

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if admin_required():
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        admin_username = os.environ.get(
            "ADMIN_USERNAME",
            "admin"
        )

        admin_password = os.environ.get(
            "ADMIN_PASSWORD",
            "change-me"
        )

        if (
            username == admin_username
            and password == admin_password
        ):

            session["admin"] = True

            return redirect(url_for("admin_dashboard"))

        flash("Incorrect admin username or password.")

    return render_template_string(
        PAGE,
        page="admin_login"
    )


@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_required():
        return redirect(url_for("admin_login"))

    db = get_db()

    payments = db.execute(
        """
        SELECT *
        FROM payments
        ORDER BY id DESC
        """
    ).fetchall()

    withdrawals = db.execute(
        """
        SELECT *
        FROM withdrawals
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template_string(
        PAGE,
        page="admin",
        payments=payments,
        withdrawals=withdrawals
    )


@app.route("/admin/payment/<int:payment_id>", methods=["POST"])
def payment_action(payment_id):

    if not admin_required():
        return "Unauthorized", 401

    status = request.form.get("status")

    if status not in {
        "pending",
        "approved",
        "rejected"
    }:
        flash("Invalid payment status.")
        return redirect(url_for("admin_dashboard"))

    db = get_db()

    db.execute(
        """
        UPDATE payments
        SET status = ?
        WHERE id = ?
        """,
        (status, payment_id)
    )

    db.commit()
    db.close()

    flash("Payment status updated.")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/withdrawal/<int:withdrawal_id>", methods=["POST"])
def withdrawal_action(withdrawal_id):

    if not admin_required():
        return "Unauthorized", 401

    status = request.form.get("status")

    if status not in {
        "pending",
        "approved",
        "rejected"
    }:
        flash("Invalid withdrawal status.")
        return redirect(url_for("admin_dashboard"))

    db = get_db()

    db.execute(
        """
        UPDATE withdrawals
        SET status = ?
        WHERE id = ?
        """,
        (status, withdrawal_id)
    )

    db.commit()
    db.close()

    flash("Withdrawal status updated.")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT
    )