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
    
    @patch('projet_voiture.CapteurRGB.CarLauncher')
    def test_monitor(self, mock_car_launcher):
        """Test que la voiture est lancée lorsque la couleur verte est détectée"""

        # Création d'une instance mock de CarLauncher
        car_launcher_mock = MagicMock()
        
        # Simuler la couleur verte pour la détection
        self.mock_sensor.color_rgb_bytes = (0, 255, 0)  # Vert (R=0, G=255, B=0)

        # On simule un fonctionnement en parallèle de monitor
        with patch('time.sleep', return_value=None):  # On empêche le vrai `time.sleep` pour accélérer les tests
            monitor_thread = threading.Thread(target=self.capteur.monitor, args=(car_launcher_mock,))
            monitor_thread.start()

        # Attendre un petit peu pour s'assurer que le thread ait démarré
        time.sleep(1)

        # Vérifie que la méthode `launch` a été appelée sur `car_launcher`
        car_launcher_mock.launch.assert_called_once()

        # Arrêter le thread après le test
        monitor_thread.join()

    @patch('projet_voiture.CapteurRGB.CarLauncher')
    def test_monitor_does_not_launch_on_non_green(self, mock_car_launcher):
        """Test que la voiture n'est pas lancée si la couleur n'est pas verte"""

        # Simuler une couleur rouge pour la détection
        self.mock_sensor.color_rgb_bytes = (255, 0, 0)  # Rouge (R=255, G=0, B=0)

        # On simule un fonctionnement en parallèle de monitor
        with patch('time.sleep', return_value=None):  # On empêche le vrai `time.sleep` pour accélérer les tests
            monitor_thread = threading.Thread(target=self.capteur.monitor, args=(mock_car_launcher,))
            monitor_thread.start()

        # Attendre un petit peu pour s'assurer que le thread ait démarré
        time.sleep(1)

        # Vérifie que la méthode `launch` n'a pas été appelée sur `car_launcher`
        mock_car_launcher.launch.assert_not_called()

        # Arrêter le thread après le test
        monitor_thread.join()

if __name__ == '__main__':
    unittest.main()