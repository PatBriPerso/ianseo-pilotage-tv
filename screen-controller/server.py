from flask import Flask, request, jsonify
import os
import subprocess
import re

# ---------------- Paramètres ----------------
PORT = 8080          # <--- Modifier ici si tu veux un autre port
PASSWORD = "changeme"  # <--- Mot de passe pour sécuriser l'accès
# --------------------------------------------

app = Flask(__name__)

# Variables globales pour le suivi
last_requested_url = None  # URL demandée par le panneau de contrôle
last_known_url = None     # URL réelle extraite du processus Chromium

def get_chromium_status():
    """
    Vérifie le statut de Chromium et extrait l'URL actuelle.
    Retourne un tuple (status, url)
    """
    try:
        # Recherche les processus chromium avec --kiosk
        cmd = "ps aux | grep 'chromium.*--kiosk' | grep -v grep"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return "hors ligne (Chromium fermé)", None
            
        # Extrait l'URL du process chromium
        cmd_line = result.stdout.strip()
        url_match = re.search(r'--kiosk\s+(\S+)', cmd_line)
        
        if not url_match:
            return "en ligne (URL non détectée)", None
            
        current_url = url_match.group(1)
        return "en ligne", current_url
        
    except Exception as e:
        return f"Erreur détection processus: {str(e)}", None

@app.route("/set-url", methods=["POST"])
def set_url():
    global last_requested_url
    password = request.form.get("password")
    url = request.form.get("url")

    if password != PASSWORD:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    if not url:
        return jsonify({"status": "error", "message": "Missing URL"}), 400

    # Stocke l'URL demandée
    last_requested_url = url

    # Ferme Chromium s'il est déjà lancé et relance avec la nouvelle URL
    os.system("pkill chromium || true")
    os.system(f"chromium --noerrdialogs --disable-infobars --disable-session-crashed-bubble --kiosk {url} &")

    return jsonify({"status": "success", "message": f"URL changed to {url}"})


@app.route("/status", methods=["GET"])
def status():
    global last_requested_url, last_known_url
    
    # Vérifie l'état actuel de Chromium
    current_status, detected_url = get_chromium_status()
    
    # Met à jour l'URL connue si une nouvelle est détectée
    if detected_url:
        last_known_url = detected_url
    
    return jsonify({
        "status": current_status,
        "last_url": last_known_url or last_requested_url or "aucune",
        "requested_url": last_requested_url,
        "actual_url": last_known_url
    })

@app.route("/", methods=["GET"])
def home():
    return "Screen Controller OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
