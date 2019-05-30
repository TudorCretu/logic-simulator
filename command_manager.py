"""Execute commands and stores system states.

Used in the Logic Simulator project to execute commands, enable save/load and undo/redo operations in the gui.

Classes
-------
Command - stores command properties.
CommandManager - makes and stores all the devices in the logic network.
"""

import abc
import copy
import pickle

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class Command(metaclass=abc.ABCMeta):
    """Abstract / Interface base class for commands."""
    @abc.abstractmethod
    def execute(self, command_manager):
        pass

    @abc.abstractmethod
    def undo(self):
        pass

    @abc.abstractmethod
    def redo(self):
        pass


class HelpCommand(Command):
    """Help command implementation."""

    def __init__(self):
        """Initialise attributes"""
        self.command_manager = None
        self.gui = None
        pass

    def execute(self, command_manager):
        """Execute help command

        Return NO_ERROR, None if successful.
        """

        self.command_manager = command_manager
        self.gui = command_manager.gui

        text = "User commands:\n" + \
               "r N     - run the simulation for N cycles\n" + \
               "c N     - continue the simulation for N cycles\n" + \
               "s X N   - set switch X to N (0 or 1)\n" + \
               "m X     - set a monitor on signal X\n" + \
               "z X     - zap the monitor on signal X\n" + \
               "h       - help (this command)\n" + \
               "q       - quit the program"
        self.gui.log_text(text)
        return self.command_manager.NO_ERROR, None

    def undo(self):
        """Attempt to undo help command. Pass the undo call to the next command

        Return error_code, error_message
        """

        # Nothing to undo, undo the next command
        return self.command_manager.undo_command()

    def redo(self):
        """Attempt to redo help command. Pass the redo call to the next command

        Return error_code, error_message
        """

        # Nothing to redo, redo the next command
        return self.command_manager.redo_command()


class SwitchCommand(Command):
    """Set switch command implementation."""

    def __init__(self, switch_name, value):
        # Initializes switch name to be switched to value
        self.command_manager = None
        self.gui = None
        self.switch_name = switch_name
        self.value = value

    def execute(self, command_manager):
        """Execute set switch command

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui

        device_id = self.command_manager.names.query(self.switch_name)
        if device_id is not None and device_id in self.gui.switches:
            try:
                self.value = int(self.value)
                if self.value == self.command_manager.devices.LOW or self.value == self.command_manager.devices.HIGH:
                    self.command_manager.devices.set_switch(device_id, self.value)
                    self.gui.log_text("Set switch " + self.switch_name + " to  " + str(self.value))
                    self.gui.switches_update_toggle()
                else:
                    raise ValueError
            except ValueError:
                return self.command_manager.INVALID_ARGUMENT, "Switch can be set to only 0 or 1."
        else:
            return self.command_manager.INVALID_ARGUMENT, "Device " + self.switch_name + " is not a SWITCH"
        return command_manager.NO_ERROR, None

    def undo(self):
        """Undo set switch command

        Return NO_ERROR, None if successful.
        """

        # Reverse the value set to a switch
        self.value = 1 - self.value
        error_code, error_message = self.execute(self.command_manager)
        return error_code, error_message

    def redo(self):
        """Redo set switch command

        Return NO_ERROR, None if successful.
        """

        # redo can be called only after undo is called, so change value back to the original
        self.value = 1 - self.value
        error_code, error_message = self.execute(self.command_manager)
        return error_code, error_message


class MonitorCommand(Command):
    """Monitor command implementation."""

    def __init__(self, signal_name):
        """Initialise signal_name to monitor"""
        self.command_manager = None
        self.gui = None
        self.initial_monitors_state = None
        self.final_monitors_state = None
        self.signal_name = signal_name

    def execute(self, command_manager):
        """Executes monitor command

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui
        self.initial_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)

        monitored, unmonitored = self.command_manager.monitors.get_signal_names()
        if self.signal_name in monitored + unmonitored:
            if self.signal_name in unmonitored:
                ids = self.command_manager.devices.get_signal_ids(self.signal_name)
                if ids is not None:
                    [device_id, output_id] = ids
                    self.command_manager.monitors.make_monitor(device_id, output_id, self.gui.completed_cycles)
                    self.gui.canvas.update_cycle_axis_layout()
                    self.gui.log_text("Set monitor on " + self.signal_name)
                    self.gui.monitors_update_toggle()
                    # update monitors set/zap toggle button

                else:
                    return self.command_manager.UNKNOWN_ERROR, "Failed in executing Monitor Command. ids is None."
            else:
                return self.command_manager.monitors.MONITOR_PRESENT, self.signal_name + " is already monitored"
        else:
            return self.command_manager.monitors.NOT_OUTPUT, "Error: " + self.signal_name + " is not an output signal"
        self.final_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        return command_manager.NO_ERROR, None

    def undo(self):
        """Undo monitor command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.initial_monitors_state
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.monitors_update_toggle()
        return self.command_manager.NO_ERROR, None

    def redo(self):
        """Redo monitor command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.final_monitors_state
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.monitors_update_toggle()
        return self.command_manager.NO_ERROR, None


class ZapCommand(Command):
    """Zap command implementation."""

    def __init__(self, signal_name):
        """Initialise signal_name to zap"""
        self.command_manager = None
        self.gui = None
        self.initial_monitors_state = None
        self.final_monitors_state = None
        self.signal_name = signal_name
        pass

    def execute(self, command_manager):
        """Executes zap command

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui
        self.initial_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)

        monitored, unmonitored = self.command_manager.monitors.get_signal_names()
        if self.signal_name in monitored + unmonitored:
            if self.signal_name in monitored:
                ids = self.command_manager.devices.get_signal_ids(self.signal_name)
                if ids is not None:
                    [device_id, output_id] = ids
                    self.command_manager.monitors.remove_monitor(device_id, output_id)
                    self.gui.canvas.update_cycle_axis_layout()
                    self.gui.log_text("Zap monitor on " + self.signal_name)
                    self.gui.monitors_update_toggle()
                else:
                    return self.command_manager.UNKNOWN_ERROR, "Failed in executing Zap Command. ids is None."
            else:
                return self.command_manager.SIGNAL_NOT_MONITORED, self.signal_name + " is not monitored"
        else:
            return self.command_manager.monitors.NOT_OUTPUT, self.signal_name + " is not an output signal"
        self.final_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        return command_manager.NO_ERROR, None

    def undo(self):
        """Undo zap command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.initial_monitors_state
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.monitors_update_toggle()
        return self.command_manager.NO_ERROR, None

    def redo(self):
        """Redo zap command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.final_monitors_state
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.monitors_update_toggle()
        return self.command_manager.NO_ERROR, None


class RunCommand(Command):
    """Run command implementation."""

    def __init__(self, cycles):
        """Initialise number of cycles."""
        self.command_manager = None
        self.gui = None
        self.cycles = cycles
        self.initial_cycles = None
        self.initial_monitors_state = None
        self.final_monitors_state = None
        self.initial_devices_state = None
        self.final_devices_state = None

    def execute(self, command_manager):
        """Execute run command

        Return NO_ERROR, None if successful.
        """

        # Run simulation from start for a number of cycles
        self.command_manager = command_manager
        self.gui = command_manager.gui
        self.initial_cycles = self.gui.completed_cycles
        self.initial_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        self.initial_devices_state = copy.deepcopy(command_manager.devices.devices_list)

        try:
            self.cycles = int(self.cycles)
            if self.cycles < 0:
                raise ValueError
            self.command_manager.monitors.reset_monitors()
            self.command_manager.devices.cold_startup()
            for _ in range(self.cycles):
                if self.command_manager.network.execute_network():
                    self.command_manager.monitors.record_signals()
                else:
                    return self.command_manager.OSCILLATING_NETWORK, \
                           "Cannot run network. The network doesn't have a stable state."
            self.gui.update_cycles(self.cycles)
            self.gui.canvas.update_cycle_axis_layout()
            self.gui.canvas.reset_pan()
            self.gui.log_text("Run simulation for " + str(self.cycles) + " cycles")

        except ValueError:
            return self.command_manager.INVALID_ARGUMENT, \
                   "Cannot run network. The number of cycles is not a positive integer."
        self.final_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        self.final_devices_state = copy.deepcopy(command_manager.devices.devices_list)

        return self.command_manager.NO_ERROR, None

    def undo(self):
        """Undo run command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.initial_monitors_state
        self.command_manager.devices.devices_list = self.initial_devices_state
        self.gui.update_cycles(self.initial_cycles)
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.canvas.pan_to_right_end()
        return self.command_manager.NO_ERROR, None

    def redo(self):
        """Redo run command

        Return NO_ERROR, None if successful.
        """
        self.command_manager.monitors.monitors_dictionary = self.final_monitors_state
        self.command_manager.devices.devices_list = self.final_devices_state
        self.gui.update_cycles(self.cycles)
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.canvas.pan_to_right_end()
        return self.command_manager.NO_ERROR, None


class ContinueCommand(Command):
    """Continue command implementation."""

    def __init__(self, cycles):
        """Initialise number of cycles."""
        self.command_manager = None
        self.gui = None
        self.cycles = cycles
        self.initial_cycles = None
        self.initial_monitors_state = None
        self.final_monitors_state = None
        self.initial_devices_state = None
        self.final_devices_state = None

    def execute(self, command_manager):
        """Continue simulation for a number of cycles

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui
        self.initial_cycles = self.gui.completed_cycles
        self.initial_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        self.initial_devices_state = copy.deepcopy(command_manager.devices.devices_list)

        if self.gui.completed_cycles == 0:
            return self.command_manager.SIMULATION_NOT_STARTED, None
        try:
            self.cycles = int(self.cycles)
            if self.cycles < 0:
                raise ValueError
            self.cycles = int(self.cycles)
            for _ in range(self.cycles):
                if self.command_manager.network.execute_network():
                    self.command_manager.monitors.record_signals()
                else:
                    return self.command_manager.OSCILLATING_NETWORK, \
                            "Cannot continue network. The network doesn't have a stable state."
            self.gui.update_cycles(self.gui.completed_cycles + self.cycles)
            self.gui.canvas.update_cycle_axis_layout()
            self.gui.canvas.pan_to_right_end()
            self.gui.log_text("Continue simulation for " + str(self.cycles)
                              + " cycles. Total cycles: " + str(self.gui.completed_cycles))
        except ValueError:
            return self.command_manager.INVALID_ARGUMENT, \
                   "Cannot continue network. The number of cycles is not a positive integer."

        self.final_monitors_state = copy.deepcopy(command_manager.monitors.monitors_dictionary)
        self.final_devices_state = copy.deepcopy(command_manager.devices.devices_list)
        return self.command_manager.NO_ERROR, None

    def undo(self):
        """Undo continue command

        Return NO_ERROR, None if successful.
        """

        # Resets monitors to the state before continuing and also updates the cycles counters
        self.command_manager.monitors.monitors_dictionary = self.initial_monitors_state
        self.command_manager.devices.devices_list = self.initial_devices_state
        self.gui.update_cycles(self.initial_cycles)
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.canvas.pan_to_right_end()
        return self.command_manager.NO_ERROR, None

    def redo(self):
        """Redo continue command

        Return NO_ERROR, None if successful.
        """

        # Restore the state before undo
        self.command_manager.monitors.monitors_dictionary = self.final_monitors_state
        self.command_manager.devices.devices_list = self.final_devices_state
        self.gui.update_cycles(self.initial_cycles + self.cycles)
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.canvas.pan_to_right_end()
        return self.command_manager.NO_ERROR, None


class SaveCommand(Command):
    """Save command implementation."""

    def __init__(self, path):
        """Initialise path of the save destination."""
        self.command_manager = None
        self.gui = None
        self.path = path

    def execute(self, command_manager):
        """Execute save command

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui
        if self.path.split('.')[-1] != "defb":
            self.path += ".defb"
        with open(self.path, 'wb') as fp:
            data = [self.command_manager.monitors, self.command_manager.devices, self.command_manager.network,
                    self.command_manager.names, self.command_manager.gui.completed_cycles]
            pickle.dump(data, fp)

        self.gui.log_text("Save file " + self.path)
        return self.command_manager.NO_ERROR, None

    def undo(self):
        """Attempt to undo save command. Pass the undo call to the next command

        Return error_code, error_message
        """

        # Nothing to undo, undo the next command
        return self.command_manager.undo_command()

    def redo(self):
        """Attempt to redo save command. Pass the redo call to the next command

        Return error_code, error_message
        """

        # Nothing to redo, redo the next command
        return self.command_manager.redo_command()


class LoadCommand(Command):
    """Load command implementation."""

    def __init__(self, path):
        """Initialise path of the load file."""
        self.command_manager = None
        self.gui = None
        self.path = path

    def execute(self, command_manager):
        """Execute load command

        Return NO_ERROR, None if successful.
        """
        self.command_manager = command_manager
        self.gui = command_manager.gui
        if self.path.split('.')[-1] == "defb":  # File is an already built network
            with open(self.path, 'rb') as fp:
                try:
                    monitors, devices, network, names, completed_cycles = pickle.load(fp)
                except pickle.UnpicklingError:
                    return self.command_manager.INVALID_DEFINITION_FILE, None

        else:  # File is a definition file
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(self.path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            completed_cycles = 0
            if not parser.parse_network():
                errors = parser.error_to_gui
                self.gui.log_text('\n'.join(errors))
                error_message = errors[0]
                return self.command_manager.INVALID_DEFINITION_FILE, error_message

        # Set new instances
        self.command_manager.monitors = monitors
        self.command_manager.devices = devices
        self.command_manager.network = network
        self.command_manager.names = names
        self.command_manager.undo_stack.clear()
        self.command_manager.redo_stack.clear()
        self.gui.monitors = self.command_manager.monitors
        self.gui.devices = self.command_manager.devices
        self.gui.network = self.command_manager.network
        self.gui.names = self.command_manager.names
        self.gui.switches = self.gui.devices.find_devices(devices.SWITCH)
        swithces_names = [names.get_name_string(switch_id) for switch_id in self.gui.switches]
        self.gui.switches_select.Clear()
        for switch_name in swithces_names:
            self.gui.switches_select.Append(switch_name)
        self.gui.canvas.monitors = self.command_manager.monitors
        self.gui.monitors_select.Clear()
        for monitor_name in self.gui.monitors.get_signal_names()[0] + self.gui.monitors.get_signal_names()[1]:
            self.gui.monitors_select.Append(monitor_name)
        self.gui.canvas.devices = self.command_manager.devices
        self.gui.canvas.update_cycle_axis_layout()
        self.gui.update_cycles(completed_cycles)
        self.gui.switches_select.SetValue("")
        self.gui.switches_update_toggle()
        self.gui.monitors_select.SetValue("")
        self.gui.monitors_update_toggle()
        self.gui.log_text("Load file " + self.path)
        self.gui.path = self.path
        self.gui.load_file_text_box.SetValue(self.path.split('/')[-1])
        return self.command_manager.NO_ERROR, None

    def undo(self):
        """Attempt to undo load command. Pass the undo call to the next command

        Return error_code, error_message
        """

        # Nothing to undo, undo the next command
        return self.command_manager.undo_command()

    def redo(self):
        """Attempt to redo load command. Pass the redo call to the next command

        Return error_code, error_message
        """

        # Nothing to redo, redo the next command
        return self.command_manager.redo_command()


class CommandManager:
    """Manages commands and executes them.

    This class contains functions required for executing commands received from gui,
    and handle undo/redo operations.

    Parameters
    ----------
    gui - instance of the gui.Gui() class.
    names - instance of the names.Names() class.
    devices - instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors - instance of the monitors.Monitors() class.

    Public methods
    --------------
    execute_command(self, command): Executes command and return error_code and error_message.

    undo_command(self): Undo command and return error_code and error_message.

    redo_command(self): Redo command and return error_code and error_message.
    """

    def __init__(self, gui, names, devices, network, monitors):
        """Initialise commands errors and undo/redo stacks."""

        # Instances of classes
        self.gui = gui
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Stacks for undo/redo commands
        self.undo_stack = []
        self.redo_stack = []

        # Errors
        [self.NO_ERROR, self.INVALID_COMMAND, self.INVALID_ARGUMENT, self.SIGNAL_NOT_MONITORED,
         self.OSCILLATING_NETWORK, self.CANNOT_OPEN_FILE, self.NOTHING_TO_UNDO, self.NOTHING_TO_REDO,
         self.SIMULATION_NOT_STARTED, self.NO_FILE, self.INVALID_DEFINITION_FILE,
         self.UNKNOWN_ERROR] = names.unique_error_codes(12)

    def execute_command(self, command):
        """Execute command given as argument

        Return error_code, error_message
        """
        if self.gui.path is None and not isinstance(command, LoadCommand):
            self.gui.raise_error(self.NO_FILE)
            return self.NO_FILE, None
        error_code, error_message = command.execute(self)
        if error_code == self.NO_ERROR:
            self.redo_stack.clear()
            self.undo_stack.append(command)
        else:
            self.gui.raise_error(error_code, error_message)
        self.gui.update_toolbar()
        return error_code, error_message

    def undo_command(self):
        """Undo last command from undo stack

        Return error_code, error_message
        """
        if len(self.undo_stack) > 0:
            command = self.undo_stack.pop()
            self.redo_stack.append(command)
            error_code, error_message = command.undo()
            self.gui.update_toolbar()
            return error_code, error_message
        else:
            return self.NOTHING_TO_UNDO, None

    def redo_command(self):
        """Undo last command from redo stack

        Return error_code, error_message
        """
        if len(self.redo_stack) > 0:
            command = self.redo_stack.pop()
            self.undo_stack.append(command)
            error_code, error_message = command.redo()
            self.gui.update_toolbar()
            return error_code, error_message
        else:
            return self.NOTHING_TO_REDO, None
