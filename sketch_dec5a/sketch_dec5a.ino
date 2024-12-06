#include <Keypad.h>
#include <DHT.h>
#include <LiquidCrystal.h>
#include <Servo.h>

// DHT Sensor Configuration
#define DHTPIN 2         // Pin where the DHT sensor is connected
#define DHTTYPE DHT11    // DHT 11 sensor
DHT dht(DHTPIN, DHTTYPE);

// Servo Configuration
Servo myServo;
#define SERVO_PIN 3      // Pin where the Servo is connected

// LCD Pins Configuration
LiquidCrystal lcd(7, 8, 9, 10, 11, 12); // RS, EN, D4, D5, D6, D7

// DC Motor Configuration
#define MOTOR_IN1 5      // Pin for Motor Driver IN1
#define MOTOR_IN2 6      // Pin for Motor Driver IN2
#define MOTOR_EN 9       // Pin for Motor Driver Enable (PWM)

// Keypad Configuration
const byte ROWS = 4; // Number of rows in the keypad
const byte COLS = 4; // Number of columns in the keypad
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {A0, A1, A2, A3}; // Connect to the row pins of the keypad
byte colPins[COLS] = {A4, A5, 4, 13};  // Connect to the column pins of the keypad
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Password Configuration
const String PASSWORD = "333";
String inputPassword = "";
bool authenticated = false;

// Custom Temperature Thresholds
const float TEMP_THRESHOLD_SERVO = 30.0; // Threshold for Servo Motor (in °C)
const float TEMP_THRESHOLD_MOTOR = 35.0; // Threshold for DC Motor (in °C)

void setup() {
  Serial.begin(9600); // Initialize Serial communication
  dht.begin();
  myServo.attach(SERVO_PIN);
  myServo.write(0); // Initial position

  // Initialize DC Motor Pins
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_EN, OUTPUT);
  analogWrite(MOTOR_EN, 0); // Start with motor off

  lcd.begin(16, 2); // 16 columns, 2 rows
  lcd.print("Enter Password");
}

void loop() {
  if (!authenticated) {
    lcd.setCursor(0, 1);
    lcd.print("                "); // Clear the second row
    lcd.setCursor(0, 1);

    char key = keypad.getKey();
    if (key) {
      if (key == '#') { // Confirm password
        if (inputPassword == PASSWORD) {
          lcd.clear();
          lcd.print("Access Granted");
          authenticated = true;
          Serial.println("Authenticated"); // Send status to Raspberry Pi
          delay(2000);
          lcd.clear();
        } else {
          lcd.clear();
          lcd.print("Access Denied");
          inputPassword = ""; // Reset password input
          delay(2000);
          lcd.clear();
          lcd.print("Enter Password");
        }
      } else if (key == '*') { // Reset input
        inputPassword = "";
        lcd.print("                "); // Clear input
      } else {
        inputPassword += key;
        lcd.print("*"); // Display '*' for each entered character
      }
    }
  } else {
    // Read Temperature and Humidity
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      lcd.clear();
      lcd.print("DHT Error!");
      delay(2000);
      return;
    }

    // Display temperature and humidity
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(temperature);
    lcd.print("C");

    lcd.setCursor(0, 1);
    lcd.print("Humidity: ");
    lcd.print(humidity);
    lcd.print("%");

    // Send data to Raspberry Pi
    Serial.print("Temp:");
    Serial.print(temperature);
    Serial.print(",Humidity:");
    Serial.println(humidity);

    // Control Servo Motor
    if (temperature > TEMP_THRESHOLD_SERVO) {
      myServo.write(90); // Move servo to 90 degrees
    } else {
      myServo.write(0); // Move servo back to 0 degrees
    }

    // Control DC Motor
    if (temperature > TEMP_THRESHOLD_MOTOR) {
      digitalWrite(MOTOR_IN1, HIGH);
      digitalWrite(MOTOR_IN2, LOW);
      analogWrite(MOTOR_EN, 200); // Set motor speed (PWM value: 200 out of 255)
    } else {
      digitalWrite(MOTOR_IN1, LOW);
      digitalWrite(MOTOR_IN2, LOW);
      analogWrite(MOTOR_EN, 0); // Turn off motor
    }

    delay(2000); // Update every 2 seconds
  }
}
