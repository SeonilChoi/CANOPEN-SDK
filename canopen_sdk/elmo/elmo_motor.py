from canopen_sdk.common import BaseMotorInterface

PI = 3.141592653589793

class ELMO(BaseMotorInterface):
    def __init__(self, node_id, object_dictionary_file_path,
                 zero_offset=0, operation_mode='PROFILE_POSITION',
                 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
                 name=None, count_per_revolution=1000):
        super().__init__(node_id, object_dictionary_file_path, zero_offset, operation_mode,
                         profile_velocity, profile_acceleration, profile_deceleration,
                         name, count_per_revolution)
        self.PulseToRad = (2 * PI) / self.count_per_revolution
        self.RadToPulse = self.count_per_revolution / (2 * PI)
        self.rated_torque = 1.0

    def initialize_motor(self):
        # Fault Reset
        self.node.sdo['controlword'].raw = 0x80

        # Operation Mode
        self.node.sdo['modes_of_operation'].raw = self.OPERATION_MODES[self.operation_mode]
        self.pause_for_seconds(0.1)

        # Profile Velocity (pulse/s)
        #self.node.sdo['profile_velocity'].raw = self.to_unsigned_int32(
        #    self.profile_velocity * self.RadToPulse)
        self.node.sdo['profile_velocity'].raw = 260000
        self.pause_for_seconds(0.1)

        # Profile Acceleration (pulse/s^2)
        #self.node.sdo['profile_acceleration'].raw = self.to_unsigned_int32(
        #    self.profile_acceleration * self.RadToPulse)
        self.node.sdo['profile_acceleration'].raw = 320000
        self.pause_for_seconds(0.1)

        # Profile Deceleration (pulse/s^2)
        #self.node.sdo['profile_deceleration'].raw = self.to_unsigned_int32(
        #    self.profile_deceleration * self.RadToPulse)
        self.node.sdo['profile_deceleration'].raw = 160000
        self.pause_for_seconds(0.1)

        # Linear Lamp
        self.node.sdo['motion_profile_type'].raw = 0
        self.pause_for_seconds(0.1)

        # Shutdown
        self.node.sdo['controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)

    def reset_motor(self):
        # Fault Reset
        self.node.sdo['controlword'].raw = 0x80
        self.pause_for_seconds(0.1)

        # Shutdown
        self.node.sdo['controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Switch On
        self.node.sdo['controlword'].raw = 0x07
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)

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

        # Read Motor Rated Current (mA)
        self.motor_rated_current = self.node.sdo['motor_rated_current'].raw
        self.pause_for_seconds(0.1)

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
        
        # Compare current and previous status word and update motor status
        previous_statusword = self.motor_status.get('statusword', None)
        if previous_statusword is None or previous_statusword != current_statusword:
            self.motor_status['statusword'] = current_statusword
            self.motor_status['ready_to_switch_on'] = bool(current_statusword & (1 << 0))
            self.motor_status['switched_on'] = bool(current_statusword & (1 << 1))
            self.motor_status['operation_enabled'] = bool(current_statusword & (1 << 2))
            self.motor_status['fault'] = bool(current_statusword & (1 << 3))
            self.motor_status['voltage_enabled'] = bool(current_statusword & (1 << 4))
            self.motor_status['quick_stop'] = bool(current_statusword & (1 << 5))
            self.motor_status['switch_on_disabled'] = bool(current_statusword & (1 << 6))
            self.motor_status['warning'] = bool(current_statusword & (1 << 7))
            
        # Read position
        position = int.from_bytes(message.data[2:6], byteorder='little')
        self.current_position = (position - self.zero_offset) * self.PulseToRad
        
        # Write to logger
        self.logger.write_key_values({
            'position': self.current_position,
            'torque': self.current_torque,
            'velocity': self.current_velocity,
            'acceleration': self.current_acceleration,
            'statusword': self.motor_status['statusword'],
            'ready_to_switch_on': self.motor_status['ready_to_switch_on'],
            'switched_on': self.motor_status['switched_on'],
            'operation_enabled': self.motor_status['operation_enabled'],
            'fault': self.motor_status['fault'],
            'voltage_enabled': self.motor_status['voltage_enabled'],
            'quick_stop': self.motor_status['quick_stop'],
            'switch_on_disabled': self.motor_status['switch_on_disabled'],
            'warning': self.motor_status['warning']
        })

    def tpdo_2_callback(self, message):
        # Read Torque
        torque = int.from_bytes(message.data[0:2], byteorder='little')
        self.current_torque = torque / 1000 * self.rated_torque

        # Read Velocity
        velocity = int.from_bytes(message.data[2:6], byteorder='little')
        self.current_velocity = velocity * self.PulseToRad

        # Compute Acceleration
        self.current_acceleration = (self.current_velocity - self.previous_velocity) / self.dt
        self.previous_velocity = self.current_velocity
        
    def command_switch_on(self):
        # Shutdown
        self.node.sdo['controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Switch On
        self.node.sdo['controlword'].raw = 0x07
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)

    def command_quick_stop(self):
        # Quick Stop
        self.node.sdo['controlword'].raw = 0x02
        self.pause_for_seconds(0.1)
        
        self.logger.close()

    def set_position(self, value):
        # Write Target Position
        position = value * self.RadToPulse + self.zero_offset
        self.node.rpdo[1]['target_position'].raw = self.to_signed_int32(position)
    
        # Enable Operation
        self.node.rpdo[1]['controlword'].raw = 0x0F
        self.node.rpdo[1].transmit()
        self.pause_for_seconds(0.01)

        # New Set-point
        self.node.rpdo[1]['controlword'].raw = 0x3F
        self.node.rpdo[1].transmit()
        self.pause_for_seconds(0.01)
        
    def set_velocity(self, value):
        """
        This function is not implemented for the ELMO motor.
        """
        pass

    def set_acceleration(self, value):
        """
        This function is not implemented for the ELMO motor.
        """
        pass

    def set_torque(self, value):
        # Write Target Torque
        torque = (value * 1000) / self.motor_rated_current
        self.node.rpdo[2]['target_torque'].raw = self.to_signed_int16(torque)

        # Enable Operation
        self.node.rpdo[1]['controlword'].raw = 0x0F
        self.node.rpdo[1].transmit()
        self.pause_for_seconds(0.01)

    def get_error_code(self):
        # Error Code
        error_code = self.node.sdo['error_code'].raw
        return error_code