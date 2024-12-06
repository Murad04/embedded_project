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
            else:
                GPIO.output(RED_LED, False)  # Turn off Red LED

            # Button Press for Timer
            if GPIO.input(BUTTON) == GPIO.LOW:
                print("Timer Started!")
                show_timer(10)  # 10-second timer
                print("Timer Ended!")

            time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    GPIO.cleanup()
    arduino.close()
