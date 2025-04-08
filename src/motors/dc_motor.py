from gpiozero import Motor
from .i_motor import Imotor

class DcMotor(Imotor):
    def __init__(self, forward, backward, *, enable=None, pwm=True, pin_factory=None):
        self.motor = Motor(forward=forward, backward=backward, enable=enable, pwm=pwm, pin_factory=pin_factory)

    def read_data(self):
        # simulate motor state
        return {
            "is_active": self.motor.is_active
        }

    def display_data(self):
        print(f"Motor is {'running' if self.motor.is_active else 'stopped'}")

    def forward(self):
        self.motor.forward()

    def backward(self):
        self.motor.backward()

    def stop(self):
        self.motor.stop()
