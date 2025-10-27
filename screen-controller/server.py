from flask import Flask, request, jsonify
import os

# ---------------- Paramètres ----------------
PORT = 8080          # <--- Modifier ici si tu veux un autre port
PASSWORD = "changeme"  # <--- Mot de passe pour sécuriser l'accès
# --------------------------------------------

app = Flask(__name__)

# Ajouter une variable globale pour la dernière URL reçue
last_url = None

@app.route("/set-url", methods=["POST"])
def set_url():
    global last_url
    password = request.form.get("password")
    url = request.form.get("url")

    if password != PASSWORD:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    if not url:
        return jsonify({"status": "error", "message": "Missing URL"}), 400

    # Stocke la dernière URL envoyée
    last_url = url

    # Ferme Chromium s'il est déjà lancé et relance avec la nouvelle URL
    os.system("pkill chromium || true")
    os.system(f"chromium --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble {url} &")

    return jsonify({"status": "success", "message": f"URL changed to {url}"})


@app.route("/status", methods=["GET"])
def status():
    global last_url
    return jsonify({
        "status": "online",
        "last_url": last_url
    })

@app.route("/", methods=["GET"])
def home():
    return "Screen Controller OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
