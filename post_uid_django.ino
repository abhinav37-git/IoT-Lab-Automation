#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>


#define SS_PIN 4
#define RST_PIN 17
#define LED_BUILTIN 2

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;
// Init array that will store new NUID
byte nuidPICC[4];

// WiFi credentials
const char* ssid = "AKR78910L";
const char* password = "abcd123444444";
const char* scannerID = "DSF6-98GF-VNB7-82DA";

// Django server details
const char* serverAddress = "http://192.168.135.44:8000/"; // Replace with your Django server address

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);
  digitalWrite(LED_BUILTIN,HIGH);
  Serial.begin(115200);
  SPI.begin(18,23,19,2); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
  Serial.println();
  Serial.print(F("Reader: "));
  rfid.PCD_DumpVersionToSerial();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  Serial.println();
  Serial.println(F("This code scans the MIFARE Classic NUID."));
  Serial.print(F("Using the following key: "));
  printHex(key.keyByte, MFRC522::MF_KEY_SIZE);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  digitalWrite(LED_BUILTIN,LOW);
}

void loop() {
  // Reset the loop if no new card is present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;
  // Verify if the NUID has been read
  if (!rfid.PICC_ReadCardSerial())
    return;
  Serial.print(F("PICC type: "));
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  Serial.println(rfid.PICC_GetTypeName(piccType));
  // Check if the PICC is of Classic MIFARE type
  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
      piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
      piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    Serial.println(F("Your tag is not of type MIFARE Classic."));
    return;
  }
  // if (rfid.uid.uidByte[0] != nuidPICC[0] ||
  //     rfid.uid.uidByte[1] != nuidPICC[1] ||
  //     rfid.uid.uidByte[2] != nuidPICC[2] ||
  //     rfid.uid.uidByte[3] != nuidPICC[3]) {
  //   Serial.println(F("A new card has been detected."));
    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }
    Serial.println(F("The NUID tag is:"));
    Serial.print(F("In hex: "));
    printHex(rfid.uid.uidByte, rfid.uid.size);
        Serial.println();
    Serial.print(F("In dec: "));
    printDec(rfid.uid.uidByte, rfid.uid.size);
        Serial.println();

    // Convert UID to string
    String hexString = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      hexString += rfid.uid.uidByte[i] < 0x10 ? " 0" : " ";
      hexString += rfid.uid.uidByte[i];
    }
    Serial.print(F("UID as hex: "));
    Serial.println(hexString);

    // Send POST request to Django server
    WiFiClient client;
    HTTPClient http;

    // Construct the POST data
    String postData = "cardID=" + hexString + "&scannerID=" + scannerID; // Replace "uid" with your desired parameter name

    // Make the POST request
    http.begin(client, String(serverAddress) + "/api/addrecord"); // Replace "/your_django_endpoint/" with your Django endpoint
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int httpResponseCode = http.POST(postData);

    // Check the response
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response: " + response);
    } else {
      Serial.println("Error sending POST request. Error code: " + String(httpResponseCode));
    }

    // Clean up
    http.end();
  // } else {
  //   Serial.println(F("Card read previously."));
  // }

  // Halt PICC
  rfid.PICC_HaltA();
  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}

// Helper routine to dump a byte array as hex values to Serial
void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

// Helper routine to dump a byte array as dec values to Serial
void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}