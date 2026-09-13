# agent.py - MQTT Client Wrapper for AquaGuard

import paho.mqtt.client as mqtt
from init import broker_ip, broker_port, username, password

class Mqtt_client:
    def __init__(self):
        self.broker = broker_ip
        self.port = int(broker_port)
        self.client_name = "AquaGuard_Default_Client"
        self.username = username
        self.password = password
        self.connected = False
        self.subscribed = False
        self.on_connected_to_form_cb = None
        
        # Initialize MQTT client instance
        self.client = mqtt.Client(self.client_name, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        if self.username != "":
            self.client.username_pw_set(self.username, self.password)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Connected to MQTT Broker successfully")
            if self.on_connected_to_form_cb:
                self.on_connected_to_form_cb()
        else:
            print(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.connected = False
        print("Disconnected from broker")

    def on_message(self, client, userdata, msg):
        pass  # Overridden by subclasses / specific modules

    def set_on_connected_to_form(self, cb):
        self.on_connected_to_form_cb = cb

    def set_broker(self, broker):
        self.broker = broker

    def set_port(self, port):
        self.port = int(port)

    def set_clientName(self, name):
        self.client_name = name
        self.client = mqtt.Client(self.client_name, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def set_username(self, uname):
        self.username = uname
        if uname != "":
            self.client.username_pw_set(self.username, self.password)

    def set_password(self, pwd):
        self.password = pwd
        if self.password != "":
            self.client.username_pw_set(self.username, self.password)

    def connect_to(self):
        try:
            self.client.connect(self.broker, self.port, 60)
        except Exception as e:
            print(f"Connection error: {e}")

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def publish_to(self, topic, message):
        self.client.publish(topic, message)

    def subscribe_to(self, topic):
        self.client.subscribe(topic)
        self.subscribed = True