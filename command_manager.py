"""Execute commands and stores system states.

Used in the Logic Simulator project to enable save/load undo/redo operations in the gui.

Classes
-------
Command - stores device properties.
CommandManager - makes and stores all the devices in the logic network.
"""

import abc


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
        self.command_manager = None
        self.gui = None
        pass

    def execute(self, command_manager):
        self.command_manager = command_manager
        self.gui = command_manager.gui

        text = "User commands:\n" + \
               "r N         - run the simulation for N cycles\n" + \
               "c N         - continue the simulation for N cycles\n" + \
               "s X N     - set switch X to N (0 or 1)\n" + \
               "m X       - set a monitor on signal X\n" + \
               "z X         - zap the monitor on signal X\n" + \
               "h             - help (this command)\n" + \
               "q            - quit the program"
        self.gui.log_text(text)
        return self.command_manager.NO_ERROR, None

    def undo(self):
        pass

    def redo(self):
        pass


class SwitchCommand(Command):
    """Help command implementation."""

    def __init__(self, *args):
        self.command_manager = None
        self.gui = None
        self.switch_name = args[0]
        self.value = args[1]

    def execute(self, command_manager):
        """Set the state of a switch"""
        self.command_manager = command_manager
        self.gui = command_manager.gui

        device_id = self.command_manager.names.query(self.switch_name)
        if device_id is not None and device_id in self.gui.switches:
            try:
                self.value = self.value
                if self.value == self.command_manager.devices.LOW or self.value == self.command_manager.devices.HIGH:
                    self.command_manager.devices.set_switch(device_id, self.value)
                    self.gui.log_text("Set switch " + self.switch_name + " to  " + str(self.value))
                    self.gui.update_switches_toggle()
                else:
                    raise ValueError
            except ValueError:
                return self.command_manager.INVALID_ARGUMENT, "Switch can be set to only 0 or 1."
        else:
            return self.command_manager.INVALID_ARGUMENT, "Device " + self.switch_name + " is not a SWITCH"
        return command_manager.NO_ERROR, None

    def undo(self):
        """Reverse the value set to a switch"""
        self.value = 1 - self.value
        error_code, error_message = self.execute(self.command_manager)
        return error_code, error_message

    def redo(self):
        """Set again the value to a switch"""
        # redo can be called only after undo is called, so change value back to the original
        self.value = 1 - self.value
        error_code, error_message = self.execute(self.command_manager)
        return error_code, error_message


class MonitorCommand(Command):
    """Help command implementation."""

    def __init__(self, signal_name):
        self.command_manager = None
        self.gui = None
        self.signal_name = signal_name

    def execute(self, command_manager):
        self.command_manager = command_manager
        self.gui = command_manager.gui

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
        return command_manager.NO_ERROR, None

    def undo(self):
        pass

    def redo(self):
        pass


class ZapCommand(Command):
    """Help command implementation."""

    def __init__(self, signal_name):
        self.command_manager = None
        self.gui = None
        self.signal_name = signal_name
        pass

    def execute(self, command_manager):
        self.command_manager = command_manager
        self.gui = command_manager.gui

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

        return command_manager.NO_ERROR, None

    def undo(self):
        return self.command_manager.NO_ERROR, None

    def redo(self):
        return self.command_manager.NO_ERROR, None


class RunCommand(Command):
    """Help command implementation."""

    def __init__(self, cycles):
        self.command_manager = None
        self.gui = None
        self.cycles = cycles

    def execute(self, command_manager):
        """Run simulation from start for a number of cycles"""
        self.command_manager = command_manager
        self.gui = command_manager.gui

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
                    return (self.command_manager.OSCILLATING_NETWORK,
                            "Cannot run network. The network doesn't have a stable state.")
            self.gui.update_cycles(self.cycles)
            self.gui.log_text("Run simulation for " + str(self.cycles) + " cycles")

        except ValueError:
            return (self.command_manager.INVALID_ARGUMENT,
                    "Cannot run network. The number of cycles is not a positive integer.")

    def undo(self):
        pass

    def redo(self):
        pass


class ContinueCommand(Command):
    """Help command implementation."""

    def __init__(self, cycles):
        self.command_manager = None
        self.gui = None
        self.cycles = cycles

    def execute(self, command_manager):
        self.command_manager = command_manager
        self.gui = command_manager.gui

        if self.gui.completed_cycles == 0:
            return self.command_manager.SIMULATION_NOT_STARTED, None
        try:
            cycles = int(self.cycles)
            if cycles < 0:
                raise ValueError
            cycles = int(cycles)
            for _ in range(self.cycles):
                if self.command_manager.network.execute_network():
                    self.command_manager.monitors.record_signals()
                else:
                    return (self.command_manager.OSCILLATING_NETWORK,
                            "Cannot continue network. The network doesn't have a stable state.")
            self.gui.update_cycles(self.gui.completed_cycles + self.cycles)
            self.gui.log_text("Continue simulation for " + str(cycles)
                              + " cycles. Total cycles: " + str(self.gui.completed_cycles))
        except ValueError:
            return (self.command_manager.INVALID_ARGUMENT,
                    "Cannot continue network. The number of cycles is not a positive integer.")

    def undo(self):
        pass

    def redo(self):
        pass


class SaveCommand(Command):
    """Help command implementation."""

    def __init__(self, path):
        self.command_manager = None
        self.path = path

    def execute(self, command_manager):
        self.command_manager = command_manager
        pass

    def undo(self):
        pass

    def redo(self):
        pass


class LoadCommand(Command):
    """Help command implementation."""

    def __init__(self, path):
        self.command_manager = None
        self.path = path

    def execute(self, command_manager):
        self.command_manager = command_manager
        pass

    def undo(self):
        pass

    def redo(self):
        pass


class CommandManager:
    """Make and store devices.

    This class contains many functions for making devices and ports.
    It stores all the devices in a list.

    Parameters
    ----------
    names: instance of the names.Names() class.

    Public methods
    --------------
    get_device(self, device_id): Returns the Device object corresponding
                                 to the device ID.

    """

    def __init__(self, gui, names, devices, network, monitors):
        """Initialise devices list and constants."""

        # Instances of classes
        self.gui = gui
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.undo_stack = []
        self.redo_stack = []

        # Errors
        [self.NO_ERROR, self.INVALID_COMMAND, self.INVALID_ARGUMENT, self.SIGNAL_NOT_MONITORED,
         self.OSCILLATING_NETWORK, self.CANNOT_OPEN_FILE, self.NOTHING_TO_UNDO, self.NOTHING_TO_REDO,
         self.SIMULATION_NOT_STARTED, self.UNKNOWN_ERROR] = names.unique_error_codes(10)

    def execute_command(self, command):
        error_type, error_message = command.execute(self)
        if error_type == self.NO_ERROR:
            self.redo_stack.clear()
            self.undo_stack.append(command)
        else:
            self.gui.raise_error(error_type, error_message)
        return error_type

    def undo_command(self):
        command = self.undo_stack.pop()
        self.redo_stack.append(command)
        error_type = command.redo()
        return error_type

    def redo_command(self):
        command = self.redo_stack.pop()
        self.undo_stack.append(command)
        error_type = command.redo()
        return error_type
