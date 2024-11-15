class TriggerMode:
    SOFTWARE = 'Software Trigger'
    HARDWARE = 'Hardware Trigger'
    CONTINUOUS = 'Continuous Acqusition'
    def __init__(self):
        pass

class MicroscopeMode:
    BFDF = 'BF/DF'
    FLUORESCENCE = 'Fluorescence'
    FLUORESCENCE_PREVIEW = 'Fluorescence Preview'
    def __init__(self):
        pass

class WaitTime:
    BASE = 0.1
    X = 0.4*2.54     # per mm
    Y = 0.4*2.54	 # per mm
    Z = 0.2     # per mm
    def __init__(self):
        pass

class AF:
    STOP_THRESHOLD = 0.85
    CROP_WIDTH = 800
    CROP_HEIGHT = 800
    def __init__(self):
        pass

class Motion:
    STEPS_PER_MM_XY = 1600 # microsteps
    STEPS_PER_MM_Z = 5333  # microsteps
    def __init__(self):
        pass
'''
# for octopi-malaria
class Motion:
    STEPS_PER_MM_XY = 40
    STEPS_PER_MM_Z = 5333
    def __init__(self):
        pass
'''

class Acquisition:
    CROP_WIDTH = 2048
    CROP_HEIGHT = 2048
    NUMBER_OF_FOVS_PER_AF = 3
    IMAGE_FORMAT = '.tif'
    IMAGE_DISPLAY_SCALING_FACTOR = 0.25
    DX = 1
    DY = 1
    DZ = 3

    def __init__(self):
        pass

class PosUpdate:
    INTERVAL_MS = 25

class MicrocontrollerDef:
    CMD_LENGTH = 4
    TIMER_PERIOD_ms = 10
    TIMEPOINT_PER_UPDATE = 25
    LOGGING_UNDERSAMPLING = 1
    DATA_INTERVAL_ms = LOGGING_UNDERSAMPLING*TIMER_PERIOD_ms*TIMEPOINT_PER_UPDATE
    RECORD_LENGTH_BYTE = 8
    MSG_LENGTH = TIMEPOINT_PER_UPDATE*RECORD_LENGTH_BYTE
    NAME = 'Teensy-LC'
    DESC = 'USB'

class CMD_SET:
    MOVE_X = 0
    MOVE_Y = 1
    MOVE_Z = 2
    TURN_ON_ILLUMINATION = 5
    TURN_OFF_ILLUMINATION = 6
    SET_ILLUMINATION = 7
    SET_SPEED = 8
    SET_MICROSTEPS = 9

class ILLUMINATION_CODE:
    ILLUMINATION_SOURCE_LED_ARRAY_FULL = 0;
    ILLUMINATION_SOURCE_LED_ARRAY_LEFT_HALF = 1
    ILLUMINATION_SOURCE_LED_ARRAY_RIGHT_HALF = 2
    ILLUMINATION_SOURCE_LED_ARRAY_LEFTB_RIGHTR = 3
    ILLUMINATION_SOURCE_LED_EXTERNAL_FET = 5
    ILLUMINATION_SOURCE_405NM = 11
    ILLUMINATION_SOURCE_488NM = 12
    ILLUMINATION_SOURCE_638NM = 13

class CAMERA:
    ROI_OFFSET_X_DEFAULT = 0
    ROI_OFFSET_Y_DEFAULT = 0
    ROI_WIDTH_DEFAULT = 3000
    ROI_HEIGHT_DEFAULT = 3000

class VOLUMETRIC_IMAGING:
    NUM_PLANES_PER_VOLUME = 20

# class MCU:
#     CMD_LENGTH = 4
#     N_BYTES_DATA = 2
#     TIMER_PERIOD_ms = 5
#     TIMEPOINT_PER_UPDATE = 25
#     DATA_INTERVAL_ms = TIMER_PERIOD_ms*TIMEPOINT_PER_UPDATE
#     RECORD_LENGTH_BYTE = 20
#     MSG_LENGTH = TIMEPOINT_PER_UPDATE*RECORD_LENGTH_BYTE

class WAVEFORMS:

    DISPLAY_RANGE_S = 10
    CYCLE_GAP = 10
    UPDATE_INTERVAL_MS = 100

    DISPLAY_UNDERSAMPLING = 1 # No:of MCU cycles after which we update the displays

SIMULATION = False    

NUMBER_OF_CHANNELS = 1
NUMBER_OF_CHANNELS_DISPLAY = 1
IS_TEMPERATURE_MEASUREMENT = False