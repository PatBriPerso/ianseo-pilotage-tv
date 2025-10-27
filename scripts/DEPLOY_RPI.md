# Déploiement simple vers un Raspberry Pi (sans Ansible)

Ce document décrit l'utilisation de `scripts/deploy_to_rpi.sh` : copie miroir du composant choisi (screen-controller ou rpi-control-panel) sur un RPi via rsync/ssh, crée un virtualenv, installe les dépendances et (optionnel) installe un service systemd.

Prérequis

- Accès SSH au Raspberry Pi (ex : pi@192.168.1.21).
- `rsync` et `ssh` installés sur la machine source.
- Python3 disponible sur la cible.

Exemples

- Déployer le contrôleur d'écran sur `pi@192.168.1.21`, installer venv et paquets :

```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.21 screen-controller
```

- Déployer et remplacer le mot de passe RPi (important : mettez le même mot de passe dans le panneau central) :

```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.21 screen-controller --password "votre_mot_de_passe"
```

- Déployer l'interface centrale (control-panel) et exposer sur un port différent :

```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.21 rpi-control-panel --port 5000
```

- Déployer et installer un service systemd qui lancera le script au démarrage :

```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.21 screen-controller --service
```

Notes de sécurité et d'usage

- Le remplacement du `PASSWORD` remplace la ligne commençant par `PASSWORD =` dans `server.py` ou `control-panel.py`. Vérifiez le fichier résultant si votre mot de passe contient des caractères spéciaux.
- Le service systemd créé demande `sudo` sur la cible; l'utilisateur SSH doit pouvoir exécuter `sudo`.
- Ce mécanisme est conçu pour un réseau local sécurisé. Pour une exposition publique, ajoutez TLS et authentification plus forte.

Dépannage rapide

- Si rsync/ssh échoue : vérifier la connectivité réseau et les permissions SSH.
- Si l'installation des paquets échoue : connectez-vous en SSH et exécutez `source venv/bin/activate && pip install -r requirements.txt` pour voir l'erreur complète.

Affichage et Chromium (Xvfb)

Le composant lance Chromium en mode kiosk. Si le service systemd s'exécute sans session graphique (pas de $DISPLAY), Chromium échoue avec "Missing X server or $DISPLAY".

Pour éviter ce problème, l'option `--service` du script installe automatiquement `Xvfb` (si possible via apt) et génère une unité systemd qui utilise `xvfb-run` pour fournir un $DISPLAY virtuel au processus. En pratique :

- Lancer le déploiement avec installation du service (Xvfb est installé automatiquement si accessible) :

```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.21 screen-controller --service
```

- Vérifications utiles après déploiement :

```bash
# afficher le statut et logs du service
sudo systemctl status screen-controller.service
sudo journalctl -u screen-controller.service -n 200 --no-pager

# vérifier que xvfb-run est installé sur la cible
ssh pi@192.168.1.21 which xvfb-run Xvfb || true

# tester manuellement (sur le RPi, dans le répertoire déployé)
xvfb-run -a python3 server.py
# puis appeler /set-url depuis une autre machine pour vérifier le lancement de Chromium
```

Notes spécifiques :

- L'installation de `xvfb` nécessite un accès apt (internet) sur la cible. Si la machine est air-gapped, installez `xvfb` manuellement.
- Si vous préférez utiliser la session graphique réelle (DISPLAY :0), modifiez manuellement l'unité systemd pour exporter `DISPLAY` et `XAUTHORITY` — cela nécessite qu'un utilisateur graphique soit connecté.
- Si vous souhaitez contrôler la résolution de l'écran virtuel, je peux ajouter des options au script (ex : `--xvfb-res 1920x1080x24`).
