#include <Wire.h>
#include "hsc_ssc_i2c.h"


/***************************************************************************************************/
/********************************************* Parameters ******************************************/
/***************************************************************************************************/
static const float TIMER_PERIOD_us = 50000; // in us
static const bool USE_SERIAL_MONITOR = false; // for debug

static const int RECORD_LENGTH_BYTE = 4+2+2;  // No:of bytes per sensor read
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
/********************************************* Timer *********************************************/
/***************************************************************************************************/
IntervalTimer myTimer;

/***************************************************************************************************/
/********************************************* sensors *********************************************/
/***************************************************************************************************/
// see hsc_ssc_i2c.h for a description of these values
// HSCDRRN160MD2A5 Chip 
#define SLAVE_ADDR 0x28
#define OUTPUT_MIN 0x666        // 10%
#define OUTPUT_MAX 0x3332       // 80% of 2^14 - 1 in Hex
#define PRESSURE_MIN -160        // mbars
#define PRESSURE_MAX 160   // mbars

uint8_t cmd[1];

uint16_t ch1;
uint16_t ch2;
// uint16_t ch3;
// uint16_t ch4;
// uint16_t ch5;
// uint16_t ch6;
// uint16_t ch7;
// uint16_t ch8;

/***************************************************************************************************/
/******************************************* setup *************************************************/
/***************************************************************************************************/
void setup() 
{

  // Initialize Native USB port
  SerialUSB.begin(2000000);
  while (!SerialUSB);           // Wait until connection is established
  buffer_rx_ptr = 0;

  analogReadResolution(12);
  delayMicroseconds(500000);

  // start the timer
  // Timer3.attachInterrupt(timer_interruptHandler);
  // Timer3.start(TIMER_PERIOD_us);

  myTimer.begin(timer_interruptHandler, TIMER_PERIOD_us)

}

/***************************************************************************************************/
/******************************** timer interrupt handling routine *********************************/
/***************************************************************************************************/
void timer_interruptHandler()
{
  timestamp = timestamp + 1;

  // read sensor value
  flag_read_sensor = true;
  
  // send data to host computer
  counter_log_data = counter_log_data + 1;
  if (counter_log_data >= LOGGING_UNDERSAMPLING)
  {
    counter_log_data = 0;
    flag_log_data = true;
  }
}

/***************************************************************************************************/
/********************************************  main loop *******************************************/
/***************************************************************************************************/
void loop()
{

  if (flag_read_sensor)
  {
    // Read the sensor

    // ch1 = analogRead(A0);
    // ch2 = analogRead(A1);
    // ch3 = analogRead(A2);
    // ch4 = analogRead(A3);
    // ch5 = analogRead(A4);
    // ch6 = analogRead(A5);
    // ch7 = analogRead(A6);
    // ch8 = analogRead(A7);

    unsigned long now = millis();
    struct cs_raw ps;
    char p_str[10], t_str[10];
    uint8_t el;
    float p, t;

    el = ps_get_raw(SLAVE_ADDR, &ps);

    flag_read_sensor = false;
  }

  if (flag_log_data)
  {
    flag_log_data = false;
    
    // field 1: time
    buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 24);
    buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 16);
    buffer_tx[buffer_tx_ptr++] = byte(timestamp >> 8);
    buffer_tx[buffer_tx_ptr++] = byte(timestamp %256);

    // field 2 ch1
    buffer_tx[buffer_tx_ptr++] = byte(ps.bridge_data >> 8);
    buffer_tx[buffer_tx_ptr++] = byte(ps.bridge_data % 256);

    // field 3, ch2
    ch2 = 0;
    buffer_tx[buffer_tx_ptr++] = byte(ps.bridge_data >> 8);
    buffer_tx[buffer_tx_ptr++] = byte(ps.bridge_data % 256);

    if (buffer_tx_ptr == MSG_LENGTH)
    {
      buffer_tx_ptr = 0;
      if(USE_SERIAL_MONITOR)
      {
        // In testing mode send the data to Serial port
          if ( el == 4 ) 
          {
                Serial.println("error sensor missing");
          } 
          else 
          {
            if ( el == 3 ) 
            {
                Serial.print("err diagnostic fault ");
                Serial.println(ps.status, BIN);
            }
            if ( el == 2 ) 
            {
                // if data has already been feched since the last
                // measurement cycle
                Serial.print("warn stale data ");
                Serial.println(ps.status, BIN);
            }
            if ( el == 1 ) 
            {
                // chip in command mode
                // no clue how to end up here
                Serial.print("warn command mode ");
                Serial.println(ps.status, BIN);
            }

            Serial.print("status      ");
            Serial.println(ps.status, BIN);
            Serial.print("bridge_data ");
            Serial.println(ps.bridge_data, DEC);
            Serial.print("temp_data   ");
            Serial.println(ps.temperature_data, DEC);
            Serial.println("");

            ps_convert(ps, &p, &t, OUTPUT_MIN, OUTPUT_MAX, PRESSURE_MIN,
            PRESSURE_MAX);
            // floats cannot be easily printed out
            dtostrf(p, 2, 2, p_str);
            dtostrf(t, 2, 2, t_str);
            Serial.print("pressure    (mbar) ");
            Serial.println(p_str);
            Serial.print("temperature (dC) ");
            Serial.println(t_str);
            Serial.println("");
      }
      else
        SerialUSB.write(buffer_tx, MSG_LENGTH);
    }
  }
}
