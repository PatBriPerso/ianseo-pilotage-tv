# Déploiement local du panneau de contrôle

Ce document décrit l'utilisation de `scripts/deploy_local.sh` pour installer l'interface centrale (`rpi-control-panel`) comme un service systemd local. Le script crée un virtualenv, installe les dépendances, et configure le démarrage automatique du panneau de contrôle.

## Prérequis

- Python3 installé sur la machine
- sudo/root pour installer le service systemd
- systemd comme gestionnaire de service (Linux)

## Exemples d'utilisation

Installer le service avec les paramètres par défaut :
```bash
sudo ./scripts/deploy_local.sh
```

Installer et configurer le port et mot de passe :
```bash
sudo ./scripts/deploy_local.sh --port 5000 --password "votre_mot_de_passe"
```

Installer sous un utilisateur spécifique (autre que celui qui lance le script) :
```bash
sudo ./scripts/deploy_local.sh --user pi
```

Supprimer le service :
```bash
sudo ./scripts/deploy_local.sh --remove
```

## Vérifications et contrôle du service

Vérifier le statut du service :
```bash
sudo systemctl status rpi-control-panel.service
```

Voir les logs en temps réel :
```bash
sudo journalctl -u rpi-control-panel.service -f
```

Redémarrer le service (après changement de configuration) :
```bash
sudo systemctl restart rpi-control-panel.service
```

## Notes d'utilisation

- Le service est installé comme `rpi-control-panel.service` dans `/etc/systemd/system/`.
- L'environnement virtuel est créé dans le dossier `rpi-control-panel/venv/`.
- Le remplacement du `PASSWORD` modifie la ligne commençant par `PASSWORD =` dans `control-panel.py`. Vérifiez le fichier résultant si votre mot de passe contient des caractères spéciaux.
- Le service démarre automatiquement au boot et redémarre en cas d'erreur.
- Les logs sont disponibles via journalctl (voir commandes ci-dessus).

## Dépannage rapide

- Si l'installation échoue : vérifiez que Python3 et venv sont installés.
- Si le service ne démarre pas : vérifiez les logs avec `journalctl`.
- Pour tester manuellement avant d'installer le service :
  ```bash
  cd rpi-control-panel
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python3 control-panel.py
  ```