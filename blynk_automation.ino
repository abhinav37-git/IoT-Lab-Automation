#define BLYNK_TEMPLATE_ID "TMPL3-HUbrmfD"
#define BLYNK_TEMPLATE_NAME "Quickstart Template"
#define BLYNK_AUTH_TOKEN "kt_ZDEo90p9qrvVUet9mbog3C7WrY2AO"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <DHTesp.h>
#include <LiquidCrystal.h>


// #define BLYNK_PRINT Serial
#define pirPin 33
#define relayPin 4
#define DHT_PIN 2
#define gas_input 36

// Initialize the LCD with the pins
LiquidCrystal lcd(13, 12, 14, 27, 26, 25);

char ssid[] = "AKR78910L";
char pass[] = "abcd123444444";

BlynkTimer timer;
DHTesp dht;

String presenceValue = "";
int distanceValue = 0;
float temperatureValue=0;
float humidityValue=0;
int masterSwitch = 1;

void handleMasterSwitch(int val){
  masterSwitch = val;
  if(val == 1){
    digitalWrite(relayPin,HIGH);
  } else if (val == 2){
    digitalWrite(relayPin,LOW);
  }
}

BLYNK_WRITE(V0)
{
 int value = param.asInt();
 handleMasterSwitch(value);
}


BLYNK_CONNECTED()
{
 Serial.println("Connect ho gya");
 Blynk.setProperty(V3, "offImageUrl", "https://static-image.nyc3.cdn.digitaloceanspaces.com/general/fte/congratulations.png");
 Blynk.setProperty(V3, "onImageUrl", "https://static-image.nyc3.cdn.digitaloceanspaces.com/general/fte/congratulations_pressed.png");
 Blynk.setProperty(V3, "url", "https://docs.blynk.io/en/getting-started/what-do-i-need-to-blynk/how-quickstart-device-was-made");
}

void myTimerEvent()
{
 readFromPIR();
}

void setup()
{
 Serial.begin(9600);
 pinMode(pirPin,INPUT);
 pinMode(relayPin,OUTPUT);
 pinMode(gas_input, INPUT);
 Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
 dht.setup(DHT_PIN, DHTesp::DHT11);
//  pinMode(TRIGGER_PIN, OUTPUT);
//  pinMode(ECHO_PIN, INPUT);

 // Set up the LCD's number of columns and rows
 lcd.begin(16, 2);
 // Print a welcome message
 lcd.print("Welcome!");

 WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
//  timer.setInterval(1000, readFromPIR);M
}

void readFromMQ2(){
  int gas =0;
	//read the input from mq2 gas sensor
	gas = analogRead(gas_input);
	//print the input om serial monitor
	Serial.println(gas);
  Blynk.virtualWrite(V1, gas);
  if(gas > 500) 
  {
    Blynk.logEvent("smoke_sensor_alert","Fire detected");
  }
}

void readFromPIR(){
 int val = digitalRead(pirPin);
 if(val == HIGH){
    if(masterSwitch == 3)
      digitalWrite(relayPin,LOW);
    Blynk.virtualWrite(V11,"Present");
 } else {
    if(masterSwitch == 3)
      digitalWrite(relayPin,HIGH);
    Blynk.virtualWrite(V11,"Absent");
 }
 Serial.print("presence: ");
 Serial.println(val);

 float temperature = dht.getTemperature();
 float humidity = dht.getHumidity();

 if (!isnan(temperature) && !isnan(humidity)) {
    if(temperature != temperatureValue){
       temperatureValue = temperature;
       Blynk.virtualWrite(V5, temperatureValue);
       lcd.clear();
       lcd.setCursor(0, 0);
       lcd.print("Temp: ");
       lcd.print(temperatureValue);
       lcd.setCursor(0, 1);
       lcd.print("Humi: ");
       lcd.print(humidityValue);
    }
    if(humidity != humidityValue){
       humidityValue = humidity;
       Blynk.virtualWrite(V6, humidityValue);
    }
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" Humidity: ");
    Serial.println(humidity);
 } else {
    Serial.println("Failed to read from DHT sensor");
 }
}

void loop()
{
 Blynk.run();
 readFromPIR();
 readFromMQ2();
 delay(1000);
}