#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import PCA9685 as PCA

class DCMotorController:
    def __init__(self):
        self.__motor0_pin_A = 17
        self.__motor0_pin_B = 18
        self.__motor1_pin_A = 27
        self.__motor1_pin_B = 22
        self.__motor0_enable = 4
        self.__motor1_enable = 5
        self.__pins = [
            self.__motor0_pin_A,
            self.__motor0_pin_B,
            self.__motor1_pin_A,
            self.__motor1_pin_B
        ]
        self.__pwm = PCA.PWM()
        self.__pwm.frequency = 60
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in self.__pins:
            GPIO.setup(pin, GPIO.OUT)

    def __set_motor_output(self, pin_a, pin_b, pwm_value):
        GPIO.output(pin_a, GPIO.HIGH if pwm_value > 0 else GPIO.LOW)
        GPIO.output(pin_b, GPIO.LOW if pwm_value > 0 else GPIO.HIGH)
        channel = self.__motor0_enable if pin_a == self.__motor0_pin_A else self.__motor1_enable
        self.__pwm.write(channel, 0, int(abs(pwm_value)))

    def move_forward(self, speed=100):
        pwm_val = self.__scale_speed(speed)
        self.__set_motor_output(self.__motor0_pin_A, self.__motor0_pin_B, pwm_val)
        self.__set_motor_output(self.__motor1_pin_A, self.__motor1_pin_B, pwm_val)

    def move_backward(self, speed=-100):
        if speed < 0:
            pwm_val = self.__scale_speed(speed)
            self.__set_motor_output(self.__motor0_pin_A, self.__motor0_pin_B, pwm_val)
            self.__set_motor_output(self.__motor1_pin_A, self.__motor1_pin_B, pwm_val)
        else:
            raise ValueError("Speed must be negative for backward movement")

    def stop(self):
        self.__set_motor_output(self.__motor0_pin_A, self.__motor0_pin_B, 0)
        self.__set_motor_output(self.__motor1_pin_A, self.__motor1_pin_B, 0)

    def __scale_speed(self, speed):
        return speed * 4095 / 100

def main():
    try:
        motor = DCMotorController()
        print("Moving forward...")
        motor.move_forward(100)
        time.sleep(2)
        print("Moving backward...")
        motor.move_backward(-100)
        time.sleep(2)
        print("Stopping...")
        motor.stop()
    except Exception as e:
        print("Error:", e)
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")

if __name__ == "__main__":
    main()
