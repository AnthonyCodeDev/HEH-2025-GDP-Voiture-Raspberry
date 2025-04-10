#!/usr/bin/env python3
import os
import datetime

class Logging:
    """
    Classe de logging pour enregistrer un message dans un fichier log.
    
    Les messages sont enregistrés dans le dossier /logs/<type_info>/,
    dans un fichier nommé <type_alerte>.log.
    
    Chaque message est précédé de la date complète au format belge (dd/mm/YYYY HH:MM:SS).
    Les types d'alerte possibles sont : INFO, WARNING, ALERT.
    """
    def __init__(self, base_log_dir="/logs"):
        self.base_log_dir = base_log_dir
        # On s'assure que le dossier de logs de base existe
        if not os.path.exists(self.base_log_dir):
            os.makedirs(self.base_log_dir)
    
    def log(self, message, type_info, type_alerte):
        """
        Log un message en l'enregistrant dans le fichier de log et en l'affichant dans la console.
        
        Paramètres:
          - message (str) : Le message à logger.
          - type_info (str) : Le sous-dossier (ex : 'system', 'errors', etc.) dans /logs/.
          - type_alerte (str) : Le type d'alerte, qui correspond aussi au nom du fichier log 
                                (valeurs possibles: INFO, WARNING, ALERT).
        """
        # Normalisation du type d'alerte
        type_alerte = type_alerte.upper()
        if type_alerte not in ["INFO", "WARNING", "ALERT"]:
            # Par défaut on définit le type à INFO si la valeur n'est pas attendue
            type_alerte = "INFO"
        
        # Récupération de la date et de l'heure au format belge : dd/mm/YYYY HH:MM:SS
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Format du message
        formatted_message = f"[{timestamp}] [{type_alerte}] {message}"
        
        # Affichage du message dans la console
        print(formatted_message)
        
        # Chemin complet du dossier de logs (ex: /logs/system)
        log_dir = os.path.join(self.base_log_dir, type_info)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Chemin du fichier de log (ex: /logs/system/INFO.log)
        log_file_path = os.path.join(log_dir, f"{type_alerte}.log")
        
        # Enregistrement du message dans le fichier en mode append
        with open(log_file_path, "a") as log_file:
            log_file.write(formatted_message + "\n")

# if __name__ == "__main__":
#     logger = Logging()
#     logger.log("Ceci est une information de test.", "system", "INFO")
#     logger.log("Attention, un avertissement a été détecté!", "system", "WARNING")
#     logger.log("Alerte critique! Intervention immédiate nécessaire.", "system", "ALERT")
