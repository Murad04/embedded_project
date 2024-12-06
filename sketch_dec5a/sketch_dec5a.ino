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

// Custom Temperature Threshold
const float TEMP_THRESHOLD = 30.0; // Set your desired temperature threshold (in °C)

void setup() {
  Serial.begin(9600);
  dht.begin();
  myServo.attach(SERVO_PIN);
  myServo.write(0); // Initial position

  lcd.begin(16, 2); // 16 columns, 2 rows
  lcd.print("System Ready!");
  delay(2000);
  lcd.clear();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    lcd.clear();
    lcd.print("DHT Error!");
    delay(2000);
    return;
  }

  // Display humidity and temperature on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  lcd.print("%");

  // Send humidity and temperature data to Raspberry Pi via Serial
  Serial.print(temperature);
  Serial.print(",");
  Serial.println(humidity);

  // Control Servo Motor based on Temperature Threshold
  if (temperature > TEMP_THRESHOLD) {
    myServo.write(90); // Move servo to 90 degrees
    lcd.setCursor(0, 1);
    lcd.print("Servo: Active ");
  } else {
    myServo.write(0); // Move servo back to 0 degrees
    lcd.setCursor(0, 1);
    lcd.print("Servo: Inactive");
  }

  delay(2000); // Update every 2 seconds
}
