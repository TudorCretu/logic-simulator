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
        self.semerr_count = 0 # count semantic errors detected
        self.error_output = []
        self.error_cursor = []
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
        self.print_msg(success)
        return success

    def print_msg(self, success):
        """
        Display all the errors occurred during parsing.
        If there is no error, show "Parsed successfully! Valid definition file"

        :param success: a boolean variable, True if parsing is successful, False otherwise
        :return: no returned value
        """
        if success is True:
            print("Parsed successfully! Valid definition file!")
        else:
            print("Totally %d errors detected: %d syntax errors and %d semantic errors"%(self.error_count, self.error_count-self.semerr_count,self.semerr_count))
            for i in range(self.error_count):
                print(self.error_output[i])
                self.scanner.display_error_location(self.error_cursor[i])

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
        # print(self.names)

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
                # make device using the type and param
                error_type = self.devices.make_device(identifier,type_id,param)
                if error_type != self.devices.NO_ERROR:
                    self.semerr_count += 1
                    self.display_error_device(error_type)
                    return False
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
        if self.symbol.type != self.scanner.KEYWORD and self.symbol.type != self.scanner.EOF: # currently a semicolon
            self.symbol = self.read_symbol()
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
        sig1_device, sig1_port, syntax_err = self.signame(0)
        if syntax_err == 1:
            return False
        sig2_device, sig2_port, syntax_err = self.signame()
        if syntax_err == 1:
            return False

        # make connection between sig1 and sig2
        error_type = self.network.make_connection(sig1_device, sig1_port, sig2_device, sig2_port)
        if error_type != self.network.NO_ERROR:
            self.semerr_count += 1
            self.display_error_connection(error_type)
            return False
        else:
            return True

    def parse_monitors(self):
        """
        Parse the section starting with the keyword MONITORS.

        :return: flag, a boolean variable indicating if the MONITORS section is error-free.
                    If this section is error-free then return True, else return False
        """
        flag = True
        if self.symbol.type != self.scanner.KEYWORD and self.symbol.type != self.scanner.EOF:
            self.symbol = self.read_symbol()
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

        error_type = self.monitors.make_monitor(current_device, current_port)
        if error_type != self.monitors.NO_ERROR:
            self.semerr_count += 1
            self.display_error_monitor(error_type)
            return False
        else:
            return True

    def signame(self, side=1): # get the name of the signal
        """
        Get the signal names for syntax in CONNECTIONS and MONITORS section.

        :param side: 0 if the signal is on the left hand side, 1 if on the right hand side.
                    Considering the MONITORS section, the default value of side is 1.
        :return: device_id (the id of current device)
                port_id (the id of the port to be monitored)
                syntax_err (a boolean variable indicating if there is a syntax error in current syntax)
                    if syntax_err=1 then there is a syntax error, otherwise syntax_err=0
        """
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            self.skip_erratic_part()
            return None, None, 1
        device_id = self.symbol.id
        self.symbol = self.read_symbol()
        # current legal symbol: '.' ',' '=' ';'
        if self.symbol.type == self.scanner.DOT: # input
            self.symbol = self.read_symbol()
            if self.check_names() is False:
                self.skip_erratic_part()
                return None, None, 1
            port_id = self.symbol.id
            self.symbol = self.read_symbol() # current legal symbol: ',' '=' ';'
            if self.check_side(side) is True:
                return device_id, port_id, 0
            else:
                return None, None, 1

        elif self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
            if side == 1: # RHS
                return device_id, None, 0
            else:
                self.display_error(self.NO_EQUALS)
                return None, None, 1

        elif self.symbol.type == self.scanner.EQUALS: # output
            if side == 0: # LHS
                return device_id, None, 0 # output
            else:
                self.symbol = self.read_symbol() # does not matter because will skip_erratic_part
                if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                    self.display_error(self.NO_SEMICOLON)
                else:
                    self.display_error(self.NO_COMMA)
                self.skip_erratic_part()
                return None, None, 1

        elif self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
            if side == 1:
                self.display_error(self.NO_SEMICOLON)
            else:
                self.display_error(self.NO_EQUALS)
            return None, None, 1

        else:
            if side == 1:
                self.symbol = self.read_symbol()  # does not matter because will skip_erratic_part
                if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                    self.display_error(self.NO_SEMICOLON)
                else:
                    self.display_error(self.NO_COMMA)
            else:
                self.display_error(self.NO_EQUALS)
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

    def check_side(self, side):
        """
        Check syntax errors after getting a syntactically valid signal.

        :param side: 0 if the signal is on the left hand side, 1 if on the right hand side.
        :return: a bool value indicating if there is a syntax error after current signal.
                    If there is, return False, otherwise return True.
        """
        if side == 0:  # left hand side, expect a '='
            if self.symbol.type != self.scanner.EQUALS:
                self.display_error(self.NO_EQUALS)
                self.skip_erratic_part()
                return False
            else:
                return True  # input & DTYPE
        else:
            if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_SEMICOLON)
                self.skip_erratic_part()
                return False
            elif self.symbol.type == self.scanner.COMMA or self.symbol.type == self.scanner.SEMICOLON:
                return True  # input & DTYPE
            else:
                self.display_error(self.NO_COMMA)
                self.skip_erratic_part()
                return False

    def display_error(self, error_type):
        """
        Report and locate a syntax error "error_type" defined in the Parser() class.

        :param error_type: a integer indicating the type of syntax error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.NO_KEYWORD:
            self.error_output.append("SyntaxError: Expected a keyword")
        elif error_type == self.NO_EQUALS:
            self.error_output.append("SyntaxError: Expected an equals sign")
        elif error_type == self.NO_SEMICOLON:
            self.error_output.append("SyntaxError: Expected a semicolon")
        elif error_type == self.NO_COMMA:
            self.error_output.append("SyntaxError: Expected a comma")
        elif error_type == self.NOT_NAME:
            self.error_output.append("SyntaxError: Expected a name")
        elif error_type == self.NOT_NUMBER:
            self.error_output.append("SyntaxError: Expected a number")
        elif error_type == self.NOT_SYMBOL:
            self.error_output.append("SyntaxError: Expected a legal symbol")
        else:
            self.error_output.append("Unknown error occurred") # not likely to occur
        self.error_cursor.append(self.symbol.cursor_position)

    def display_error_device(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Devices() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.devices.INVALID_QUALIFIER:
            self.error_output.append("SemanticError: INVALID_QUALIFIER")
        elif error_type == self.devices.NO_QUALIFIER:
            self.error_output.append("SemanticError: NO_QUALIFIER")
        elif error_type == self.devices.QUALIFIER_PRESENT:
            self.error_output.append("SemanticError: QUALIFIER_PRESENT")
        elif error_type == self.devices.BAD_DEVICE:
            self.error_output.append("SemanticError: BAD_DEVICE")
        elif error_type == self.devices.DEVICE_PRESENT:
            self.error_output.append("SemanticError: DEVICE_PRESENT")
        else:
            self.error_output.append("Unknown error occurred")  # not likely to occur
        self.error_cursor.append(self.symbol.cursor_position)

    def display_error_connection(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Network() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.network.INPUT_TO_INPUT:
            self.error_output.append("SemanticError: INPUT_TO_INPUT")
        elif error_type == self.network.OUTPUT_TO_OUTPUT:
            self.error_output.append("SemanticError: OUTPUT_TO_OUTPUT")
        elif error_type == self.network.INPUT_CONNECTED:
            self.error_output.append("SemanticError: INPUT_CONNECTED")
        elif error_type == self.network.PORT_ABSENT:
            self.error_output.append("SemanticError: PORT_ABSENT")
        elif error_type == self.network.DEVICE_ABSENT:
            self.error_output.append("SemanticError: DEVICE_ABSENT")
        else:
            self.error_output.append("Unknown error occurred") # not likely to occur
        self.error_cursor.append(self.symbol.cursor_position)

    def display_error_monitor(self,error_type):
        """
        Report and locate a semantic error "error_type" defined in the Monitors() class.

        :param error_type: a integer indicating the type of semantic error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.monitors.NOT_OUTPUT:
            self.error_output.append("SemanticError: NOT_OUTPUT")
        elif error_type == self.monitors.MONITOR_PRESENT:
            self.error_output.append("SemanticError: MONITOR_PRESENT")
        else:
            self.error_output.append("Unknown error occurred") # not likely to occur
        self.error_cursor.append(self.symbol.cursor_position)

    def skip_erratic_part(self): # so-called recovery
        """
        This function is used for error recovery, it skips everything in the file before finding the next punctuation.
        These types of symbols defined in Scanner() are punctuations: COMMA, SEMICOLON, KEYWORD, EOF
        If a syntax error is detected, this function maybe called. Otherwise it is not called
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
        self.symbol = self.scanner.get_symbol()
        # print(self.symbol.cursor_position)
        while self.symbol.type is None:
            self.display_error(self.NOT_SYMBOL)
            self.symbol = self.scanner.get_symbol()
            # print(self.symbol.cursor_position)
            # print(current_symbol.type)
        return self.symbol



#--------------------------------------local testing allowed-----------------------------------------------------------------------

# # Folder to keep test definition files
# test_file_dir = "test_functions"
# names = Names()
# devices = Devices(names)
# network = Network(names, devices)
# monitors = Monitors(names, devices, network)
# file_path = test_file_dir + "/read_symbol.txt"
# scanner = Scanner(file_path, names)
# parser = Parser(names, devices, network, monitors, scanner)
# a = parser.read_symbol()
# a = parser.read_symbol()
# print(parser.error_cursor)
# # print(parser.error_cursor[0]) # the cursor is None, msg captured right
# parser.print_msg(False)
