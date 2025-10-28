# control-panel.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

# ---------------- Paramètres ----------------
TVS = [
    {"name": "TV Gauche [1-8]", "ip": "adgtv01.local", "port": 7828},
    {"name": "TV Milieu [9-16]", "ip": "adgtv02.local", "port": 7828},
    {"name": "TV Droite [17-24]", "ip": "adgtv03.local", "port": 7828},
    {"name": "TV Entrée", "ip": "adgtv04.local", "port": 7828},
    {"name": "TV Buvette", "ip": "adgtv05.local", "port": 7828},
]

# Liste des affichages prédéfinis (nom + url)
DISPLAYS = [
    {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
    {"name": "TF1", "url": "https://www.tf1.fr"},
    {"name": "France 2", "url": "https://www.france.tv/france-2/"},
    {"name": "Canal+", "url": "https://www.canalplus.com/"},
]

PASSWORD = "changeme"  # doit correspondre aux RPi
INTERFACE_PORT = 5000  # port pour l'interface centrale
# --------------------------------------------

app = Flask(__name__)

# initialisation des champs
for tv in TVS:
    tv.setdefault("url", "")
    tv.setdefault("status", "?")
    tv.setdefault("last_url", "")

# -------- Fonctions --------
def check_tv_status(tv):
    try:
        r = requests.get(f"http://{tv['ip']}:{tv['port']}/status", timeout=TIMEOUT)
        data = r.json()
        tv["status"] = data.get("status", "Erreur")
        tv["last_url"] = data.get("last_url", "")
    except Exception as e:
        tv["status"] = f"Erreur : {e}"
        tv["last_url"] = ""

# -------- Routes --------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", tvs=TVS, displays=DISPLAYS, password=PASSWORD)

@app.route("/tv_status")
def tv_status():
    result = []
    for tv in TVS:
        check_tv_status(tv)
        result.append({
            "name": tv["name"],
            "status": tv["status"],
            "last_url": tv["last_url"]
        })
    return jsonify(result)

@app.route("/update_tvs", methods=["POST"])
def update_tvs():
    # Met à jour noms, ip, port depuis le formulaire
    for i, tv in enumerate(TVS):
        tv["name"] = request.form.get(f"name_{i}", tv["name"])
        tv["ip"] = request.form.get(f"ip_{i}", tv["ip"])
        port_val = request.form.get(f"port_{i}", tv.get("port", 8080))
        try:
            tv["port"] = int(port_val)
        except:
            tv["port"] = tv.get("port", 8080)
    return redirect(url_for("home"))

@app.route("/send/<int:index>", methods=["POST"])
def send_url(index):
    tv = TVS[index]
    url = request.form.get("url", "").strip()
    tv["url"] = url
    try:
        requests.post(f"http://{tv['ip']}:{tv['port']}/set-url",
                      data={"url": url, "password": PASSWORD}, timeout=TIMEOUT)
    except Exception as e:
        tv["status"] = f"Erreur : {e}"
    return redirect(url_for("home"))

@app.route("/send_all", methods=["POST"])
def send_all():
    url = request.form.get("url", "").strip()
    for tv in TVS:
        tv["url"] = url
        try:
            requests.post(f"http://{tv['ip']}:{tv['port']}/set-url",
                          data={"url": url, "password": PASSWORD}, timeout=TIMEOUT)
        except Exception as e:
            tv["status"] = f"Erreur : {e}"
    return redirect(url_for("home"))

# Envoi d'un affichage (display) à une TV spécifique
@app.route("/send_display/<int:display_index>/to/<int:tv_index>", methods=["POST"])
def send_display_to_tv(display_index, tv_index):
    if display_index < 0 or display_index >= len(DISPLAYS) or tv_index < 0 or tv_index >= len(TVS):
        return redirect(url_for("home"))
    disp = DISPLAYS[display_index]
    tv = TVS[tv_index]
    tv["url"] = disp["url"]
    try:
        requests.post(f"http://{tv['ip']}:{tv['port']}/set-url",
                      data={"url": disp["url"], "password": PASSWORD}, timeout=TIMEOUT)
    except Exception as e:
        tv["status"] = f"Erreur : {e}"
    return redirect(url_for("home"))

# Envoi d'un affichage à toutes les TV
@app.route("/send_display/<int:display_index>/to_all", methods=["POST"])
def send_display_to_all(display_index):
    if display_index < 0 or display_index >= len(DISPLAYS):
        return redirect(url_for("home"))
    disp = DISPLAYS[display_index]
    for tv in TVS:
        tv["url"] = disp["url"]
        try:
            requests.post(f"http://{tv['ip']}:{tv['port']}/set-url",
                          data={"url": disp["url"], "password": PASSWORD}, timeout=TIMEOUT)
        except Exception as e:
            tv["status"] = f"Erreur : {e}"
    return redirect(url_for("home"))

# -------- Lancement --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=INTERFACE_PORT)
