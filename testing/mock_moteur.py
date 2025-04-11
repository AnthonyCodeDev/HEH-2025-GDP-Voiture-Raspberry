#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

class TestMotorController(unittest.TestCase):
    """
    Tests unitaires pour le contrôleur de moteur DC.

    Auteur : Rayan El Khachani
    Date   : 11-04-2025
    """

    @patch.dict('sys.modules', {'RPi': MagicMock(), 'RPi.GPIO': MagicMock(), 'PCA': MagicMock(), 'PWM': MagicMock()})
    def setUp(self):
        """
        Configure l'environnement de test en mockant les modules matériels,
        et initialise une instance du contrôleur de moteur.

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        # Ajouter le chemin parent à sys.path
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Importer après avoir mocké les modules
        from projet_voiture.ControllerMotor import ControllerMotor
        self.ControllerMotor = ControllerMotor
        
        # Créer une instance du contrôleur
        self.controller = self.ControllerMotor()

    def test_forward(self):
        """
        Teste que la méthode forward active correctement les moteurs en écrivant
        la valeur PWM maximale sur les bons canaux.

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        self.controller.forward(100)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 4095)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 4095)

    def test_backward(self):
        """
        Teste que la méthode backward active les moteurs pour reculer à vitesse maximale.

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        self.controller.backward(-100)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 4095)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 4095)

    def test_stop(self):
        """
        Teste que la méthode stop arrête correctement les moteurs (PWM = 0).

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        self.controller.stop()
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 0)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 0)

    def test_backward_invalid_speed(self):
        """
        Teste que backward soulève une exception si la vitesse est positive.

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        with self.assertRaises(ValueError):
            self.controller.backward(50)

    def test_init(self):
        """
        Test du constructeur de ControllerMotor pour s'assurer que les attributs principaux
        sont bien initialisés et que l'objet PWM mocké est utilisé.

        Auteur : Rayan El Khachani
        Date   : 11-04-2025
        """
        # Vérifie que l'objet est bien une instance de ControllerMotor
        self.assertIsInstance(self.controller, self.ControllerMotor)

        # Vérifie que les attributs essentiels existent
        self.assertTrue(hasattr(self.controller, '_ControllerMotor__moteur0_enable_pin'))
        self.assertTrue(hasattr(self.controller, '_ControllerMotor__moteur1_enable_pin'))
        self.assertTrue(hasattr(self.controller, '_ControllerMotor__gpio_pins'))
        self.assertTrue(hasattr(self.controller, '_ControllerMotor__pwm_controller'))

        # Vérifie que le contrôleur PWM est bien une instance mockée
        self.assertIsInstance(self.controller._ControllerMotor__pwm_controller, MagicMock)


if __name__ == '__main__':
    unittest.main()
