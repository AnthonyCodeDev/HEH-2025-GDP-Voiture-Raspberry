import RPi.GPIO as GPIO
import time
import PWM as PCA

class ControllerMotor:
    """
    Contrôleur de moteurs DC.

    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    Quoi   : Contrôle de deux moteurs à courant continu via un pont en H.
    """
    def __init__(self):
        """
        Initialise le contrôleur des moteurs.
        Configure les broches GPIO et l'objet PWM.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Contrôle de deux moteurs à courant continu via un pont en H.
        """
        self.__moteur0_enable_pin = 4
        self.__moteur1_enable_pin = 5
        self.__moteur0_pin_a = 17
        self.__moteur1_pin_a = 27
        self.__moteur0_pin_b = 18
        self.__moteur1_pin_b = 22

        self.__gpio_pins = [
            self.__moteur0_pin_a,
            self.__moteur0_pin_b,
            self.__moteur1_pin_a,
            self.__moteur1_pin_b
        ]
        
        self.__pwm_controller = PCA.PWM()
        self.__pwm_controller.frequency = 60
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in self.__gpio_pins:
            GPIO.setup(pin, GPIO.OUT)

    def __apply_motor_state(self, pin_a, pin_b, pwm_value):
        """
        Applique l'état des sorties pour un moteur.

        :param pin_a: Broche de commande A.
        :param pin_b: Broche de commande B.
        :param pwm_value: Valeur PWM ajustée pour la vitesse.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Permet d'appliquer l'état des sorties pour un moteur.
        """
        GPIO.output(pin_a, GPIO.HIGH if pwm_value > 0 else GPIO.LOW)
        GPIO.output(pin_b, GPIO.LOW if pwm_value > 0 else GPIO.HIGH)
        channel = self.__moteur0_enable_pin if pin_a == self.__moteur0_pin_a else self.__moteur1_enable_pin
        self.__pwm_controller.write(channel, 0, int(abs(pwm_value)))

    def forward(self, speed=100):
        """
        Fait avancer les moteurs à la vitesse spécifiée.

        :param speed: Vitesse de 0 à 100.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Faire avancer les moteurs à la vitesse spécifiée.
        """
        pwm_val = self.__scale_speed(speed)
        self.__apply_motor_state(self.__moteur0_pin_a, self.__moteur0_pin_b, pwm_val)
        self.__apply_motor_state(self.__moteur1_pin_a, self.__moteur1_pin_b, pwm_val)

    def backward(self, speed=-100):
        """
        Fait reculer les moteurs à la vitesse spécifiée.

        :param speed: Vitesse négative entre 0 et -100.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Faire reculer les moteurs à la vitesse spécifiée.
        """
        if speed < 0:
            pwm_val = self.__scale_speed(speed)
            self.__apply_motor_state(self.__moteur0_pin_a, self.__moteur0_pin_b, pwm_val)
            self.__apply_motor_state(self.__moteur1_pin_a, self.__moteur1_pin_b, pwm_val)
        else:
            raise ValueError("La vitesse doit être négative pour le mouvement arrière")

    def stop(self):
        """
        Arrête les moteurs.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Arrêter les moteurs.
        """
        self.__apply_motor_state(self.__moteur0_pin_a, self.__moteur0_pin_b, 0)
        self.__apply_motor_state(self.__moteur1_pin_a, self.__moteur1_pin_b, 0)

    def __scale_speed(self, speed):
        """
        Convertit une vitesse de 0 à 100 en une valeur PWM comprise entre 0 et 4095.

        :param speed: Vitesse (positive pour avancer, négative pour reculer).
        :return: Valeur PWM correspondante.
        
        Auteur : Anthony Vergeylen
        Date   : 08-04-2025
        Quoi   : Convertir une vitesse de 0 à 100 en une valeur PWM.
        """
        return speed * 4095 / 100

def main():
    """
    Fonction principale pour tester le contrôleur de moteurs.
    Fait avancer pendant 2 secondes, reculer pendant 2 secondes, puis arrête.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    Quoi   : Fonction principale pour tester le contrôleur de moteurs.
    """
    try:
        motor_ctrl = ControllerMotor()
        print("Mouvement avant...")
        motor_ctrl.forward(100)
        time.sleep(2)
        
        print("Mouvement arrière...")
        motor_ctrl.backward(-100)
        time.sleep(2)
        
        print("Arrêt...")
        motor_ctrl.stop()
    except Exception as err:
        print("Erreur :", err)
    finally:
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé.")

if __name__ == "__main__":
    main()
