import RPi.GPIO as GPIO
import time
import serial
import adafruit_matrixkeypad

# Pins Configuration
TRIG = 1  # Pin for Ultrasonic TRIG
ECHO = 24  # Pin for Ultrasonic ECHO
RED_LED = 16  # Pin for Red LED
BUTTON = 18  # Pin for Button
BUZZER = 25  # Pin for Buzzer
MOTOR_IN1 = 23  # Pin for Motor Driver IN1
MOTOR_IN2 = 27  # Pin for Motor Driver IN2
MOTOR_EN = 22   # Pin for Motor Driver Enable (PWM)

# Arduino Serial
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
arduino.flush()

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(MOTOR_IN1, GPIO.OUT)
GPIO.setup(MOTOR_IN2, GPIO.OUT)
GPIO.setup(MOTOR_EN, GPIO.OUT)

# PWM for Motor Speed Control
motor_pwm = GPIO.PWM(MOTOR_EN, 100)  # Frequency = 100Hz
motor_pwm.start(0)  # Start with motor off

# Keypad Configuration
cols = [4, 17, 27, 22]  # Column pins (adjust based on your keypad wiring)
rows = [5, 6, 13, 19]   # Row pins (adjust based on your keypad wiring)

keys = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

# Password Configuration
PASSWORD = "333"
input_password = ""
authenticated = False

def read_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def control_motor(start):
    if start:
        GPIO.output(MOTOR_IN1, True)
        GPIO.output(MOTOR_IN2, False)
        motor_pwm.ChangeDutyCycle(75)  # Set motor speed (0-100%)
    else:
        GPIO.output(MOTOR_IN1, False)
        GPIO.output(MOTOR_IN2, False)
        motor_pwm.ChangeDutyCycle(0)  # Stop motor

def show_timer(duration):
    for remaining in range(duration, -1, -1):
        print(f"Timer: {remaining}s")  # Debug print (can be replaced with additional hardware display if needed)
        time.sleep(1)
    GPIO.output(BUZZER, True)
    time.sleep(1)
    GPIO.output(BUZZER, False)

try:
    print("System Ready!")
    time.sleep(2)

    while True:
        # Password Authentication
        if not authenticated:
            print("Enter Password:")
            input_password = ""
            while not authenticated:
                keys_pressed = keypad.pressed_keys
                if keys_pressed:
                    key = keys_pressed[0]
                    print(key, end='', flush=True)  # Show key (debug purpose)
                    if key == "#":  # Confirm password with '#'
                        if input_password == PASSWORD:
                            print("\nAccess Granted!")
                            authenticated = True
                        else:
                            print("\nAccess Denied!")
                            input_password = ""  # Reset input
                    elif key == "*":  # Reset password input
                        input_password = ""
                        print("\nPassword Reset")
                    else:
                        input_password += key
                    time.sleep(0.3)

        # System Functionality after Authentication
        if authenticated:
            # Read Humidity from Arduino
            if arduino.in_waiting > 0:
                humidity = arduino.readline().decode('utf-8').strip()
                print(f"Humidity: {humidity}%")  # Debug print

            # Read Distance
            distance = read_distance()
            print(f"Distance: {distance} cm")  # Debug print

            # Control Red LED based on distance
            if distance < 10:
                GPIO.output(RED_LED, True)  # Turn on Red LED
                control_motor(True)  # Start motor
            else:
                GPIO.output(RED_LED, False)  # Turn off Red LED
                control_motor(False)  # Stop motor

            # Button Press for Timer
            if GPIO.input(BUTTON) == GPIO.LOW:
                print("Timer Started!")
                show_timer(10)  # 10-second timer
                print("Timer Ended!")

            time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    motor_pwm.stop()
    GPIO.cleanup()
    arduino.close()
