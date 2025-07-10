import time
from canopen_sdk.common import BaseMotorInterface

PI = 3.141592653589793

class EROB(BaseMotorInterface):
    def __init__(self, node_id, object_dictionary_file_path, 
                 name=None, pulse_per_revolution=1000, zero_offset=0, operation_mode='PROFILE_POSITION',
                 profile_velocity=1.0, profile_acceleration=1.0, profile_deceleration=1.0,
                 min_position_limit=-1.0, max_position_limit=1.0):
        super().__init__(node_id, object_dictionary_file_path, 
                         name, pulse_per_revolution, 
                         zero_offset, operation_mode,
                         profile_velocity, profile_acceleration, profile_deceleration,
                         min_position_limit, max_position_limit)
        self.PulseToRad = (2 * PI) / self.pulse_per_revolution
        self.RadToPulse = self.pulse_per_revolution / (2 * PI)
        self.error_message = {}
    
    def initialize_motor(self):
        # Fault Reset
        self.node.sdo['Controlword'].raw = 0x80
        self.pause_for_seconds(0.1)

        # Operation Mode
        self.node.sdo['Modes of operation'].raw = self.OPERATION_MODES[self.operation_mode]
        self.pause_for_seconds(0.1)

        # Profile Velocity (pulse/s)
        self.node.sdo['Profile velocity'].raw = self.to_unsigned_int32(
            self.profile_velocity * self.RadToPulse)
        self.pause_for_seconds(0.1)

        # Profile Acceleration (pulse/s^2)
        self.node.sdo['Profile acceleration'].raw = self.to_unsigned_int32(
            self.profile_acceleration * self.RadToPulse)
        self.pause_for_seconds(0.1)

        # Profile Deceleration (pulse/s^2)
        self.node.sdo['Profile deceleration'].raw = self.to_unsigned_int32(
            self.profile_deceleration * self.RadToPulse)
        self.pause_for_seconds(0.1)

        # Linear Lamp
        self.node.sdo['Motion profile type'].raw = 0
        self.pause_for_seconds(0.1)

        # Set Position range limit
        self.node.sdo['Software position limit'][1].raw = self.to_signed_int32(
            self.min_position_limit * self.RadToPulse
        )
        self.pause_for_seconds(0.1)
        self.node.sdo['Software position limit'][2].raw = self.to_signed_int32(
            self.max_position_limit * self.RadToPulse
        )
        self.pause_for_seconds(0.1)

        # Read Motor Rated Current (mA)
        self.motor_rated_current = self.node.sdo['Motor rated current'].raw
        self.pause_for_seconds(0.1)

        # Shutdown
        self.node.sdo['Controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Switch On
        self.node.sdo['Controlword'].raw = 0x07
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['Controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)
        
    def reset_motor(self):
        # Fault Reset
        self.node.sdo['Controlword'].raw = 0x80
        self.pause_for_seconds(0.1)

        # Shutdown
        self.node.sdo['Controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Switch On
        self.node.sdo['Controlword'].raw = 0x07
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['Controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)
       
    def setup_pdo_mapping(self):
        # Read PDO setting
        self.node.tpdo.read()
        self.node.rpdo.read()

        # TPDO 1 mapping (motor -> controller)
        self.node.tpdo[1].clear()
        self.node.tpdo[1].add_variable('Statusword')
        self.node.tpdo[1].add_variable('Position actual value')
        self.node.tpdo[1].cob_id = 0x180 + self.node_id
        self.node.tpdo[1].trans_type = 1
        self.node.tpdo[1].event_timer = 0
        self.node.tpdo[1].enabled = True

        # TPDO 2 mapping
        self.node.tpdo[2].clear()
        self.node.tpdo[2].add_variable('Torque sensor')
        self.node.tpdo[2].add_variable('Velocity actual value')
        self.node.tpdo[2].cob_id = 0x280 + self.node_id
        self.node.tpdo[2].trans_type = 1
        self.node.tpdo[2].event_timer = 0
        self.node.tpdo[2].enabled = True

        # RPDO 1 mapping (controller -> motor)
        self.node.rpdo[1].clear()
        self.node.rpdo[1].add_variable('Controlword')
        self.node.rpdo[1].add_variable('Target Position')
        self.node.rpdo[1].cob_id = 0x200 + self.node_id
        self.node.rpdo[1].trans_type = 255
        self.node.rpdo[1].enabled = True

        # RPDO 2 mapping
        self.node.rpdo[2].clear()
        self.node.rpdo[2].add_variable('Controlword')
        self.node.rpdo[2].add_variable('Target torque')
        self.node.rpdo[2].cob_id = 0x300 + self.node_id
        self.node.rpdo[2].trans_type = 255
        self.node.rpdo[2].enabled = True

        # Saves and Applies PDO setting
        self.node.nmt.state = 'PRE-OPERATIONAL'
        self.node.tpdo.save()
        self.node.rpdo.save()
        self.node.nmt.state = 'OPERATIONAL'

    def add_pdo_callback(self):
        # Add TPDO 1 callback
        self.network.subscribe(self.node.tpdo[1].cob_id, self.node.tpdo[1].on_message)
        self.node.tpdo[1].add_callback(self.tpdo_1_callback)

        # Add TPDO 2 callback
        self.network.subscribe(self.node.tpdo[2].cob_id, self.node.tpdo[2].on_message)
        self.node.tpdo[2].add_callback(self.tpdo_2_callback)
        
    def tpdo_1_callback(self, message):
        # Read Statusword
        current_statusword = int.from_bytes(message.data[0:2], byteorder='little', signed=False)
        
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
        position = int.from_bytes(message.data[2:6], byteorder='little', signed=True)
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
        torque = int.from_bytes(message.data[0:4], byteorder='little', signed=True)
        self.current_torque = torque / 1000
        
        # Read Velocity
        velocity = int.from_bytes(message.data[4:8], byteorder='little', signed=True)
        self.current_velocity = velocity * self.PulseToRad
        
        # Compute Acceleration
        self.current_acceleration = (self.current_velocity - self.previous_velocity) / self.dt
        self.previous_velocity = self.current_velocity

    def command_switch_on(self):
        # Shutdown
        self.node.sdo['Controlword'].raw = 0x06
        self.pause_for_seconds(0.1)

        # Switch On
        self.node.sdo['Controlword'].raw = 0x07
        self.pause_for_seconds(0.1)

        # Enable Operation
        self.node.sdo['Controlword'].raw = 0x0F
        self.pause_for_seconds(0.1)
        
    def command_quick_stop(self):
        # Quick Stop
        self.node.sdo['Controlword'].raw = 0x02
        self.pause_for_seconds(0.1)
        
    def set_position(self, value):
        # Write Target Position
        position = value * self.RadToPulse + self.zero_offset
        self.node.rpdo[1]['Target Position'].raw = self.to_signed_int32(position)
        
        # New set-point & Change set immediately
        self.node.rpdo[1]['Controlword'].raw = 0x103F # I don't understand why it works...
        self.node.rpdo[1].transmit()
        #self.pause_for_seconds(0.05)
        time.sleep(0.02)

    def set_velocity(self, value):
        """
        This function is not implemented for the eRob motor.
        """
        pass

    def set_acceleration(self, value):
        """
        This function is not implemented for the eRob motor.
        """
        pass

    def set_torque(self, value):
        # Write Target Torque
        torque = value * 1000 / self.motor_rated_current
        self.node.rpdo[2]['Target torque'].raw = self.to_signed_int16(torque)
 
        # New set-point & Change set immediately
        self.node.rpdo[2]['Controlword'].raw = 0x103F # I don't understand why it works...
        self.node.rpdo[2].transmit()
        #self.pause_for_seconds(0.05)
        time.sleep(0.02)

    def reset_node_id(self, node_id):
        self.node.sdo[0x100B].raw = node_id
        self.pause_for_seconds(0.1)

        self.node.sdo[0x1010][1].raw = 0x65766173
        self.pause_for_seconds(0.1)
        
    def get_error_code(self):
        # Error Code
        error_code = self.node.sdo['Error Code'].raw
        return error_code

