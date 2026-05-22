//#define MPM_ENABLE
#include <science_can.h>
#include <circular_buffer.h>

#include <science_can.h>
#include <circular_buffer.h>

#include <science_can.h>
#include <Servo.h>

// SCIENCE MODULE
module_t CAN_MODULE = kModuleOptics;

#define BLUE_LED_PIN      7
#define UV_LED_PIN        8
#define SERVO_PIN         9

// Spectrometer Specific Pins
#define SPEC_TRG              A0
#define SPEC_ST               A1
#define SPEC_CLK              A2
#define SPEC_VIDEO            A3

#define SPEC_CHANNELS         288
#define EXPSR_LOW             200   // Exposure too low
#define EXPSR_HI              400   // Exposure too high

// SPECTROMETER PARAMETERS
uint16_t data[SPEC_CHANNELS];

int integrateTime;
double delayTime;
int maxVal                    = 0;

/* This is the exposure level, 
* it ranges between 0-3 (inclusive) 
* to vary between the different 
* preset exposure levels (integration time)
*/
uint8_t expsrLev              = 0;
const int integrateClkVals[]  = {1, 2000, 10000, 29000};

/* The best values for the clock speed, 
* note that each of these is divided by 5 
* for the final value for cycle time. 
*/
const int delayVals[]         = {1, 5, 10, 20};

// SERVO PARAMETERS
Servo OpticalServo;
const int initial_pos         = 0; //added
int rel_pos                   = 0; //added

const int servo_backward      = 0; //added
const int servo_forward       = 90; //added


/* updateExpsrTime()
* (uint8_t) -> (None)
* 
*  Update exposure time based on input
*  
*  parameters:
*   - expsrLevel (uint8_t): Index of the exposure time wanted
*                           from the preset array above
* 
* returns:
*   - None
*/
void updateExpsrTime(uint8_t expsrLevel){
  integrateTime = integrateClkVals[expsrLevel];
  delayTime = delayVals[expsrLevel] / 5;
  return;
}


/* UV_LED_step()
* (uint_8) -> (None)
* 
* Toggles the UV LED on or off depending on the 
* received CAN input
* 
* parameters:
*   - steps (uint8_t): Input from CAN packet deciding 
*                       whether to turn LED on or off
* 
* return:
*   - None
*/
void UV_LED_step(uint8_t steps)
{
  digitalWrite(UV_LED_PIN, !bool(steps));
  return;
}


/* blue_LED_step()
* (uint_8) -> (None)
* 
* Toggles the Blue LED on or off depending on the 
* received CAN inpu
* 
* parameters:
*   - steps (uint8_t): Input from CAN packet deciding 
*                       whether to turn LED on or off
* 
* return:
*   - None
*/
void blue_LED_step(uint8_t steps)
{
  digitalWrite(BLUE_LED_PIN, !bool(steps));
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
void servo_step(uint8_t steps)
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
  
  OpticalServo.write(goal_pos);
  delay (10); 
}


/* readSpectrometer()
* (None) -> (None)
* 
* Reads the pixel values from the Hamamatsu C12880MA 
* Mini-Spectrometer. Code is taken from Github and 
* modified (not originally ours). The pixel values
* are stored in the "data" buffer array defined above.
* 
* parameters:
*   - None
* 
* return:
*   - None
*/
void readSpectrometer(){

  // Start clock cycle and set start pulse to on
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, LOW);

  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delayTime);

  //integration time start
  for(int i = 0; i < integrateTime; i++){

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }
  //integration time end


  /*
  * RSX specific: our spectrometer has an error where it the reading is off by
  * exactly two clock cycles. The following two cycles is a necessary correction
  * otherwise every reading is off by ~5 nm. Usually needs 86 but we need 88.
  */

  digitalWrite(SPEC_ST, LOW);
  for(int i = 0; i < 88; i++){
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);
  }

  //Read from SPEC_VIDEO
  maxVal = 0;
  for(int i = 0; i < SPEC_CHANNELS; i++){
      data[i] = analogRead(SPEC_VIDEO);
      if (data[i] > maxVal){
        maxVal = data[i];
      }
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);
  }


  // Signal to reset frame
  digitalWrite(SPEC_ST, HIGH);
  for(int i = 0; i < 7; i++){
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);
  }

  // Exposure/integration time updating
  // uncomment for auto_exposure

  // <START>

  // if (maxVal < EXPSR_LOW){
  //   expsrLev = (int) fmin(expsrLev + 1, 3);
  //   updateExpsrTime(expsrLev);
  // }
  // if (maxVal > EXPSR_HI){
  //   expsrLev = (int) fmax(expsrLev - 1, 0);
  //   updateExpsrTime(expsrLev);
  // }

  //<END>

  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
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

  // Set up Spectrometer
  pinMode(SPEC_CLK, OUTPUT);
  pinMode(SPEC_ST, OUTPUT);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);

  updateExpsrTime(expsrLev); //Lowest exposure time possible

  Science::MPM::sample_extraction_buffer.base_ = reinterpret_cast<uint8_t>(data);
  Science::MPM::sample_extraction_buffer.len_ = SPEC_CHANNELS * 2;
  Science::MPM::sample_extraction_buffer.available = true;

  // Set UV and Blue LED pins
  pinMode (UV_LED_PIN, OUTPUT);
  digitalWrite(UV_LED_PIN, HIGH);
  
  pinMode (BLUE_LED_PIN, OUTPUT);
  digitalWrite(BLUE_LED_PIN, HIGH);
  
  // Set up Servo
  OpticalServo.attach(SERVO_PIN);
  OpticalServo.write(initial_pos);
  //Serial.print("Starting from servo pos: ");
  //Serial.println(initial_pos);
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
        case kPeripheralUVLED:
          UV_LED_step(incoming_message.data_[0]);
          break;

        case kPeripheralBlueLED:
          blue_LED_step(incoming_message.data_[0]);
          break;

        case kPeripheralServo:
          servo_step(incoming_message.data_[0]);
          break;

        case kPeripheralSpectrometer:
          readSpectrometer();
          Science::MPM::queue_send = true;
          Science::MPM::frame = incoming_message.multipacket_id_;
          Science::MPM::recv = incoming_message.sender_;
          

        default:
          Serial.println("Invalid peripheral for optical module");
          break;
      }

      delay(10);
    }
  }
}

//MPM::queue_send = true;
//        MPM::frame = buf.multipacket_id_;
//        MPM::recv = buf.sender_;