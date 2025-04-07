from gpiozero import DistanceSensor

from composants.ISensor import ISensor

MAX_DIST = 400 #in cm
MIN_DIST = 2   #in cm
ANGLE = 15.0   #in °

class UltrasoundSensor(DistanceSensor, ISensor):
    """
    Class for ultrasound sensor that detects obstacles using sound waves, needed to check car's surroundings to later make decisions from the output

    @param name: name of the component (str)
    @param pins: list of pins used by the component (list<int>)
    @param voltage: voltage used by the component (float)
    @param MAX_DIST: constant for maximal distance that can be read
    @param MIN_DIST: constant for minimal distance that can be read
    @param ANGLE: constant for the angle of the sensor
    """    

    def __init__(self, name: str="", pins: list=..., voltage: float=0.0):

        #pins[0] = echo pin
        #pins[1] = trigger pin
        DistanceSensor.__init__(pins[0], pins[1], max_distance=MAX_DIST, threshold_distance=MIN_DIST)
        self._name = name
        self._color = None

    def read_data(self):
        """Reads data from the sensor"""

        return self.calculate_distance()

    def display_data(self):
        """Displays data after treating"""

        #appeler log_listener après
        data = self.read_data()
        pass

    def calculate_distance(self):
        return self.distance * 100 #for cm
