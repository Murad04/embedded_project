import RPi.GPIO as GPIO
import time
import serial

# Pins Configuration
TRIG = 23
ECHO = 24
RED_LED = 16
BUZZER = 25

# Initialize Serial Communication
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
arduino.flush()

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED, GPIO.OUT)
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

try:
    print("System Ready!")
    while True:
        # Read Data from Arduino
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            print(f"Arduino: {data}")

            if "Access Denied" in data:
                GPIO.output(BUZZER, True)
                time.sleep(1)
                GPIO.output(BUZZER, False)

            elif "Access Granted" in data:
                print("System Active")

            elif "Temp:" in data and "Humidity:" in data:
                # Parse temperature and humidity
                parts = data.split(',')
                temp = parts[0].split(':')[1].strip()
                humidity = parts[1].split(':')[1].strip()
                print(f"Temperature: {temp}°C, Humidity: {humidity}%")

        # Ultrasonic Sensor to Control Red LED
        distance = read_distance()
        if distance < 10:
            GPIO.output(RED_LED, True)
        else:
            GPIO.output(RED_LED, False)

        # Example of Sending Motor Commands
        if distance < 10:
            arduino.write(b"Motor:ON\n")  # Start motor if object is close
        else:
            arduino.write(b"Motor:OFF\n")  # Stop motor if no object is close

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    GPIO.cleanup()
    arduino.close()
