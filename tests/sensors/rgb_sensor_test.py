import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the 'src' directory to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'src')))


from sensors.rgb_sensor import rgb_sensor

class TestRGBSensor(unittest.TestCase):

    @patch('sensors.rgb_sensor.pigpio.pi')
    def setUp(self, mock_pi):
        # Mock de l'instance pigpio
        self.mock_pi = mock_pi.return_value
        self.mock_pi.connected = True  # Simule une connexion réussie au daemon pigpio
        self.mock_pi.i2c_open.return_value = 1  # Simule un handle I2C valide
    
        # Crée une instance de rgb_sensor avec des paramètres fictifs
        self.sensor = rgb_sensor(name="TestRGB", pins=[1, 2], address=0x29, bus=1)

    def test_couleur_RGB_rouge(self):
        self.sensor.color = (255, 0, 0)
        result = self.sensor.couleur_RGB()
        self.assertEqual(result, "RED")
    
    def test_couleur_RGB_GREEN(self):
        self.sensor.color = (0, 255, 0)
        result = self.sensor.couleur_RGB()
        self.assertEqual(result, "GREEN")

    def test_couleur_RGB_bleu(self):
        self.sensor.color = (0, 0, 255)
        result = self.sensor.couleur_RGB()
        self.assertEqual(result, "BLUE")    

    def test_couleur_mixte_reponse(self):
        test_colors = [
            ((34, 139, 34), "GREEN"),
            ((0, 128, 0), "GREEN"),
            ((50, 205, 50), "GREEN"),
            ((50,168,82), "GREEN"),
            ((24,82,24), "GREEN"),
            ((138,1,13), "RED"),
            ((181,60,70), "RED"),
            ((110,35,41), "RED"),
            ((25,25,133), "BLUE"),
            ((71,71,191), "BLUE"),
            ((10,10,87), "BLUE"),
        ]
        
        for color, expected in test_colors:
            with self.subTest(color=color):
                self.sensor.color = color
                result = self.sensor.couleur_RGB()
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()