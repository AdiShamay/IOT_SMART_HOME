# emulator.py - AquaGuard Emulators Module

import os
import PyQt5
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')

import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from init import *
from agent import Mqtt_client

class MC(Mqtt_client):
    def __init__(self, emulator_instance):
        super().__init__()
        self.emulator_instance = emulator_instance

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        QMetaObject.invokeMethod(self.emulator_instance, "handle_incoming_command",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, topic), Q_ARG(str, m_decode))

class ConnectionDock(QDockWidget):
    def __init__(self, mc, name, topic_sub, topic_pub):
        QDockWidget.__init__(self)
        self.name = name
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        
        self.eConnectbtn = QPushButton("Enable Sensor Module")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        
        formLayout = QFormLayout()
        self.ValueDisplay = QLineEdit()
        self.ValueDisplay.setText('')
        
        formLayout.addRow("Connection", self.eConnectbtn)
        formLayout.addRow("Live Data", self.ValueDisplay)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle(f"Module: {self.name}")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.eConnectbtn.setText("Module Active")

    def on_button_connect_click(self):
        self.mc.set_broker(broker_ip)
        self.mc.set_port(int(broker_port))
        self.mc.set_clientName(f"AquaGuard_Emulator_{random.randrange(1,10000)}")
        self.mc.connect_to()
        self.mc.start_listening()
        
        if self.topic_sub:
            self.mc.subscribe_to(self.topic_sub)
            
        # The Temperature sensor must listen to the heater commands to know when to heat up
        if 'temp' in self.topic_sub:
            self.mc.subscribe_to(comm_topic + 'heater/sub')

    def update_state_display(self, text):
        self.ValueDisplay.setText(text)

class MainWindow(QMainWindow):
    def __init__(self, args):
        QMainWindow.__init__(self)
        self.name = args[1]
        self.emulator_type = args[2]
        self.update_rate = int(args[3])
        
        self.topic_sub = comm_topic + self.emulator_type + '/sub'
        self.topic_pub = comm_topic + self.emulator_type + '/pub'
        
        self.mc = MC(self)
        
        self.current_temp = 22.0
        self.target_temp = 22.0
        self.auto_min = 26.0
        self.auto_max = 30.0
        self.heating_mode = "OFF" 
        self.is_actively_heating = False
        
        self.light_mode = "MANUAL_OFF" 
        self.force_motion = False
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.create_data)
        self.timer.start(self.update_rate * 1000)

        self.setGeometry(100, 100, 340, 130)
        self.setWindowTitle(self.name)
        
        self.connectionDock = ConnectionDock(self.mc, self.name, self.topic_sub, self.topic_pub)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    @pyqtSlot(str, str)
    def handle_incoming_command(self, topic, message):
        if 'heater' in topic:
            if 'MANUAL:' in message:
                try:
                    self.target_temp = float(message.split(':')[1])
                    self.heating_mode = "MANUAL"
                except:
                    pass
            elif 'AUTO:' in message:
                try:
                    values = message.split(':')[1].split(',')
                    self.auto_min = float(values[0])
                    self.auto_max = float(values[1])
                    self.heating_mode = "AUTO"
                    self.is_actively_heating = False
                except:
                    pass
            elif message == 'OFF':
                self.heating_mode = "OFF"
                self.is_actively_heating = False
                
        elif 'light' in topic:
            if message in ["MANUAL_ON", "MANUAL_OFF", "AUTO"]:
                self.light_mode = message

        elif 'motion' in topic:
            if message == 'SIMULATE':
                self.force_motion = True

    def create_data(self):
        if not self.mc.connected:
            self.connectionDock.on_button_connect_click()
            
        current_data = ""
        
        if self.emulator_type == 'motion':
            motion_val = 1 if self.force_motion else 0
            self.force_motion = False 
            current_data = f"From: {self.name} Value: {motion_val}"
            self.connectionDock.update_state_display(f"Intrusion Sensor: {'DETECTED' if motion_val==1 else 'Clear'}")
            
        elif self.emulator_type == 'temp':
            if self.heating_mode == "MANUAL":
                if self.current_temp < self.target_temp:
                    self.current_temp += 0.5 
                else:
                    self.heating_mode = "OFF" 
            elif self.heating_mode == "AUTO":
                if self.current_temp <= self.auto_min:
                    self.is_actively_heating = True
                elif self.current_temp >= self.auto_max:
                    self.is_actively_heating = False
                    
                if self.is_actively_heating:
                    self.current_temp += 0.5
                elif self.current_temp > 22.0:
                    self.current_temp -= 0.1 
            else: 
                if self.current_temp > 22.0:
                    self.current_temp -= 0.2
                    
            current_data = f"From: {self.name} Value: {round(self.current_temp, 1)}"
            self.connectionDock.update_state_display(f"{round(self.current_temp, 1)}°C")
            
        elif self.emulator_type == 'heater':
            if self.heating_mode == "MANUAL":
                status = f"Heating ON (Target: {self.target_temp}°C)"
            elif self.heating_mode == "AUTO":
                status = f"Auto Mode (Min: {self.auto_min}°C, Max: {self.auto_max}°C)"
            else:
                status = "OFF"
            
            current_data = f"From: {self.name} State: {status}"
            self.connectionDock.update_state_display(status)
            
        elif self.emulator_type == 'light':
            ambient_lux = random.choice([800, 400, 250, 100])
            
            if self.light_mode == "MANUAL_ON":
                light_state = "ON"
            elif self.light_mode == "MANUAL_OFF":
                light_state = "OFF"
            else:
                light_state = "ON (Auto-Darkness)" if ambient_lux < 300 else "OFF (Auto-Daylight)"
                
            current_data = f"From: {self.name} Lux: {ambient_lux} | Light: {light_state}"
            self.connectionDock.update_state_display(f"Sensor: {ambient_lux}Lux | Output: {light_state}")

        if current_data:
            self.mc.publish_to(self.topic_pub, current_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    argv = sys.argv
    if len(argv) == 1:
        argv.append('WaterMotionSensor')
        argv.append('motion')
        argv.append('5')
        
    mainwin = MainWindow(argv)
    mainwin.show()
    sys.exit(app.exec_())