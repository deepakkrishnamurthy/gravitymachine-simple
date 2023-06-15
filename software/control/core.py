# set QT_API environment variable
import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

import control.utils.byte_operations as utils
from control._def import *

from queue import Queue
import time
import numpy as np
import pyqtgraph as pg
from datetime import datetime
from pathlib import Path
import control.utils.CSV_Tool as CSV_Tool

class Waveforms(QObject):

    signal_plot1 = Signal(np.ndarray,np.ndarray)
    signal_plot2 = Signal(np.ndarray,np.ndarray)
    signal_plot3 = Signal(np.ndarray,np.ndarray)

    signal_readings = Signal(np.ndarray)
    signal_plots = Signal(np.ndarray,np.ndarray)

    def __init__(self,microcontroller):
        QObject.__init__(self)
        self.file = open(str(Path.home()) + "/Downloads/" + datetime.now().strftime('%Y-%m-%d %H-%M-%-S.%f') + ".csv", "w+")

        # self.csv_register = CSV_Tool.CSV_Register(header = [SAVE_DATA])


        self.microcontroller = microcontroller

        self.time = 0
        self.time_array = np.array([])

        self.ch = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.ch[str(i)] = 0

        self.pressure = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.pressure[str(i)] = 0

        self.ch_array = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.ch_array[str(i)] = np.array([])

        self.pressure_array = {}
        for i in range(NUMBER_OF_CHANNELS):
            self.pressure_array[str(i)] = np.array([])

        self.timer_update_waveform = QTimer()
        self.timer_update_waveform.setInterval(MCU.DATA_INTERVAL_ms/2)
        self.timer_update_waveform.timeout.connect(self.update_waveforms)
        self.timer_update_waveform.start()

        self.first_run = True
        self.time_ticks_start = 0

        self.time_now = 0
        self.time_diff = 0
        self.time_prev = time.time()

        self.counter_display = 0
        self.counter_file_flush = 0

        self.logging_is_on = True

    def logging_onoff(self,state,experimentID):

        self.logging_is_on = state
        if state == False:
            self.file.close()
        else:
            self.experimentID = experimentID
            self.file = open(str(Path.home()) + "/Downloads/" + self.experimentID + '_' + datetime.now().strftime('%Y-%m-%d %H-%M-%-S.%f') + ".csv", "w+")
            self.file.write(str(SAVE_DATA) +'\n')

    def update_waveforms(self):

        readout = self.microcontroller.read_received_packet_nowait()
        if readout is not None:

            self.time_now = time.time()

            # chunck of measurements, n = TIMEPOINT_PER_UPDATE
            t_chunck = np.array([])
            ch_chunck = {}
            for k in range(NUMBER_OF_CHANNELS):
                ch_chunck[str(k)] = np.array([])
            pressure_chunck = {}
            for k in range(NUMBER_OF_CHANNELS):
                pressure_chunck[str(k)] = np.array([])

            for i in range(MCU.TIMEPOINT_PER_UPDATE):
                # time
                self.time_ticks = int.from_bytes(readout[i*MCU.RECORD_LENGTH_BYTE:i*MCU.RECORD_LENGTH_BYTE+4], byteorder='big', signed=False)
                if self.first_run:
                    self.time_ticks_start = self.time_ticks
                    self.first_run = False
                self.time = (self.time_ticks - self.time_ticks_start)*MCU.TIMER_PERIOD_ms/1000

                # channel readings
                for k in range(NUMBER_OF_CHANNELS):
                    self.ch[str(k)] = utils.unsigned_to_unsigned(readout[i*MCU.RECORD_LENGTH_BYTE+4+k*2:i*MCU.RECORD_LENGTH_BYTE+6+k*2],2)
                    ch_chunck[str(k)] = np.append(ch_chunck[str(k)],self.ch[str(k)])


                if IS_PRESSURE_MEASUREMENT:
                    # Convert the pressure to real units
                    for k in range(NUMBER_OF_CHANNELS-1):


                        self.pressure[str(k)] = PressureSensorDef.raw_reading_to_pressure (self.ch[str(k)])

                        print(k, '\t', self.ch[str(k)])

                        pressure_chunck[str(k)] = np.append(pressure_chunck[str(k)],self.pressure[str(k)])

            

                # line to write
                record_from_MCU = str(self.time_ticks) + ','
                for k in range(NUMBER_OF_CHANNELS):
                    record_from_MCU = record_from_MCU + str(self.ch[str(k)]) + ','
                for k in range(NUMBER_OF_CHANNELS-1):
                    record_from_MCU = record_from_MCU + str(self.pressure[str(k)]) + ','
                record_settings = (str(self.time_now))
               
                # saved variables
                if self.logging_is_on:
                    self.file.write(record_from_MCU + record_settings + '\n')

                # append variables for plotting
                t_chunck = np.append(t_chunck,self.time)

            self.time_array = np.append(self.time_array,t_chunck)
            for k in range(NUMBER_OF_CHANNELS):
                self.ch_array[str(k)] = np.append(self.ch_array[str(k)],ch_chunck[str(k)])
            for k in range(NUMBER_OF_CHANNELS-1):
                self.pressure_array[str(k)] = np.append(self.pressure_array[str(k)],pressure_chunck[str(k)])

            # emit signals with reduced display refresh rate
            self.counter_display = self.counter_display + 1
            if self.counter_display>=1:
                self.counter_display = 0
                # emit plots
                if IS_PRESSURE_MEASUREMENT:
                    plot_arrays = self.pressure_array[str(0)]
                    for k in range(1,NUMBER_OF_CHANNELS_DISPLAY):
                        
                        print(len(self.pressure_array[str(k)]))

                        plot_arrays = np.vstack((plot_arrays,self.pressure_array[str(k)]))
                    self.signal_plots.emit(self.time_array,plot_arrays)
                    # emit readings
                    readings_to_display = np.array([])
                    for k in range(NUMBER_OF_CHANNELS_DISPLAY):
                        readings_to_display = np.append(readings_to_display,self.pressure[str(k)])
                    self.signal_readings.emit(readings_to_display)
                else:
                    plot_arrays = self.ch_array[str(0)]
                    for k in range(1,NUMBER_OF_CHANNELS_DISPLAY):
                        plot_arrays = np.vstack((plot_arrays,self.ch_array[str(k)]))
                    self.signal_plots.emit(self.time_array,plot_arrays)
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