"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
import sys
from names import Names
from scanner import Symbol, Scanner
from network import Network
from devices import Device, Devices
from monitors import Monitors
import builtins
import os
from io import StringIO

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

        self.error_type_list = [self.NO_KEYWORD, self.NO_EQUALS, self.NO_SEMICOLON, self.NO_COMMA, self.NO_BACKSLASH, self.NOT_NAME, self.NOT_NUMBER, self.NOT_SYMBOL] = self.names.unique_error_codes(8)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        flag1 = self.parse_devices()
        flag2 = self.parse_connections()
        flag3 = self.parse_monitors()
        success = (flag1 and flag2 and flag3)
        # success = True
        return success

    def parse_devices(self):
        if self.symbol.type == self.scanner.EOF:
            return False
        flag = True  # any error changes this to false
        if self.symbol.type != self.scanner.KEYWORD:
            self.symbol = self.read_symbol()  # check keyword first

        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID:
            if self.add_device() is False:  # type not name
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                # print(self.symbol.type)
                if self.add_device() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON:  # end of this section
                return flag
            else:
                return False  # just end parsing this section
        else:
            self.display_error(self.NO_KEYWORD)  # no keyword
            return False  # just raise error and exit

    def add_device(self):
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            return False
        identifier = self.symbol  # current self.symbol is the IDENTIFIER

        self.symbol = self.read_symbol() # read in the following '='
        if self.symbol.type == self.scanner.EQUALS:

            self.symbol = self.read_symbol() # the type of device
            if self.check_names() is False: # type not a name
                return False

            device_type = self.symbol
            type_id = self.get_type_id(device_type) # type of device to be passed to make_device
            self.symbol = self.read_symbol() # now self.symbol maybe ','or '/' or ';'

            if self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                # make device with type only
                error_type = self.devices.make_device(identifier,type_id)
                if error_type != self.devices.NO_ERROR:
                    self.display_error_device(error_type)
                    return False
                return True

            elif self.symbol.type == self.scanner.BACKSLASH:
                param = self.get_parameter()

                if param is None:
                    # self.display_error(self.NOT_NUMBER) handled by check in get_param
                    return False
                elif self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                    # make device using the type and param, have 1 param
                    error_type = self.devices.make_device(identifier.id,type_id,param)
                    # print(identifier.id)
                    if error_type != self.devices.NO_ERROR:
                        self.display_error_device(error_type)
                        return False
                    return True
                elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                    self.display_error(self.NO_SEMICOLON)
                    return False
                else:
                    self.display_error(self.NO_COMMA) # no comma
                    self.skip_erratic_part()
                    return False

            elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_SEMICOLON)
                return False

            else:
                self.display_error(self.NO_COMMA) # no comma or '/' actually
                self.skip_erratic_part()
                return False

        else:
            self.display_error(self.NO_EQUALS) # no equal
            self.skip_erratic_part()
            return False

    def get_parameter(self):
        self.symbol = self.read_symbol() # read in a param
        if self.check_number() is False:
            return None
        param = int(self.symbol.id) # get the parameter value
        self.symbol = self.read_symbol() # match the loop in add_devices
        return param

    def get_type_id(self, device_type): # device type not specified in EBNF, so the parser handles this rather than scanner
        device_type_string = self.names.get_name_string(device_type.id)
        # print(device_type_string)
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
            type_id = self.devices.CLOCK
        elif device_type_string == "DTYPE":
            type_id = self.devices.D_TYPE
        else:
            return None
        return type_id

    def parse_connections(self):
        if self.symbol.type == self.scanner.EOF:
            return False
        flag = True  # any error changes this to false
        if self.symbol.type != self.scanner.KEYWORD:
            self.symbol = self.read_symbol()  # check keyword first

        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS_ID:
            if self.add_connection() is False:
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                if self.add_connection() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON:
                return flag
            else:
                return False
        else:
            self.display_error(self.NO_KEYWORD)
            return False # just raise error and exit

    def add_connection(self):
        sig1_device, sig1_port = self.signame()
        if self.symbol.type == self.scanner.EQUALS:
            sig2_device, sig2_port = self.signame()
            # make connection between sig1 and sig2
            error_type = self.network.make_connection(sig1_device, sig1_port, sig2_device, sig2_port)
            if error_type != self.network.NO_ERROR:
                self.display_error_connection(error_type)
                return False
            return True
        else:
            self.display_error(self.NO_EQUALS)  # no equal
            self.skip_erratic_part()
            return False

    def parse_monitors(self):
        if self.symbol.type == self.scanner.EOF:
            return False
        flag = True  # any error changes this to false
        if self.symbol.type != self.scanner.KEYWORD:
            self.symbol = self.read_symbol()  # check keyword first
            
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITORS_ID:
            current_device, current_port = self.signame() # add_monitor
            error_type = self.monitors.make_monitor(current_device,current_port)
            if error_type != self.monitors.NO_ERROR:
                self.display_error_monitor(error_type)
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                current_device, current_port = self.signame()
                error_type = self.monitors.make_monitor(current_device, current_port)
                if error_type != self.monitors.NO_ERROR:
                    self.display_error_monitor(error_type)

            if self.symbol.type == self.scanner.SEMICOLON:
                return flag
            else:
                return False
        else:
            self.display_error(self.NO_KEYWORD)
            return False # just raise error and exit

    def signame(self): # get the name of the signal
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            return None, None
        device_id = self.symbol
        self.symbol = self.read_symbol()

        if self.symbol == self.scanner.DOT: # input
            self.symbol = self.read_symbol()
            if self.check_names() is False:
                return None, None
            port_id = self.symbol
            self.read_symbol()
            return device_id, port_id # input & DTYPE

        elif self.symbol == self.scanner.COMMA or self.symbol == self.scanner.SEMICOLON: # output
            return device_id, None # output

        elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
            self.display_error(self.NO_SEMICOLON)
            return None, None

        else:
            self.display_error(self.NO_COMMA)
            self.skip_erratic_part()
            return None

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
        elif error_type == self.NOT_SYMBOL:
            print("SyntaxError: Expected a legal symbol")
        else:
            print("Unknown error occurred")

    def display_error_device(self,error_type):
        self.error_count += 1
        if error_type == self.devices.INVALID_QUALIFIER:
            print("SemanticError: INVALID_QUALIFIER")
        if error_type == self.devices.NO_QUALIFIER:
            print("SemanticError: NO_QUALIFIER")
        if error_type == self.devices.QUALIFIER_PRESENT:
            print("SemanticError: QUALIFIER_PRESENT")
        if error_type == self.devices.BAD_DEVICE:
            print("SemanticError: BAD_DEVICE")
        if error_type == self.devices.DEVICE_PRESENT:
            print("SemanticError: DEVICE_PRESENT")

    def display_error_connection(self,error_type):
        self.error_count += 1
        if error_type == self.network.INPUT_TO_INPUT:
            print("Semantic error: INPUT_TO_INPUT")
        if error_type == self.network.OUTPUT_TO_OUTPUT:
            print("Semantic error: OUTPUT_TO_OUTPUT")
        if error_type == self.network.INPUT_CONNECTED:
            print("Semantic error: INPUT_CONNECTED")
        if error_type == self.network.PORT_ABSENT:
            print("Semantic error: PORT_ABSENT")
        if error_type == self.network.DEVICE_ABSENT:
            print("Semantic error: DEVICE_ABSENT")

    def display_error_monitor(self,error_type):
        self.error_count += 1
        if error_type == self.monitors.NOT_OUTPUT:
            print("SemanticError: NOT_OUTPUT")
        if error_type == self.monitors.MONITOR_PRESENT:
            print("SemanticError: MONITOR_PRESENT")

    def skip_erratic_part(self): # so-called recovery
        while self.symbol.type != self.scanner.COMMA: # go to the next comma within the section
            if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.SEMICOLON or self.symbol.type == self.scanner.EOF:
                return # end of section or file, terminate
            self.symbol = self.read_symbol()

    def read_symbol(self):
        current_symbol = self.scanner.get_symbol()
        while current_symbol.type is None:
            self.display_error(self.NOT_SYMBOL)
            current_symbol = self.scanner.get_symbol()
        return current_symbol

# Function to make "open" function to work with StringIo objects
def replace_open():
    # The next line redefines the open function
    old_open, builtins.open = builtins.open, lambda *args, **kwargs: args[0] \
                                if isinstance(args[0], StringIO) \
                                else old_open(*args, **kwargs)

    # The methods below have to be added to the StringIO class in order for the "with" statement to work
    # StringIO.__enter__ = lambda self: self
    # StringIO.__exit__= lambda self, a, b, c: None


replace_open()
# Folder to keep test definition files
test_file_dir = "test_definition_files"

#names = Names()
#devices = Devices(names)
#network = Network(names, devices)
#monitors = Monitors(names, devices, network)
#file_path = test_file_dir + "/test_model.txt"
#scanner = Scanner(file_path, names)
#parser = Parser(names, devices, network, monitors, scanner)
#flag = parser.parse_devices()