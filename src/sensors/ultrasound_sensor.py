#Created by Wiktor Chabowski
#07-04-2024
#Part of nano-computers project

from gpiozero import DistanceSensor

from .i_sensor import i_sensor

MAX_DIST = 400.0 #in cm
MIN_DIST = 2.0  #in cm
ANGLE = 15.0   #in °

class ultrasound_sensor(i_sensor):
    """
    Class for ultrasound sensor that detects obstacles using sound waves, needed to check car's surroundings to later make decisions from the output

    @param name: name of the component (str)
    @param pins: list of pins used by the component (list<int>)
    @param voltage: voltage used by the component (float)
    @param MAX_DIST: constant for maximal distance that can be read
    @param MIN_DIST: constant for minimal distance that can be read
    @param ANGLE: constant for the angle of the sensor
    """    

    def __init__(self, name: str="", pins: list=[], voltage: float=0.0):

        #pins[0] = echo pin
        #pins[1] = trigger pin
        if pins is None or len(pins) < 2:
            raise ValueError("Pins must be a list with at least two elements: [echo_pin, trigger_pin].")
        
        max_cm = MAX_DIST / 100
        min_cm = MIN_DIST / 100
        
        #Calling DistanceSensor to initialize _sensor separately. It avoids metaclass errors while inheritating directly
        self._sensor = DistanceSensor(echo=pins[0], trigger=pins[1], max_distance=max_cm, threshold_distance=min_cm)
        self._name = name
        self._voltage = voltage

    def read_data(self):
        """Reads data from the sensor
        
        :raises Exception: Error while reading data from sensor
        """
        try:
            return self.calculate_distance()
        except ValueError as e:
            raise ValueError(f"Error reading ultrasound sensor data: {e}")

    def display_data(self):
        """Displays data after treating
        
        :raises Exception: Error while displaying data
        """

        #appeler log_listener après
        try:
            distance_m = self.read_data()
            print(f"Distance: {distance_m:.2f} cm")
        except Exception as e:
            print(f"Error displaying ultrasound sensor data: {e}")

    def calculate_distance(self):
        """Takes the distance from the sensor and converts it in cm before returning
        
        :returns distance_cm * 100: in cm (float)
        :raises Exception: Error with incorrect distance measured
        """

        distance_cm = self._sensor.distance * 100 # DistanceSensor returns the distance in meters.
        if distance_cm is None or distance_cm < MIN_DIST or distance_cm > MAX_DIST:
            raise ValueError("Invalid distance measurement.")
        return distance_cm  # Convert meters to centimeters.
    
    def getSensor(self):
        return self._sensor