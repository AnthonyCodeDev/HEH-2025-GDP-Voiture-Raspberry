#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajoute le dossier racine du projet au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock des modules matériels pour éviter les erreurs sur Windows
sys.modules['smbus'] = MagicMock()

class TestControllerServo(unittest.TestCase):
    def setUp(self):
        """
        Patch le constructeur de PWM dans le module ControllerServo pour éviter l'accès réel au matériel.
        """
        # Patch la méthode _get_pi_revision et _get_bus_number
        self.patcher1 = patch('projet_voiture.PWM.PWM._get_pi_revision', return_value='non-linux')
        self.patcher2 = patch('projet_voiture.PWM.PWM._get_bus_number', return_value=1)
        self.patcher1.start()
        self.patcher2.start()
        
        # Créer notre mock PWM
        self.mock_pwm_instance = MagicMock()
        
        # IMPORTANT: Nous devons patcher l'import de PWM dans ControllerServo
        # pour qu'il retourne notre mock au lieu d'instancier la vraie classe
        self.patcher_pwm = patch('projet_voiture.ControllerServo.PCA', return_value=self.mock_pwm_instance)
        self.patcher_pwm.start()
        
        # Import ControllerServo après avoir configuré les mocks
        from projet_voiture.ControllerServo import ControllerServo
        self.ControllerServo = ControllerServo  # Garde une référence à la classe

    def tearDown(self):
        """Arrête tous les patchers après chaque test"""
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher_pwm.stop()

    def test_initialization(self):
        """Test l'initialisation du contrôleur et la configuration de la fréquence PWM."""
        servo = self.ControllerServo()
        
        # Vérifie que les valeurs par défaut sont correctement initialisées
        self.assertEqual(servo.center_val, 320)
        self.assertEqual(servo.min_val, 200)
        self.assertEqual(servo.max_val, 500)
        
        # Vérifie que la fréquence PWM est définie correctement
        self.assertEqual(servo.pwm.frequency, 60)

    def test_rotate(self):
        """Test de la méthode rotate pour des angles positifs et négatifs."""
        servo = self.ControllerServo()
        
        # Réinitialiser le mock
        self.mock_pwm_instance.write.reset_mock()
        
        # Test avec un angle centré (0°)
        servo.rotate(0)
        self.mock_pwm_instance.write.assert_called_with(0, 0, 320)
    