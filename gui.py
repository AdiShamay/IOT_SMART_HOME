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

class MainSignals(QObject):
    update_temp = pyqtSignal(float)
    trigger_alert = pyqtSignal(str)
    update_status = pyqtSignal(str)

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
                mainwin.signals.update_temp.emit(temp_val)
            except:
                pass

        if 'motion' in topic and 'Value: 1' in m_decode:
            if hasattr(mainwin, 'controlDock') and mainwin.controlDock.is_locked():
                alert_msg = f"Security Alert: Intrusion detected in the pool area! [{m_decode}]"
                mainwin.signals.trigger_alert.emit(alert_msg)
                return

        mainwin.signals.update_status.emit(f"{da.timestamp()}: [{topic}] {m_decode}")

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
        self.setWindowTitle("AquaGuard Live Status")

    def update_alarm_window(self, text):
        self.alarmBox.append(text)

class ControlDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        
        self.light_manual_on = False
        self.light_auto_on = False
        self.heat_manual_on = False
        self.heat_auto_on = False

        heatGroup = QGroupBox("🌡️ Pool Temperature & Heating")
        heatLayout = QVBoxLayout()
        
        self.tempDisplay = QLineEdit()
        self.tempDisplay.setReadOnly(True)
        self.tempDisplay.setText("Waiting for data...")
        self.tempDisplay.setStyleSheet("font-weight: bold; color: blue; font-size: 14px; margin-bottom: 10px;")
        
        heatLayout.addWidget(QLabel("Current Pool Temperature:"))
        heatLayout.addWidget(self.tempDisplay)
        
        # Manual Heating Row
        heatLayout.addWidget(QLabel("Option A: Manual Heating"))
        manLayout = QHBoxLayout()
        manLayout.addWidget(QLabel("Heat water to:"))
        self.manualTempCombo = QComboBox()
        self.manualTempCombo.addItems(["26", "28", "30", "32", "34"])
        self.manualTempCombo.setCurrentIndex(2)
        manLayout.addWidget(self.manualTempCombo)
        
        self.heaterManualBtn = QPushButton("Start Manual Heating")
        self.heaterManualBtn.clicked.connect(self.on_manual_toggle)
        manLayout.addWidget(self.heaterManualBtn)
        heatLayout.addLayout(manLayout)
        
        # Auto Heating Row
        heatLayout.addWidget(QLabel("Option B: Automatic Heating"))
        autoLayout = QHBoxLayout()
        autoLayout.addWidget(QLabel("Turn ON when below:"))
        self.autoMinCombo = QComboBox()
        self.autoMinCombo.addItems(["24", "26", "28", "30"])
        self.autoMinCombo.setCurrentIndex(1) # Default 26
        autoLayout.addWidget(self.autoMinCombo)
        
        autoLayout.addWidget(QLabel("and heat up to:"))
        self.autoMaxCombo = QComboBox()
        self.autoMaxCombo.addItems(["26", "28", "30", "32", "34"])
        self.autoMaxCombo.setCurrentIndex(1) # Default 30
        autoLayout.addWidget(self.autoMaxCombo)
        
        self.heaterAutoBtn = QPushButton("Start Auto Heating")
        self.heaterAutoBtn.clicked.connect(self.on_auto_toggle)
        autoLayout.addWidget(self.heaterAutoBtn)
        
        heatLayout.addLayout(autoLayout)
        heatGroup.setLayout(heatLayout)

        lightGroup = QGroupBox("💡 Pool Lighting")
        lightLayout = QVBoxLayout()
        lightLayout.addWidget(QLabel("Choose lighting mode:"))
        
        lBtnLayout = QHBoxLayout()
        self.lightManualBtn = QPushButton("Manual: Turn ON")
        self.lightManualBtn.clicked.connect(self.on_light_manual_toggle)
        
        self.lightAutoBtn = QPushButton("Auto Mode: Turn ON when Dark")
        self.lightAutoBtn.clicked.connect(self.on_light_auto_toggle)
        
        lBtnLayout.addWidget(self.lightManualBtn)
        lBtnLayout.addWidget(self.lightAutoBtn)
        lightLayout.addLayout(lBtnLayout)
        lightGroup.setLayout(lightLayout)

        secGroup = QGroupBox("🔒 Security System")
        secLayout = QVBoxLayout()
        self.lockCheckBox = QCheckBox("Arm Pool Security (Alert on Motion)")
        self.lockCheckBox.setStyleSheet("color: darkred; font-weight: bold;")
        
        self.testMotionBtn = QPushButton("Simulate Intrusion (Test Alarm)")
        self.testMotionBtn.clicked.connect(self.on_test_motion)
        
        secLayout.addWidget(self.lockCheckBox)
        secLayout.addWidget(self.testMotionBtn)
        secGroup.setLayout(secLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(heatGroup)
        mainLayout.addWidget(lightGroup)
        mainLayout.addWidget(secGroup)
        
        widget = QWidget(self)
        widget.setLayout(mainLayout)
        self.setWidget(widget)
        self.setWindowTitle("User Control Panel")

    def process_incoming_temperature(self, current_temp):
        self.tempDisplay.setText(str(current_temp) + " °C")
        
        # Turn off manual button automatically when target is reached
        if self.heat_manual_on and current_temp >= float(self.manualTempCombo.currentText()):
            self.reset_heat_buttons()
            self.mc.publish_to(comm_topic + 'heater/sub', 'OFF')

    def is_locked(self):
        return self.lockCheckBox.isChecked()

    def on_test_motion(self):
        self.mc.publish_to(comm_topic + 'motion/sub', 'SIMULATE')

    def reset_heat_buttons(self):
        self.heat_manual_on = False
        self.heat_auto_on = False
        self.heaterManualBtn.setText("Start Manual Heating")
        self.heaterManualBtn.setStyleSheet("")
        self.heaterAutoBtn.setText("Start Auto Heating")
        self.heaterAutoBtn.setStyleSheet("")

    def on_manual_toggle(self):
        if not self.heat_manual_on:
            self.reset_heat_buttons()
            self.heat_manual_on = True
            target = self.manualTempCombo.currentText()
            self.heaterManualBtn.setText("Turn OFF Manual Heating")
            self.heaterManualBtn.setStyleSheet("background-color: orange; font-weight: bold;")
            self.mc.publish_to(comm_topic + 'heater/sub', f'MANUAL:{target}')
        else:
            self.reset_heat_buttons()
            self.mc.publish_to(comm_topic + 'heater/sub', 'OFF')

    def on_auto_toggle(self):
        if not self.heat_auto_on:
            self.reset_heat_buttons()
            self.heat_auto_on = True
            min_temp = self.autoMinCombo.currentText()
            max_temp = self.autoMaxCombo.currentText()
            self.heaterAutoBtn.setText("Turn OFF Auto Heating")
            self.heaterAutoBtn.setStyleSheet("background-color: #a5d6a7; font-weight: bold;")
            self.mc.publish_to(comm_topic + 'heater/sub', f'AUTO:{min_temp},{max_temp}')
        else:
            self.reset_heat_buttons()
            self.mc.publish_to(comm_topic + 'heater/sub', 'OFF')

    def on_light_manual_toggle(self):
        self.light_auto_on = False
        self.lightAutoBtn.setStyleSheet("")
        
        if not self.light_manual_on:
            self.light_manual_on = True
            self.lightManualBtn.setText("Manual: Turn OFF")
            self.lightManualBtn.setStyleSheet("background-color: yellow; font-weight: bold;")
            self.mc.publish_to(comm_topic + 'light/sub', 'MANUAL_ON')
        else:
            self.light_manual_on = False
            self.lightManualBtn.setText("Manual: Turn ON")
            self.lightManualBtn.setStyleSheet("")
            self.mc.publish_to(comm_topic + 'light/sub', 'MANUAL_OFF')

    def on_light_auto_toggle(self):
        self.light_manual_on = False
        self.lightManualBtn.setText("Manual: Turn ON")
        self.lightManualBtn.setStyleSheet("")
        
        if not self.light_auto_on:
            self.light_auto_on = True
            self.lightAutoBtn.setStyleSheet("background-color: #a5d6a7; font-weight: bold;")
            self.mc.publish_to(comm_topic + 'light/sub', 'AUTO')
        else:
            self.light_auto_on = False
            self.lightAutoBtn.setStyleSheet("")
            self.mc.publish_to(comm_topic + 'light/sub', 'MANUAL_OFF')

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
        
        self.signals = MainSignals()
        
        self.setGeometry(100, 100, 850, 750)
        self.setWindowTitle("AquaGuard - Smart Pool Dashboard")
        
        self.connectionDock = ConnectionDock(self.mc)
        self.statusDock = StatusDock(self.mc)
        self.controlDock = ControlDock(self.mc)
        
        self.signals.update_temp.connect(self.controlDock.process_incoming_temperature)
        self.signals.trigger_alert.connect(self.show_critical_alert)
        self.signals.update_status.connect(self.statusDock.update_alarm_window)
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.statusDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.controlDock)

    def show_critical_alert(self, msg):
        self.statusDock.update_alarm_window(f"<font color='red'><b>{da.timestamp()}: {msg}</b></font>")
        QMessageBox.critical(self, "Security Emergency", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindow()
    mainwin.show()
    sys.exit(app.exec_())