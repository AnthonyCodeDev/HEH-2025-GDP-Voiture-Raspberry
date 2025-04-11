import time

# --------------------------
# Fake Sensor and Controller Classes for Simulation
# --------------------------

class FakeSensor:
    def __init__(self, name, values):
        """
        :param name: Name of the sensor (for printing).
        :param values: A list of values to simulate readings. Once exhausted, the last value is repeatedly returned.
        """
        self.name = name
        self.values = values
        self.index = 0

    def start_thread(self):
        print(f"{self.name} sensor thread started.")

    def stop_thread(self):
        print(f"{self.name} sensor thread stopped.")

    def get_distance(self):
        if self.index < len(self.values):
            result = self.values[self.index]
            self.index += 1
        else:
            result = self.values[-1]
        print(f"{self.name} sensor reading: {result}")
        return result

class FakeMotorController:
    def forward(self, speed):
        print(f"Motor command: Moving forward at speed {speed}")

    def stop(self):
        print("Motor command: STOP")

class FakeServoController:
    def setToDegree(self, angle):
        print(f"Servo command: Set to {angle}°")

# --------------------------
# Car Simulation Class using the given mode_course code
# --------------------------

class CarSimulation:
    def __init__(self):

        self.capteur_front = FakeSensor("Front", [15]*10)   # Always returns 15 (<20)
        self.capteur_left  = FakeSensor("Left", [30, 35])   # Simulate a change to trigger right turn
        self.capteur_right = FakeSensor("Right", [40]*10)   # Constant values 

        # Fake controllers for motors and servos
        self.motor_ctrl = FakeMotorController()
        self.servo_ctrl = FakeServoController()

        # Configuration parameters
        self.motor_speed_forwards = 10
        self.motor_speed_backwards = 5
        self.acceleration = 1
        self.angle_virage_droite = 90    
        self.angle_virage_gauche = 0   
        self.angle_central = 45        

        # For simplicity, we don’t simulate the infrared sensor in this scenario.

    def mode_course(self):
        bobby_speed = True

        # Start sensor threads
        self.capteur_front.start_thread()  
        self.capteur_left.start_thread()     
        self.capteur_right.start_thread()    

        try:
            # We'll simulate one cycle of obstacle detection and reaction.
            # rthweretyhqerhqeyh
            for _ in range(2): 
                if bobby_speed:
                    self.motor_ctrl.forward(self.motor_speed_forwards)  # Maintain moderate speed
                time.sleep(0.1)  # Simulate sensor update delay

                # Obtain the front distance reading
                dist_forward = self.capteur_front.get_distance()
                if dist_forward is None:
                    continue  # Sensor not ready

                if dist_forward >= 20:
                    # No immediate obstacle; in simulation we know it's <20 so skip this branch you bastard.
                    continue

                # Obstacle detected; begin braking
                if bobby_speed:
                    self.motor_ctrl.forward(self.motor_speed_backwards * self.acceleration)

                # Get lateral sensor readings after braking
                curr_dist_left = self.capteur_left.get_distance()
                curr_dist_right = self.capteur_right.get_distance()

                time.sleep(0.1)  # Wait before taking new lateral readings

                # Get new lateral readings (simulate update)
                new_left = self.capteur_left.get_distance()
                new_right = self.capteur_right.get_distance()

                # Determine turning decision based on sensor changes.
                # The original code logic: if (curr_dist_left - new reading < 0) then turn right.
                if (curr_dist_left - new_left < 0):
                    bobby_speed = False
                    self.servo_ctrl.setToDegree(self.angle_virage_droite)
                    self.motor_ctrl.forward(self.motor_speed_forwards - 2)  # Small acceleration
                    print("Action: Turn RIGHT triggered based on left sensor change.")
                elif (curr_dist_right - new_right < 0):
                    bobby_speed = False
                    self.servo_ctrl.setToDegree(self.angle_virage_gauche)
                    self.motor_ctrl.forward(self.motor_speed_forwards - 2)
                    print("Action: Turn LEFT triggered based on right sensor change.")

                bobby_speed = True
                time.sleep(0.5)  # Allow time for the maneuver
                self.servo_ctrl.setToDegree(self.angle_central)  # Reset servo to center

                # For the simulation, exit the loop after one cycle.
                break

            # Simulate final stop commands (e.g., after detecting a finish line)
            time.sleep(2)
            self.motor_ctrl.stop()

        finally:
            # Stop all sensor threads regardless of errors or completion.
            self.capteur_front.stop_thread()  
            self.capteur_left.stop_thread()       
            self.capteur_right.stop_thread()
            print("Simulation complete.")

# --------------------------
# Run the simulation
# --------------------------

if __name__ == "__main__":
    sim = CarSimulation()
    sim.mode_course()