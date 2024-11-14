import platform
import serial
import serial.tools.list_ports
import time
import numpy as np

from control._def import *

# add user to the dialout group to avoid the need to use sudo

class Microcontroller():
    def __init__(self,parent=None):
        self.serial = None
        self.platform_name = platform.system()
        self.tx_buffer_length = MicrocontrollerDef.CMD_LENGTH
        self.rx_buffer_length = MicrocontrollerDef.MSG_LENGTH

        # AUTO-DETECT the uController! By Deepak
        ucontroller_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if MicrocontrollerDef.DESC in p.description]
        if not ucontroller_ports:
            raise IOError("No {} found".format(MicrocontrollerDef.NAME))
        if len(ucontroller_ports) > 1:
            print('Multiple uControllers found - using the first')
        else:
            print('Using uController found at : {}'.format(ucontroller_ports[0]))

        # establish serial communication
        self.serial = serial.Serial(ucontroller_ports[0],2000000)
        time.sleep(0.1)
        print('Serial Connection Open')

    def close(self):
        self.serial.close()

    def toggle_LED(self,state):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 3
        cmd[1] = state
        self.serial.write(cmd)
    
    def toggle_laser(self,state):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 4
        cmd[1] = state
        self.serial.write(cmd)

    def turn_on_illumination(self):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.TURN_ON_ILLUMINATION
        self.serial.write(cmd)

    def turn_off_illumination(self):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.TURN_OFF_ILLUMINATION
        self.serial.write(cmd)

    def set_illumination(self,illumination_source,intensity):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.SET_ILLUMINATION
        cmd[1] = illumination_source
        cmd[2] = int((intensity/100)*65535) >> 8
        cmd[3] = int((intensity/100)*65535) & 0xff
        self.serial.write(cmd)

    def move_x(self,delta):
        direction = int((np.sign(delta)+1)/2)
        n_microsteps = abs(delta*Motion.STEPS_PER_MM_XY)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_X
        cmd[1] = direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.X*abs(delta))

    def move_x_usteps(self,usteps):
        direction = int((np.sign(usteps)+1)/2)
        n_microsteps = abs(usteps)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_X
        cmd[1] = direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.X*abs(usteps)/Motion.STEPS_PER_MM_XY)

    def move_y(self,delta):
        direction = int((np.sign(delta)+1)/2)
        n_microsteps = abs(delta*Motion.STEPS_PER_MM_XY)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_Y
        cmd[1] = direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.Y*abs(delta))

    def move_y_usteps(self,usteps):
        direction = int((np.sign(usteps)+1)/2)
        n_microsteps = abs(usteps)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_Y
        cmd[1] = direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.Y*abs(usteps)/Motion.STEPS_PER_MM_XY)

    def move_z(self,delta):
        direction = int((np.sign(delta)+1)/2)
        n_microsteps = abs(delta*Motion.STEPS_PER_MM_Z)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_Z
        cmd[1] = 1-direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.Z*abs(delta))

    def move_z_usteps(self,usteps):
        direction = int((np.sign(usteps)+1)/2)
        n_microsteps = abs(usteps)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.MOVE_Z
        cmd[1] = 1-direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        time.sleep(WaitTime.BASE + WaitTime.Z*abs(usteps)/Motion.STEPS_PER_MM_Z)

    def set_stepper_speed(self, speed):

        direction = int((np.sign(speed)+1)/2)

        speed_abs = abs(speed)

        if speed_abs > 65535:
            speed_abs = 65535

        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.SET_SPEED
        cmd[1] = 1-direction
        cmd[2] = int(speed_abs) >> 8
        cmd[3] = int(speed_abs) & 0xff
        self.serial.write(cmd)

        print('Set stepper speed: {}'.format(speed))

    def set_microsteps(self, microsteps):

        if microsteps > 64:
            microsteps = 64
        elif microsteps < 8:
            microsteps = 8

        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = CMD_SET.SET_MICROSTEPS
        cmd[1] = microsteps
        cmd[2] = 0
        cmd[3] = 0
        self.serial.write(cmd)

        print('Set microstepping: {}'.format(microsteps))





    def send_command(self,command):
        cmd = bytearray(self.tx_buffer_length)
        self.serial.write(cmd)

    def read_received_packet(self):

        # wait to receive data
        while self.serial.in_waiting==0:
            pass
        while self.serial.in_waiting % self.rx_buffer_length != 0:
            pass

        num_bytes_in_rx_buffer = self.serial.in_waiting

        # get rid of old data
        if num_bytes_in_rx_buffer > self.rx_buffer_length:
            # print('getting rid of old data')
            for i in range(num_bytes_in_rx_buffer-self.rx_buffer_length):
                self.serial.read()
        
        # read the buffer
        data=[]
        for i in range(self.rx_buffer_length):
            data.append(ord(self.serial.read()))

        return data

    # def read_received_packet_nowait(self):
    #     # wait to receive data
    #     if self.serial.in_waiting==0:
    #         return None
    #     if self.serial.in_waiting % self.rx_buffer_length != 0:
    #         # self.serial.reset_input_buffer()
    #         num_bytes_in_rx_buffer = self.serial.in_waiting

    #         print(num_bytes_in_rx_buffer)
    #         for i in range(num_bytes_in_rx_buffer):
    #             self.serial.read()
    #         print('reset input buffer')
    #         return None
        
    #     # get rid of old data
    #     num_bytes_in_rx_buffer = self.serial.in_waiting
    #     if num_bytes_in_rx_buffer > self.rx_buffer_length:
    #         print('getting rid of old data')
    #         for i in range(num_bytes_in_rx_buffer-self.rx_buffer_length):
    #             self.serial.read()
        
    #     # read the buffer
    #     data=[]
    #     for i in range(self.rx_buffer_length):
    #         data.append(ord(self.serial.read()))
    #     return data

    def read_received_packet_nowait(self):
        # Wait to receive data
        if self.serial.in_waiting == 0:
            print('No data recvd')
            return None
        
        # Check if the available data is a multiple of the expected packet length
        if self.serial.in_waiting % self.rx_buffer_length != 0:
            print(f"Unexpected buffer length: {self.serial.in_waiting}")
            # Discard all data in the input buffer
            self.serial.reset_input_buffer()
            print("Input buffer reset")
            return None
        
        # If there is more data than needed, discard old data until the buffer matches rx_buffer_length
        num_bytes_in_rx_buffer = self.serial.in_waiting
        if num_bytes_in_rx_buffer > self.rx_buffer_length:
            print("Clearing excess data from buffer")
            # Read and discard extra bytes in one go
            self.serial.read(num_bytes_in_rx_buffer - self.rx_buffer_length)
        
        # Read exactly rx_buffer_length bytes from the buffer
        # data = self.serial.read(self.rx_buffer_length)
        # # Convert to list of integer values (if needed)
        # return [ord(byte) for byte in data]

        # read the buffer
        data=[]
        for i in range(self.rx_buffer_length):
            data.append(ord(self.serial.read()))
        return data



# class Microcontroller_Simulation():
#     def __init__(self,parent=None):
#         self.tx_buffer_length = MCU.CMD_LENGTH
#         self.rx_buffer_length = MCU.MSG_LENGTH
#         self.t = 0

#     def close(self):
#         pass

#     def read_received_packet(self):
#         pass

#     def read_received_packet_nowait(self):
#         data = bytearray(MCU.MSG_LENGTH)
#         ptr = 0
#         for k in range(MCU.TIMEPOINT_PER_UPDATE):
#             self.t = self.t + 1
#             data[ptr+0] = int(self.t >> 24)
#             data[ptr+1] = int((self.t >> 16) & 0xff)
#             data[ptr+2] = int((self.t >> 8) & 0xff)
#             data[ptr+3] = int(self.t & 0xff)
#             for i in range(NUMBER_OF_CHANNELS*2):
#                 data[ptr+4+i] = np.random.bytes(1)[0]
#             ptr = ptr + MCU.RECORD_LENGTH_BYTE
#         return data

class Microcontroller_Simulation():
    def __init__(self,parent=None):
        self.tx_buffer_length = MicrocontrollerDef.CMD_LENGTH
        self.rx_buffer_length = MicrocontrollerDef.MSG_LENGTH
        self.t = 0

    def close(self):
        pass

    def toggle_LED(self,state):
        pass
    
    def toggle_laser(self,state):
        pass

    def move_x(self,delta):
        pass

    def move_y(self,delta):
        pass

    def move_z(self,delta):
        pass

    def move_x_usteps(self,usteps):
        pass

    def move_y_usteps(self,usteps):
        pass

    def move_z_usteps(self,usteps):
        pass

    def set_stepper_speed(self, speed):
        print('Set stepper speed: {}'.format(speed))
        pass

    def set_microsteps(self, microsteps):
        print('Set stepper microsteps: {}'.format(microsteps))
        pass

    def send_command(self,command):
        pass

    def read_received_packet(self):
        pass

    def read_received_packet_nowait(self):
        data = bytearray(MicrocontrollerDef.MSG_LENGTH)
        ptr = 0
        for k in range(MicrocontrollerDef.TIMEPOINT_PER_UPDATE):
            self.t = self.t + 1
            data[ptr+0] = int(self.t >> 24)
            data[ptr+1] = int((self.t >> 16) & 0xff)
            data[ptr+2] = int((self.t >> 8) & 0xff)
            data[ptr+3] = int(self.t & 0xff)
            for i in range(NUMBER_OF_CHANNELS*2):
                data[ptr+4+i] = np.random.bytes(1)[0]
            ptr = ptr + MicrocontrollerDef.RECORD_LENGTH_BYTE
        return data

    def turn_on_illumination(self):
        pass

    def turn_off_illumination(self):
        pass

    def set_illumination(self,illumination_source,intensity):
        pass
