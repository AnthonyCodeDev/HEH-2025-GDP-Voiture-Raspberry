import time
import board
import busio
import adafruit_tcs34725

# Initialisation du bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialisation du capteur
capteur = adafruit_tcs34725.TCS34725(i2c)

# Activer l’éclairage LED interne (facultatif mais utile)
capteur.enable = True
capteur.integration_time = 100  # temps d'intégration en ms

def detecter_couleur(r, g, b):
    if r > g and r > b:
        return "🔴 Je vois du rouge"
    elif g > r and g > b:
        return "🟢 Je vois du vert"
    elif b > r and b > g:
        return "🔵 Je vois du bleu"
    else:
        return "⚪ Couleur indéterminée ou blanche"

try:
    while True:
        r, g, b = capteur.color_rgb_bytes
        print(f"R: {r}, G: {g}, B: {b} -> {detecter_couleur(r, g, b)}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Arrêt du programme")
