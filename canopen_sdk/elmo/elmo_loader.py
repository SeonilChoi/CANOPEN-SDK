import os
from canopen_sdk.elmo import ELMO

class ELMOLoader:
    @staticmethod
    def load_motor(motor_config):
        if not os.path.exists('canopen_sdk/elmo/elmo.dcf'):
            raise FileNotFoundError(f"Object dictionary file not found: canopen_sdk/elmo/elmo.dcf")
        
        return ELMO(motor_config['node_id'], 'canopen_sdk/elmo/elmo.dcf',
                    motor_config['zero_offset'], motor_config['operation_mode'],
                    motor_config['profile_velocity'], motor_config['profile_acceleration'],
                    motor_config['profile_deceleration'], motor_config['name'],
                    motor_config['count_per_revolution'])