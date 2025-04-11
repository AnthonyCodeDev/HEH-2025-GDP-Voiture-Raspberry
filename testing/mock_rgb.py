import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time
import threading

# Mock des modules matériels pour éviter les erreurs sur Windows
sys.modules['board'] = MagicMock()
sys.modules['busio'] = MagicMock()
sys.modules['adafruit_tcs34725'] = MagicMock()

# Ajoute le dossier racine du projet au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from projet_voiture.CapteurRGB import CapteurRGB

class TestCapteurRGB(unittest.TestCase):

    @patch('projet_voiture.CapteurRGB.adafruit_tcs34725.TCS34725')
    @patch('projet_voiture.CapteurRGB.busio.I2C')
    def setUp(self, mock_i2c, mock_tcs34725):
        # Mock du capteur RGB
        self.mock_sensor = mock_tcs34725.return_value
        self.mock_sensor.color_rgb_bytes = (0, 0, 0)  # Valeurs par défaut

        # Instanciation de CapteurRGB avec les mocks
        self.capteur = CapteurRGB()
        self.capteur.sensor = self.mock_sensor

    def test_calibrate(self):
        # Simule des valeurs RGB pendant la calibration
        self.mock_sensor.color_rgb_bytes = (100, 150, 200)
        with patch('time.time', side_effect=[0, 0.1, 0.2, 0.3, 5.1]):  # Simule le temps pour la calibration
            self.capteur.calibrate()

        # Vérifie que les valeurs de référence sont correctement calculées
        self.assertEqual(self.capteur.ref_r, 100)
        self.assertEqual(self.capteur.ref_g, 150)
        self.assertEqual(self.capteur.ref_b, 200)

    def test_detect_color(self):
        # Test des différentes couleurs détectées
        self.assertEqual(self.capteur.detect_color(255, 50, 50), "rouge")
        self.assertEqual(self.capteur.detect_color(50, 255, 50), "vert")
        self.assertEqual(self.capteur.detect_color(50, 50, 255), "bleu")
        self.assertEqual(self.capteur.detect_color(100, 100, 100), "indéterminé")

    def test_threshold_values(self):

        # Valeurs différentes
        test_values = [-1, 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000]
        for value in test_values:
            with self.assertRaises(ValueError, msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec threshold incorrect"):
                CapteurRGB(threshold=value,integration_time=100, calibration_duration=5)

    def test_integration_time_values(self):

        # Valeurs différentes
        test_values = [-1, 69420]
        for value in test_values:
            with self.assertRaises(ValueError, msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec integration_time incorrect"):
                CapteurRGB(threshold=5,integration_time=value, calibration_duration=5)

    def test_calibration_duration_values(self):

        # Valeurs différentes
        test_values = [-1, 42069]
        for value in test_values:
            with self.assertRaises(ValueError, msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec calibration_duration incorrect"):
                CapteurRGB(threshold=5,integration_time=100, calibration_duration=value)

if __name__ == '__main__':
    unittest.main()
