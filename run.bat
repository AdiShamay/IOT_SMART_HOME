@echo off
echo Starting AquaGuard IoT System...

:: 1. Start the System Manager (Backend logic & DB logging)
start "AquaGuard Manager" python manager.py
timeout 3

:: 2. Start the Main User Dashboard (GUI)
start "AquaGuard GUI" python gui.py
timeout 3

:: 3. Start the Emulators (Motion sensor, Temperature, Heater, Lights)
start "Emulator: Water Motion Sensor" python emulator.py WaterMotionSensor motion 5
timeout 2
start "Emulator: Temperature Sensor" python emulator.py TemperatureSensor temp 7
timeout 2
start "Emulator: Pool Heater" python emulator.py PoolHeater heater 6
timeout 2
start "Emulator: Pool Light" python emulator.py PoolLight light 8

echo All AquaGuard components have been launched!