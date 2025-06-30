import os
from canopen_sdk.erob import EROB

class EROBLoader:
    @staticmethod
    def load_motor(motor_config):
        if not os.path.exists('canopen_sdk/erob/ZeroErr_Driver_V1.5.eds'):
            raise FileNotFoundError(f"Object dictionary file not found: ZeroErr_Driver_V1.5.eds")

        return EROB(motor_config['node_id'], 'canopen_sdk/erob/ZeroErr_Driver_V1.5.eds',
                    motor_config['zero_offset'], motor_config['operation_mode'],
                    motor_config['profile_velocity'], motor_config['profile_acceleration'],
                    motor_config['profile_deceleration'], motor_config['name'],
                    motor_config['pulse_per_revolution'])

