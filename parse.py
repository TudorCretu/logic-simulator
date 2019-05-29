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
        self.semerr_count = 0  # count semantic errors detected
        self.error_output = []
        self.error_to_gui = []  # for error display in GUI
        self.error_cursor = []
        self.errline_num = []
        self.errline_pos = []
        self.error_type_list = [
            self.NO_KEYWORD_DEVICES, self.NO_KEYWORD_CONNECTIONS,
            self.NO_KEYWORD_MONITORS, self.NO_EQUALS, self.NO_SEMICOLON,
            self.NO_COMMA, self.NOT_NAME, self.NOT_NUMBER,
            self.NOT_SYMBOL] = self.names.unique_error_codes(9)

    def parse_network(self):
        """Parse the circuit definition file."""
        flag1 = self.parse_devices()
        flag2 = self.parse_connections()
        flag3 = self.parse_monitors()
        # illegal symbols counted here, not in each section
        success = (self.error_count == 0)
        if success is True:
            flag4, device_id, port_id = self.network.check_network()
            # oscillating network will be reported when running simulation
            # it is perhaps a runtime error, so not handled here
            if flag4 is False:
                self.semerr_count += 1
                self.error_count += 1
                port_str = self.names.get_name_string(port_id)
                device_str = self.names.get_name_string(device_id)
                self.error_output.append(
                    "InputPortNotConnectedError: Input port "
                    "'%s' of device '%s' is not connected"
                    % (port_str, device_str))
            success = (success and flag4)
        self.print_msg(success)
        return success

    def print_msg(self, success):
        """
        Display all the errors occurred during parsing.
        Build the string list for GUI error display
        If there is no error,
            put "Parsed successfully! Valid definition file"
        :param success: a boolean variable.
                    True if parsing is successful, False otherwise.
        :return: no returned value.
        """
        if success is True:
            print("Parsed successfully! Valid definition file!")
            self.error_to_gui.append(
                "Parsed successfully! Valid definition file!")
        else:
            print("File '%s' contains %d error(s): "
                  "%d syntax error(s) and %d semantic error(s)\n"
                  % (self.scanner.file.name.split('/')[-1], self.error_count,
                     self.error_count - self.semerr_count, self.semerr_count))
            self.error_to_gui.append("File '%s' contains %d error(s):"
                                     " %d syntax error(s) "
                                     "and %d semantic error(s)\n"
                                     % (self.scanner.file.name.split('/')[-1],
                                        self.error_count,
                                        self.error_count - self.semerr_count,
                                        self.semerr_count))
            n = len(self.error_cursor)
            if self.error_count > n:  # notice the unconnected input error
                for i in range(n):
                    print(self.error_output[i])
                    self.error_to_gui.append(self.error_output[i])
                    # self.out_for_gui.append(self.error_output[i])
                    self.error_to_gui.append(self.scanner.show_error_location(
                        self.errline_num[i],
                        self.errline_pos[i],
                        self.error_cursor[i]))
                print(self.error_output[n])
                self.error_to_gui.append(self.error_output[i])
            else:
                for i in range(n):
                    print(self.error_output[i])
                    self.error_to_gui.append(self.error_output[i])
                    self.error_to_gui.append(self.scanner.show_error_location(
                        self.errline_num[i],
                        self.errline_pos[i],
                        self.error_cursor[i]))

    def parse_devices(self):
        """
        Parse the section starting with the keyword DEVICES.
        :return: flag: a boolean variable indicating
                    if the DEVICES section is error-free.
                    If it is then return True, else return False
        """
        self.symbol = self.read_symbol()
        flag = True
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.DEVICES_ID:
            if self.add_device() is False:  # type not name
                flag = False

            while self.symbol.type == self.scanner.COMMA:
                # print(self.symbol.type)
                if self.add_device() is False:
                    flag = False

            if self.symbol.type == self.scanner.SEMICOLON:  # end of section
                return flag
            else:
                return False  # just end parsing this section
        else:
            self.display_error(self.NO_KEYWORD_DEVICES)  # no keyword
            return False  # just raise error and exit

    def add_device(self):
        """
        Read in each syntax in DEVICE section.
        Then try to detect syntax errors before adding a device
            and raise possible semantic errors.
        If there is no error, then a new device is added.
        :return: a bool value indicating
                if a device can be added.
                If it can be added return True, else return False.
        """
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            return False
        # current self.symbol is the IDENTIFIER
        identifier = self.symbol.id

        self.symbol = self.read_symbol()
        # read in the following '='
        if self.symbol.type == self.scanner.EQUALS:

            self.symbol = self.read_symbol()  # the type of device
            if self.check_names() is False:  # type not a name
                return False

            # type of device to be passed to make_device
            type_id = self.symbol.id
            self.symbol = self.read_symbol()
            # now self.symbol maybe ','or '/' or ';'

            param = None
            if self.symbol.type == self.scanner.FORWARDS_SLASH:
                param = self.get_parameter()
                if param is None:
                    # self.NOT_NUMBER handled by check in get_param()
                    return False

            if self.symbol.type == self.scanner.COMMA \
                    or self.symbol.type == self.scanner.SEMICOLON:
                if self.error_count == 0:
                    # make device using the type and param
                    error_type = self.devices.make_device(
                        identifier, type_id, param)
                    if error_type != self.devices.NO_ERROR:
                        self.semerr_count += 1
                        self.display_error_device(error_type,
                                                  identifier, type_id)
                        return False
                    else:
                        return True
                else:
                    return True  # no syntax error

            elif self.symbol.type == self.scanner.KEYWORD\
                    or self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_SEMICOLON)
                return False
            else:
                self.display_error(self.NO_COMMA)  # no comma
                self.skip_erratic_part()
                return False

        else:
            self.display_error(self.NO_EQUALS)  # no equal
            self.skip_erratic_part()
            return False

    def get_parameter(self):
        """
        Get the parameter value right after the forwards slash.
        :return: If there is a number after the forwards slash,
                then return the number 'param', else return None
        """
        self.symbol = self.read_symbol()  # read in a param
        if self.check_number() is False:
            return None
        param = int(self.symbol.id)  # get the parameter value
        self.symbol = self.read_symbol()  # match the loop in add_devices
        return param

    def parse_connections(self):
        """
        Parse the section starting with the keyword CONNECTIONS.
        :return: flag: a boolean variable indicating
                    if the CONNECTIONS section is error-free.
                    If it is then return True, else return False
        """
        flag = True
        if self.symbol.type != self.scanner.KEYWORD \
                and self.symbol.type != self.scanner.EOF:
            # currently a semicolon
            self.symbol = self.read_symbol()
        if self.symbol.type == self.scanner.KEYWORD \
                and self.symbol.id == self.scanner.CONNECTIONS_ID:
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
            self.display_error(self.NO_KEYWORD_CONNECTIONS)
            return False  # just raise error and exit

    def add_connection(self):
        """
        Read in each syntax in CONNECTIONS section.
        Then try to detect syntax errors before adding a connection
            and raise possible semantic errors.
        If there is no error, then a new connection is added.
        :return: a bool value indicating
                if this connection can be added.
                If it can be added return True, else return False.
        """
        sig1_device, sig1_port, syntax_err = self.signame(0)
        if syntax_err == 1:
            return False
        sig2_device, sig2_port, syntax_err = self.signame()
        if syntax_err == 1:
            return False
        if self.error_count == 0:
            # make connection between sig1 and sig2
            error_type, err_device, err_port = self.network.make_connection(
                sig1_device, sig1_port, sig2_device, sig2_port)
            if error_type != self.network.NO_ERROR:
                print(err_device)
                if err_device is None:
                    self.display_error_connection(error_type,
                                                  sig1_device, sig1_port,
                                                  sig2_device, sig2_port)
                else:
                    self.display_error_connection(error_type,
                                                  err_device, err_port)
                return False
            else:
                return True
        else:
            return True  # no syntax error

    def parse_monitors(self):
        """
        Parse the section starting with the keyword MONITORS.
        :return: flag: a boolean variable indicating
                    if MONITORS section is error-free.
                    If it is then return True, else return False
        """
        flag = True
        if self.symbol.type != self.scanner.KEYWORD\
                and self.symbol.type != self.scanner.EOF:
            self.symbol = self.read_symbol()
        if self.symbol.type == self.scanner.KEYWORD\
                and self.symbol.id == self.scanner.MONITORS_ID:
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
            self.display_error(self.NO_KEYWORD_MONITORS)
            return False  # just raise error and exit

    def add_monitor(self):
        """
        Read in each syntax in MONITORS section
        Then try to detect syntax errors before adding a monitor,
            and raise possible semantic errors.
        If there is no error, then a new monitor is added.
        :return: a bool value indicating
                if a monitor can be added.
                If it can be added return True, else return False.
        """
        current_device, current_port, syntax_err = self.signame()
        if syntax_err == 1:
            return False
        if self.error_count == 0:
            error_type = self.monitors.make_monitor(
                current_device, current_port)
            if error_type != self.monitors.NO_ERROR:
                self.semerr_count += 1
                self.display_error_monitor(
                    error_type, current_device, current_port)
                return False
            else:
                return True
        else:
            return True  # no syntax error

    def signame(self, side=1):  # get the name of the signal
        """
        Get the signal names in CONNECTIONS and MONITORS section.
        :param side: 0 if the signal is on the left hand side,
                    1 if on the right hand side.
                    The default value of side is 1.
        :return: device_id: the symbol id of current signal's device.
                port_id: the symbol id of current signal's port.
                syntax_err: a boolean variable indicating
                    if there is a syntax error in current syntax.
                    if syntax_err=1 then there is a syntax error,
                    otherwise syntax_err=0
        """
        self.symbol = self.read_symbol()
        if self.check_names() is False:
            self.skip_erratic_part()
            return None, None, 1
        device_id = self.symbol.id
        self.symbol = self.read_symbol()
        # current legal symbol: '.' ',' '=' ';'
        if self.symbol.type == self.scanner.DOT:  # input
            self.symbol = self.read_symbol()
            if self.check_names() is False:
                self.skip_erratic_part()
                return None, None, 1
            port_id = self.symbol.id
            self.symbol = self.read_symbol()
            # current legal symbol: ',' '=' ';'
            if self.check_side(side) is True:
                return device_id, port_id, 0
            else:
                return None, None, 1

        elif self.symbol.type == self.scanner.COMMA \
                or self.symbol.type == self.scanner.SEMICOLON:
            if side == 1:  # RHS
                return device_id, None, 0
            else:
                self.display_error(self.NO_EQUALS)
                return None, None, 1

        elif self.symbol.type == self.scanner.EQUALS:  # output
            if side == 0:  # LHS
                return device_id, None, 0  # output
            else:
                self.symbol = self.read_symbol()
                # does not matter because will skip_erratic_part
                if self.symbol.type == self.scanner.KEYWORD \
                        or self.symbol.type == self.scanner.EOF:
                    self.display_error(self.NO_SEMICOLON)
                else:
                    self.display_error(self.NO_COMMA)
                self.skip_erratic_part()
                return None, None, 1

        elif self.symbol.type == self.scanner.KEYWORD \
                or self.symbol.type == self.scanner.EOF:
            if side == 1:
                self.display_error(self.NO_SEMICOLON)
            else:
                self.display_error(self.NO_EQUALS)
            return None, None, 1

        else:
            if side == 1:
                self.symbol = self.read_symbol()
                # does not matter because will skip_erratic_part
                if self.symbol.type == self.scanner.KEYWORD\
                        or self.symbol.type == self.scanner.EOF:
                    self.display_error(self.NO_SEMICOLON)
                else:
                    self.display_error(self.NO_COMMA)
            else:
                self.display_error(self.NO_EQUALS)
            self.skip_erratic_part()
            return None, None, 1

    def check_names(self):
        """
        Check if self.symbol is a valid NAME in the EBNF grammar.
        If it is not a NAME, raise syntax error recover.
        :return: a bool value indicating if self.symbol is a NAME.
                    If it is, return True, otherwise return False.
        """
        # the type of device should be a name
        if self.symbol.type != self.scanner.NAME:
            self.display_error(self.NOT_NAME)
            self.skip_erratic_part()
            return False
        else:
            return True

    def check_number(self):  # similar to check_names
        """
        Check if self.symbol is a valid NUMBER in the EBNF grammar.
        If it is not a NUMBER, raise syntax error and recover.
        :return: a bool value indicating if self.symbol is a NUMBER.
                    If it is, return True, otherwise return False.
        """
        # param should be a number
        if self.symbol.type != self.scanner.NUMBER:
            self.display_error(self.NOT_NUMBER)
            self.skip_erratic_part()
            return False
        else:
            return True

    def check_side(self, side):
        """
        Check syntax errors after getting a syntactically valid signal.
        :param side: 0 if the signal is on the left hand side
                    1 if on the right hand side.
        :return: a bool value indicating
                    if there is a syntax error after current signal.
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
            if self.symbol.type == self.scanner.KEYWORD \
                    or self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_SEMICOLON)
                self.skip_erratic_part()
                return False
            elif self.symbol.type == self.scanner.COMMA \
                    or self.symbol.type == self.scanner.SEMICOLON:
                return True  # input & DTYPE
            else:
                self.display_error(self.NO_COMMA)
                self.skip_erratic_part()
                return False

    def display_error(self, error_type):
        """
        Report and locate a syntax error defined in the Parser().
        :param error_type: a integer indicating the type of error.
        :return: no returned value.
        """
        self.error_count += 1
        if error_type == self.NO_KEYWORD_DEVICES:
            self.error_output.append("SyntaxError: "
                                     "Expected a keyword 'DEVICES'")
        elif error_type == self.NO_KEYWORD_CONNECTIONS:
            self.error_output.append("SyntaxError: "
                                     "Expected a keyword 'CONNECTIONS'")
        elif error_type == self.NO_KEYWORD_MONITORS:
            self.error_output.append("SyntaxError: "
                                     "Expected a keyword 'MONITORS'")
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
            self.error_output.append("Unknown error occurred")
        self.error_cursor.append(self.symbol.cursor_position)
        self.errline_num.append(self.symbol.line_number)
        self.errline_pos.append(self.symbol.cursor_pos_at_start_of_line)

    def display_error_device(self, error_type,
                             identifier_id=None, type_id=None):
        """
        Report and locate a semantic error defined in the Devices().
        :param error_type: a integer indicating the type of semantic error.
                identifier_id: symbol id of the identifier
                type_id: symbol id of device type
        :return: no returned value.
        """
        self.error_count += 1
        self.semerr_count += 1
        device_id_str = self.names.get_name_string(identifier_id)
        if type_id is not None:
            device_type_str = self.names.get_name_string(type_id)
        if error_type == self.devices.INVALID_QUALIFIER:
            self.error_output.append(
                "InvalidParameterError: Parameter value of "
                "Device '%s' is not valid"
                % (device_id_str))
        elif error_type == self.devices.NO_QUALIFIER:
            self.error_output.append(
                "MissingParameterError: Parameter of "
                "Device '%s' is not specified"
                % (device_id_str))
        elif error_type == self.devices.QUALIFIER_PRESENT:
            self.error_output.append(
                "ExcessParametersError: Device '%s' has "
                "too many parameters specified"
                % (device_id_str))
        elif error_type == self.devices.BAD_DEVICE:
            self.error_output.append(
                "TypeNotFoundError: Device's type '%s' does not match "
                "one of the following:\n'CLOCK','SWITCH','AND','NAND',"
                "'OR','NOR','XOR','DTYPE'"
                % (device_type_str))
        elif error_type == self.devices.DEVICE_PRESENT:
            self.error_output.append(
                "RepeatedIdentifierError: Device '%s' is already defined"
                % (device_id_str))
        else:
            self.error_output.append("Unknown error occurred")
        self.error_cursor.append(self.symbol.cursor_position)
        self.errline_num.append(self.symbol.line_number)
        self.errline_pos.append(self.symbol.cursor_pos_at_start_of_line)

    def display_error_connection(self, error_type,
                                 sig1_device=None, sig1_port=None,
                                 sig2_device=None, sig2_port=None):
        """
        Report and locate a semantic error defined in the Network().
        :param error_type: a integer indicating the type of error.
                sig1_device: symbol id of device of first signal
                sig1_port: symbol id of port of first signal
                sig2_device: symbol id of device of second signal
                sig2_port: symbol id of port of second signal
        :return: no returned value.
        """
        self.error_count += 1
        self.semerr_count += 1
        if sig1_device is None:
            device_str1 = ""
        else:
            device_str1 = self.names.get_name_string(sig1_device)
        if sig1_port is None:
            port_str1 = ""
        else:
            port_str1 = "." + self.names.get_name_string(sig1_port)
        if sig2_device is None:
            device_str2 = ""
        else:
            device_str2 = self.names.get_name_string(sig2_device)
        if sig2_port is None:
            port_str2 = ""
        else:
            port_str2 = "." + self.names.get_name_string(sig2_port)
        if error_type == self.network.INPUT_TO_INPUT:
            self.error_output.append(
                "IllegalConnectionError: Signal '%s%s' "
                "and '%s%s' are both input signals"
                % (device_str1, port_str1, device_str2, port_str2))
        elif error_type == self.network.OUTPUT_TO_OUTPUT:
            self.error_output.append(
                "IllegalConnectionError: Signal '%s%s' "
                "and '%s%s' are both output signals"
                % (device_str1, port_str1, device_str2, port_str2))
        elif error_type == self.network.INPUT_CONNECTED:
            self.error_output.append(
                "InputPortConnectionPresentError: Signal "
                "'%s%s' is already connected"
                % (device_str1, port_str1))
        elif error_type == self.network.PORT_ABSENT:
            self.error_output.append(
                "InvalidPortError: Device '%s' does not have port '%s'"
                % (device_str1, port_str1))
        elif error_type == self.network.DEVICE_ABSENT:
            self.error_output.append(
                "DeviceAbsentError:Device '%s' is not defined"
                % (device_str1))
        else:
            self.error_output.append("Unknown error occurred")
        self.error_cursor.append(self.symbol.cursor_position)
        self.errline_num.append(self.symbol.line_number)
        self.errline_pos.append(self.symbol.cursor_pos_at_start_of_line)

    def display_error_monitor(self, error_type, device_id=None, port_id=None):
        """
        Report and locate a semantic error defined in the Monitors().
        :param error_type: a integer indicating the type of error.
                device_id: symbol id of device of current signal
                port_id: symbol id of port of current signal
        :return: no returned value.
        """
        self.error_count += 1
        self.semerr_count += 1
        device_str = self.names.get_name_string(device_id)
        if port_id is not None:
            port_str = "." + self.names.get_name_string(port_id)
        if error_type == self.monitors.NOT_OUTPUT:
            self.error_output.append(
                "MonitorNotOutputSignalError: Signal '%s%s' is not an output"
                % (device_str, port_str))
        elif error_type == self.monitors.MONITOR_PRESENT:
            self.error_output.append(
                "MonitorPresentError: Signal '%s%s' is already monitored"
                % (device_str, port_str))
        elif error_type == self.network.DEVICE_ABSENT:
            self.error_output.append(
                "DeviceAbsentError:Device '%s' is not defined" % (device_str))
        else:
            self.error_output.append("Unknown error occurred")
        self.error_cursor.append(self.symbol.cursor_position)
        self.errline_num.append(self.symbol.line_number)
        self.errline_pos.append(self.symbol.cursor_pos_at_start_of_line)

    def skip_erratic_part(self):  # recovery
        """
        This function is used for error recovery.
        It skips everything before finding the next punctuation.
        These symbols are punctuations: COMMA, SEMICOLON, KEYWORD, EOF
        For syntax errors, this function maybe called.
        For semantic errors, this function will not be called.
        :return: no returned value.
        """
        # go to the next comma within the section
        while self.symbol.type != self.scanner.COMMA:
            if self.symbol.type == self.scanner.KEYWORD \
                    or self.symbol.type == self.scanner.SEMICOLON \
                    or self.symbol.type == self.scanner.EOF:
                return  # end of section or file, must terminate here
            self.symbol = self.read_symbol()

    def read_symbol(self):
        """
        Read in the next symbol to be considered by the parser.
        If the scanner gets an invalid symbol, report syntax error,
            and then recover by moving on to get the next symbol.
        :return: current_symbol, the next valid symbol for the parser.
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


# --------------------------------------local testing allowed-----------------------------------------------------------------------

# # Folder to keep test definition files
# test_file_dir = "test_definition_files"
# names = Names()
# devices = Devices(names)
# network = Network(names, devices)
# monitors = Monitors(names, devices, network)
# file_path = test_file_dir + "/test_model.txt"
# scanner = Scanner(file_path, names)
# parser = Parser(names, devices, network, monitors, scanner)
# parser.parse_network()
