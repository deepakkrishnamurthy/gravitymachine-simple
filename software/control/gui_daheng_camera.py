# set QT_API environment variable
import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

# app specific libraries
import control.widgets as widgets
import control.camera as camera
import control.core as core
import control.microcontroller as microcontroller
from control._def import *

# Data logging
import control.core_data_logging as core_data_logging
import control.widgets_data_logging as widgets_data_logging

# Motion control
import control.widgets_motion_control as widgets_motion_control

class OctopiGUI(QMainWindow):

	# variables
	fps_software_trigger = 100

	def __init__(self, is_simulation = False, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# load objects
		if is_simulation is True:
			self.camera = camera.Camera_Simulation()

			# self.microcontroller = microcontroller.Microcontroller_Simulation()
			self.microcontroller = microcontroller.Microcontroller()
		else:
			self.camera = camera.Camera()
			self.microcontroller = microcontroller.Microcontroller_Simulation()


		
		# Camera related control
		self.configurationManager = core.ConfigurationManager()
		self.streamHandler = core.StreamHandler()
		self.liveController = core.LiveController(self.camera,self.microcontroller,self.configurationManager)
		self.imageSaver = core.ImageSaver(Acquisition.IMAGE_FORMAT)
		self.imageDisplay = core.ImageDisplay()

		# Data-logging related control
		self.waveforms = core_data_logging.Waveforms(self.microcontroller)

		# Stepper control
		self.stepper_control = core.StepperController(self.microcontroller)

		# load widgets
		self.waveformDisplay = widgets_data_logging.WaveformDisplay()
		self.controlPanel = widgets_data_logging.ControlPanel()

		# Stepper control widget
		self.stepperControlWidget = widgets_motion_control.StepperControlWidget(self.stepper_control)



		# open the camera
		# camera start streaming
		self.camera.open()
		self.camera.set_software_triggered_acquisition()
		self.camera.set_callback(self.streamHandler.on_new_frame)
		self.camera.enable_callback()

		# load widgets
		self.cameraSettingWidget = widgets.CameraSettingsWidget(self.camera,self.liveController)
		self.liveControlWidget = widgets.LiveControlWidget(self.streamHandler,self.liveController,self.configurationManager)
		self.recordingControlWidget = widgets.RecordingWidget(self.streamHandler,self.imageSaver)

		# layout widgets
		layout = QGridLayout() #layout = QStackedLayout()
		layout.addWidget(self.cameraSettingWidget,0,0)
		layout.addWidget(self.liveControlWidget,1,0)
		layout.addWidget(self.recordingControlWidget,4,0)

		layout.addWidget(self.waveformDisplay,0,1)
		layout.addWidget(self.controlPanel,1,1)

		layout.addWidget(self.stepperControlWidget, 2, 1)


		
		# transfer the layout to the central widget
		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)

		# load window
		self.imageDisplayWindow = core.ImageDisplayWindow()
		self.imageDisplayWindow.show()

		# make connections
		self.streamHandler.signal_new_frame_received.connect(self.liveController.on_new_frame)
		self.streamHandler.image_to_display.connect(self.imageDisplay.enqueue)
		self.streamHandler.packet_image_to_write.connect(self.imageSaver.enqueue)
		self.imageDisplay.image_to_display.connect(self.imageDisplayWindow.display_image) # may connect streamHandler directly to imageDisplayWindow
		self.liveControlWidget.signal_newExposureTime.connect(self.cameraSettingWidget.set_exposure_time)
		self.liveControlWidget.signal_newAnalogGain.connect(self.cameraSettingWidget.set_analog_gain)
		self.liveControlWidget.update_camera_settings()

		# data-logging connections
		self.controlPanel.signal_logging_onoff.connect(self.waveforms.logging_onoff)
		self.waveforms.signal_plots.connect(self.waveformDisplay.plot)
		self.waveforms.signal_readings.connect(self.controlPanel.display_readings)
		
		# motion control connections


	def closeEvent(self, event):
		event.accept()
		# self.softwareTriggerGenerator.stop() @@@ => 
		self.waveforms.close()
		self.liveController.stop_live()
		self.camera.close()
		self.imageSaver.close()
		self.imageDisplay.close()
		self.imageDisplayWindow.close()