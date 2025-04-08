#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Tentative d'import du module PCA9685.
# En cas d'absence, on définit une version dummy pour le beta test.
try:
    import PCA9685 as PCA
except ModuleNotFoundError:
    # Définition d'une classe PWM dummy qui simule l'écriture sur le PWM
    class DummyPWM:
        def __init__(self):
            self.frequency = 60  # Fréquence par défaut

        def write(self, channel, on, off):
            # Pour le test, on affiche les commandes envoyées au PWM
            print(f"DummyPWM.write() - Canal : {channel}, on : {on}, off : {off}")

    # On encapsule la classe PWM dans un objet type PCA9685 pour garder la syntaxe d'origine.
    class DummyPCA9685:
        PWM = DummyPWM

    PCA = DummyPCA9685
    print("Module PCA9685 non trouvé, utilisation de la version dummy pour les tests.")


class DCMotor:
    def __init__(self):
        # Définition des broches pour le contrôle de la direction
        self.__Motor0_A = 17  # Moteur 0, entrée A
        self.__Motor0_B = 18  # Moteur 0, entrée B
        self.__Motor1_A = 27  # Moteur 1, entrée A
        self.__Motor1_B = 22  # Moteur 1, entrée B
        # Broches d'activation de la vitesse
        self.__EN_M0 = 4      # Moteur 0
        self.__EN_M1 = 5      # Moteur 1

        self.__pins = [
            self.__Motor0_A,
            self.__Motor0_B,
            self.__Motor1_A,
            self.__Motor1_B
        ]

        # Création d'un objet PWM via le module PCA9685 ou sa version dummy
        self.__pwm = PCA.PWM()
        self.__pwm.frequency = 60

        # Configuration des GPIO en mode BCM
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in self.__pins:
            GPIO.setup(pin, GPIO.OUT)

    def __set_motor_state(self, motor_a, motor_b, pwm_value):
        """
        Définit l'état du moteur :
          - La broche motor_a est mise à HIGH si pwm_value > 0, sinon LOW.
          - La broche motor_b est mise à LOW si pwm_value > 0, sinon HIGH.
          - La vitesse est réglée via la méthode write() du PWM.
        """
        GPIO.output(motor_a, GPIO.HIGH if pwm_value > 0 else GPIO.LOW)
        GPIO.output(motor_b, GPIO.LOW if pwm_value > 0 else GPIO.HIGH)
        # Choix du canal d'activation en fonction du moteur utilisé
        channel = self.__EN_M0 if motor_a == self.__Motor0_A else self.__EN_M1
        self.__pwm.write(channel, 0, int(abs(pwm_value)))

    def motor_forward(self, vitesse=100):
        """
        Fait avancer les moteurs dans le sens avant.
        'vitesse' est comprise entre 0 et 100.
        """
        pwm_val = self.__regleof3(vitesse)
        self.__set_motor_state(self.__Motor0_A, self.__Motor0_B, pwm_val)
        self.__set_motor_state(self.__Motor1_A, self.__Motor1_B, pwm_val)

    def motor_backward(self, vitesse=-100):
        """
        Fait reculer les moteurs dans le sens arrière.
        La valeur de 'vitesse' doit être négative.
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
        Convertit une valeur de vitesse de 0 à 100 en une valeur PWM comprise entre 0 et 4095.
        """
        return vitesse * 4095 / 100


def main():
    try:
        # Instanciation de l'objet DCMotor
        motor = DCMotor()

        # Faire avancer la voiture à 100% de la vitesse pendant 2 secondes
        print("La voiture avance...")
        motor.motor_forward(100)
        time.sleep(2)

        # Faire reculer la voiture à 100% de la vitesse pendant 2 secondes
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
