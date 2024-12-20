import RPi.GPIO as GPIO
import time
from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C
import board
import busio

# Pins Configuration
TRIG = 16
ECHO = 18
RED_LED = 40
BUZZER = 12

# I2C LCD Configuration
lcd_columns = 16
lcd_rows = 2

# Create I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the I2C LCD
lcd = Character_LCD_I2C(i2c, lcd_columns, lcd_rows,address=0x27)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

def read_distance():
    # Send a 10-microsecond pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for ECHO to go HIGH
    timeout_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() - timeout_start > 0.02:  # 20ms timeout
            print("Timeout: ECHO signal did not go HIGH")
            return -1  # Return -1 to indicate a timeout error

    # Wait for ECHO to go LOW
    timeout_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() - timeout_start > 0.02:  # 20ms timeout
            print("Timeout: ECHO signal did not go LOW")
            return -1  # Return -1 to indicate a timeout error

    # Calculate the duration of the pulse
    pulse_duration = pulse_end - pulse_start

    # Convert the duration to distance in cm
    distance = pulse_duration * 17150  # Speed of sound = 343 m/s
    return round(distance, 2)


try:
    lcd.clear()
    lcd.message = "System Ready\n"
    print("System Ready!")
    time.sleep(2)

    while True:
        # Ultrasonic Sensor to Control Red LED
        distance = read_distance()
        print(f"Distance: {distance} cm")  # Debug print
        
        if distance < 10:
            GPIO.output(RED_LED, True)
            lcd.clear()
            lcd.message = f"Object Close\nDist: {distance} cm"
        else:
            GPIO.output(RED_LED, False)
            lcd.clear()
            lcd.message = "Safe Distance\n"

        # Trigger buzzer if an object is too close
        if distance < 5:
            GPIO.output(BUZZER, True)
            time.sleep(0.5)
            GPIO.output(BUZZER, False)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting program...")
    lcd.clear()
    lcd.message = "System Halted"

finally:
    GPIO.cleanup()
