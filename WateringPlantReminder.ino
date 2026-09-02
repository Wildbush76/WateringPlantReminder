#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "2db9dd7d-1637-47db-96d4-495484ed45e7"
#define CHARACTERISTIC_UUID "38072c05-608d-441e-987e-69ee78d4a58c"
#define MOISTURE_SENSOR D0

//#define DEBUG


//constants
const uint8_t SENSOR_WAKE_TIME = (uint8_t)1000;             //milliseconds
const uint64_t READING_INTERVAL = (uint64_t)(1000000 * 3600);  //in microseconds
const uint32_t BLE_BROADCAST_TIMEOUT = 1000 * 30;           //milliseconds

//variables
BLEServer *server = nullptr;
BLEService *service = nullptr;
bool active_connection = false;


//functions
void startSleep();
bool initBLE();
uint16_t readMoistureSensor();
void StartBLEBroadcast();
void error();



class BLECallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) {
    active_connection = true;
  }
  void onDisconnect(BLEServer *server) {
    startSleep();
  }
};

void error() {
  digitalWrite(LED_BUILTIN,LOW);
  delay(5000);
  //trigger sleep
  startSleep();
}

uint16_t readMoistureSensor() {
  return touchRead(MOISTURE_SENSOR);
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
  pinMode(LED_BUILTIN, OUTPUT);

  if (!initBLE()) {
    error();
    return;
  }



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
