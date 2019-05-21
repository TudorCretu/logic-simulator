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
    def execute(self):
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
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class SwitchCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class MonitorCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class ZapCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class RunCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class ContinueCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class QuitCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class SaveCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

class LoadCommand(Command):
    """Help command implementation."""

    def __init__(self):
        pass

    def execute(self):
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

    def execute_command(self, command, *args):
        error_type = command.execute(*args)
        if error_type == self.NO_ERROR:
            self.redo_stack.clear()
            self.undo_stack.append(command)
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
