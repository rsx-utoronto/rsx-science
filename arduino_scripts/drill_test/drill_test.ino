#include <science_can.h>
#include <Servo.h>

// SCIENCE MODULE
module_t CAN_MODULE = kModuleDrill;

#define SERVO_PIN                 5
#define ELECTROMAGNET_PIN         7
#define LINEAR_ACTUATOR_POWER     8
#define LINEAR_ACTUATOR_DIRECTION 9
#define ULTRASONIC_TRIG           4
#define ULTRASONIC_ECHO           2

// SERVO PARAMETERS
Servo DrillServo;
const int initial_pos           = 0; //added
int rel_pos                     = 0; //added

const int servo_backward        = 0; //added
const int servo_forward         = 90; //added

// ULTRASONIC PARAMETERS
long duration;
int distance;


/* electromagnet_step()
* (uint_8) -> (None)
* 
* Toggles the electromagnet on or off depending on the 
* received CAN input
* 
* parameters:
*   - steps (uint8_t): Input from CAN packet deciding 
*                       whether to turn electromagnet
*                       on or off
* 
* return:
*   - None
*/
void electromagnet_step(uint8_t steps)
{
  digitalWrite(ELECTROMAGNET_PIN, !bool(steps));
  return;
} 


/* servo_step()
* (uint_8) -> (None)
* 
* Moves the positional servo between two specific positions 
* mentioned above as "servo_backward" and servo_forward".
* 
* parameters:
*   - steps (uint8_t): Input from CAN packet deciding 
*                       which servo position to go to
* 
* return:
*   - None
*/
void servo_step(int steps)
{
  int goal_pos;

  switch (steps) {
    case 0: 
      rel_pos = servo_backward;
      break;

    case 1: 
      rel_pos = servo_forward;
      break;

    default:
      Serial.println("Servo command not recognized"); 
      return;
      break;
  }

  // Set the final goal position and make sure its valid
  goal_pos = initial_pos + rel_pos;
  goal_pos %= 180;
   
  Serial.print("Moving to servo position: ");
  Serial.println(goal_pos);
  
  DrillServo.write(goal_pos);
  delay (10); 
}


/* linear_actuator_step()
* (uint8_t) -> (None)
* 
* Drives the linear actuator on the drill by giving
* signals to Syren50 motor driver depending on the input
* 
* parameters:
*   - steps (uint8_t): Command from CAN specifying one of three
*                      possible movements for the linear actuator
*                      
* returns:
*   - None
*/
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

  // Set Syren50 Motor Driver pins
  pinMode (LINEAR_ACTUATOR_POWER, OUTPUT);
  digitalWrite(LINEAR_ACTUATOR_POWER, LOW); 

  pinMode (LINEAR_ACTUATOR_DIRECTION, OUTPUT);
  digitalWrite(LINEAR_ACTUATOR_DIRECTION, LOW);

  // Set Electromagnet pins
  pinMode (ELECTROMAGNET_PIN, OUTPUT);
  digitalWrite(ELECTROMAGNET_PIN, LOW);

  // Set Ultrasnoic Sensor pins
  pinMode(ULTRASONIC_TRIG, OUTPUT); // Trig pin sends the pulse, so it is an Output
  pinMode(ULTRASONIC_ECHO, INPUT);  // Echo pin receives the pulse, so it is an Input

  // Set up Servo
  DrillServo.attach(SERVO_PIN);
  DrillServo.write(initial_pos);
  // Serial.print("Starting from servo pos: ");
  // Serial.println(initial_pos);
  delay(10);
}


void loop() {

  // Check for CAN message
  if (const int recv_cnt = Science::process_can()){
    Serial.print("Received ");
    Serial.print(recv_cnt);
    Serial.println(" Messages.");

    for (int i = 0; i < recv_cnt; ++i){
      Science::ScienceCANMessage incoming_message = Science::rx_buffer.pop();

      // Run peripheral specific command
      switch (incoming_message.peripheral_) {
        case kPeripheralLinearActuator:
          linear_actuator_step(incoming_message.data_[0]);
          break;

        case kPeripheralElectromagnet:
          electromagnet_step(incoming_message.data_[0]);
          break;

        case kPeripheralServo:
          servo_step(incoming_message.data_[0]);
          break;

        default:
          Serial.println("Invalid peripheral for drill module");
          break;
      }
    }

  // 1. Clear the trigPin by pulling it LOW first
  digitalWrite(ULRTASONIC_TRIG, LOW);
  delayMicroseconds(2);

  // 2. Trigger the sensor by sending a 10-microsecond HIGH pulse
  digitalWrite(ULTRASONIC_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);

  // 3. Read the echoPin. pulseIn() returns the sound wave travel time in microseconds
  duration = pulseIn(ULTRASONIC_ECHO, HIGH);

  // 4. Calculate the distance in centimeters
  // Speed of sound is ~0.0343 cm/us. We divide by 2 because the wave travels to the object and back.
  distance = duration * 0.0343 / 2;

  Science::ScienceCANMessage send_back;
  send_back.priority_ = 0x1;
  send_back.multipacket_id_ = 0x0;
  send_back.sender_ = kModuleDrill;
  send_back.receiver_ = kModuleRPi;
  send_back.peripheral_ = kPeripheralUltrasonic;
  send_back.dlc_ = 4;
  *((float*) (send_back.data_)) = distance; // Copy 32b float into 8b[4]
  Science::tx_buffer.push(send_back);

  while (!Science::rx_buffer.empty()) {
    Science::ScienceCANMessage incoming_message = Science::rx_buffer.pop();
    if (incoming_message.peripheral_ = kPeripheralUltrasonic) {

    }
  }

  if (const int send_cnt = Science::process_tx()) {
    Serial.print("Sent ");
    Serial.print(send_cnt);
    Serial.println(" Messages.");
  }

    delay(10);
  }
}