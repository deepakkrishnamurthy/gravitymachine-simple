#include <AccelStepper.h>

static const uint8_t X_driver_ADDRESS = 0b00;
static const float R_SENSE = 0.11f;



static const int X_dir = 4;
static const int X_step = 5;
static const int X_en = 3;

static const int X_N_microstepping = 1;
static const long steps_per_mm_X = 100*X_N_microstepping; 

AccelStepper stepper_X = AccelStepper(AccelStepper::DRIVER, X_step, X_dir);

#define ButtonUp 9
#define ButtonDown 10

#define MS1 6
#define MS2 7
#define SPREAD 8



int up;
int down;


void setup() 
{
  // put your setup code here, to run once:

  pinMode(13, OUTPUT);
  digitalWrite(13,LOW);
    
  pinMode(X_dir, OUTPUT);
  pinMode(X_step, OUTPUT);

  pinMode(X_en, OUTPUT);
  digitalWrite(X_en, HIGH);

  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(SPREAD, OUTPUT);

  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(SPREAD, HIGH);

  // Stepper configuration
  stepper_X.setPinsInverted(false, false, true);
  stepper_X.setMaxSpeed(10000);
  stepper_X.setAcceleration(1000);
  stepper_X.enableOutputs();

  pinMode(ButtonUp, INPUT_PULLUP);
  pinMode(ButtonDown, INPUT_PULLUP);

  digitalWrite(X_en, LOW);
}
void loop() {
  // put your main code here, to run repeatedly:
  //
        //  up=digitalRead(ButtonUp);
        //  down=digitalRead(ButtonDown);

           up = HIGH;
           down =LOW;
            digitalWrite(13, HIGH);
            if(down&!up)             // The motor goes up
            {
              stepper_X.move(1000);
              // digitalWrite(13,HIGH);
            // digitalWrite(13, HIGH);delay(100);digitalWrite(13, LOW);delay(100);
            }
            else if(up&!down)                      // The motor goes down
            {
              stepper_X.move(-1000);
              // digitalWrite(13,HIGH);
            //  digitalWrite(13, HIGH);delay(1000);digitalWrite(13, LOW);delay(1000);
            }
            else
            {
              stepper_X.move(0);
              digitalWrite(13,LOW);
              digitalWrite(13, HIGH);
            }
            stepper_X.run();

            digitalWrite(13,LOW);
  //digitalWrite(13, HIGH);delay(500);digitalWrite(13, LOW);delay(500);
}