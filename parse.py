"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
# import sys
from scanner import Symbol, Scanner
from network import Network
from devices import Device, Devices
from monitors import Monitors

class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.symbol = Symbol()
        self.error_count = 0
        self.error_type_list = [self.NO_KEYWORD, self.NO_EQUALS, self.NO_SEMICOLON, self.NO_COMMA, self.NO_BACKSLASH, self.NOT_NAME, self.NOT_NUMBER, self.DUPLICATE] = self.names.unique_error_code(8)
        self.monitoring_list = []

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        flag1 = self.parse_devices()
        flag2 = self.parse_connections()
        flag3 = self.parse_monitors()
        success = (flag1 and flag2 and flag3)
        return success

    def parse_devices(self):
        flag = True # any error changes this to false
        self.symbol = self.scanner.get_symbol() # check keyword first
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID:
            if self.add_device() is False: # type not name
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                if self.add_device() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON: # end of this section
                return flag
            else:
                self.display_error(self.NO_SEMICOLON) # no semicolon
                return False
                # self.skip_erratic_part() or just end parsing this section
        else:
            self.display_error(self.NO_KEYWORD) # no keyword
            return False
            # self.skip_erratic_part() or just raise error and exit

    def add_device(self):
        self.symbol = self.scanner.get_symbol()
        if self.check_names() is False:
            return False
        identifier = self.symbol  # current self.symbol is the IDENTIFIER

        self.symbol = self.scanner.get_symbol() # read in the following '='
        if self.symbol.type == self.scanner.EQUALS:

            self.symbol = self.scanner.get_symbol() # the type of device
            if self.check_names() is False: # type not a name
                return False

            device_type = self.symbol
            type_id = self.get_type_id(device_type)

            if type_id is None:
                self.display_error(self.devices.BAD_DEVICE)
                self.skip_erratic_part()
                return False
            self.symbol = self.scanner.get_symbol() # now self.symbol maybe ','or '/'

            if self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                # make device with type only
                error_type = self.devices.make_device(identifier,device_type)
                if error_type == self.devices.NO_ERROR:
                    return True
                else:
                    self.display_error(error_type)
                    return False

            elif self.symbol.type == self.scanner.BACKSLASH:
                param = []
                while self.symbol.type == self.scanner.BACKSLASH:
                    if self.add_parameter() is False: # param not a number
                        return False
                    param.append(self.add_parameter())

                if self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                    # make device using the type and param
                    error_type = self.devices.make_device(identifier,device_type,param[0])
                    # we are told at most one property is needed，semantic errors may be raised here
                    if error_type == self.devices.NO_ERROR:
                        return True
                    else:
                        self.display_error(error_type)
                        return False
                else:
                    self.display_error(self.NO_COMMA)  # no comma
                    self.skip_erratic_part()
                    return False

            else:
                self.display_error(self.NO_COMMA) # no comma or '/' actually
                self.skip_erratic_part()
                return False

        else:
            self.display_error(self.NO_EQUALS) # no equal
            self.skip_erratic_part()
            return False

    def add_parameter(self):
        self.symbol = self.scanner.get_symbol() # read in a param
        if self.check_number() is False:
            return False
        param = self.symbol # get the parameter value
        self.symbol = self.scanner.get_symbol() # match the loop in add_devices
        return param

    def get_type_id(self, device_type):
        device_type_string = self.names.get_name_string(device_type.id)
        if device_type_string == "AND":
            type_id = self.devices.AND
        elif device_type_string == "NAND":
            type_id = self.devices.NAND
        elif device_type_string == "OR":
            type_id = self.devices.OR
        elif device_type_string == "NOR":
            type_id = self.devices.NOR
        elif device_type_string == "XOR":
            type_id = self.devices.XOR
        elif device_type_string == "SWITCH":
            type_id = self.devices.SWITCH
        elif device_type_string == "CLOCK":
            type_id = self.devices.SWITCH
        elif device_type_string == "DTYPE":
            type_id = self.devices.SWITCH
        else:
            return None
        return type_id

    def parse_connections(self):
        flag = True
        self.symbol = self.scanner.get_symbol()  # check keyword first
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS_ID:
            if self.add_connection() is False:
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                if self.add_connection() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON:
                return flag
            else:
                self.display_error(self.NO_SEMICOLON)
                return False
        else:
            self.display_error(self.NO_KEYWORD)
            return False
            # self.skip_erratic_part() or just raise error and exit

    def add_connection(self):
        signal1 = self.signame()
        if signal1 is None:
            return False
        if self.symbol.type == self.scanner.EQUALS:
            signal2 = self.signame()
            if signal2 is None:
                return False
            # make connection between sig1 and sig2
            return True
        else:
            self.display_error(self.NO_EQUALS)  # no equal
            self.skip_erratic_part()
            return False

    def parse_monitors(self):
        flag = True
        self.symbol = self.scanner.get_symbol()  # check keyword first
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITORS_ID:
            current_device, current_port = self.signame()
            if current_device is None:
                flag = False
            else:
                error_type = self.monitors.make_monitor(current_device,current_port)
                if error_type != self.monitors.NO_ERROR:
                    self.display_error(error_type)
                    flag = False

            while self.symbol.type == self.scanner.COMMA:
                current_device, current_port = self.signame()
                if current_device is None:
                    flag = False
                else:
                    error_type = self.monitors.make_monitor(current_device, current_port)
                    if error_type != self.monitors.NO_ERROR:
                        self.display_error(error_type)
                        flag = False

            if self.symbol.type == self.scanner.SEMICOLON:
                return flag
            else:
                self.display_error(self.NO_SEMICOLON)
                return False
        else:
            self.display_error(self.NO_KEYWORD)
            return False
            # self.skip_erratic_part() or just raise error and exit

    def signame(self): # get the name of the signal
        self.symbol = self.scanner.get_symbol()
        if self.check_names() is False:
            return None, None
        device_id = self.symbol
        self.symbol = self.scanner.get_symbol()
        if  self.symbol == self.scanner.DOT: # input
            self.symbol = self.scanner.get_symbol()
            if self.check_names() is False:
                return None, None

            port_id = self.symbol
            self.scanner.get_symbol()
            return device_id, port_id # input & DTYPE

        elif self.symbol == self.scanner.COMMA or self.symbol == self.scanner.SEMICOLON: # output
            return device_id, None # output

        else:
            self.display_error(self.NO_COMMA)
            self.skip_erratic_part()
            return None

    def find(self, x):
        for m in self.monitoring_list:
            if x == m:
                return True
        return False

    def check_names(self): # skip erratic part then symbol becomes the next ',' or ';' or KEYWORD or EOF
        if self.symbol.type != self.scanner.NAME:  # the type of device should be a name
            self.display_error(self.NOT_NAME)
            self.skip_erratic_part()
            return False
        else:
            return True

    def check_number(self): # similar to check_names
        if self.symbol.type != self.scanner.NUMBER:  # param should be a number
            self.display_error(self.NOT_NUMBER)
            self.skip_erratic_part()
            return False
        else:
            return True

    def display_error(self, error_type):
        self.error_count += 1
        if error_type == self.NO_KEYWORD:
            print("SyntaxError: Expected a keyword")
        elif error_type == self.NO_EQUALS:
            print("SyntaxError: Expected an equals sign")
        elif error_type == self.NO_SEMICOLON:
            print("SyntaxError: Expected a semicolon")
        elif error_type == self.NO_COMMA:
            print("SyntaxError: Expected a comma")
        # elif error_type == self.NO_DOT:
        #     print("SyntaxError: Expected a backslash")
        elif error_type == self.NO_BACKSLASH:
            print("SyntaxError: Expected a backslash")
        elif error_type == self.NOT_NAME:
            print("SyntaxError: Expected a name")
        elif error_type == self.NOT_NUMBER:
            print("SyntaxError: Expected a number")
        else:
            print("Unknown error occurred")

    def skip_erratic_part(self): # so-called recovery
        while self.symbol.type != self.scanner.COMMA: # go to the next comma within the section
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.SEMICOLON or self.symbol.type == self.scanner.EOF:
                return # end of section or file, terminate