# HEH-2025-GDP-Voiture-Raspberry

Ce projet implémente un système de voiture robotique autonome basé sur Raspberry Pi. La voiture utilise plusieurs capteurs (distance ultrason, ligne, RGB) pour naviguer de façon autonome tout en évitant les obstacles.

## Fonctionnalités

- **Navigation autonome** avec évitement d'obstacles
- **Détection de couleurs** pour déclencher des actions (démarrage avec couleur verte)
- **Détection de ligne noire** pour l'arrêt automatique
- **Interface web** pour contrôler la voiture à distance
- **Modes spéciaux** : trajectoire en 8, rotation sur place

## Structure du projet

```
HEH-2025-GDP-Voiture-Raspberry/
├── projet_voiture/           # Code principal de la voiture
│   ├── CapteurDistance.py    # Classe pour les capteurs à ultrasons
│   ├── CapteurRGB.py         # Classe pour le capteur de couleur
│   ├── CarLauncher.py        # Gestionnaire de démarrage
│   ├── ControllerCar.py      # Contrôleur principal de la voiture
│   ├── ControllerMotor.py    # Contrôleur des moteurs CC
│   ├── ControllerServo.py    # Contrôleur du servomoteur
│   ├── LineFollower.py       # Détecteur de ligne noire
│   ├── Logging.py            # Système de journalisation
│   ├── main.py               # Point d'entrée principal
│   ├── PWM.py                # Driver pour le contrôle PWM (PCA9685)
│   ├── VoitureController.py  # Contrôleur simple de la voiture
│   ├── WebServerCar.py       # Serveur web pour l'interface de contrôle
│   └── templates/            # Templates pour l'interface web
│       └── web.html          # Interface web
├── testing/                  # Tests unitaires
│   ├── mock_moteur.py        # Tests pour le contrôleur de moteur
│   ├── mock_rgb.py           # Tests pour le capteur RGB
│   ├── mock_servo_moteur.py  # Tests pour le servomoteur
│   ├── mock_ultrason.py      # Tests pour les capteurs à ultrasons
│   └── test_lineFollower.py  # Tests pour le détecteur de ligne
```

## Démarrage

1. Clonez ce dépôt sur votre Raspberry Pi
2. Assurez-vous d'avoir installé toutes les dépendances requises
3. Lancez l'application principale :

```bash
cd HEH-2025-GDP-Voiture-Raspberry
python3 projet_voiture/main.py
```

## Matériel requis

- Raspberry Pi (compatible avec GPIOZero)
- Capteurs à ultrasons (x3)
- Capteur RGB
- Capteur de ligne infrarouge
- Servomoteur pour la direction
- Moteurs CC (x2)
- Module PWM PCA9685
- Batterie et alimentation

## Interface Web

Une interface web est disponible sur le port 5000 du Raspberry Pi, permettant de:
- Lancer la voiture en mode autonome
- Voir les mesures des capteurs en temps réel
- Arrêter la voiture
- Exécuter des manœuvres spéciales (tour en 8, rotation)

## Tests

Le projet inclut des tests unitaires pour chaque composant. Pour les exécuter :

```bash
cd HEH-2025-GDP-Voiture-Raspberry/testing
python3 -m unittest discover
```
