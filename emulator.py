# emulator.py - AquaGuard Emulators Module

import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from init import *
from agent import Mqtt_client

class MC(Mqtt_client):
    def __init__(self):
        super().__init__()
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f"Message from {topic}: {m_decode}")
        try:
            mainwin.connectionDock.update_btn_state(m_decode)
        except:
            print("Failed to update state")

class ConnectionDock(QDockWidget):
    def __init__(self, mc, name, topic_sub, topic_pub):
        QDockWidget.__init__(self)
        self.name = name
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        formLayout = QFormLayout()
        self.ValueDisplay = QLineEdit()
        self.ValueDisplay.setText('')
        
        formLayout.addRow("Turn On/Off", self.eConnectbtn)
        formLayout.addRow("Pub Topic", QLabel(self.topic_pub))
        formLayout.addRow("Status / Value", self.ValueDisplay)
        
        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle(f"Emulator: {self.name}")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(broker_ip)
        self.mc.set_port(int(broker_port))
        self.mc.set_clientName(f"AquaGuard_Emulator_{random.randrange(1,10000)}")
        self.mc.connect_to()
        self.mc.start_listening()
        if self.topic_sub:
            self.mc.subscribe_to(self.topic_sub)

    def update_btn_state(self, messg):
        if 'Set' in messg or 'Command' in messg:
            self.ValueDisplay.setText(messg)

class MainWindow(QMainWindow):
    def __init__(self, args):
        QMainWindow.__init__(self)
        self.name = args[1]
        self.topic_sub = comm_topic + args[2] + '/sub'
        self.topic_pub = comm_topic + args[2] + '/pub'
        self.update_rate = int(args[3])
        
        self.mc = MC()
        
        # Timer for generating simulated sensor/actuator data
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.create_data)
        self.timer.start(self.update_rate * 1000)

        self.setGeometry(100, 100, 300, 150)
        self.setWindowTitle(self.name)
        
        self.connectionDock = ConnectionDock(self.mc, self.name, self.topic_sub, self.topic_pub)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def create_data(self):
        if not self.mc.connected:
            self.connectionDock.on_button_connect_click()
            
        # Simulate varying data based on emulator type
        val = random.randrange(20, 35)
        current_data = f"From: {self.name} Value: {val}"
        self.connectionDock.ValueDisplay.setText(str(val))
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
    app.exec_()