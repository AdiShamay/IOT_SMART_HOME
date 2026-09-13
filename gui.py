# gui.py - AquaGuard Main GUI Application

import sys
import random
from PyQt5.QtWidgets import *
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
        print(f"GUI received from [{topic}]: {m_decode}")
        mainwin.statusDock.update_alarm_window(f"{da.timestamp()}: [{topic}] {m_decode}")

class StatusDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.alarmBox = QTextEdit()
        self.alarmBox.setReadOnly(True)
        
        self.subAlarmBtn = QPushButton("Subscribe to System Topics", self)
        self.subAlarmBtn.clicked.connect(self.on_subscribe_click)
        
        formLayout = QFormLayout()
        formLayout.addRow("Live Status & Messages:", self.alarmBox)
        formLayout.addRow("", self.subAlarmBtn)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("AquaGuard Status & Alerts")

    def on_subscribe_click(self):
        self.mc.subscribe_to(comm_topic + '#')
        self.subAlarmBtn.setStyleSheet("background-color: green")
        self.subAlarmBtn.setText("Subscribed")

    def update_alarm_window(self, text):
        self.alarmBox.append(text)

class ControlDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        
        self.heaterBtn = QPushButton("Turn ON Heater", self)
        self.heaterBtn.clicked.connect(self.on_heater_click)
        
        self.lightBtn = QPushButton("Toggle Pool Lights", self)
        self.lightBtn.clicked.connect(self.on_light_click)
        
        formLayout = QFormLayout()
        formLayout.addRow("Pool Heating Control", self.heaterBtn)
        formLayout.addRow("Lighting Control", self.lightBtn)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("Manual Controls")

    def on_heater_click(self):
        self.mc.publish_to(comm_topic + 'Heater/sub', 'Set temperature to: ON')
        self.heaterBtn.setStyleSheet("background-color: orange")

    def on_light_click(self):
        self.mc.publish_to(comm_topic + 'Light/sub', 'Toggle Light State')
        self.lightBtn.setStyleSheet("background-color: yellow")

class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.connectBtn = QPushButton("Connect to Broker", self)
        self.connectBtn.clicked.connect(self.on_connect_click)
        self.connectBtn.setStyleSheet("background-color: red")
        
        formLayout = QFormLayout()
        formLayout.addRow("", self.connectBtn)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("MQTT Connection")

    def on_connect_click(self):
        self.mc.set_broker(broker_ip)
        self.mc.set_port(int(broker_port))
        self.mc.set_clientName(f"AquaGuard_GUI_{random.randrange(1, 10000)}")
        self.mc.connect_to()
        self.mc.start_listening()
        self.connectBtn.setStyleSheet("background-color: green")
        self.connectBtn.setText("Connected")

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.mc = MC()
        self.setGeometry(100, 100, 700, 500)
        self.setWindowTitle("AquaGuard - Main Control Dashboard")
        
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