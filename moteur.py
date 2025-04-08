import RPi.GPIO as GPIO
from time import sleep

# Configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Définir les pins
IN4 = 19
IN5 = 18
ENA = 16

GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(IN5, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Créer un PWM à 100 Hz
pwm = GPIO.PWM(ENA, 100)
pwm.start(100)  # 100% de vitesse

print("➡️ Moteur AVANCE (19 HIGH, 18 LOW)")
GPIO.output(IN4, GPIO.HIGH)
GPIO.output(IN5, GPIO.LOW)
sleep(2)

print("⛔ STOP")
GPIO.output(IN4, GPIO.LOW)
GPIO.output(IN5, GPIO.LOW)
sleep(1)

print("⬅️ Moteur RECULE (19 LOW, 18 HIGH)")
GPIO.output(IN4, GPIO.LOW)
GPIO.output(IN5, GPIO.HIGH)
sleep(2)

print("🛑 Arrêt et nettoyage")
GPIO.output(IN4, GPIO.LOW)
GPIO.output(IN5, GPIO.LOW)
pwm.stop()
GPIO.cleanup()
