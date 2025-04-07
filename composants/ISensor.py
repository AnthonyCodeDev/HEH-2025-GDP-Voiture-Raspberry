from abc import abstractmethod, ABCMeta
from gpiozero import *

class ISensor:
    """
    Interface for all sensors with common behavior
    """

    __metadata__ = ABCMeta

    @abstractmethod
    def read_data(self):
        """Reads data from the sensor"""
        pass

    @abstractmethod
    def display_data(self):
        """Displays data after treating"""
        pass


