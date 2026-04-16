from flask import Flask, request, jsonify, render_template_string
import pyotp
import os

app = Flask(__name__)

USERNAME = "admin"
PASSWORD = "secret123"
TOTP_SECRET = "JBSWY3DPEHPK3PXP"
AUTH_TOKEN = "supersecure-office-token-2024"

LOGIN_ATTEMPTS = {}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    ip = request.remote_addr
    attempts = LOGIN_ATTEMPTS.get(ip, 0)
    if attempts >= 5:
        return jsonify({"error": "Too many attempts"}), 429

    username = data.get("username") or data.get("login") or ""
password = data.get("password") or data.get("pass") or ""
    otp = data.get("otp", "")

    if username != USERNAME or password != PASSWORD:
        LOGIN_ATTEMPTS[ip] = attempts + 1
        return jsonify({"error": "Invalid credentials"}), 401

    totp = pyotp.TOTP(TOTP_SECRET)
    if not totp.verify(otp):
        LOGIN_ATTEMPTS[ip] = attempts + 1
        return jsonify({"error": "Invalid OTP"}), 401

    LOGIN_ATTEMPTS[ip] = 0
    return jsonify({"token": AUTH_TOKEN, "message": "Access granted"})

@app.route("/office")
def office():
    token = request.headers.get("X-Secure-Token")
    if token != AUTH_TOKEN:
        return "<h2>403 — Доступ запрещён. Требуется защищённый канал.</h2>", 403

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Внутренняя сеть офиса</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; 
                   display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #16213e; border-radius: 16px; padding: 40px; 
                    text-align: center; box-shadow: 0 0 30px rgba(0,200,150,0.2); }
            .status { color: #00c896; font-size: 18px; margin: 16px 0; }
            .badge { background: #00c896; color: #000; padding: 4px 12px; 
                     border-radius: 20px; font-size: 13px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Защищённая сеть офиса</h1>
            <p class="status">Соединение установлено</p>
            <p>Добро пожаловать в корпоративный ресурс.</p>
            <p>Канал авторизован. Трафик защищён.</p>
            <br>
            <span class="badge">VPN-CHANNEL ACTIVE</span>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
