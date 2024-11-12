#include <Wire.h>
#include "hsc_ssc_i2c.h"
#include <AccelStepper.h>


/***************************************************************************************************/
/********************************************* Parameters ******************************************/
/***************************************************************************************************/
static const int TIMER_PERIOD_us = 1000; // in us
static const int interval_send_data = 10000; // in us

static const int RECORD_LENGTH_BYTE = 8;  // No:of bytes per sensor read
static const int MSG_LENGTH = 25*RECORD_LENGTH_BYTE;

static const int CMD_LENGTH = 4;
byte buffer_rx[500];
byte buffer_tx[MSG_LENGTH];
volatile int buffer_rx_ptr;
volatile int buffer_tx_ptr;

volatile bool flag_log_data = false;
volatile bool flag_read_sensor = false;

// data logging
# define LOGGING_UNDERSAMPLING  1
volatile int counter_log_data = 0;

// other variables
uint16_t tmp_uint16;
int16_t tmp_int16;
long tmp_long;
volatile uint32_t timestamp = 0; // in number of TIMER_PERIOD_us
/***************************************************************************************************/
/********************************************* Stepper motor control *********************************************/
/***************************************************************************************************/
// driver 1 actuator 1
static const int Theta_dir = 28;
static const int Theta_step = 26;
static const int Theta_en = 36;
static const int Theta_N_microstepping = 16;
static const long steps_per_rad_Theta = 78.74*Theta_N_microstepping; 
constexpr float MAX_VELOCITY_Theta = 7.62; 
constexpr float MAX_ACCELERATION_Theta = 100;


AccelStepper stepper_Theta = AccelStepper(AccelStepper::DRIVER, Theta_step, Theta_dir);

// Encoders
static const int Theta_encoder_A = 12;
static const int Theta_encoder_B = 13;

volatile int32_t Theta_pos = 0;



/***************************************************************************************************/
/********************************************* Timer *********************************************/
/***************************************************************************************************/
IntervalTimer myTimer;



uint16_t ch1;
uint16_t ch2;
// uint16_t ch3;
// uint16_t ch4;
// uint16_t ch5;
// uint16_t ch6;
// uint16_t ch7;
// uint16_t ch8;
/***************************************************************************************************/
/********************************************* Diagnostics/Testing *********************************/
/***************************************************************************************************/
static const bool USE_SERIAL_MONITOR = false; // for debug
int ledState = LOW;
volatile unsigned long blinkCount = 0; // use volatile for shared variables

/***************************************************************************************************/
/******************************************* setup *************************************************/
/***************************************************************************************************/
void setup() 
{

  // Initialize Native USB port
  if (USE_SERIAL_MONITOR)
  {
    Serial.begin(9600);
  }
  else
  {
    SerialUSB.begin(2000000);

    while (!SerialUSB);           // Wait until connection is established
  }

  buffer_rx_ptr = 0;


  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delayMicroseconds(100000); 
  digitalWrite(LED_BUILTIN, LOW);  // turn the LED on (HIGH is the voltage level)
  analogReadResolution(12);

// Stepper setup
  pinMode(Theta_dir, OUTPUT);
  pinMode(Theta_step, OUTPUT);

  stepper_Theta.setPinsInverted(false, false, true);
  

  stepper_Theta.setMaxSpeed(MAX_VELOCITY_Theta*steps_per_rad_Theta);
  

  stepper_Theta.setAcceleration(MAX_ACCELERATION_Theta*steps_per_rad_Theta);

  stepper_Theta.enableOutputs();
  

// Encoders
  attachInterrupt(digitalPinToInterrupt(Theta_encoder_A), ISR_Theta_encoder_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(Theta_encoder_B), ISR_Theta_encoder_B, CHANGE);
  Theta_pos = 0;



  stepper_Z.enableOutputs();
    
  myTimer.begin(timer_interruptHandler, TIMER_PERIOD_us);

}

/***************************************************************************************************/
/******************************** timer interrupt handling routine *********************************/
/***************************************************************************************************/
void timer_interruptHandler()
{ 
  timestamp = timestamp + 1;

  
  // send data to host computer
  counter_send_data = counter_log_data + 1;
  if (counter_send_data >= interval_send_data/TIMER_PERIOD_us)
  {
    counter_send_data = 0;
    flag_send_data = true;
  }
}

void blinkLED() {
  if (ledState == LOW) {
    ledState = HIGH;
    // blinkCount = blinkCount + 1;  // increase when LED turns on
  } else {
    ledState = LOW;
  }
  digitalWrite(LED_BUILTIN, ledState);
}

/***************************************************************************************************/
/********************************************  main loop *******************************************/
/***************************************************************************************************/
void loop()
{   

    while (SerialUSB.available())
    {
        buffer_rx[buffer_rx_ptr] = SerialUSB.read();
        buffer_rx_ptr = buffer_rx_ptr + 1;

        if (buffer_rx_ptr == CMD_LENGTH) 
        {
            buffer_rx_ptr = 0;
            cmd_id = buffer_rx[0];

            switch(buffer_rx[1])
            {
                case CONFIGURE_STEPPER_DRIVER:
                {
                    int microstepping_setting = buffer_rx[2];
                    if(microstepping_setting>16)
                        microstepping_setting = 16;
                                
                    Theta_driver.microsteps(microstepping_setting);
                    MICROSTEPPING_Z = microstepping_setting==0?1:microstepping_setting;
                    steps_per_mm_Z = FULLSTEPS_PER_REV_Z*MICROSTEPPING_Z/SCREW_PITCH_Z_MM;
                    
                    break;
                }
                case SET_MAX_VELOCITY_ACCELERATION:
                {
                    MAX_VELOCITY_Theta = float(uint16_t(buffer_rx[3])*256+uint16_t(buffer_rx[4]))/100;
                    MAX_ACCELERATION_Theta = float(uint16_t(buffer_rx[5])*256+uint16_t(buffer_rx[6]))/10;
                    stepper_Theta.setMaxSpeed(MAX_VELOCITY_Theta*steps_per_rad_Theta);
                    stepper_Theta.setAcceleration(MAX_ACCELERATION_Theta*steps_per_rad_Theta);
                    break;


                }
                
                        
    

        }

        // send position update to computer
      if(flag_send_data)
      {
    
        buffer_tx[0] = cmd_id;
        buffer_tx[1] = mcu_cmd_execution_in_progress; // cmd_execution_status
        
        uint32_t Theta_pos_int32t = uint32_t( Theta_use_encoder?Theta_pos:int32_t(stepper_Theta.currentPosition()) );
        buffer_tx[2] = byte(Theta_pos_int32t>>24);
        buffer_tx[3] = byte((Theta_pos_int32t>>16)%256);
        buffer_tx[4] = byte((Theta_pos_int32t>>8)%256);
        buffer_tx[5] = byte((Theta_pos_int32t)%256);
        
        uint32_t Theta_speed_measured = uint32_t( Y_use_encoder?Y_pos:int32_t(stepper_Y.currentPosition()) );
        buffer_tx[6] = byte(Y_pos_int32t>>24);
        buffer_tx[7] = byte((Y_pos_int32t>>16)%256);
        buffer_tx[8] = byte((Y_pos_int32t>>8)%256);
        buffer_tx[9] = byte((Y_pos_int32t)%256);
    
        
        SerialUSB.write(buffer_tx,MSG_LENGTH);
        flag_send_data = false;
        
      }
            
        
    


      
}

// Encoder interrupt handling
void ISR_Theta_encoder_A(){
  if(digitalRead(Theta_encoder_B)==0 && digitalRead(Theta_encoder_A)==1 )
    Theta_pos = Theta_pos + 1;
  else if (digitalRead(Theta_encoder_B)==1 && digitalRead(Theta_encoder_A)==0)
    Theta_pos = Theta_pos + 1;
  else
    Theta_pos = Theta_pos - 1;
}

void ISR_Theta_encoder_B(){
  if(digitalRead(Theta_encoder_B)==0 && digitalRead(Theta_encoder_A)==1 )
    Theta_pos = Theta_pos - 1;
  else if (digitalRead(Theta_encoder_B)==1 && digitalRead(Theta_encoder_A)==0)
    Theta_pos = Theta_pos - 1;
  else
    Theta_pos = Theta_pos + 1;
}

// Handle microstepping changes

void set_microstepping(int microsteps)
{
    switch microsteps
    {
        case 1:
        {

        }
        case 2:
        {
            
        }
        case 4:
        {

        }
        case 8:
        {

        }
        case 16:
        {

        }
    }
}



                
            

