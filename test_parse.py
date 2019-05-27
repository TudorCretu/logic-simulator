"""Test the parser module."""

import builtins
import pytest
import os

from names import Names
from scanner import Symbol, Scanner
from parse import Parser
from network import Network
from devices import Device, Devices
from monitors import Monitors

def create_parser(file_path):
    """Return a new instance of the Devices class."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    return parser

# -------------------------------------DEVICE Block tests----------------------------------------
def test_parse_devices_success():
    """Test if parse_devices() returns True correctly for a valid file"""

    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/fully_correct.txt"

    parser =create_parser(file_path)
    assert parser.parse_devices() is True

def test_DEVICES_missing_devices_keyword(capfd):
    """Test if parse_devices returns true correctly"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_devices_keyword_error.txt"
    parser =create_parser(file_path)
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a keyword"

def test_DEVICES_type_not_found_error(capfd):
    """Test if parse_devices returns true correctly"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/type_not_found_error.txt"
    parser =create_parser(file_path)
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "TypeNotFoundError: Device's type 'SWITCHEY' does not match one of the following:\n'CLOCK','SWITCH','AND','NAND','OR','NOR','XOR','DTYPE'"

def test_DEVICES_expected_name_error(capfd):
    """Test reporting of missing expected Name symbol in DEVICE block"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_name_error.txt"
    parser =create_parser(file_path)
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a name"

def test_DEVICES_resued_name_error(capfd):
    """Test if reuse of device name is reported in DEVICE block"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/reused_name_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "RepeatedIdentifierError: Device 'SW1' is already defined"


def test_DEVICES_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a comma"


def test_DEVICES_expected_equals_error(capfd):
    """Test if missing expected equals symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_equals_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected an equals sign"

def test_DEVICES_expected_number_error(capfd):
    """Test if a missing expected sumber symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_number_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a number"

def test_DEVICES_expected_semicolon_error(capfd):
    """Test if missing expected semicolon symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a semicolon"

def test_DEVICES_missing_parameter_error(capfd):
    """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/missing_parameter_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "MissingParameterError: Parameter value of Device 'SW1' is not specified"

def test_DEVICES_invalid_parameter_error(capfd):
    """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/invalid_parameter_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "InvalidParameterError: Parameter value of Device 'AND1' is not valid"
    
def test_DEVICES_excess_parameter_error(capfd):
    """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/excess_parameter_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "ExcessParametersError: Device 'XOR1' has too many parameters specified"

def test_DEVICES_mutliple_errors():
    """Test that a sequence of known errors are reported indicating proper recovery occurs
    within DEVICE block"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/multiple_errors.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    
    assert parser.error_output[0] == "SyntaxError: Expected a name"
    assert parser.error_output[1] == "RepeatedIdentifierError: Device 'SW2' is already defined"
    assert parser.error_output[2] == "InvalidParameterError: Parameter value of Device 'SW4' is not valid"
    assert parser.error_output[3] == "SyntaxError: Expected a comma"
    assert parser.error_output[4] == "SyntaxError: Expected a semicolon"

    


# -------------------------------------CONNECTION Block tests----------------------------------------
test_file_dir = "test_definition_files/test_connections"

def test_parse_connections_success():
    """Test if parse_devices returns true correctly"""

    file_path = test_file_dir + "/fully_correct.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is True

def test_CONNECTIONS_expected_name_error(capfd):
    """Test if missing name symbol in CONNECTIONS is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_name_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a name"


def test_CONNECTIONS_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a comma"

def test_CONNECTIONS_expected_equals_error(capfd):
    """Test if missing expected equals symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_equals_error.txt"
    parser =create_parser(file_path)
    parser.parse_devices()
    assert parser.parse_connections() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected an equals sign"
    

def test_CONNECTIONS_expected_semicolon_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a semicolon"
    
def test_CONNECTIONS_device_absent_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/device_absent_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "DeviceAbsentError:Device 'XOR8' is not defined"
    
                              
    
def test_CONNECTIONS_invalid_port_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/invalid_port_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "InvalidPortError: Device 'XOR1' does not have port '.I9'"
  
                              
def test_CONNECTIONS_2sig(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/input_2signals.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "InputPortConnectionPresentError: Connection between signals 'SW2' and 'XOR1.I1' already exists"
                              
def test_CONNECTIONS_input_input_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/input_input.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "IllegalConnectionError: Signal 'D1.CLEAR' and 'XOR1.I1' are both input signals"
    
def test_CONNECTIONS_output_output_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/output_output.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "IllegalConnectionError: Signal 'SW1' and 'SW2' are both output signals"

def test_CONNECTIONS_mutliple_errors():
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/multiple_errors.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    assert parser.parse_connections() is False


    assert parser.error_output[0] == "SyntaxError: Expected a name"
    assert parser.error_output[1] == "InvalidPortError: Device 'XOR1' does not have port '.I3'"
    assert parser.error_output[2] == "SyntaxError: Expected a semicolon"
    
# problem of DTYPE with no port specified ie XOR1.I1 = D1 ; # no dot for port                               
                              

# -------------------------------------MONITOR Block tests----------------------------------------
def test_parse_monitors_success():
    """Test if parse_monitors returns true correctly"""

    file_path = test_file_dir + "/fully_correct.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    parser.parse_connections()

    assert parser.parse_monitors() is True


def test_MONITORS_expected_name_error(capfd):
    """Test if missing expected name symbol is reported in MONITORS BLOCK"""

    test_file_dir = "test_definition_files/test_monitors"
    file_path = test_file_dir + "/expected_name_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    parser.parse_connections()

    assert parser.parse_monitors() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a name"

def test_MONITORS_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in MONITORS BLOCK"""

    test_file_dir = "test_definition_files/test_monitors"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    parser.parse_connections()
    assert parser.parse_monitors() is False

    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a comma"


def test_MONITORS_expected_semicolon_error(capfd):
    """Test if missing expected ; symbol is reported in MONITORS BLOCK"""
    test_file_dir = "test_definition_files/test_monitors"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)

    parser.parse_devices()
    parser.parse_connections()

    assert parser.parse_monitors() is False
    out,err = capfd.readouterr()
    assert parser.error_output[0] == "SyntaxError: Expected a semicolon"


def test_MONITORS_mutliple_errors():
    test_file_dir = "test_definition_files/test_monitors"
    pass
