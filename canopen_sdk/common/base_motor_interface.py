from abs import ABC, abstractmethod
import time
import ctypes

class BaseMotorInterface(ABC):
	OPERATION_MODES = {
		'PROFILE_POSITION':      0x01,
		'PROFILE_VELOCITY':      0x03,
		'PROFILE_TORQUE':        0x04,
		'Reserved':              0x05,
		'HOMING':                0x06,
		'INTERPOLATED_POSITION': 0x07,
		'CYCLIC_SYNC_POSITION':  0x08,
        'CYCLIC_SYNC_VELOCITY':  0x09,
        'CYCLIC_SYNC_TORQUE':    0x0A
	}

    """
    :param node_id: Node ID
	:param eds_file_path: EDS file path
	:param zero_offset
	"""
	def __init__(self, node_id, eds_file_path, 
	             zero_offset=0, operation_mode='PROFILE_POSITION',
				 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
				 name=None, count_per_revolution=1000):
		self.node_id = node_id
		self.eds_file_path = eds_path
		self.zero_offset = zero_offset
		self.operation_mode = operation_mode
		self.profile_velocity = profile_velocity
		self.profile_acceleration = profile_acceleration
		self.profile_deceleration = profile_deceleration
		self.name = name if name is not None else f"joint_{node_id}"
		self.count_per_revolution = count_per_revolution

		self.node = None
		self.network = None
		self.dt = 0.01
		self.target_position = 0
		self.target_torque = 0
		self.current_position = 0
		self.current_velocity = 0
		self.previous_velocity = 0
		self.current_acceleration = 0
		self.current_torque_sensor = 0
		self.motor_status = {
            'statusword': None,
            'ready_to_switch_on': 0,
            'switch_on': 0,
            'operation_enabled': 0,
            'fault': 0,
            'voltage_enabled': 0,
            'quick_stop': 0,
            'switch_on_disabled': 0,
            'warning': 0,
        }

	@abstractmethod
	def initialize_motor(self):
	    """Initialize motor"""
		pass

	@abstractmethod
	def reset_motor(self):
	    """Reset motor"""
		pass
	
	@abstractmethod
	def configure_PDO_mapping(self):
	    """Set PDO mapping"""
		pass

    @abstractmethod
	def add_PDO_callback(self):
	    """Add PDO callback to the network"""
        pass

	@abstractmethod
	def command_switch_on(self):
	    """switch on"""
		pass

	def reset_zero_offset(self, value):
	    """Reset zero offset"""
		self.zero_offset = value

	def get_zero_offset(self):
	    """Get zero offset"""
		return self.zero_offset
	
	def set_dt(self, val=0.01):
	    """Set dt"""
		self.dt = value

	@abstractmethod
	def set_position(self, value):
	    """Set motor position"""
		pass

	@abstractmethod
	def get_position(self):
	    """Get motor position"""
		pass

    @abstractmethod
	def set_velocity(self, value):
	    """Set motor velocity"""
		pass

	@abstractmethod
	def get_velocity(self):
	    """Get motor velocity"""
		pass

	@abstractmethod
	def set_acceleraion(self, value):
	    """Set motor acceleration"""
		pass

	@abstractmethod
	def get_acceleration(self):
	    """Get motor acceleration"""

	@abstractmethod
	def set_torque(self, value):
	    """Set motor torque"""
		pass

	@abstractmethod
	def get_torque(self):
	    """Get motor torque"""
		pass

	def pause_for_seconds(self, value):
	    """Pauses execution for the given number of seconds to complete the command write"""
		time.sleep(value)

	def to_unsigned_int32(self, value):
	    """convert a value to an unsigned 32-bit integer"""
		return ctypes.c_uint32(int(value)).value
