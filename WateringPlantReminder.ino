#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <Adafruit_NeoPixel.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "2db9dd7d-1637-47db-96d4-495484ed45e7"
#define CHARACTERISTIC_UUID "38072c05-608d-441e-987e-69ee78d4a58c"
#define MOISTURE_SENSOR A0
#define MOISTURE_SENSOR_POWER A1

//#define DEBUG


//constants
const uint32_t ERROR_COLOR = 0xFF0000;
const uint32_t OK_COLOR = 0x00FF00;
const uint32_t SLEEP_COLOR = 0x87CEEB;
const uint8_t SENSOR_WAKE_TIME = (uint8_t)1000;             //milliseconds
const uint64_t READING_INTERVAL = (uint64_t)(1000000 * 600);  //in microseconds
const uint32_t BLE_BROADCAST_TIMEOUT = 1000 * 30;           //milliseconds

//variables
BLEServer *server = nullptr;
BLEService *service = nullptr;
Adafruit_NeoPixel status_led(1, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);
bool active_connection = false;


//functions
void startSleep();
bool initBLE();
void initMoistureSensor();
uint16_t readMoistureSensor();
void StartBLEBroadcast();



class BLECallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) {
    active_connection = true;
  }
  void onDisconnect(BLEServer *server) {
    startSleep();
  }
};

void set_status_led(uint32_t color) {
#ifdef DEBUG
  status_led.setPixelColor(0, color);
  status_led.show();
#endif
}

void initMoistureSensor() {
  pinMode(MOISTURE_SENSOR_POWER, OUTPUT);
  digitalWrite(MOISTURE_SENSOR_POWER, HIGH);
  delay(SENSOR_WAKE_TIME);
}

uint16_t readMoistureSensor() {
  return analogRead(MOISTURE_SENSOR);
}

bool initBLE() {
  if (!BLEDevice::init("Plant Monitor")) {
    return false;
  }
  server = BLEDevice::createServer();
  server->setCallbacks(new BLECallbacks());
  service = server->createService(SERVICE_UUID);
  return true;
}

void startBLEBroadcast() {
  service->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();
}

void startSleep() {
  esp_sleep_enable_timer_wakeup(READING_INTERVAL);
  esp_deep_sleep_start();
}


void setup() {

  pinMode(NEOPIXEL_POWER, OUTPUT);
#ifdef DEBUG
  digitalWrite(NEOPIXEL_POWER, HIGH);  //enable light for showing status
  status_led.clear();
  status_led.setBrightness(127);  //set half bright
#else
  digitalWrite(NEOPIXEL_POWER, LOW);
#endif

  if (!initBLE()) {
    set_status_led(ERROR_COLOR);
    return;
  }
  initMoistureSensor();
  set_status_led(OK_COLOR);

  uint16_t value = readMoistureSensor();
  BLECharacteristic *moisture =
    service->createCharacteristic(CHARACTERISTIC_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE);
  moisture->setValue(value);
  startBLEBroadcast();

  delay(BLE_BROADCAST_TIMEOUT);
  if (!active_connection)
    startSleep();
}

void loop() {
  //do nothing
}
