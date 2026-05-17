#include <science_can.h>

#include <Servo.h>

module_t CAN_MODULE = kModuleDrill;
#define LINEAR_ACTUATOR_POWER 8
#define LINEAR_ACTUATOR_DIRECTION 9
#define ELECTROMAGNET_PIN 7
#define SERVO_PIN 5

Servo DrillServo;

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

  pinMode (LINEAR_ACTUATOR_POWER, OUTPUT);
  pinMode (LINEAR_ACTUATOR_DIRECTION, OUTPUT);
  pinMode (ELECTROMAGNET_PIN, OUTPUT);

  digitalWrite(LINEAR_ACTUATOR_POWER, LOW); 
  digitalWrite(LINEAR_ACTUATOR_DIRECTION, LOW);
  digitalWrite(ELECTROMAGNET_PIN, LOW);

  DrillServo.attach(SERVO_PIN);
  DrillServo.write(initial_pos);
  Serial.print("Starting from servo pos: ");
  Serial.println(initial_pos);
  delay(10);
}

void linear_actuator_step(uint8_t steps)
{
  switch(steps) {
    case 0x1:
      digitalWrite(LINEAR_ACTUATOR_POWER, HIGH); 
      digitalWrite(LINEAR_ACTUATOR_DIRECTION, HIGH);
      break;
    case 0x0:
      digitalWrite(LINEAR_ACTUATOR_POWER, LOW); 
      digitalWrite(LINEAR_ACTUATOR_DIRECTION, LOW);
      break;
    case 0xFF:
      digitalWrite(LINEAR_ACTUATOR_POWER, HIGH); 
      digitalWrite(LINEAR_ACTUATOR_DIRECTION, LOW);
      break;

    default:
      digitalWrite(LINEAR_ACTUATOR_POWER, LOW); 
      digitalWrite(LINEAR_ACTUATOR_DIRECTION, LOW);
      break;
  }
}

void electromagnet_step(int steps)
{
  digitalWrite(ELECTROMAGNET_PIN, steps);
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
  DrillServo.write(goal_pos);
  delay (100); 
}

void loop() {
  if (const int recv_cnt = Science::process_can()){
    Serial.print("Received ");
    Serial.print(recv_cnt);
    Serial.println(" Messages.");

    for (int i = 0; i < recv_cnt; ++i){
      Science::ScienceCANMessage incoming_message = Science::rx_buffer.pop();

      if (incoming_message.peripheral_ = kPeripheralLinearActuator) {
        linear_actuator_step(incoming_message.data_[0]);
      }

      if (incoming_message.peripheral_ = kPeripheralElectromagnet) {
        electromagnet_step(incoming_message.data_[0]);
      }

      if (incoming_message.peripheral_ = kPeripheralServo) {
        servo_step(incoming_message.data_[0]);
      }
    }
  }
}
