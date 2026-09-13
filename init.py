import socket

# MQTT Broker Configuration
broker_ip = socket.gethostbyname('broker.hivemq.com')
broker_port = 1883
port = 1883
username = ''
password = ''

# Communication Topics
comm_topic = 'pr/AquaGuard/'
conn_time = 0
manag_time = 10

# Database Configuration
db_name = 'data/aquaguard.db'
db_init = True  

# Thresholds
Water_max = 0.02
Elec_max = 1.8