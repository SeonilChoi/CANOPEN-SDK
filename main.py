import time
from canopen_sdk.manager import load_motor_manager

motor_manager = load_motor_manager('config/motor_config.json', channel='can1')
motor_manager.start_sync_all_motors()

time.sleep(1.0)
positions = motor_manager.get_positions()
print(positions)

motor_manager.set_position('j_11', 0.05)
# motor_manager.set_position('j_2', 1.0)
time.sleep(1.0)
positions = motor_manager.get_positions()
print(positions)

# motor_manager.set_position('j_1', 0.0)
# motor_manager.set_position('j_2', 0.0)
# time.sleep(1.0)
# positions = motor_manager.get_positions()
# print(positions)

# motor_manager.set_position('j_1', 1.0)
# motor_manager.set_position('j_2', 1.0)
# time.sleep(1.0)
# positions = motor_manager.get_positions()
# print(positions)

# motor_manager.set_position('j_1', 0.0)
# motor_manager.set_position('j_2', 0.0)
# time.sleep(1.0)
# positions = motor_manager.get_positions()
# print(positions)

# motor_manager.set_position('j_1', 1.0)
# motor_manager.set_position('j_2', 1.0)
# time.sleep(1.0)
# positions = motor_manager.get_positions()
# print(positions)

# motor_manager.set_position('j_1', 0.0)
# motor_manager.set_position('j_2', 0.0)
# time.sleep(1.0)
# positions = motor_manager.get_positions()
# print(positions)

motor_manager.stop_sync_all_motors()
