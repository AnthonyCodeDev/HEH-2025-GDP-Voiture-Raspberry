from flask import Flask, render_template, request, redirect, url_for
import threading
import time
from moteur import MotorController  # Module personnalisé pour contrôler les moteurs
import RPi.GPIO as GPIO

def tourner_sur_place(duration=10, speed=100):
    """
    Fait tourner la voiture sur elle-même pendant un certain temps.

    :param duration: Durée de la rotation en secondes (par défaut : 10).
    :param speed: Vitesse de rotation (entre 0 et 100).
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    Quoi   : Rotation sur place de la voiture.
    """
    motor = MotorController()
    try:
        print("🔁 Rotation sur place...")
        # Calcul de la valeur PWM en fonction de la vitesse
        pwm_val = motor._MotorController__scale_speed(speed)
        # On fait tourner le véhicule : un moteur en avant, l'autre en arrière
        motor._MotorController__apply_motor_state(
            motor._MotorController__moteur0_pin_a,
            motor._MotorController__moteur0_pin_b,
            pwm_val
        )
        motor._MotorController__apply_motor_state(
            motor._MotorController__moteur1_pin_a,
            motor._MotorController__moteur1_pin_b,
            -pwm_val
        )
        time.sleep(duration)
        print("🛑 Arrêt du mouvement")
        motor.stop()
    except Exception as e:
        print("Erreur pendant la rotation :", e)
    finally:
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé.")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('web.html')

@app.route('/action', methods=['POST'])
def handle_action():
    action = request.form['action']
    if action == 'lancer':
        print("🚀 Lancement de la voiture")
        # Lancer la fonction dans un thread pour éviter de bloquer le serveur Flask
        thread = threading.Thread(target=tourner_sur_place, args=(10, 100))
        thread.start()
    elif action == 'reset':
        print("🔄 Réinitialisation et relancement")
        # Vous pouvez intégrer ici la logique pour réinitialiser et relancer la voiture
    elif action == 'avancer':
        print("➡️ Avancer la voiture")
        # Vous pouvez intégrer ici la logique pour faire avancer la voiture
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
