import time
import canopen

class MotorManager:
    def __init__(self, channel='can0', bustype='socketcan', bitrate=1000000):
        # CANOpen Network
        self.network = canopen.Network()
        self.network.connect(channel=channel, bustype=bustype, bitrate=bitrate)

        # Motor Config
        self.motors = {}
        self.name_to_id = {}

    def add_motor(self, motor):
        # Add Motor to Network
        motor.node = self.network.add_node(motor.node_id, motor.object_dictionary_file_path)
        motor.node.sdo.RESPONSE_TIMEOUT = 2.0
        motor.node.sdo.MAX_RETRIES = 3
        motor.network = self.network

        # Add Motor to Manager
        self.motors[motor.name] = motor
        self.name_to_id[motor.name] = motor.node_id

    def reset_all_motors(self):
        # Stop
        self.network.nmt.send_command(0x02)
        self.pause_for_seconds(0.5)

        # Reset
        self.network.nmt.send_command(0x82)
        self.pause_for_seconds(1.0)

        # Reset All Motors
        for motor in self.motors.values():
            motor.reset_motor()

        # Start
        self.network.nmt.send_command(0x01)
        self.pause_for_seconds(0.5)
        
    def initialize_all_motors(self):
        # Initialize All Motors
        for motor in self.motors.values():
            motor.initialize_motor()
        self.pause_for_seconds(0.5)

    def setup_all_PDO_mapping(self):
        # Setup PDO Mapping
        for motor in self.motors.values():
            motor.setup_pdo_mapping()
        
        # Start
        self.network.nmt.send_command(0x01)
        self.pause_for_seconds(0.5)
        
    def command_all_switches_on(self):
        # Command All Switches On
        for motor in self.motors.values():
            motor.command_switch_on()
        self.pause_for_seconds(0.5)

    def add_all_PDO_callbacks(self):
        # Add PDO Callbacks
        for motor in self.motors.values():
            motor.add_pdo_callback()
        self.pause_for_seconds(0.5)

    def start_sync_all_motors(self, interval=0.01):
        # Reset
        self.reset_all_motors()

        # Initialize
        self.initialize_all_motors()

        # PDO Mapping
        self.setup_all_PDO_mapping()

        # Switch On
        self.command_all_switches_on()

        # PDO Callbacks
        self.add_all_PDO_callbacks()

        # Set dt
        for motor in self.motors.values():
            motor.set_dt(interval)

        # Start Sync
        self.network.sync.start(interval)
        
    def stop_sync_all_motors(self):
        for motor in self.motors.values():
            motor.command_quick_stop()
        
        # Stop Sync
        self.network.sync.stop()

        # Stop all nodes
        self.network.nmt.send_command(0x02)
        
        self.network.disconnect()
        
    def set_position(self, name, value):
        if name in self.motors:
            self.motors[name].set_position(value)
    
    def set_velocity(self, name, value):
        """This function is not implemented for the base class"""
        pass

    def set_acceleration(self, name, value):
        """This function is not implemented for the base class"""
        pass

    def set_torque(self, name, value):
        if name in self.motors:
            self.motors[name].set_torque(value)
        
    def get_positions(self):
        positions = {}
        for name, motor in self.motors.items():
            positions[name] = motor.get_position()
        return positions

    def get_velocities(self):
        velocities = {}
        for name, motor in self.motors.items():
            velocities[name] = motor.get_velocity()
        return velocities
    
    def get_accelerations(self):
        accelerations = {}
        for name, motor in self.motors.items():
            accelerations[name] = motor.get_acceleration()
        return accelerations
    
    def get_torques(self):
        torques = {}
        for name, motor in self.motors.items():
            torques[name] = motor.get_torque()
        return torques
    
    def get_motor_states(self):
        states = {}
        for name, motor in self.motors.items():
            states[name] = motor.get_motor_state()
        return states
    
    def get_error_codes(self):
        error_codes = {}
        for name, motor in self.motors.items():
            error_codes[name] = motor.get_error_code()
        return error_codes
    
    def check_motor_states(self):
        is_error = False
        motor_states = self.get_motor_states()
        for _, state in motor_states.items():
            if state['fault'] is True:
                is_error = True
                break

            if state['switch_on_disabled'] is True:
                is_error = True
                break

            if state['operation_enabled'] is False:
                is_error = True
                break
        if is_error:
            error_codes = self.get_error_codes()
            self.stop_sync_all_motors()
            return is_error, error_codes
        return is_error, None
    
    def pause_for_seconds(self, value):
        time.sleep(value)
