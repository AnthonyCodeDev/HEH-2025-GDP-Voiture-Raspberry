import time
from moteur import MotorController
import RPi.GPIO as GPIO

def tourner_sur_place(duration=10, speed=100):
    """
    Fait tourner la voiture sur elle-même pendant un certain temps.

    :param duration: Durée de la rotation en secondes (par défaut : 10).
    :param speed: Vitesse de rotation (0 à 100).
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    Quoi   : Rotation sur place de la voiture.
    """
    motor = MotorController()
    try:
        print("🔁 Rotation sur place...")
        # On fait avancer un moteur et reculer l'autre
        pwm_val = motor._MotorController__scale_speed(speed)
        motor._MotorController__apply_motor_state(motor._MotorController__moteur0_pin_a,
                                                  motor._MotorController__moteur0_pin_b,
                                                  pwm_val)
        motor._MotorController__apply_motor_state(motor._MotorController__moteur1_pin_a,
                                                  motor._MotorController__moteur1_pin_b,
                                                  -pwm_val)
        time.sleep(duration)
        print("🛑 Arrêt du mouvement")
        motor.stop()
    except Exception as e:
        print("Erreur pendant la rotation :", e)
    finally:
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé.")

if __name__ == "__main__":
    tourner_sur_place()
