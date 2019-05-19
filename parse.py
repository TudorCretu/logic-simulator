"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


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
        self.error_type_list = [self.NO_KEYWORD, self.NO_EQUALS, self.NO_SEMICOLON, self.NO_COMMA, self.NO_BACKSLASH] = range(5)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.parse_devices()
        self.parse_connections()
        self.parse_monitors()
        return True

    def parse_devices(self):
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID:
            self.symbol = self.scanner.get_symbol()
            self.add_device()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.add_device()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.display_error(self.NO_SEMICOLON) # no semicolon
                # self.skip_erratic_part() or just end parsing this section
        else:
            self.display_error(self.NO_KEYWORD) # no keyword
            # self.skip_erratic_part() or just raise error and exit

    def add_device(self):
        identifier = self.symbol # current self.symbol is the IDENTIFIER
        self.symbol = self.scanner.get_symbol() # read in the following '='
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol() # the type of device
            device_type = self.symbol
            self.symbol = self.scanner.get_symbol() # now self.symbol maybe ','or '/'
            if self.symbol.type == self.scanner.COMMA:
                # make device with type only
                self.symbol = self.scanner.get_symbol()
            elif self.symbol.type == self.scanner.BACKSLASH:
                param = []
                while self.symbol.type == self.scanner.BACKSLASH:
                    param.append(self.add_parameter())
                if self.symbol.type == self.scanner.COMMA:
                    # make device using the type and param
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(self.NO_COMMA)  # no comma
                    self.skip_erratic_part()
            else:
                self.display_error(self.NO_COMMA) # no comma
                self.skip_erratic_part()
        else:
            self.display_error(self.NO_EQUALS) # no equal
            self.skip_erratic_part()

    def add_parameter(self):
        self.symbol = self.scanner.get_symbol()
        param = self.symbol # get the parameter value
        self.symbol = self.scanner.get_symbol()
        return param

    def parse_connections(self):


    def parse_monitors(self):


    def display_error(self, error_type):
        self.error_count += 1
        if error_type == self.NO_KEYWORDS:
            print("SyntaxError: Expected a keyword")
        elif error_type == self.NO_EQUALS:
            print("SyntaxError: Expected an equals sign")
        elif error_type == self.NO_SEMICOLON:
            print("SyntaxError: Expected a semicolon")
        elif error_type == self.NO_COMMA:
            print("SyntaxError: Expected a comma")
        elif error_type == self.NO_BACKSLASH:
            print("SyntaxError: Expected a backslash")

    def skip_erratic_part(self):
        while self.symbol.type != self.scanner.COMMA: # go to the next comma within the section
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.KEYWORD or self.symbol.type == self.scanner.SEMICOLON or self.symbol.type == self.scanner.EOF:
                return # end of section or file, terminate
        self.symbol = self.scanner.get_symbol()