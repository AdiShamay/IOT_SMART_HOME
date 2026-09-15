# AquaGuard - Smart IoT Pool Manager 💧

AquaGuard is a comprehensive Internet of Things (IoT) system designed to monitor, control, and secure residential swimming pools. The system utilizes the MQTT protocol for real-time communication between smart edge sensors, a central data manager, and a graphical user dashboard.

## 🌟 Key Features & Options

* **Security & Intrusion Detection:** Simulates a water motion sensor that detects unauthorized entry (e.g., unsupervised children) and instantly triggers a critical red alarm on the user dashboard.
* **Smart Heating System:**
  * *Manual Mode:* Set a specific target temperature and the heater will warm the water until reached.
  * *Auto Mode:* Set a minimum and maximum temperature. The system automatically turns on the heater when the water drops below the minimum threshold and stops heating once it reaches the target.
* **Automated Lighting:** Simulates ambient light sensing. Can be toggled manually or set to "Auto Mode" to turn on pool lights only when it gets dark.
* **Data Manager & Logging:** A dedicated background manager application that collects all sensor telemetry and system events from the MQTT broker and logs them into a local SQLite database for historical tracking.
* **Live GUI Dashboard:** A PyQt5-based user interface that provides full control over the pool's features, displays real-time data, and features a live system logs and alerts window.

## 🛠️ Technology Stack

* **Language:** Python
* **Communication:** MQTT Protocol (Eclipse Paho MQTT Client) / HiveMQ Public Broker
* **GUI Framework:** PyQt5
* **Database:** SQLite3

## 🚀 How to Run the Project Locally

### Prerequisites

Make sure you have Python installed on your machine. You will need to install the required Python libraries. Open your terminal or command prompt and run the following command:

```bash
pip install paho-mqtt PyQt5 pandas
```

### Running the System

Simply double-click the **run.bat** file in the project directory. This will automatically open separate terminal windows for the Manager, the GUI, and all 4 Sensor Emulators.

## 📝 Important Notes

* **MQTT Broker:** This project connects to the public HiveMQ broker (broker.hivemq.com) over port 1883. Ensure you have an active internet connection for the components to communicate.