# manager.py - AquaGuard System Manager

import time
import random
from init import *
import data_acq as da
from agent import Mqtt_client

def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print(f"Manager received from [{topic}]: {m_decode}")
    
    # Process and save incoming data to SQLite DB
    if 'WaterMotionSensor' in topic:
        da.add_IOT_data('WaterMotionSensor', da.timestamp(), m_decode)
    elif 'TemperatureSensor' in topic:
        da.add_IOT_data('TemperatureSensor', da.timestamp(), m_decode)
    elif 'Heater' in topic:
        da.add_IOT_data('PoolHeater', da.timestamp(), m_decode)

def main():
    # Initialize DB tables if needed
    if db_init:
        da.init_db(db_name)
        print("Database initialized by Manager.")

    # Create Manager MQTT client
    client_id = f"AquaGuard_Manager_{random.randrange(1, 10000)}"
    client = Mqtt_client()
    client.set_clientName(client_id)
    
    # Connect and start listening to all subtopics under comm_topic
    client.connect_to()
    client.start_listening()
    client.client.on_message = on_message
    client.subscribe_to(comm_topic + '#')
    
    print("AquaGuard Manager is running and listening for MQTT messages...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.stop_listening()
        client.client.disconnect()
        print("Manager stopped.")

if __name__ == "__main__":
    main()