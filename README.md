# RPi TV Control README

# 📺 Contrôle à distance des TV via Raspberry Pi

Ce projet permet de contrôler à distance les URL affichées sur plusieurs Raspberry Pi branchés à des TV dans un gymnase ou une salle d’affichage. Chaque Raspberry Pi exécute un mini-serveur Flask qui reçoit les commandes de l’interface centrale sur le PC.

---

## 🖥️ Prérequis

* Raspberry Pi avec Raspbian et Chromium installé
* PC Debian avec Python 3 et navigateur
* Tous les appareils sur le même réseau local

---

## 1️⃣ Installation sur les Raspberry Pi

### Étape 1 : Créer le dossier du projet

```bash
mkdir ~/screen-controller
cd ~/screen-controller
```

### Étape 2 : Copier l'application

Copier le contenu du dossier `screen-controller` de cette repo dans le 
dossier `~/screen-controller` du Raspberry Pi.

### Étape 3 : Installer les dépendances

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
deactivate
```

### Étape 4 : Modifier les paramètres

Dans le fichier `server.py`, modifier éventuellement le PORT
et modifier absolument le PASSWORD (il faut mettre le même
sur tous les Raspberry).

```python
# ---------------- Paramètres ----------------
PORT = 8080          # Modifier si nécessaire
PASSWORD = "changeme"  # Mot de passe pour sécuriser l'accès
# --------------------------------------------
```

### Étape 5 : Lancer le serveur

```bash
source venv/bin/activate
python3 server.py
deactivate
```

* Le serveur écoute sur `http://IP_DU_RPI:PORT/`
* Pour tester depuis un PC sur le même réseau (changer password):

```bash
curl -X POST -d "url=https://www.wikipedia.org&password=changeme" http://IP_DU_RPI:PORT/set-url
```

---

## 2️⃣ Installation de l’interface centrale sur le PC

### Étape 1 : Créer le dossier du projet

Sur le PC "maître" :

```bash
mkdir ~/tv-control-panel
cd ~/tv-control-panel
```

### Étape 2 : Copier l'application

Copier le contenu du dossier `rpi-control-panel` de cette repo dans le 
dossier `~/tv-control-panel` du Raspberry Pi.

### Étape 3 : Installer les dépendances

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
deactivate
```

### Étape 4 : Modifier les paramètres

Dans le fichier `control-panel.py`, modifier éventuellement le INTERFACE_PORT
et modifier absolument le PASSWORD (il faut mettre le même
que celui des Raspberry).

Puis il faut lister toutes les TV en leur donnant un nom (`name`),
en mettant l'adresse IP du raspberry (`ip`) et en mettant le `port`
choisi lors de l'installation de chaque Raspberry.

```python
# ---------------- Paramètres ----------------
TVS = [
    {"name": "TV 1", "ip": "192.168.1.21", "port": 8080},
    {"name": "TV 2", "ip": "192.168.1.22", "port": 8080},
    {"name": "TV 3", "ip": "192.168.1.23", "port": 8080},
    {"name": "TV 4", "ip": "192.168.1.24", "port": 8080},
    {"name": "TV 5", "ip": "192.168.1.25", "port": 8080},
]

PASSWORD = "changeme"  # doit correspondre aux RPi
INTERFACE_PORT = 5000  # port pour l'interface centrale
# --------------------------------------------
```

### Étape 5 : Lancer l’interface

```bash
source venv/bin/activate
python3 control-panel.py
deactivate
```

* Accéder à l’interface : `http://localhost:5000`
* Modifier les noms, IP, ports et URLs des TV
* Envoyer une URL à une TV ou à toutes

---

## 🔧 Paramètres

| Élément                                  | Description                                  |
| ---------------------------------------- | -------------------------------------------- |
| `PORT` dans `server.py`                  | Port d’écoute du serveur sur le RPi          |
| `PASSWORD` dans `server.py`              | Mot de passe pour sécuriser l’accès          |
| `INTERFACE_PORT` dans `control-panel.py` | Port de l’interface centrale Flask sur le PC |
| `TVS` dans `control-panel.py`            | Liste des TV avec `name`, `ip` et `port`     |

---

## ⚡ Astuces

* Mode Kiosk Chromium : lancement automatique en plein écran sans barre d’adresse.
* Pour tester chaque RPi : `http://IP_DU_RPI:PORT/` → doit répondre `Screen Controller OK`.
* Les erreurs de connexion sont affichées dans la colonne **État** de l’interface centrale.
