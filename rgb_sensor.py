import time
import board
import busio
import adafruit_tcs34725

# Initialisation du bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialisation du capteur
capteur = adafruit_tcs34725.TCS34725(i2c)

# Activer l’éclairage LED interne
capteur.enable = True
capteur.integration_time = 100  # en ms

# Fonction pour détecter une couleur dominante
def detecter_couleur(r, g, b):
    if r > g and r > b:
        return "🔴 Je vois du rouge"
    elif g > r and g > b:
        return "🟢 Je vois du vert"
    elif b > r and b > g:
        return "🔵 Je vois du bleu"
    else:
        return "⚪ Couleur indéterminée ou blanche"

# Phase de calibration
print("🛠️ Calibration en cours... Ne touchez à rien pendant 5 secondes.")
nb_mesures = 0
somme_r = 0
somme_g = 0
somme_b = 0
debut = time.time()
while time.time() - debut < 5:
    r, g, b = capteur.color_rgb_bytes
    somme_r += r
    somme_g += g
    somme_b += b
    nb_mesures += 1
    time.sleep(0.1)

# Calcul des valeurs moyennes de référence
ref_r = somme_r // nb_mesures
ref_g = somme_g // nb_mesures
ref_b = somme_b // nb_mesures
print(f"✅ Calibration terminée. RGB de base : R={ref_r}, G={ref_g}, B={ref_b}")
print("🕵️ Détection des couleurs en cours...")

# Définir un seuil de détection (écart minimum pour considérer un changement)
SEUIL = 10

try:
    while True:
        r, g, b = capteur.color_rgb_bytes

        # Vérification si l'écart est significatif
        ecart_r = abs(r - ref_r)
        ecart_g = abs(g - ref_g)
        ecart_b = abs(b - ref_b)

        if ecart_r > SEUIL or ecart_g > SEUIL or ecart_b > SEUIL:
            print(f"R: {r}, G: {g}, B: {b} -> {detecter_couleur(r, g, b)}")
        else:
            print("🎯 Rien de nouveau détecté (environnement stable)")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("🛑 Arrêt du programme")
