import os
from canopen_sdk.erob import EROB

class EROBLoader:
    @staticmethod
    def load_motor(motor_config):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'ZeroErr_Driver_V1.5.eds')

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Object dictionary file not found: {file_path}")

        return EROB(motor_config['node_id'], file_path,
                    motor_config['name'], motor_config['pulse_per_revolution'],
                    motor_config['zero_offset'], motor_config['operation_mode'],
                    motor_config['profile_velocity'], motor_config['profile_acceleration'],
                    motor_config['profile_deceleration'],
                    motor_config['min_position_limit'], motor_config['max_position_limit'])

