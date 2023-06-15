class MCU:
    CMD_LENGTH = 4
    N_BYTES_DATA = 2
    TIMER_PERIOD_ms = 5
    TIMEPOINT_PER_UPDATE = 25
    DATA_INTERVAL_ms = TIMER_PERIOD_ms*TIMEPOINT_PER_UPDATE
    RECORD_LENGTH_BYTE = 8
    MSG_LENGTH = TIMEPOINT_PER_UPDATE*RECORD_LENGTH_BYTE

class PressureSensorDef:


	PRESSURE_MIN = -160 # P_min in mbars
	PRESSURE_MAX = 160 # P_min in mbars

	PRESSURE_UNITS = 'mBars' 

	PRESSURE_DEFAULT = 0.0


	BIT_DEPTH = 14

	OUTPUT_MIN = 0.1*(2**BIT_DEPTH - 1)
	OUTPUT_MAX = 0.9*(2**BIT_DEPTH - 1)

	def __init__(self):
		pass

	def raw_reading_to_pressure(raw):


		return 1.0 * (raw - PressureSensorDef.OUTPUT_MIN) * (PressureSensorDef.PRESSURE_MAX - PressureSensorDef.PRESSURE_MIN) / (PressureSensorDef.OUTPUT_MAX - PressureSensorDef.OUTPUT_MIN) + PressureSensorDef.PRESSURE_MIN;



SIMULATION = False    

NUMBER_OF_CHANNELS = 2
NUMBER_OF_CHANNELS_DISPLAY = 2
IS_TEMPERATURE_MEASUREMENT = False

SAVE_DATA = ['Time (s)', 'Pressure (ch1)', 'Pressure (ch2)']