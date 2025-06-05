import time
from canopen_sdk.manager import load_motor_manager

motor_manager = load_motor_manager('config/motor_config.json')
motor_manager.start_sync_all_motors()

positions = motor_manager.get_positions()
print(positions)

motor_manager.set_position('j_elmo', 3.141592*40)
time.sleep(10.0)
positions = motor_manager.get_positions()
print(positions)

motor_manager.set_position('j_elmo', 0.0)
time.sleep(10.0)
positions = motor_manager.get_positions()
print(positions)

motor_manager.stop_sync_all_motors()