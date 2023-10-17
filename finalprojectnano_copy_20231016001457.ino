#include <ArduinoHttpClient.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <WiFiNINA.h>  // Include the WiFiNINA library

// WiFi network credentials
char ssid[] = "aryan";     // Replace with your WiFi network SSID
char pass[] = "24700124"; // Replace with your WiFi network password

// Define pin constants for sensors
#define SOIL_MOISTURE_SENSOR A0
#define MQ135_SENSOR A1

// Define LCD configuration
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Define IFTTT Webhooks constants
const char* apiKey = "dLfaUJTccstZHrqErwcjurFLGFpHEalm1qFqZ-ZNJ6b"; // Replace with your IFTTT Webhooks API key
const char* eventSoilMoisture = "email_to_farmer";
const char* eventAirQuality = "email_to_farmer";
const int soilMoistureThresholdMin = 90; // Adjust as needed
const int airQualityThreshold = 150;     // Adjust as needed

WiFiClient client;

void setup() {
  Serial.begin(9600);
  pinMode(SOIL_MOISTURE_SENSOR, INPUT);
  Wire.begin();
  lcd.init();
  lcd.backlight();

  // Connect to WiFi
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Attempting for Connecting to WiFi...");
    delay(1000);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  }
  else {
    Serial.println("Connection failed.");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  int soilMoistureValue = readSoilMoistureSensor();
  int airQualityValue = readMQ135Sensor();

  // Display sensor values on LCD
  lcd.setCursor(0, 0);
  lcd.print("Soil Moisture:");
  lcd.setCursor(0, 1);
  lcd.print("     ");
  lcd.setCursor(0, 1);
  lcd.print(soilMoistureValue);
  lcd.print("%");
  delay(2000);
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Air Quality:");
  lcd.setCursor(0, 1);
  lcd.print("     ");
  lcd.setCursor(0, 1);
  lcd.print(airQualityValue);
  delay(2000);
  lcd.clear();

  // Check soil moisture threshold and send email alert if exceeded
  if (soilMoistureValue <= 40) {
    sendEmailAlert("email_to_farmer", "Soil Mosturing Sensor", "LOW Moisture");
  }
  else if(soilMoistureValue > 40 && soilMoistureValue <= 80) {
    sendEmailAlert("email_to_farmer", "Soil Mosturing Sensor", "MID Moisture");
  }
  else if(soilMoistureValue >80 && soilMoistureValue<=100) {
    sendEmailAlert("email_to_farmer", "Soil Mosturing Sensor", "HIGH Moisture");
  }


  // Check air quality threshold and send email alert if exceeded
  if (airQualityValue>0 && airQualityValue<=150) {
    sendEmailAlert("email_to_farmer", "Air Quality Alert", "Air Quality is GOOD");
  }
  else if(airQualityValue>150 && airQualityValue<=299)
  {
    sendEmailAlert("email_to_farmer", "Air Quality Alert", "Air Quality is FAIR");
  }
  else if(airQualityValue>299)
  {
    sendEmailAlert("email_to_farmer", "Air Quality Alert", "Air Quality is DANGEROUS");
  }

  // Continue displaying and serial printing sensor data
  Serial.print("Soil Moisture: ");
  Serial.print(soilMoistureValue);
  Serial.println("%");
  Serial.print("Air Quality: ");
  Serial.println(airQualityValue);
  senddata(soilMoistureValue,airQualityValue);

  delay(2000);
}


int readSoilMoistureSensor() {
  int soilMoistureValue = analogRead(SOIL_MOISTURE_SENSOR);
  int moisturePercentage = map(soilMoistureValue, 0, 1023, 0, 100);
  return moisturePercentage;
}

int readMQ135Sensor() {
  int airQualityValue = analogRead(MQ135_SENSOR);
  return airQualityValue;
}

void sendEmailAlert(const char* event, const char* value1, const char* value2) {
  if (client.connect("maker.ifttt.com", 80)) {
    String jsonData = "{\"value1\":\"" + String(value1) + "\",\"value2\":\"" + String(value2) + "\"}";
    String url = "/trigger/" + String(event) + "/with/key/" + String(apiKey);

    client.print("POST " + url + " HTTP/1.1\r\n");
    client.print("Host: maker.ifttt.com\r\n");
    client.print("Content-Type: application/json\r\n");
    client.print("Content-Length: " + String(jsonData.length()) + "\r\n\r\n");
    client.print(jsonData);
    client.print("\r\n");

    delay(1000);

    while (client.available()) {
      char c = client.read();
      Serial.print(c);
    }

    client.stop();
  } else {
    Serial.println("Error connecting to IFTTT");
  }
}
void senddata(int value1, int value2) {
  if (client.connect("192.168.78.69", 12345)) {
    // Connected to Raspberry Pi
    Serial.println("Connected to Raspberry Pi");

    // Data to send
    String dataToSend = String(value1) + "," + String(value2);

    // Send the data
    client.println(dataToSend);

    // Close the connection
    client.stop();

    // Wait for a moment before sending more data
    delay(5000);
  } else {
    Serial.println("Connection failed");
  }
}