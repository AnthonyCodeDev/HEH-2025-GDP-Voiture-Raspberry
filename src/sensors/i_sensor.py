#Created by Wiktor Chabowski
#07-04-2024
#Part of nano-computers project

from abc import abstractmethod, ABC

class i_sensor(ABC):
    """
    Interface for all sensors with common behavior
    """

    @abstractmethod
    def read_data(self):
        """Reads data from the sensor"""
        pass

    @abstractmethod
    def display_data(self):
        """Displays data after treating"""
        pass

    @abstractmethod
    def _save_log(self, data, path):
        """Save the read data to a specified log file, depending of the sensor (data or errors)"""
        pass