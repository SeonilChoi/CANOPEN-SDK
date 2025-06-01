from canopen_sdk.common import BaseMotorInterface

PI = 3.141592653589793

class MotorInterface(BaseMotorInterface):
    def __init__(self, node_id, eds_file_path,
	             zero_offset=0, operation_mode='PROFILE_POSITION',
				 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
				 name=None, count_per_revolution=1000):
		
		self.PulseToRad = 2 * PI / self.count_per_revolution
	    self.RadToPulse = self.count_per_revolution / (2 * PI)

	def initialize_motor(self):
		# Fault Reset
		self.node.sdo['controlword'].raw = 0x80

		# Operation Mode
		self.node.sdo['modes_of_operation'].raw = self.OPERATION_MODE[self.operation_mode]
        self.pauseForSeconds(0.1)

		# Profile Velocity (pulse/s)
		self.node.sdo['profile_velocity'].raw = self.toUnsignedInt32(
			self.profile_velocity * self.RadToPulse)
		self.pauseForSeconds(0.1)

		# Profile Acceleration (pulse/s^2)
		self.node.sdo['profile_acceleration'].raw = self.toUnsignedInt32(
			self.profile_acceleration * self.RadToPulse)
		self.pauseForSeconds(0.1)

		# Profile Deceleration (pulse/s^2)
		self.node.sdo['profile_deceleration'].raw = self.toUnsignedInt32(
			self.profile_deceleration * self.RadToPulse)
		self.pauseForSeconds(0.1)

		# Linear Lamp
		self.node.sdo['motion_profile_type'].raw = 0
		self.pauseForSeconds(0.1)

		# Shutdown
		self.node.sdo['controlword'].raw = 0x06
		self.pauseForSeconds(0.1)

		# Enable Operation
		self.node.sdo['controlword'].raw = 0x0F
		self.pauseForSeconds(0.1)

	def reset_motor(self):
		# Fault Reset
		self.node.sdo['controlword'].raw = 0x80
		self.pauseForSeconds(0.1)

		# Shutdown
		self.node.sdo['controlword'].raw = 0x06
		self.pauseForSeconds(0.1)

		# Switch On
		self.node.sdo['controlword'].raw = 0x07
		self.pauseForSeconds(0.1)

		# Enable Operation
		self.node.sdo['controlword'].raw = 0x0F
		self.pauseForSeconds(0.1)

	def configure_PDO_mapping(self):
		# Read PDO setting
		self.node.tpdo.read()
		self.node.rpdo.read()

		# TPDO 1 mapping (motor -> controller)
		self.node.tpdo[1].clear()
		self.node.tpdo[1].add_variable('statusword')
		self.node.tpdo[1].add_variable('position_actual_value')
		self.node.tpdo[1].cob_id = 0x180 + self.node_id
		self.node.tpdo[1].trans_type = 1
		self.node.tpdo[1].event_timer = 0
		self.node.tpdo[1].enabled = True
		
		# TPDO 2 mapping
		self.node.tpdo[2].clear()
		self.node.tpdo[2].add_variable('torque_actual_value')
		self.node.tpdo[2].add_variable('velocity_actual_value')
		self.node.tpdo[2].cob_id = 0x280 + self.node_id
		self.node.tpdo[2].trans_type = 1
		self.node.tpdo[2].event_timer = 0
		self.node.tpdo[2].enabled = True

		# RPDO 1 mapping (controller -> motor)
		self.node.rpdo[1].clear()
		self.node.rpdo[1].add_variable('controlword')
		self.node.rpdo[1].add_variable('target_position')
		self.node.rpdo[1].cob_id = 0x200 + self.node_id
		self.node.rpdo[1].trans_type = 0
		self.node.rpdo[1].enabled = True

		# RPDO 2 mapping
		self.node.rpdo[2].clear()
		self.node.rpdo[2].add_variable('target_torque')
		self.node.rpdo[2].cob_id = 0x300 + self.node_id
		self.node.rpdo[2].trans_type = 0
		self.node.rpdo[2].enabled = True

		# Saves and Applies PDO setting
		self.node.nmt.state = 'PRE-OPERATIONAL'
		self.node.tpdo.save()
		self.node.rpdo.save()
		self.node.nmt.state = 'OPERATIONAL'

	def add_PDO_callback(self):
		# Add TPDO 1 callback
		self.network.subscribe(self.node.tpdo[1].cob_id, self.node.tpdo[1].on_message)
		self.node.tpdo[1].add_callback(self.tpdo_1_callback)

		# Add TPDO 2 callback
		self.network.subscribe(self.node.tpdo[2].cob_id, self.node.tpdo[2].on_message)
		self.node.tpdo[2].add_callback(self.tpdo_2_callback)

	def tpdo_1_callback(self, message):
	    # Read Status word
		current_statusword = int.from_bytes(message.data[0:2], byteorder='little')
		
		# Compare current and previous status word
		previous_statusword = self.motor_status.get('statusword', None)
		if previous_statusword is None or previous_statusword != statusword
			
		# Read position
		position = int.from_bytes(message.data[2:5])


		
