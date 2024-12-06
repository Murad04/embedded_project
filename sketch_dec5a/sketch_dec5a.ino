#include <Keypad.h>
#include <DHT.h>
#include <LiquidCrystal.h>

// DHT Sensor Configuration
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// DC Motor Configuration
#define MOTOR_IN1 5
#define MOTOR_IN2 6
#define MOTOR_EN 9

// LCD Configuration
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

// Keypad Configuration
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {A0, A1, A2, A3};
byte colPins[COLS] = {A4, A5, 4, 13};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Password Configuration
const String PASSWORD = "333";
String inputPassword = "";
bool authenticated = false;

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  lcd.begin(16, 2);
  lcd.print("Enter Password");

  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_EN, OUTPUT);
  analogWrite(MOTOR_EN, 0); // Motor off
}

void loop() {
  // Keypad Authentication
  if (!authenticated) {
    lcd.setCursor(0, 1);
    lcd.print("                "); // Clear row
    lcd.setCursor(0, 1);

    char key = keypad.getKey();
    if (key) {
      if (key == '#') { // Confirm password
        if (inputPassword == PASSWORD) {
          lcd.clear();
          lcd.print("Access Granted");
          authenticated = true;
          Serial.println("Access Granted"); // Notify Raspberry Pi
          delay(2000);
          lcd.clear();
        } else {
          lcd.clear();
          lcd.print("Access Denied");
          Serial.println("Access Denied"); // Notify Raspberry Pi
          inputPassword = "";
          delay(2000);
          lcd.clear();
          lcd.print("Enter Password");
        }
      } else if (key == '*') { // Reset input
        inputPassword = "";
      } else {
        inputPassword += key;
        lcd.print("*"); // Show *
      }
    }
  } else {
    // Send temperature and humidity to Raspberry Pi
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (!isnan(temperature) && !isnan(humidity)) {
      Serial.print("Temp:");
      Serial.print(temperature);
      Serial.print(",Humidity:");
      Serial.println(humidity);
    }

    // Receive command from Raspberry Pi to control DC Motor
    if (Serial.available() > 0) {
      String command = Serial.readString();
      command.trim();
      if (command == "Motor:ON") {
        digitalWrite(MOTOR_IN1, HIGH);
        digitalWrite(MOTOR_IN2, LOW);
        analogWrite(MOTOR_EN, 200); // Start motor
        lcd.setCursor(0, 1);
        lcd.print("Motor Running   ");
      } else if (command == "Motor:OFF") {
        digitalWrite(MOTOR_IN1, LOW);
        digitalWrite(MOTOR_IN2, LOW);
        analogWrite(MOTOR_EN, 0); // Stop motor
        lcd.setCursor(0, 1);
        lcd.print("Motor Stopped   ");
      }
    }

    delay(2000); // Update every 2 seconds
  }
}
