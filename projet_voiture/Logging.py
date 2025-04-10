#!/usr/bin/env python3
import os
import datetime

class Logging:
    """
    Classe de gestion des logs qui affiche le message avec un niveau d'alerte 
    et enregistre tous les messages dans un fichier unique situé dans le dossier de logs.
    
    Le niveau d'alerte (ex : "INFO", "WARNING", "ALERT") est utilisé uniquement pour l'affichage 
    dans la console. Pour l'enregistrement, tous les messages sont stockés dans un fichier nommé 
    selon le paramètre `type_info`, par exemple `/logs/system.log` ou `/logs/errors.log`.
    
    Chaque message est préfixé d'un timestamp au format belge (dd/mm/YYYY HH:MM:SS).
    """
    def __init__(self, base_log_dir="/logs"):
        """
        Initialise l'objet Logging et s'assure que le répertoire de logs de base existe.
        
        :param base_log_dir: Chemin du répertoire de base pour l'enregistrement des logs (défaut : "/logs").
        """
        self.base_log_dir = base_log_dir
        if not os.path.exists(self.base_log_dir):
            os.makedirs(self.base_log_dir)
    
    def log(self, message, type_info, type_alerte):
        """
        Affiche le message avec un niveau d'alerte et enregistre le message dans un fichier unique.
        
        Le message est affiché dans la console avec le niveau d'alerte (INFO, WARNING, ALERT). 
        Pour l'enregistrement, le message est stocké dans un fichier nommé "<type_info>.log" situé dans le dossier de base `/logs/`.
        
        :param message: Message à logger (str).
        :param type_info: Nom utilisé pour le fichier de log (ex : "system", "errors", etc.). 
                          Le message sera sauvegardé dans `/logs/<type_info>.log`.
        :param type_alerte: Niveau d'alerte du message, utilisé uniquement pour l'affichage (valeurs possibles : "INFO", "WARNING", "ALERT") (str).
        """
        # Normalisation du type d'alerte pour l'affichage
        type_alerte = type_alerte.upper()
        if type_alerte not in ["INFO", "WARNING", "ALERT"]:
            type_alerte = "INFO"
        
        # Création du timestamp au format belge
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Formatage du message à afficher
        formatted_message = f"[{timestamp}] [{type_alerte}] {message}"
        
        # Affichage du message dans la console
        print(formatted_message)
        
        # Détermination du chemin complet du fichier de log dans le dossier de base (/logs)
        log_file_path = os.path.join(self.base_log_dir, f"{type_info}.log")
        
        # Enregistrement du message dans le fichier en mode ajout
        with open(log_file_path, "a") as log_file:
            log_file.write(formatted_message + "\n")
