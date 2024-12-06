import RPi.GPIO as GPIO
import time
import serial
from adafruit_character_lcd.character_lcd import Character_LCD_Mono

# Pins Configuration
TRIG = 23
ECHO = 24
RED_LED = 16
BUZZER = 25

# LCD Configuration
lcd_columns = 16
lcd_rows = 2
lcd_rs = 6
lcd_en = 5
lcd_d4 = 22
lcd_d5 = 27
lcd_d6 = 17
lcd_d7 = 4
lcd_backlight = 12

lcd = Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

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
    lcd.clear()
    lcd.message = "System Ready\n"
    print("System Ready!")
    time.sleep(2)

    while True:
        # Read Data from Arduino
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            print(f"Arduino: {data}")

            if "Access Denied" in data:
                GPIO.output(BUZZER, True)
                lcd.clear()
                lcd.message = "Access Denied\nTry Again"
                time.sleep(1)
                GPIO.output(BUZZER, False)

            elif "Access Granted" in data:
                lcd.clear()
                lcd.message = "Access Granted\nSystem Active"
                print("System Active")

            elif "Temp:" in data and "Humidity:" in data:
                # Parse temperature and humidity
                parts = data.split(',')
                temp = parts[0].split(':')[1].strip()
                humidity = parts[1].split(':')[1].strip()
                print(f"Temperature: {temp}°C, Humidity: {humidity}%")
                lcd.clear()
                lcd.message = f"Temp: {temp}C\nHumidity: {humidity}%"

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
    lcd.clear()
    lcd.message = "System Halted"

finally:
    GPIO.cleanup()
    arduino.close()
