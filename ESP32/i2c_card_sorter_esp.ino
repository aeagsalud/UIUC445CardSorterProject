/* Code involving the ESP32's servo movement modified ffrom 
 https://dronebotworkshop.com/esp32-servo/

 modified 8 Nov 2013
 by Scott Fitzgerald

 modified for the ESP32 on March 2017
 by John Bennett

 modified 14 Apr 2024
 by Steve Guzman

 see http://www.arduino.cc/en/Tutorial/Sweep for a description of the original code
 */

#include <Arduino.h>
#include <ESP32Servo.h>
#include "Wire.h"

#define I2C_DEV_ADDR 0x55
#define sdaPin 4
#define sclPin 5

// servo object to controll the platform's rotation
Servo rotatePlatform;

int pos = 0; // servo position
int servoPin = 9;
long testing = 0;
char cardColor = 0;
int motorLock = 0;

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
    cardColor = c;
  }

  motorLock += 1;


}

void setup() {
  // serial line communication setup
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  // setup to communicate between Pi and ESP32
  Wire.onReceive(onReceive);
  Wire.onRequest(onRequest);
  initialized = Wire.begin((uint8_t)I2C_DEV_ADDR,(int) sdaPin,(int) sclPin, 0);
  if (initialized = true){
    Serial.println("initialization successful");
  }


  // Servo timer allocation
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
  	rotatePlatform.setPeriodHertz(50);    // standard 50 hz servo
	rotatePlatform.attach(servoPin, 500, 2400); // attaches the servo on pin 18 to the servo object
	
}

void loop() {

  while (motorLock == 10) {

    if (cardColor == 114) {
      pos = 0;
    } else if (cardColor == 103) {
      pos = 45;
    } else if (cardColor == 98) {
      pos = 90;
    } else {
      pos = 135;
    }

    rotatePlatform.write(pos);
    delay(5000);

    motorLock = 0;
  }

}