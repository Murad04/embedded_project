import RPi.GPIO as GPIO
import time
import serial

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
        # Read data from Arduino
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            print(f"Arduino: {data}")  # Print the data from Arduino

            if "Access Granted" in data:
                print("Authentication successful! System is active.")
                GPIO.output(RED_LED, True)
            elif "Access Denied" in data:
                print("Authentication failed! System is locked.")
                GPIO.output(RED_LED, False)
            elif "Temp:" in data and "Humidity:" in data:
                # Parse temperature and humidity
                parts = data.split(',')
                temp = parts[0].split(':')[1].strip()
                humidity = parts[1].split(':')[1].strip()
                print(f"Temperature: {temp}°C, Humidity: {humidity}%")

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
