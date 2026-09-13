@echo off
echo Starting AquaGuard IoT System...

:: 1. Start the System Manager and keep window open
start "AquaGuard Manager" cmd /k venv\Scripts\python.exe manager.py

:: 2. Start the Main User Dashboard (GUI) and keep window open
start "AquaGuard GUI" cmd /k venv\Scripts\python.exe gui.py

:: 3. Start the Emulators and keep windows open
start "Emulator: Water Motion Sensor" cmd /k venv\Scripts\python.exe emulator.py WaterMotionSensor motion 5
start "Emulator: Temperature Sensor" cmd /k venv\Scripts\python.exe emulator.py TemperatureSensor temp 7
start "Emulator: Pool Heater" cmd /k venv\Scripts\python.exe emulator.py PoolHeater heater 6
start "Emulator: Pool Light" cmd /k venv\Scripts\python.exe emulator.py PoolLight light 8

echo All AquaGuard components have been launched!