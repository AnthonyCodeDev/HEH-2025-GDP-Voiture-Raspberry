import os 

class CarLauncher:
    """
    Classe pour lancer le contrôle autonome de la voiture.

    QUI: Vergeylen Anthony
    QUOI: Utilise une instance existante de ControllerCar pour démarrer le contrôle autonome.
    """
    def __init__(self, car_controller):
        self.car_controller = car_controller

    def launch(self):
        self.car_controller.run()

    def shutdown(self):
        print("🔒 Arrêt de la voiture en cours...")
        self.car_controller.cleanup()
        os._exit(0)