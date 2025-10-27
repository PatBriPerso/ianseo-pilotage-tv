## Contexte rapide

Ce dépôt gère un panneau central (PC) qui envoie des URL à plusieurs Raspberry Pi connectés à des TV.
Deux composants principaux :

- `rpi-control-panel/` : application Flask qui expose une interface web (templates/index.html) pour gérer les TV et envoyer des URLs.
- `screen-controller/` : micro-serveur Flask simple exécuté sur chaque RPi qui reçoit `POST /set-url` et lance Chromium en mode kiosk.

## Architecture et flux essentiels

- Le panneau central appelle directement les RPi via HTTP : POST `http://{ip}:{port}/set-url` avec `data={"url":..., "password":...}` (voir `control-panel.py`).
- Chaque RPi expose `/status` (GET) pour renvoyer l'état et la `last_url` (voir `server.py`). L'UI centrale interroge `/tv_status` qui mappe vers `/status` de chaque RPi.
- Les identifiants/paramètres sont gérés par des constantes en haut des fichiers : `PASSWORD`, `PORT` (sur RPi) et `TVS`, `DISPLAYS`, `INTERFACE_PORT` (sur la centrale).

## Conventions importantes à respecter

- Configuration par modification directe du fichier : changez `PASSWORD` dans `screen-controller/server.py` et `rpi-control-panel/control-panel.py` (doit être identique sur tous les hôtes).
- Liste des TV : modifiez la variable `TVS` dans `rpi-control-panel/control-panel.py` (champ `name`, `ip`, `port`).
- Les routes et interactions sont synchrones et simples (pas d'asynchronisme, pas de queue). Le code suppose un LAN fiable et IP fixes.

## Exemples concrets utiles pour l'agent

- Envoyer une URL à une RPi (exemple utilisé par l'UI) :

  requests.post(f"http://{tv['ip']}:{tv['port']}/set-url", data={"url": url, "password": PASSWORD}, timeout=3)

- Vérifier l'état d'une RPi (utilisé dans la centrale) :

  r = requests.get(f"http://{tv['ip']}:{tv['port']}/status", timeout=2)

- Commande exécutée côté RPi pour afficher une URL :

  os.system("pkill chromium || true")
  os.system(f"chromium --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble {url} &")

## Développement & flux de travail (découverts dans README.md)

- Installation (both PC & RPi): créer un venv, `pip install -r requirements.txt` dans chaque dossier (`rpi-control-panel/` et `screen-controller/`).
- Lancer :

  - RPi : `python3 server.py` (écoute sur `0.0.0.0:PORT`) — vérifier `http://IP_DU_RPI:PORT/` retourne `Screen Controller OK`.
  - Centrale : `python3 control-panel.py` puis ouvrir `http://localhost:5000`.

## Patterns de code observés

- Pas de gestion centralisée des secrets : le `PASSWORD` est en clair dans le code.
- Peu d'abstraction : les interactions réseau sont implémentées inline via `requests.post/get` et `os.system`.
- UI : Jinja2 templates Bootstrap dans `rpi-control-panel/templates/index.html` ; le front-end déclenche `/tv_status` pour rafraîchir l'état.

## Points d'attention / risques détectables par l'agent

- Sécurité : mot de passe en clair, pas de TLS, pas d'authentification forte — éviter d'exposer sur un réseau non fiable.
- Robustesse réseau : les timeouts sont courts (2-3s) et les exceptions sont transformées en message d'état (string) — le code s'appuie sur ce comportement.
- Commande Chromium lancée via `os.system` : l'agent doit conserver le même style si on modifie le comportement (pkill puis relancer en &).

## Où faire des changements (fichiers clés)

- `screen-controller/server.py` — point d'entrée du RPi ; modifiez `PORT`, `PASSWORD` et la logique d'affichage.
- `rpi-control-panel/control-panel.py` — liste `TVS`, `DISPLAYS`, `PASSWORD`, interface et envoi d'URLs.
- `rpi-control-panel/templates/index.html` — structure HTML/JS de l'UI (rafraîchissement automatique via `/tv_status`).

## Notes finales pour l'agent

- Restez pragmatique : réutiliser les constantes en tête de fichier pour les changements de configuration.
- Quand vous proposez des améliorations, mentionnez explicitement les modifications de fichiers et fournissez des commandes de test rapides (par ex. curl vers `/set-url` et GET `/status`).

---

Si vous voulez que j'inclue des instructions supplémentaires (ex : automatisation systemd pour démarrer `server.py` au boot, ou exemples d'intégration TLS), dites-moi lesquelles et je les ajouterai.
