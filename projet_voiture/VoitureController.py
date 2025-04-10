from ControllerMotor import ControllerMotor
import RPi.GPIO as GPIO
import time

class VoitureController:
    def __init__(self, duration=10, speed=100):
        self.duration = duration
        self.speed = speed
        self.motor = ControllerMotor()

    def lancer_voiture(self):
        try:
            print("🚀 Lancement de la voiture en mode avance (simple)...")
            self.motor.forward(self.speed)
            time.sleep(self.duration)
            print("🛑 Arrêt de la voiture")
            self.motor.stop()
        except Exception as e:
            print("Erreur lors du lancement de la voiture (mode avance):", e)
        finally:
            GPIO.cleanup()
            print("Nettoyage des GPIO terminé.")