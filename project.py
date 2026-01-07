from flask import Flask, request, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# TELEGRAM CONFIG (EDIT THIS)
# -----------------------------
BOT_TOKEN = "7788988731:AAGWwwNuMvE4ArftgqAzRGWRrkVeH-B1sdM"
CHAT_ID = "7326443655"

# -----------------------------
# Common passwords
# -----------------------------
COMMON_PASSWORDS = [
    "admin", "password", "123456", "12345678",
    "qwerty", "admin123", "root", "1234"
]

# -----------------------------
# Password strength + risk
# -----------------------------
def check_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c in "!@#$%^&*()" for c in password):
        score += 1

    if score <= 1:
        return "Weak", 80
    elif score == 2:
        return "Medium", 50
    else:
        return "Strong", 20

# -----------------------------
# Attack classification
# -----------------------------
def classify_attack(username, password, strength):
    if username.lower() in ["admin", "root"]:
        return "Brute-force Attempt"
    if password.lower() in COMMON_PASSWORDS:
        return "Automated Bot Attack"
    if strength == "Strong":
        return "Targeted Human Attack"
    return "Suspicious Login Attempt"

# -----------------------------
# Send Telegram Alert
# -----------------------------
def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# -----------------------------
# HTML Page
# -----------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Router Login</title></head>
<body>
<h2>Router Admin Login</h2>

<form method="POST">
Username:<br>
<input type="text" name="username" required><br><br>
Password:<br>
<input type="password" name="password" required><br><br>
<button type="submit">Login</button>
</form>

{% if message %}
<p style="color:red;"><b>{{ message }}</b></p>
<p>Password Strength: {{ strength }}</p>
<p>Risk Score: {{ risk }}</p>
<p>Attack Type: {{ attack_type }}</p>
{% endif %}
</body>
</html>
"""

# -----------------------------
# Main Route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    strength = ""
    risk = ""
    attack_type = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        strength, risk = check_strength(password)
        attack_type = classify_attack(username, password, strength)

        device_info = request.headers.get("User-Agent")
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = (
            f"Time: {time_now}\n"
            f"Username: {username}\n"
            f"Password: {password}\n"
            f"Strength: {strength}\n"
            f"Risk: {risk}\n"
            f"Attack Type: {attack_type}\n"
            f"Device: {device_info}\n"
            f"----------------------\n"
        )

        with open("trapped_hackers.txt", "a") as f:
            f.write(log_entry)

        alert_message = (
            "🚨 IoT Honeypot Alert 🚨\n\n"
            f"Time: {time_now}\n"
            f"Username: {username}\n"
            f"Password: {password}\n"
            f"Strength: {strength}\n"
            f"Risk Score: {risk}\n"
            f"Attack Type: {attack_type}\n"
            f"Device: {device_info}"
        )

        send_alert(alert_message)

        message = "Connection Failed"

    return render_template_string(
        HTML_PAGE,
        message=message,
        strength=strength,
        risk=risk,
        attack_type=attack_type
    )

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)