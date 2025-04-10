#Created by Wiktor Chabowski
#07-04-2024
#Part of nano-computers project

import time
import os
from datetime import datetime
from gpiozero import DigitalInputDevice

from .i_sensor import i_sensor

class infrared_sensor(i_sensor):
    """
    Class for infrared sensor needed to check the black arrival line. The car stops when black is detected, else it continues

    @param name: name of the component (str)
    @param pin: pin used by the component (int)
    @param state: state for white - False and black - True (bool)
    """

    def __init__(self, name: str="", pin: int=0):
        """Constructor of the infrared sensor, initializing with name, pins voltage and state (False by default)
        Assumes pull_up=True and active_state=True 
        """

        self._digitalDevice = DigitalInputDevice(pin=pin, pull_up=True, active_state=True)
        self._name = name
        self._state = self._digitalDevice.value

    def _save_log(self, data, path):

        if not os.path.isabs(path):
            self._save_log("path must be an absolute path from root", '/logs/infrared_log_errors.log')
            raise ValueError("file_path must be an absolute path from root")

        try:
            #ISO 8601 format
            timestamp = datetime.now().isoformat()

            with open(path, 'a') as log_file:
                log_file.write(f"{timestamp} - {data}\n")
        except Exception as e:
            self._save_log(e, '/logs/infrared_log_errors.log')
            raise Exception(f"Error logging sensor data: {e}")

    def read_data(self):
        """Reads data from the sensor
        
        :raises Exception: Error while reading data from sensor
        """

        try:
            value = self._digitalDevice.value
            self._state = value
            return self._state
        except Exception as e:
            self._save_log(e, '/logs/infrared_log_errors.log')
            raise Exception(f"Error reading infrared sensor data: {e}")

    def display_data(self):
        """Displays the current :attr:`_state`
        
        :raises Exception: Error while displaying data
        """

        try:
            if self._digitalDevice.value:
                start_time = time.monotonic()
                #continue checking until 0.5 second have passed
                while (time.monotonic() - start_time) < 0.5:

                    #lazy waiting
                    time.sleep(0.005)
                    if not self._digitalDevice.value:
                        self._save_log("WHITE", '/logs/infrared_log.log')
                        print("WHITE")
                        return
                self._save_log("BLACK", '/logs/infrared_log.log')
                #if it remains after 0.5 seconds
                print("BLACK")
            else:
                self._save_log("WHITE", '/logs/infrared_log.log')
                print("WHITE")
        except Exception as e:
            self._save_log(e, '/logs/infrared_log_errors.log')
            print(f"Error displaying sensor data: {e}")
