import os
import time
import ctypes
from abc import ABC, abstractmethod
from canopen_sdk.logger import Logger

class BaseMotorInterface(ABC):
    OPERATION_MODES = {
        'PROFILE_POSITION':      0x01,
        'PROFILE_VELOCITY':      0x03,
        'PROFILE_TORQUE':        0x04,
        'HOMING':                0x06,
        'INTERPOLATED_POSITION': 0x07,
        'CYCLIC_SYNC_POSITION':  0x08,
        'CYCLIC_SYNC_VELOCITY':  0x09,
        'CYCLIC_SYNC_TORQUE':    0x0A
    }

    def __init__(self, node_id, object_dictionary_file_path, 
                 name=None, pulse_per_revolution=1000, zero_offset=0, operation_mode='PROFILE_POSITION',
                 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
                 min_position_limit=-1.0, max_position_limit=1.0):
        self.node_id = node_id
        self.object_dictionary_file_path = object_dictionary_file_path
        self.name = name if name is not None else f"joint_{node_id}"
        self.pulse_per_revolution = pulse_per_revolution
        self.zero_offset = zero_offset
        self.operation_mode = operation_mode
        self.profile_velocity = profile_velocity
        self.profile_acceleration = profile_acceleration
        self.profile_deceleration = profile_deceleration
        self.min_position_limit = min_position_limit
        self.max_position_limit = max_position_limit
        
        self.node = None
        self.network = None
        self.dt = 0.01
        self.current_position = 0
        self.current_velocity = 0
        self.previous_velocity = 0
        self.current_acceleration = 0
        self.current_torque = 0
        self.motor_rated_current = 0
        self.motor_status = {
            'statusword': None,
            #'ready_to_switch_on': 0,
            #'switched_on': 0,
            'operation_enabled': 0,
            'fault': 0,
            #'voltage_enabled': 0,
            #'quick_stop': 0,
            'switch_on_disabled': 0,
            #'warning': 0,
        }
        self.error_code = 0
        base_dir   = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        parent_dir = os.path.dirname(parent_dir)
        file_path  = os.path.join(parent_dir, 'logs', f'{self.name}.csv')
        #self.logger = Logger(file_path)
        
    @abstractmethod
    def initialize_motor(self):
        """Initialize motor"""
        pass

    @abstractmethod
    def reset_motor(self):
        """Reset motor"""
        pass
    
    @abstractmethod
    def setup_pdo_mapping(self):
        """Set PDO mapping"""
        pass

    @abstractmethod
    def add_pdo_callback(self):
        """Add PDO callback to the network"""
        pass

    @abstractmethod
    def command_switch_on(self):
        """switch on"""
        pass

    @abstractmethod
    def command_quick_stop(self):
        """quick stop"""
        pass

    @abstractmethod
    def set_position(self, value):
        """Set motor position"""
        pass

    @abstractmethod
    def set_velocity(self, value):
        """Set motor velocity"""
        pass

    @abstractmethod
    def set_acceleration(self, value):
        """Set motor acceleration"""
        pass

    @abstractmethod
    def set_torque(self, value):
        """Set motor torque"""
        pass

    def set_zero_offset(self, value):
        """Set zero offset"""
        self.zero_offset = value

    def set_dt(self, value=0.01):
        """Set dt"""
        self.dt = value

    def pause_for_seconds(self, value):
        """Pauses execution for the given number of seconds to complete the command write"""
        time.sleep(value)

    def get_zero_offset(self):
        """Get zero offset"""
        return self.zero_offset

    def to_unsigned_int32(self, value):
        """convert a value to an unsigned 32-bit integer"""
        return ctypes.c_uint32(int(value)).value
    
    def to_signed_int32(self, value):
        """convert a value to a signed 32-bit integer"""
        return ctypes.c_int32(int(value)).value
    
    def get_position(self):
        """Get motor position"""
        return self.current_position
    
    def get_velocity(self):
        """Get motor velocity"""
        return self.current_velocity
    
    def get_acceleration(self):
        """Get motor acceleration"""
        return self.current_acceleration

    def get_torque(self):
        """Get motor torque"""
        return self.current_torque
    
    def get_position_range_limit(self):
        """Get position range limit"""
        return self.min_position_limit, self.max_position_limit

    def get_motor_state(self):
        """Get motor state"""
        return {
            #'node_id': self.node_id,
            #'name': self.name,
            'position': self.current_position,
            'velocity': self.current_velocity,
            'acceleration': self.current_acceleration,
            'torque': self.current_torque,
            'statusword': self.motor_status['statusword'],
            #'ready_to_switch_on': self.motor_status['ready_to_switch_on'],
            #'switched_on': self.motor_status['switched_on'],
            'operation_enabled': self.motor_status['operation_enabled'],
            'fault': self.motor_status['fault'],
            #'voltage_enabled': self.motor_status['voltage_enabled'],
            #'quick_stop': self.motor_status['quick_stop'],
            'switch_on_disabled': self.motor_status['switch_on_disabled'],
            #'warning': self.motor_status['warning'],
        }
 
    def get_error_code(self):
        """
        Get Error Code
        # Error Code
        error_code = self.node.sdo['Error Code'].raw
        return error_code
        """
        return self.error_code
 
    @abstractmethod
    def reset_node_id(self, node_id):
        """"Reset the node ID"""
        pass
        
    def close_logger(self):
        pass
        """Close logger"""
        #self.logger.close()
