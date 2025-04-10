import unittest
from unittest.mock import patch, MagicMock
from gpiozero.pins.mock import MockFactory
from gpiozero import Device
import sys
import os

# Ajouter le dossier 'src' au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from projet_voiture.CapteurDistance import CapteurDistance


class TestUltrasoundSensor(unittest.TestCase):
    
    @patch('projet_voiture.CapteurDistance.DistanceSensor')
    def setUp(self, mock_distance_sensor):
        """Initialise le test avec un mock de DistanceSensor.
        Cree un mock pour chaque instance predefinies dans le constructeur de CapteurDistance.
        """
        Device.pin_factory = MockFactory()
    
        # creation d’un mock de capteur
        self.mock_sensor = MagicMock()
        self.mock_sensor.distance = 0.1  # Simule une distance de 10 cm
        mock_distance_sensor.return_value = self.mock_sensor
    
        # creation de l’objet a tester
        self.sensor = CapteurDistance(trigger=23,echo=21,sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=4.0)

        # self.directions = ["left", "right", "front"]

    def test_calculate_distance_valid(self):
        """Teste les distances valides pour chaque orientation.
        
        :return: 10 cm"""
        self.mock_sensor.distance = 0.1  # 10 cm
        result = self.sensor.get_distance()
        self.assertAlmostEqual(result, 10.0,delta=0.1,msg=f"echec : La distance mesuree est {result} cm, mais elle devrait être proche de 400 cm.")

    def test_calculate_distance_below_min(self):
        """Teste les distances en dessous de la valeur minimale possible par les restrictions du capteur.
        
        :raises: ValueError."""
        self.mock_sensor.distance = 0.01  # 1 cm
        with self.assertRaises(ValueError,msg="echec : La distance mesuree est en dessous de la plage autorisee."):
            self.sensor.get_distance()

    def test_calculate_distance_above_max(self):
        """Teste les distances au-dessus de la valeur maximale possible par les restrictions du capteur.
        
        :raises: ValueError."""
        self.mock_sensor.distance = 4.5  # 450 cm
        with self.assertRaises(ValueError,msg="echec : La distance mesuree est au-dessus de la plage autorisee."):
            self.sensor.get_distance()

    def test_calculate_distance_exact_min(self):
        """Teste la distance exacte correspondant a la distance minimal possible pour le capteur.
        
        :raises: ValueError."""
        self.mock_sensor.distance = 0.02  # 2 cm
        result = self.sensor.get_distance()
        self.assertAlmostEqual(result, 2.0, delta=0.1,msg=f"echec : La distance mesuree est {result} cm, elle devrait être proche de 2 cm.")

    def test_calculate_distance_exact_max(self):
        """Teste la distance exacte correspondant a la distance maximal possible pour le capteur.
        
        :raises: ValueError."""
        self.mock_sensor.distance = 4.0  # 400 cm
        result = self.sensor.get_distance()
        self.assertAlmostEqual(result, 400.0, delta=0.1, msg=f"echec : La distance mesuree est {result} cm, elle devrait être proche de 400 cm.")

    def test_runtime_error_distance(self):
        """Teste les erreurs d'execution (timeout par exemple) lors de la lecture des distances.
        
        :raises: RuntimeError."""
        self.mock_sensor.distance = MagicMock(side_effect=RuntimeError("Sensor error"))
        with self.assertRaises(RuntimeError, msg="echec : le code ne detecte pas le RuntimeError, donnee dans le cas d'un timeout."):
            self.sensor.get_distance()

    def test_with_sample_count_as_zero(self):
        """Teste la creation de la classe avec un nombre d'echantillons egal a zero.
        
        :raises: ValueError."""
        with self.assertRaises(ValueError,msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec nombre d'echantillons egal a zero."):
            CapteurDistance(trigger=23,echo=21,sensor_sample_count=0, sensor_sample_delay=0.01, max_distance=4.0)

    def test_with_sample_delay_as_zero(self):
        """Teste la creation de la classe avec un delai d'echantillonnage egal a zero.

        :raises: ValueError."""
        with self.assertRaises(ValueError,msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec delai d'echantillonnage egal a zero."):
            CapteurDistance(trigger=23,echo=21,sensor_sample_count=5, sensor_sample_delay=0, max_distance=4.0)
    
    def test_with_sample_count_as_very_high(self):
        """Teste la creation de la classe avec un nombre d'echantillons beaucoup trop eleve.

        :raises:: ValueError."""
        with self.assertRaises(ValueError,msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec nombre d'echantillons beaucoup trop eleve."):
            CapteurDistance(trigger=23,echo=21,sensor_sample_count=1000000, sensor_sample_delay=0.01, max_distance=4.0)
    
    def test_with_sample_delay_as_very_high(self):
        """Teste la creation de la classe avec un delai d'echantillonnage beaucoup trop eleve.

        :raises: ValueError"""
        with self.assertRaises(ValueError,msg="Echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec delai d'echantillonnage beaucoup trop eleve."):
            CapteurDistance(trigger=23,echo=21,sensor_sample_count=5, sensor_sample_delay=1000000, max_distance=4.0)
    
    def test_with_max_distance_as_zero(self):
        """Teste la creation de la classe avec une distance maximale egale a zero.

        :raises: ValueError"""
        with self.assertRaises(ValueError,msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec distance maximale egale a zero."):
            CapteurDistance(trigger=23,echo=21,sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=0)

    def test_wrong_pin_trigger_list(self):
        """Teste la creation de la classe avec des pin trigger incorrect.
        
        :raises: ValueError"""
        list_wrong_trigger = [-1,0,10,15,30]
        for trigger_pin in list_wrong_trigger:
            with self.assertRaises(ValueError, msg="echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec pin trigger incorrect."):
                CapteurDistance(trigger=trigger_pin, echo=21, sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=4.0)

    def test_wrong_ping_echo(self):
        """Teste la creation de la classe avec des pin echo incorrect.

        :raises: ValueError"""
        list_wrong_echo = [-1,0,10,15,30]
        for echo_pin in list_wrong_echo:
            with self.assertRaises(ValueError, msg="Echec : le code ne detecte pas le ValueError, donnee dans le cas d'une instanciation avec pin echo incorrect."):
                CapteurDistance(trigger=23, echo=echo_pin, sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=4.0)
        
if __name__ == '__main__':
    unittest.main()