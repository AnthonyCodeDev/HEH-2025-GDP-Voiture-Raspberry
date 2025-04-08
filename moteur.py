from gpiozero import LED
from time import sleep

moteur1 = LED(5)  # Pin GPIO 5 (moteur 1)
moteur2 = LED(4)  # Pin GPIO 4 (moteur 2)

def demarrer_moteurs():
    print("Démarrage des moteurs (en avant).")
    moteur1.on()
    moteur2.on()

def arreter_moteurs():
    print("Arrêt des moteurs.")
    moteur1.off()
    moteur2.off()

if __name__ == "__main__":
    try:
        demarrer_moteurs()
        sleep(5)
        arreter_moteurs()
    except KeyboardInterrupt:
        arreter_moteurs()
        print("Interrompu par l’utilisateur.")
