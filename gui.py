# gui.py - AquaGuard Main GUI Application

import os
import PyQt5
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')

import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from init import *
from agent import Mqtt_client
import data_acq as da

class MC(Mqtt_client):
    def __init__(self):
        super().__init__()
        
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        
        if 'mainwin' not in globals() or mainwin is None:
            return

        if 'temp' in topic:
            try:
                temp_val = float(m_decode.split('Value: ')[1])
                if hasattr(mainwin, 'controlDock'):
                    mainwin.controlDock.process_incoming_temperature(temp_val)
            except:
                pass

        if 'motion' in topic and 'Value: 1' in m_decode:
            if hasattr(mainwin, 'controlDock') and mainwin.controlDock.is_locked():
                alert_msg = f"Security Alert: Intrusion detected in the pool area! [{m_decode}]"
                if hasattr(mainwin, 'statusDock'):
                    mainwin.statusDock.update_alarm_window(f"<font color='red'><b>{da.timestamp()}: {alert_msg}</b></font>")
                QMessageBox.critical(None, "Pool Security Emergency", alert_msg)
                return

        if hasattr(mainwin, 'statusDock'):
            mainwin.statusDock.update_alarm_window(f"{da.timestamp()}: [{topic}] {m_decode}")

class StatusDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.alarmBox = QTextEdit()
        self.alarmBox.setReadOnly(True)
        
        formLayout = QFormLayout()
        formLayout.addRow("System Logs & Alerts:", self.alarmBox)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("AquaGuard Status")

    def update_alarm_window(self, text):
        self.alarmBox.append(text)

class ControlDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        
        self.tempDisplay = QLineEdit()
        self.tempDisplay.setReadOnly(True)
        self.tempDisplay.setText("Waiting for data...")
        self.tempDisplay.setStyleSheet("font-weight: bold; color: blue; font-size: 14px;")

        # Security Section
        self.lockCheckBox = QCheckBox("Arm Pool Security (Alert on Motion)")
        self.lockCheckBox.setStyleSheet("color: darkred; font-weight: bold;")
        self.testMotionBtn = QPushButton("Simulate Intrusion (Test Alarm)")
        self.testMotionBtn.clicked.connect(self.on_test_motion)

        # Heating Section
        self.targetTempCombo = QComboBox()
        self.targetTempCombo.addItems(["26", "28", "30", "32", "34"])
        self.targetTempCombo.setCurrentIndex(2)

        self.heaterOneTimeBtn = QPushButton("Start One-Time Heating")
        self.heaterOneTimeBtn.clicked.connect(self.on_manual_heat)
        self.heaterOneTimeBtn.setStyleSheet("background-color: #ffcc80;")

        self.heaterAutoBtn = QPushButton("Enable Auto-Maintain Temp")
        self.heaterAutoBtn.clicked.connect(self.on_auto_heat)
        self.heaterAutoBtn.setStyleSheet("background-color: #a5d6a7;")

        self.heaterOffBtn = QPushButton("Turn OFF Heating")
        self.heaterOffBtn.clicked.connect(self.on_off_heat)
        self.heaterOffBtn.setStyleSheet("background-color: #ef9a9a;")

        # Lighting Section
        self.lightOnBtn = QPushButton("Turn ON")
        self.lightOnBtn.clicked.connect(lambda: self.on_light_control("MANUAL_ON"))
        
        self.lightOffBtn = QPushButton("Turn OFF")
        self.lightOffBtn.clicked.connect(lambda: self.on_light_control("MANUAL_OFF"))
        
        self.lightAutoBtn = QPushButton("Auto (Sensor Mode)")
        self.lightAutoBtn.clicked.connect(lambda: self.on_light_control("AUTO"))
        
        # Layouts
        formLayout = QFormLayout()
        formLayout.addRow("Current Pool Temperature:", self.tempDisplay)
        
        # Security Group
        secLayout = QHBoxLayout()
        secLayout.addWidget(self.lockCheckBox)
        secLayout.addWidget(self.testMotionBtn)
        formLayout.addRow("Security Controls:", secLayout)
        
        # Heating Group
        formLayout.addRow("1. Select Target Temperature:", self.targetTempCombo)
        heatLayout = QHBoxLayout()
        heatLayout.addWidget(self.heaterOneTimeBtn)
        heatLayout.addWidget(self.heaterAutoBtn)
        heatLayout.addWidget(self.heaterOffBtn)
        formLayout.addRow("2. Choose Heating Mode:", heatLayout)
        
        # Lighting Group
        lightLayout = QHBoxLayout()
        lightLayout.addWidget(self.lightOnBtn)
        lightLayout.addWidget(self.lightOffBtn)
        lightLayout.addWidget(self.lightAutoBtn)
        formLayout.addRow("Lighting Controls:", lightLayout)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("User Control Panel")

    def process_incoming_temperature(self, current_temp):
        self.tempDisplay.setText(str(current_temp) + " °C")

    def is_locked(self):
        return self.lockCheckBox.isChecked()

    def on_test_motion(self):
        self.mc.publish_to(comm_topic + 'motion/sub', 'SIMULATE')

    def on_manual_heat(self):
        target = self.targetTempCombo.currentText()
        self.mc.publish_to(comm_topic + 'heater/sub', f'MANUAL:{target}')

    def on_auto_heat(self):
        target = self.targetTempCombo.currentText()
        self.mc.publish_to(comm_topic + 'heater/sub', f'AUTO:{target}')

    def on_off_heat(self):
        self.mc.publish_to(comm_topic + 'heater/sub', 'OFF')

    def on_light_control(self, mode):
        self.mc.publish_to(comm_topic + 'light/sub', mode)

class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.connectBtn = QPushButton("Connect System to Cloud")
        self.connectBtn.clicked.connect(self.on_connect_click)
        self.connectBtn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        formLayout = QFormLayout()
        formLayout.addRow("", self.connectBtn)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("System Connection")

    def on_connect_click(self):
        self.mc.set_broker(broker_ip)
        self.mc.set_port(int(broker_port))
        self.mc.set_clientName(f"AquaGuard_GUI_{random.randrange(1, 10000)}")
        self.mc.connect_to()
        self.mc.start_listening()
        self.mc.subscribe_to(comm_topic + '#')
        self.connectBtn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.connectBtn.setText("System Connected and Active")
        self.connectBtn.setEnabled(False)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.mc = MC()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("AquaGuard - Smart Pool Dashboard")
        
        self.connectionDock = ConnectionDock(self.mc)
        self.statusDock = StatusDock(self.mc)
        self.controlDock = ControlDock(self.mc)
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.statusDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.controlDock)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())