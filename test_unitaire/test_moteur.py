import unittest
from unittest.mock import patch, MagicMock
from moteur import moteur  

class TestMoteur(unittest.TestCase):

    @patch('moteur.PWMOutputDevice')
    @patch('moteur.Motor')
    def setUp(self, mock_motor, mock_pwm):
        # Crée des objets mock pour les moteurs et PWM
        self.mock_motor = mock_motor
        self.mock_pwm = mock_pwm
        self.mock_motor_instance = MagicMock()
        self.mock_pwm_instance = MagicMock()
        self.mock_motor.return_value = self.mock_motor_instance
        self.mock_pwm.return_value = self.mock_pwm_instance
        self.mon_moteur = moteur()
        
    def test_avancer_valide_avant(self):
        self.mon_moteur.avancer(0.6, 1)
        self.mock_motor_instance.forward.assert_called()
        self.assertEqual(self.mock_pwm_instance.value, 0.6)

    def test_avancer_valide_arriere(self):
        self.mon_moteur.avancer(0.4, 0)
        self.mock_motor_instance.backward.assert_called()
        self.assertEqual(self.mock_pwm_instance.value, 0.4)

    def test_vitesse_negative(self):
        with self.assertRaises(ValueError):
            self.mon_moteur.avancer(-0.1, 1)

    def test_vitesse_superieure_1(self):
        with self.assertRaises(ValueError):
            self.mon_moteur.avancer(1.5, 0)

    def test_vitesse_pas_de_reponse(self):
        with self.assertRaises(ValueError):
            self.mon_moteur.avancer(None, 0)
    
    def test_direction_invalide(self):
        with self.assertRaises(ValueError):
            self.mon_moteur.avancer(0.5, 99)

    def test_arret(self):
        self.mon_moteur.arret()
        self.mock_motor_instance.stop.assert_called()
        self.assertEqual(self.mock_pwm_instance.value, 0)

if __name__ == '__main__':
    unittest.main()
