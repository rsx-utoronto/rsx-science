#include <science_can.h>

#include <Servo.h>

module_t CAN_MODULE = kModuleDrill;
#define UV_LED_PIN 8
#define BLUE_LED_PIN 7
#define SERVO_PIN 9

Servo OpticalServo;

const int initial_pos = 0; //added
int rel_pos = 0; //added

const int servo_home = 0; //added
const int servo_forward = 90; //added

void setup() {
  Serial.begin(115200);

  SPI.begin();

  // Reset MCP2515
  Science::mcp2515.reset();

  // Set CAN speed (must match your bus!)
  Science::mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);

  // Switch to normal mode
  Science::mcp2515.setNormalMode();

  Serial.println("MCP2515 init OK Yayyyyy :)");

  pinMode (UV_LED_PIN, OUTPUT);
  pinMode (BLUE_LED_PIN, OUTPUT);

  OpticalServo.attach(SERVO_PIN);
  //OpticalServo.write(initial_pos);
  //Serial.print("Starting from servo pos: ");
  //Serial.println(initial_pos);
  //delay(10);
}

void UV_LED_step(int steps)
{
  digitalWrite(UV_LED_PIN, steps);
}

void blue_LED_step(int steps)
{
  digitalWrite(BLUE_LED_PIN, steps);
} 

void servo_step(int steps)
{
  int goal_pos = 0; //added

  switch (steps) {
    case 0: 
      rel_pos = servo_home;
      break;

    case 1: 
      rel_pos = servo_forward;
      break;

    default: 
      rel_pos = 0;
      break;
  }
  goal_pos = initial_pos + rel_pos;
  goal_pos %= 180; 
  Serial.print("Moving to servo position: ");
  Serial.println(goal_pos);
  OpticalServo.write(goal_pos);
  delay (100); 
}

void loop() {
  if (const int recv_cnt = Science::process_can()){
    Serial.print("Received ");
    Serial.print(recv_cnt);
    Serial.println(" Messages.");

    for (int i = 0; i < recv_cnt; ++i){
      Science::ScienceCANMessage incoming_message = Science::rx_buffer.pop();

      if (incoming_message.peripheral_ = kPeripheralUVLED) {
        UV_LED_step(incoming_message.data_[0]);
      }

      if (incoming_message.peripheral_ = kPeripheralBlueLED) {
        blue_LED_step(incoming_message.data_[0]);
      }

      if (incoming_message.peripheral_ = kPeripheralServo) {
        servo_step(incoming_message.data_[0]);
      }
    }
  }
}