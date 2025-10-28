# Déploiement des écrans Raspberry Pi

Ce document décrit l'utilisation de `scripts/deploy_to_rpi.sh` pour installer le contrôleur d'écran (`screen-controller`) sur les Raspberry Pi. Le script copie les fichiers, configure un environnement virtuel Python et paramètre le démarrage automatique du contrôleur.

## Prérequis sur le Raspberry Pi

- Raspbian/Raspberry Pi OS installé
- Python3 et chromium installés
- SSH activé et clés configurées pour l'utilisateur pi
- IP fixe configurée (optionel)
- Session graphique (bureau) active pour l'utilisateur pi

## Exemples d'utilisation

Déployer avec les paramètres par défaut :
```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.100
```

Déployer avec port et mot de passe spécifiques :
```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.100 --port 8080 --password "votre_mot_de_passe"
```

Activer le démarrage automatique :
```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.100 --autostart
```

Désactiver l'autostart :
```bash
./scripts/deploy_to_rpi.sh pi@192.168.1.100 --no-autostart
```

## Vérification du déploiement

1. Tester l'accès HTTP :
   ```bash
   curl http://192.168.1.100:8080/status
   ```

2. Vérifier que le serveur répond "Screen Controller OK" :
   ```bash
   curl http://192.168.1.100:8080/
   ```

3. Tester l'envoi d'une URL :
   ```bash
   curl -X POST -d "url=https://example.com&password=votre_mot_de_passe" http://192.168.1.100:8080/set-url
   ```

## Structure du déploiement

- Le code est copié dans `~/screen-controller/`
- Un virtualenv Python est créé dans `~/screen-controller/venv/`
- Si autostart activé :
  - Fichier `.desktop` créé dans `~/.config/autostart/`
  - Démarrage automatique dans la session de l'utilisateur pi

## Notes importantes

- Le script utilise SSH/rsync pour le déploiement. Assurez-vous d'avoir un accès SSH configuré.
- Le remplacement du `PASSWORD` modifie la ligne commençant par `PASSWORD =` dans `server.py`.
- L'autostart est configuré au niveau utilisateur (pas systemd).
- L'écran doit être en mode desktop (pas console).
- Chromium est lancé en mode kiosk.
- L'utilisateur pi doit être connecté au bureau pour que l'affichage fonctionne.

## Dépannage

1. Si l'écran reste noir :
   - Vérifiez que l'utilisateur pi est connecté au bureau
   - Vérifiez les logs dans `~/screen-controller/error.log`

2. Si le serveur ne répond pas :
   - Vérifiez que le processus tourne : `ps aux | grep server.py`
   - Vérifiez les logs : `tail -f ~/screen-controller/error.log`
   - Testez manuellement :
     ```bash
     cd ~/screen-controller
     source venv/bin/activate
     python3 server.py
     ```

3. Si chromium ne démarre pas :
   - Vérifiez que DISPLAY est défini : `echo $DISPLAY`
   - Testez chromium manuellement : `chromium --kiosk https://example.com`

## Support et ajustements

- Pour les problèmes d'affichage : vérifiez la configuration du bureau et l'auto-login.
- Pour les problèmes réseau : vérifiez le pare-feu et la configuration réseau.
- Les logs sont dans `~/screen-controller/error.log`.
