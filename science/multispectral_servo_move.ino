#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
char recievedChar;
boolean newData = false; 

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  Serial.begin(9600);
}

void loop() {
    recvOneChar();
    turn_servo();
}

void recvOneChar() {
    if (Serial.available() > 0) {
        recievedChar = Serial.read();
        newData = true;
    }
}

void turn_servo() {
    if (newData == true) {
        if (recievedChar == 'f'){
          myservo.write(0);
          delay(1850);
        }
        else if (recievedChar == 'b'){
          myservo.write(180);
          delay(1850);
        }
        else{
          myservo.write(90);
          delay(1850);
        }
        newData = false;
    }
}



