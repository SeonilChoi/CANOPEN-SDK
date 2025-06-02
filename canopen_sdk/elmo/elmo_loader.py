import os
from canopen_sdk.elmo import ELMO

class ELMOLoader:
    @staticmethod
    def load_motor(motor_config):
        if not os.path.exists(motor_config['object_dictionary_file_path']):
            raise FileNotFoundError(f"Object dictionary file not found: {motor_config['object_dictionary_file_path']}")
        
        return ELMO(motor_config['node_id'], motor_config['object_dictionary_file_path'],
                    motor_config['zero_offset'], motor_config['operation_mode'],
                    motor_config['profile_velocity'], motor_config['profile_acceleration'],
                    motor_config['profile_deceleration'], motor_config['name'],
                    motor_config['count_per_revolution'])