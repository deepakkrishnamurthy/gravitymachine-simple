# set QT_API environment variable
import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

import control.utils as utils
from control._def import *

from queue import Queue
from collections import deque
import time
import numpy as np
import pyqtgraph as pg
from datetime import datetime
from pathlib import Path

class Waveforms(QObject):

    signal_plot1 = Signal(np.ndarray,np.ndarray)
    signal_plot2 = Signal(np.ndarray,np.ndarray)
    signal_plot3 = Signal(np.ndarray,np.ndarray)

    signal_readings = Signal(np.ndarray)
    signal_plots = Signal(np.ndarray,np.ndarray)

    def __init__(self,microcontroller):
        QObject.__init__(self)
        self.file = open(str(Path.home()) + "/Downloads/" + datetime.now().strftime('%Y-%m-%d %H-%M-%-S.%f') + ".csv", "w+")
        # self.file.write('Time (s),Paw (cmH2O),Flow (l/min),Volume (ml),Vt (ml),Ti (s),RR (/min),PEEP (cmH2O)\n')
        self.microcontroller = microcontroller

        self.maxLen = 2*MicrocontrollerDef.TIMEPOINT_PER_UPDATE*WAVEFORMS.DISPLAY_UNDERSAMPLING  # Max length of data we want to store in the Rec buffer

        # self.maxLen = 200

        self.time = 0
        self.time_array = deque(maxlen=self.maxLen)

        self.ch = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.ch[str(i)] = 0

        # Stores a chunk of data from several consecutive measurements
        self.ch_array = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.ch_array[str(i)] = deque(maxlen=self.maxLen)

        # Stores a chunk of data from several consecutive measurements

        self.timer_update_waveform = QTimer()
        self.timer_update_waveform.setInterval(MicrocontrollerDef.DATA_INTERVAL_ms)
        self.timer_update_waveform.timeout.connect(self.update_waveforms)
        self.timer_update_waveform.start()

        self.first_run = True
        self.time_ticks_start = 0

        self.time_now = 0
        self.time_diff = 0
        self.time_prev = time.time()

        self.counter_display = 0
        self.counter_file_flush = 0

        self.logging_is_on = False

    def logging_onoff(self,state,experimentID):

        self.logging_is_on = state
        if state == False:
            self.file.close()
        else:
            self.experimentID = experimentID
            self.file = open(str(Path.home()) + "/Downloads/" + self.experimentID + '_' + datetime.now().strftime('%Y-%m-%d %H-%M-%-S.%f') + ".csv", "w+")

    def update_waveforms(self):

        readout = self.microcontroller.read_received_packet_nowait()

        print('updating data log from MCU')
        if readout is not None:

            print('data received')

            self.time_now = time.time()

            # chunck of measurements, n = TIMEPOINT_PER_UPDATE
            t_chunck = np.array([])
            ch_chunck = {}
            for k in range(NUMBER_OF_CHANNELS):
                ch_chunck[str(k)] = np.array([])
        

            for i in range(MicrocontrollerDef.TIMEPOINT_PER_UPDATE):
                # time
                self.time_ticks = int.from_bytes(readout[i*MicrocontrollerDef.RECORD_LENGTH_BYTE:i*MicrocontrollerDef.RECORD_LENGTH_BYTE+4], byteorder='big', signed=False)
                if self.first_run:
                    self.time_ticks_start = self.time_ticks
                    self.first_run = False
                self.time = (self.time_ticks - self.time_ticks_start)*MicrocontrollerDef.TIMER_PERIOD_ms/1000

                # channel readings
                for k in range(NUMBER_OF_CHANNELS):
                    self.ch[str(k)] = utils.unsigned_to_unsigned(readout[i*MicrocontrollerDef.RECORD_LENGTH_BYTE+4+k*2:i*MicrocontrollerDef.RECORD_LENGTH_BYTE+8+k*2],4)
                    ch_chunck[str(k)] = np.append(ch_chunck[str(k)],self.ch[str(k)])

             
                # line to write
                record_from_MCU = str(self.time_ticks) + ','
                for k in range(NUMBER_OF_CHANNELS):
                    record_from_MCU = record_from_MCU + str(self.ch[str(k)]) + ','
                record_settings = (str(self.time_now))
               
                # saved variables
                if self.logging_is_on:
                    self.file.write(record_from_MCU + '\n')

                # append variables for plotting
                t_chunck = np.append(t_chunck,self.time)

            self.time_array.append([t_chunck])

            for k in range(NUMBER_OF_CHANNELS):
                self.ch_array[str(k)].append([ch_chunck[str(k)]])
             # Send the data to the display and plotting widgets (at a reduced rate if needed)

            # emit signals with reduced display refresh rate
            self.counter_display = self.counter_display + 1
            if self.counter_display >= WAVEFORMS.DISPLAY_UNDERSAMPLING:

                self.counter_display = 0
                # emit plots
                plot_arrays = ch_chunck[str(0)]

                for k in range(1,NUMBER_OF_CHANNELS_DISPLAY):

                    plot_arrays = np.vstack((plot_arrays, ch_chunck[str(k)]))


                self.signal_plots.emit(t_chunck, plot_arrays)

                # emit readings
                readings_to_display = np.array([])
                for k in range(NUMBER_OF_CHANNELS_DISPLAY):
                    readings_to_display = np.append(readings_to_display,self.ch[str(k)])
                self.signal_readings.emit(readings_to_display)

        # file flushing
        if self.logging_is_on:
            self.counter_file_flush = self.counter_file_flush + 1
            if self.counter_file_flush>=500:
                self.counter_file_flush = 0
                self.file.flush()

    def close(self):
        self.file.close()