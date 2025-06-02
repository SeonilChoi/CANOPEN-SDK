import os
import json
from canopen_sdk.manager.motor_manager import MotorManager

from canopen_sdk.elmo import ELMOLoader

def load_motor_manager(motor_config_file_path, channel='can0', bustype='socketcan', bitrate=1000000):
    # Check if file exists
    if not os.path.exists(motor_config_file_path):
        raise FileNotFoundError(f"Motor config file not found: {motor_config_file_path}")

    # Load Motor Config
    with open(motor_config_file_path, 'r') as f:
        motor_configs = json.load(f)

    # Create Motor Manager
    motor_manager = MotorManager(channel=channel, bustype=bustype, bitrate=bitrate)

    # Add motors to manager
    for motor_config in motor_configs:
        if motor_config['vendor'] == 'elmo':
            motor = ELMOLoader.load_motor(motor_config)
            motor_manager.add_motor(motor)
        else:
            raise ValueError(f"Unsupported vendor: {motor_config['vendor']}")

    return motor_manager
