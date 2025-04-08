import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ENA = 5  # PWM OUT2
IN1 = 18  # Sens 1
IN2 = 19  # Sens 2

GPIO.setup([ENA, IN1, IN2], GPIO.OUT)

# Allume PWM (100%)
GPIO.output(ENA, GPIO.HIGH)

print("🟢 Avance (IN1 HIGH / IN2 LOW)")
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)
sleep(2)

print("🟡 Stop")
GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
sleep(1)

print("🔴 Recule (IN1 LOW / IN2 HIGH)")
GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.HIGH)
sleep(2)

print("🛑 Fin")
GPIO.output(ENA, GPIO.LOW)
GPIO.cleanup()
