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
        """Initialise attributes and types of syntax error."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.symbol = Symbol()
        # self.cursor = 0 # this might be needed
        self.error_count = 0
        self.exist_semerr = 0 # marking variable, once a semantic error detected, stop adding anything and detect syntax error only
        self.error_type_list = [self.NO_KEYWORD, self.NO_EQUALS, self.NO_SEMICOLON, self.NO_COMMA, self.NOT_NAME, self.NOT_NUMBER, self.NOT_SYMBOL] = self.names.unique_error_codes(7)

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
        """
        Parse the section starting with the keyword DEVICES.

        :return: flag, a boolean variable indicating if the DEVICES section is error-free.
                    If this section is error-free then return True, else return False
        """
        self.symbol = self.read_symbol()
        flag = True
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
        """
        Read in each syntax in DEVICE section, try to detect syntax errors before adding a device
        and raise possible semantic error when adding the device.
        If there is no error, then a new device is added according to the syntax.

        :return: a bool value indicating if a device can be added according to the current syntax.
                    If it can be added return True, else return False.
        """
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            return False
        identifier = self.symbol.id  # current self.symbol is the IDENTIFIER

        self.symbol = self.read_symbol() # read in the following '='
        if self.symbol.type == self.scanner.EQUALS:

            self.symbol = self.read_symbol() # the type of device
            if self.check_names() is False: # type not a name
                return False

            # device_type = self.symbol
            type_id = self.symbol.id # type of device to be passed to make_device
            self.symbol = self.read_symbol() # now self.symbol maybe ','or '/' or ';'

            param = None
            if self.symbol.type == self.scanner.BACKSLASH:
                param = self.get_parameter()
                if param is None:
                    # self.display_error(self.NOT_NUMBER) handled by check in get_param
                    return False

            if self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                if self.exist_semerr == 0:
                    # make device using the type and param, have 1 param
                    error_type = self.devices.make_device(identifier,type_id,param)
                    if error_type != self.devices.NO_ERROR:
                        self.exist_semerr = 1
                        self.display_error_device(error_type)
                        return False
                    else:
                        return True
                else:
                    return True
            elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_SEMICOLON)
                return False
            else:
                self.display_error(self.NO_COMMA) # no comma
                self.skip_erratic_part()
                return False

        else:
            self.display_error(self.NO_EQUALS) # no equal
            self.skip_erratic_part()
            return False

    def get_parameter(self):
        """
        Get the parameter value right after the backslash for syntax in DEVICE section.

        :return: If there is a number after the backslash then return this number, else return None
        """
        self.symbol = self.read_symbol() # read in a param
        if self.check_number() is False:
            return None
        param = int(self.symbol.id) # get the parameter value
        self.symbol = self.read_symbol() # match the loop in add_devices
        return param

    def parse_connections(self):
        """
        Parse the section starting with the keyword CONNECTIONS.

        :return: flag, a boolean variable indicating if the CONNECTIONS section is error-free.
                    If this section is error-free then return True, else return False
        """
        flag = True
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
        """
        Read in each syntax in CONNECTIONS section, try to detect syntax errors before adding a connection
        and raise possible semantic error when adding the connection.
        If there is no error, then a new connection is added according to the syntax.

        :return: a bool value indicating if a connection can be added according to the current syntax.
                    If it can be added return True, else return False.
        """
        sig1_device, sig1_port, syntax_err = self.signame()
        if syntax_err == 1:
            return False
        if self.symbol.type == self.scanner.EQUALS:
            sig2_device, sig2_port, syntax_err = self.signame()
            if syntax_err == 1:
                return False
            if self.exist_semerr == 0:
                # make connection between sig1 and sig2
                error_type = self.network.make_connection(sig1_device, sig1_port, sig2_device, sig2_port)
                if error_type != self.network.NO_ERROR:
                    self.exist_semerr = 1
                    self.display_error_connection(error_type)
                    return False
                else:
                    return True
            else:
                return True
        else:
            self.display_error(self.NO_EQUALS)  # no equal
            self.skip_erratic_part()
            return False

    def parse_monitors(self):
        """
        Parse the section starting with the keyword MONITORS.

        :return: flag, a boolean variable indicating if the MONITORS section is error-free.
                    If this section is error-free then return True, else return False
        """
        flag = True
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITORS_ID:
            if self.add_monitor() is False:
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                if self.add_monitor() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON:
                return flag
            else:
                return False
        else:
            self.display_error(self.NO_KEYWORD)
            return False # just raise error and exit

    def add_monitor(self):
        """
        Read in each syntax in MONITORS section, try to detect syntax errors before adding a monitor
        and raise possible semantic error when adding the monitor.
        If there is no error, then a new monitor is added according to the syntax.

        :return: a bool value indicating if a monitor can be added according to the current syntax.
                    If it can be added return True, else return False.
        """
        current_device, current_port, syntax_err = self.signame()  # add_monitor
        if syntax_err == 1:
            return False
        if self.exist_semerr == 0:
            error_type = self.monitors.make_monitor(current_device, current_port)
            if error_type != self.monitors.NO_ERROR:
                self.exist_semerr = 1
                self.display_error_monitor(error_type)
                return False
            else:
                return True
        else:
            return True

    def signame(self): # get the name of the signal
        """
        Get the signal names for syntax in CONNECTIONS and MONITORS section.

        :return: device_id (the id of current device)
                port_id (the id of the port to be monitored)
                syntax_err (a boolean variable indicating if there is a syntax error in current syntax)
                    if syntax_err=1 then there is a syntax error, otherwise syntax_err=0
        """
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            return None, None, 1
        device_id = self.symbol.id
        self.symbol = self.read_symbol()

        if self.symbol == self.scanner.DOT: # input
            self.symbol = self.read_symbol()
            if self.check_names() is False:
                return None, None, 1
            port_id = self.symbol.id
            self.read_symbol()
            return device_id, port_id, 0 # input & DTYPE

        elif self.symbol == self.scanner.COMMA or self.symbol == self.scanner.SEMICOLON or self.symbol == self.scanner.EQUALS: # output
            return device_id, None, 0 # output

        elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
            self.display_error(self.NO_SEMICOLON)
            return None, None, 1

        else:
            self.display_error(self.NO_COMMA)
            self.skip_erratic_part()
            return None, None, 1

    def check_names(self): # with skip_erratic_part(), self.symbol becomes the next ',' or ';' or KEYWORD or EOF
        """
        Check if current self.symbol is a valid NAME according to the EBNF grammar.
        If it is not a NAME, then raise syntax error and skip current syntax.

        :return: a bool value indicating if self.symbol is a NAME symbol.
                    If it is a NAME, return True, otherwise return False.
        """
        if self.symbol.type != self.scanner.NAME:  # the type of device should be a name
            self.display_error(self.NOT_NAME)
            self.skip_erratic_part()
            return False
        else:
            return True

    def check_number(self): # similar to check_names
        """
        Check if current self.symbol is a valid NUMBER according to the EBNF grammar.
        If it is not a NUMBER, then raise syntax error and skip current syntax.

        :return: a bool value indicating if self.symbol is a NUMBER symbol.
                    If it is a NUMBER, return True, otherwise return False.
        """
        if self.symbol.type != self.scanner.NUMBER:  # param should be a number
            self.display_error(self.NOT_NUMBER)
            self.skip_erratic_part()
            return False
        else:
            return True

    def display_error(self, error_type):
        """
        Report and locate a syntax error "error_type" defined in the Parser() class.

        :param error_type: a integer indicating the type of syntax error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.NO_KEYWORD:
            print("SyntaxError: Expected a keyword")
        elif error_type == self.NO_EQUALS:
            print("SyntaxError: Expected an equals sign")
        elif error_type == self.NO_SEMICOLON:
            print("SyntaxError: Expected a semicolon")
        elif error_type == self.NO_COMMA:
            print("SyntaxError: Expected a comma")
        elif error_type == self.NOT_NAME:
            print("SyntaxError: Expected a name")
        elif error_type == self.NOT_NUMBER:
            print("SyntaxError: Expected a number")
        elif error_type == self.NOT_SYMBOL:
            print("SyntaxError: Expected a legal symbol")
        else:
            print("Unknown error occurred") # not likely to occur
        # self.scanner.display_error_location(self.symbol.cursor_position)

    def display_error_device(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Devices() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
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
        else:
            print("Unknown error occurred")  # not likely to occur
        self.scanner.display_error_location(self.symbol.cursor_position)

    def display_error_connection(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Network() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
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
        else:
            print("Unknown error occurred") # not likely to occur
        self.scanner.display_error_location(self.symbol.cursor_position)

    def display_error_monitor(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Monitors() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.monitors.NOT_OUTPUT:
            print("SemanticError: NOT_OUTPUT")
        if error_type == self.monitors.MONITOR_PRESENT:
            print("SemanticError: MONITOR_PRESENT")
        else:
            print("Unknown error occurred") # not likely to occur
        self.scanner.display_error_location(self.symbol.cursor_position)

    def skip_erratic_part(self): # so-called recovery
        """
        This function is used for error recovery, it skips everything in the file before finding the next punctuation.
        These types of symbols defined in Scanner() are punctuations: COMMA, SEMICOLON, KEYWORD, EOF
        If a syntax error is detected, then this function is called.
        If a semantic error is detected, the parser stops adding anything, and it will only focus on syntax errors.

        :return: no returned value.
        """
        while self.symbol.type != self.scanner.COMMA: # go to the next comma within the section
            if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.SEMICOLON or self.symbol.type == self.scanner.EOF:
                return # end of section or file, must terminate here
            self.symbol = self.read_symbol()

    def read_symbol(self):
        """
        Read in the next symbol to be considered by the parser.
        If the scanner gets an invalid symbol, report syntax error and move on to get the next symbol.

        :return: current_symbol, the next valid symbol to be considered by the parser.
        """
        # self.cursor = self.symbol.cursor_position
        current_symbol = self.scanner.get_symbol()
        while current_symbol.type is None:
            self.display_error(self.NOT_SYMBOL)
            current_symbol = self.scanner.get_symbol()
        return current_symbol



#--------------------------------------local testing allowed-----------------------------------------------------------------------

# Function to make "open" function to work with StringIo objects
# def replace_open():
#     # The next line redefines the open function
#     old_open, builtins.open = builtins.open, lambda *args, **kwargs: args[0] \
#                                 if isinstance(args[0], StringIO) \
#                                 else old_open(*args, **kwargs)
#
#     # The methods below have to be added to the StringIO class in order for the "with" statement to work
#     # StringIO.__enter__ = lambda self: self
#     # StringIO.__exit__= lambda self, a, b, c: None
#
#
# replace_open()
# # Folder to keep test definition files
# test_file_dir = "test_definition_files"
#
# names = Names()
# devices = Devices(names)
# network = Network(names, devices)
# monitors = Monitors(names, devices, network)
# file_path = test_file_dir + "/test_model.txt"
# scanner = Scanner(file_path, names)
# parser = Parser(names, devices, network, monitors, scanner)
# flag = parser.parse_devices()