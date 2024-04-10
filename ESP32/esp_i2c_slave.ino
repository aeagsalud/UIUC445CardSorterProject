#include "Wire.h"

#define I2C_DEV_ADDR 0x55
#define sdaPin 4
#define sclPin 5

uint32_t i = 0;
bool initialized;

// Requests from the master device upon a slave read request
void onRequest(){
  Wire.print(i++);
  Wire.print(" Packets.");
  Serial.println("onRequest");
}

// Reading data from the master
void onReceive(int len){
  Serial.printf("onReceive[%d]: ", len);
  while(Wire.available()){
    char c = Wire.read();
    Serial.println(c);
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Wire.onReceive(onReceive);
  Wire.onRequest(onRequest);
  initialized = Wire.begin((uint8_t)I2C_DEV_ADDR,(int) sdaPin,(int) sclPin, 0);
  if (initialized = true){
    Serial.println("initialization successful");
  }
}

void loop() {

}