import unittest
from unittest.mock import MagicMock, patch
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from projet_voiture.LineFollower import LineFollower

class TestLineFollower(unittest.TestCase):

    def setUp(self):
        patcher_sensor = patch('projet_voiture.LineFollower.DigitalInputDevice')
        self.MockDigitalInputDevice = patcher_sensor.start()
        self.addCleanup(patcher_sensor.stop)

        self.mock_sensor = MagicMock()
        self.MockDigitalInputDevice.return_value = self.mock_sensor

        self.follower = LineFollower(gpio_pin=20)
        self.mock_sensor.is_active = False

    def test_monitor_négative(self):
        """
        Teste si la méthode monitor() retourne True lorsque la ligne noire est détectée."""  
        result = self.follower.monitor()
        self.assertTrue(result, msg="monitor() doit retourner True quand la ligne noire est détectée")
    
    def test_monitor_positif(self): 
        """
        Teste si la méthode monitor() retourne False lorsque la ligne noire n'est pas détectée.
        """
        self.mock_sensor.is_active = True 
        result = self.follower.monitor()
        self.assertFalse(result,msg=f"monitor() doit retourner False quand la ligne noire n'est pas détectée, mais a retourné {result}")

    def test_monitor_TypeError(self): 
        """
        Teste si la méthode monitor() lève une exception TypeError lorsque le paramètre est de type str.
        """
        self.mock_sensor.is_active = "tyrffytrfty"
        with self.assertRaises(TypeError, msg="monitor() doit lever une exception TypeError quand le paramètre est de type str"):
            self.follower.monitor()

    def test_mauvais_pin_ValueError(self):
        """
        Teste si la méthode __init__() lève une exception ValueError lorsque le GPIO pin est négatif.
        """
        with self.assertRaises(ValueError, msg="Le GPIO pin ne peut pas être négatif"):
            LineFollower(gpio_pin=-1)

    def test_mauvais_pin_TypeError(self):
        """
        Teste si la méthode __init__() lève une exception TypeError lorsque le GPIO pin n'est pas un entier.
        """
        with self.assertRaises(TypeError, msg="Le GPIO pin doit être un entier"):
            LineFollower(gpio_pin=None)


if __name__ == '__main__':
    unittest.main()
