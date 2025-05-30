from canopen_sdk.common import BaseMotorInterface

PI = 3.141592653589793

class MotorInterface(BaseMotorInterface):
    def __init__(self, node_id, eds_file_path,
	             zero_offset=0, operation_mode='PROFILE_POSITION',
				 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
				 name=None, count_per_revolution=1000):
		
		self.PulseToRad = 2 * PI / self.count_per_revolution
	    self.RadToPulse = self.count_per_revolution / (2 * PI)

	def initializeMotor(self):
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

	def resetMotor(self):
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

	def 

