import unittest
from unittest.mock import patch, MagicMock
import CapteurUltrason as HCSR04  

class TestHCSR04(unittest.TestCase):

    @patch('HCSR04.GPIO')
    def setUp(self, mock_GPIO):
        # (trigger,echo, max et min definit par defaut dans le constructeur)
        self.capteur_frontal = HCSR04(31, 29)
        self.capteur_gauche = HCSR04(37, 35)
        self.capteur_droite = HCSR04(23, 21)

        self.capteurs = [
            (self.capteur_frontal,"frontal"),
            (self.capteur_droite,"droite"),
            (self.capteur_gauche,"gauche"),
        ]
        
        mock_GPIO.input.side_effect =[0, 1, 0]

    @patch('HCSR04.time')
    def test_mesure_distance_avec_succes(self, mock_time, mock_GPIO):
        # temps = (distance*2)/34300 => 0.000583 = (10*2)/34300
        mock_time.time.side_effect = [0, 0.000583]

        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                distance = capteur.calculate_dist()
                self.assertAlmostEqual(distance, 10, delta=0.1)

    def test_capteur_timeout_lors_de_la_distance(self, mock_gpio):
        mock_gpio.wait_for_edge.return_value = None    
        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                distance = capteur.calculate_dist()
                self.assertIsNone(distance)

    @patch('HCSR04.time')
    def test_si_distance_inferieur_a_2cm(self, mock_gpio,mock_time):
        # temps = (distance*2)/34300 => 0.0000583 = (1*2)/34300 
        mock_time.time.side_effect = [0, 0.0000583]

        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                with self.assertRaises(ValueError):
                    capteur.calculate_dist()

    @patch('HCSR04.time')
    def test_si_distance_superieur_a_400cm(self, mock_gpio,mock_time):
        # temps = (distance*2)/34300 => 0.029 = (500*2)/34300 
        mock_time.time.side_effect = [0, 0.029]

        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                with self.assertRaises(ValueError):
                    capteur.calculate_dist()

    @patch('HCSR04.time')
    def test_distance_exactement_2cm(self, mock_gpio, mock_time):
        # temps = (distance*2)/34300 => (2 * 2) / 34300 = 0.000116
        mock_time.time.side_effect = [0, 0.000116]
        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                distance = capteur.calculate_dist()
                self.assertAlmostEqual(distance, 2, delta=0.1)

    @patch('HCSR04.GPIO')
    @patch('HCSR04.time')
    def test_distance_exactement_400cm(self, mock_gpio, mock_time):
        # temps = (distance*2)/34300 => (400 * 2) / 34300 = 0.0233
        mock_time.time.side_effect = [0, 0.0233]
        for capteur, nom in self.capteurs:
            with self.subTest(capteur=nom):
                distance = capteur.calculate_dist()
                self.assertAlmostEqual(distance, 400, delta=0.1)

if __name__ == '__main__':
    unittest.main()