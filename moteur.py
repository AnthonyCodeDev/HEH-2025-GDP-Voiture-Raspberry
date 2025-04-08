#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import PCA9685 as PCA  # Assurez-vous que ce module est installé et accessible

class DCMotor:
    def __init__(self):
        # Définition des broches pour le contrôle des moteurs
        self.__Motor0_A = 17  # Moteur 0, entrée A : contrôle de la direction
        self.__Motor0_B = 18  # Moteur 0, entrée B : contrôle de la direction
        self.__Motor1_A = 27  # Moteur 1, entrée A : contrôle de la direction
        self.__Motor1_B = 22  # Moteur 1, entrée B : contrôle de la direction
        self.__EN_M0 = 4      # Moteur 0, activation de la vitesse
        self.__EN_M1 = 5      # Moteur 1, activation de la vitesse
        
        self.__pins = [
            self.__Motor0_A, 
            self.__Motor0_B, 
            self.__Motor1_A, 
            self.__Motor1_B
        ]
        
        # Instanciation d'un objet PWM et réglage de la fréquence sur 60Hz
        self.__pwm = PCA.PWM()
        self.__pwm.frequency = 60
        
        # Configuration initiale des GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in self.__pins:
            GPIO.setup(pin, GPIO.OUT)
    
    def __set_motor_state(self, motor_a, motor_b, pwm_value):
        """
        Méthode privée qui définit l'état du moteur:
        - motor_a et motor_b contrôlent la direction en définissant HIGH ou LOW.
        - pwm_value règle la vitesse du moteur (ici convertie de 0-100 à 0-4095).
        """
        GPIO.output(motor_a, GPIO.HIGH if pwm_value > 0 else GPIO.LOW)
        GPIO.output(motor_b, GPIO.LOW if pwm_value > 0 else GPIO.HIGH)
        # Choisit la broche d'activation selon le moteur utilisé
        self.__pwm.write(
            self.__EN_M0 if motor_a == self.__Motor0_A else self.__EN_M1, 
            0, 
            int(abs(pwm_value))
        )
    
    def motor_forward(self, vitesse=100):
        """
        Fait avancer les moteurs dans le sens avant.
        La vitesse est réglée de 0 à 100.
        """
        pwm_val = self.__regleof3(vitesse)
        self.__set_motor_state(self.__Motor0_A, self.__Motor0_B, pwm_val)
        self.__set_motor_state(self.__Motor1_A, self.__Motor1_B, pwm_val)
    
    def motor_backward(self, vitesse=-100):
        """
        Fait reculer les moteurs dans le sens arrière.
        Pour reculer, la vitesse doit être négative.
        """
        if vitesse < 0:
            pwm_val = self.__regleof3(vitesse)
            self.__set_motor_state(self.__Motor0_A, self.__Motor0_B, pwm_val)
            self.__set_motor_state(self.__Motor1_A, self.__Motor1_B, pwm_val)
        else:
            raise ValueError("La vitesse doit être négative pour reculer")
    
    def motor_stop(self):
        """
        Arrête les moteurs.
        """
        self.__set_motor_state(self.__Motor0_A, self.__Motor0_B, 0)
        self.__set_motor_state(self.__Motor1_A, self.__Motor1_B, 0)
    
    def __regleof3(self, vitesse):
        """
        Convertit une valeur de vitesse de 0 à 100 en une valeur de PWM de 0 à 4095.
        """
        return vitesse * 4095 / 100

def main():
    try:
        # Instanciation de l'objet pour contrôler les moteurs
        motor = DCMotor()
        
        # Faire avancer la voiture à vitesse maximale pendant 2 secondes
        print("La voiture avance...")
        motor.motor_forward(100)
        time.sleep(2)
        
        # Faire reculer la voiture à vitesse maximale pendant 2 secondes
        print("La voiture recule...")
        motor.motor_backward(-100)
        time.sleep(2)
        
        # Arrêter la voiture
        print("Arrêt de la voiture.")
        motor.motor_stop()
    
    except Exception as e:
        print("Erreur détectée :", e)
    
    finally:
        # Nettoyage des GPIO
        GPIO.cleanup()
        print("GPIO nettoyé.")

if __name__ == "__main__":
    main()
