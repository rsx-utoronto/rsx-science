#include <circular_buffer.h>
#include <science_can.h>
#include <Servo.h>

Servo rightAngleServo;

//Science Module
module_t CAN_MODULE = kModuleMultispectral; 

#define SERVO_PIN 9

// SERVO PARAMETERS
Servo DrillServo;
const int initial_pos           = 90;
int rel_pos                     = 0;

const int backward_vel        = -90; 
const int forward_vel         = 90; 

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

  // attaches the servo on pin 9 to the servo object
  rightAngleServo.attach(3);

  // Serial.println("Servo attached!");

  // Set up Servo
  DrillServo.attach(SERVO_PIN);
  DrillServo.write(initial_pos);
  // Serial.print("Starting from servo pos: ");
  // Serial.println(initial_pos);
  delay(10);
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
      rel_pos = backward_vel;
      break;

    case 1: 
      rel_pos = forward_vel;
      break;

    default:
      Serial.println("Servo command not recognized"); 
      return;
      break;
  }

  // Set the final goal position and make sure its valid
  goal_pos = initial_pos + rel_pos;
  goal_pos %= 181;
   
  Serial.print("Moving one step forward: ");
  Serial.println(goal_pos);
  
  DrillServo.write(goal_pos);
  delay (10); 
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

        case kPeripheralServo:
          servo_step(incoming_message.data_[0]);
          break;

        default:
          Serial.println("Invalid peripheral for drill module");
          break;
      }
    }
    delay(10);
  }
}