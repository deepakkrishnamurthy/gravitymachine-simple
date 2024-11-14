#include <Wire.h>
#include <AccelStepper.h>


/***************************************************************************************************/
/********************************************* Parameters ******************************************/
/***************************************************************************************************/
// data logging
// # define LOGGING_UNDERSAMPLING  1
volatile int counter_log_data = 0;
int cmd_id;


static const int SET_SPEED = 8;
static const int SET_MICROSTEPS = 9;

static const int TIMER_PERIOD_us = 10000; // in us
static const int LOGGING_UNDERSAMPLING = 1;
static const int interval_send_data = LOGGING_UNDERSAMPLING*TIMER_PERIOD_us; // in us

static const int RECORD_LENGTH_BYTE = 8;  // No:of bytes per sensor read
static const int MSG_LENGTH = 25*RECORD_LENGTH_BYTE; // MSG_LENGTH is length of data sent

static const int CMD_LENGTH = 4;  // Length of data received
byte buffer_rx[500];
byte buffer_tx[MSG_LENGTH];
volatile int buffer_rx_ptr;
volatile int buffer_tx_ptr;

volatile bool flag_log_data = false;
volatile bool flag_read_sensor = false;




// other variables
uint16_t tmp_uint16;
int16_t tmp_int16;
long tmp_long;
volatile uint32_t timestamp = 0; // in number of TIMER_PERIOD_us
/***************************************************************************************************/
/********************************************* Stepper motor control *********************************************/
/***************************************************************************************************/
// driver 1 actuator 1
static const int Theta_dir = 4;
static const int Theta_step = 5;
static const int Theta_en = 3;

#define MS1 6
#define MS2 7
#define SPREAD 8

int Theta_N_microsteps = 8;




bool THETA_DIR = 1;
int THETA_SPEED = 5000;
constexpr int THETA_SPEED_MAX = 10000;



AccelStepper stepper_Theta = AccelStepper(AccelStepper::DRIVER, Theta_step, Theta_dir);



/***************************************************************************************************/
/********************************************* Encoder *********************************************/
/***************************************************************************************************/
// Encoders
static const int Theta_encoder_A = 14;
static const int Theta_encoder_B = 15;

volatile int32_t Theta_pos = 0;

volatile uint32_t Theta_pos_prev=0, Theta_pos_curr = 0;

volatile int32_t Theta_speed_measured = 0;

bool Theta_use_encoder = true;
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

  // // Initialize Native USB port
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

  pinMode(Theta_en, OUTPUT);

  digitalWrite(Theta_en, HIGH);


  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(SPREAD, OUTPUT);

  // digitalWrite(MS1, LOW);
  // digitalWrite(MS2, LOW);
  // digitalWrite(SPREAD, HIGH);

  set_microstepping(8);

  stepper_Theta.setPinsInverted(false, false, true);
  stepper_Theta.setMaxSpeed(10000);
  stepper_Theta.setAcceleration(1000);
  stepper_Theta.enableOutputs();

  
  
// Encoders

  pinMode(Theta_encoder_A, INPUT_PULLUP);
  pinMode(Theta_encoder_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(Theta_encoder_A), ISR_Theta_encoder_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(Theta_encoder_B), ISR_Theta_encoder_B, CHANGE);
  Theta_pos = 0;

  digitalWrite(Theta_en, LOW);
    
  myTimer.begin(timer_interruptHandler, TIMER_PERIOD_us);

  stepper_Theta.setSpeed(THETA_DIR*THETA_SPEED);


}

/***************************************************************************************************/
/******************************** timer interrupt handling routine *********************************/
/***************************************************************************************************/
void timer_interruptHandler()
{ 
  timestamp = timestamp + 1;


  // Theta_speed_measured = 1000*(Theta_pos - Theta_pos_prev)/TIMER_PERIOD_us;

  Theta_speed_measured = Theta_speed_measured + 20;


  Theta_pos_prev = Theta_pos;


  // send data to host computer
  counter_log_data = counter_log_data + 1;
  if (counter_log_data >= interval_send_data/TIMER_PERIOD_us)
  {
    counter_log_data = 0;
    flag_log_data = true;
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
    if (microsteps == 8)
    {
        digitalWrite(MS1, LOW);
        digitalWrite(MS2, LOW);
        digitalWrite(SPREAD, HIGH);

    }
    else if (microsteps == 16)
    {

        digitalWrite(MS1, HIGH);
        digitalWrite(MS2, HIGH);
        digitalWrite(SPREAD, HIGH);
    }
    else if (microsteps == 32)
    {
        digitalWrite(MS1, HIGH);
        digitalWrite(MS2, LOW);
        digitalWrite(SPREAD, HIGH);

    }
    else if (microsteps == 64)
    {
        digitalWrite(MS1, LOW);
        digitalWrite(MS2, HIGH);
        digitalWrite(SPREAD, HIGH);
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

    // testing
    // if (abs(Theta_pos) > 1000)
    // {
    //   Theta_pos = 0;
    //   // THETA_DIR = -THETA_DIR;
    //   THETA_SPEED = -THETA_SPEED;
    //   stepper_Theta.setSpeed(-THETA_SPEED);
    //   blinkLED();
    // }

    // stepper_Theta.move(1000);

    while (SerialUSB.available())
    {
        buffer_rx[buffer_rx_ptr] = SerialUSB.read();
        buffer_rx_ptr = buffer_rx_ptr + 1;

        if (buffer_rx_ptr == CMD_LENGTH) 
        {
            buffer_rx_ptr = 0;
            cmd_id = int(buffer_rx[0]);

            if (cmd_id == SET_SPEED)
            { 
                blinkLED();

                THETA_DIR = (2*buffer_rx[1] - 1);
                THETA_SPEED = THETA_DIR*(uint16_t(buffer_rx[3])*256+uint16_t(buffer_rx[4]));

                if (abs(THETA_SPEED) > THETA_SPEED_MAX)
                {
                  THETA_SPEED = THETA_DIR*THETA_SPEED_MAX;
                }
                stepper_Theta.setSpeed(THETA_SPEED);

            }
            else if (cmd_id == SET_MICROSTEPS)
            {
                blinkLED();
                Theta_N_microsteps = int(buffer_rx[1]);
                set_microstepping(Theta_N_microsteps);

            }


          }
      }

    

      // stepper_Theta.run();

      //   // send position update to computer
      if(flag_log_data)
      {
        flag_log_data = false;
        // field 1: time
          buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 24);
          buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 16);
          buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 8);
          buffer_tx[buffer_tx_ptr++] = byte(timestamp %256);

          // field 2 Stepper speed (measured)
          buffer_tx[buffer_tx_ptr++] = byte(Theta_speed_measured >> 24);
          buffer_tx[buffer_tx_ptr++] = byte(Theta_speed_measured >> 16);
          buffer_tx[buffer_tx_ptr++] = byte(Theta_speed_measured >> 8);
          buffer_tx[buffer_tx_ptr++] = byte(Theta_speed_measured %256);

          // field 3, ch2
          // ch2 = 0;
          // buffer_tx[buffer_tx_ptr++] = byte(ch2 >> 8);
          // buffer_tx[buffer_tx_ptr++] = byte(ch2 % 256);
          if (buffer_tx_ptr == MSG_LENGTH)
          {
              buffer_tx_ptr = 0;
              SerialUSB.write(buffer_tx, MSG_LENGTH);
              blinkLED();

          }

        
      }

      stepper_Theta.runSpeed();

            
}





                
            

