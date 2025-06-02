from canopen_sdk.elmo import ELMO, ELMOLoader

motor_config = {
    'node_id': 1,
    'object_dictionary_file_path': 'canopen_sdk/elmo/elmo.dcf',
    'zero_offset': 0,
    'operation_mode': 'PROFILE_POSITION',
    'profile_velocity': 1.0,
    'profile_acceleration': 1.0,
    'profile_deceleration': 1.0,
    'name': 'elmo_motor',
    'count_per_revolution': 1000
}

motor = ELMOLoader.load_motor(motor_config)