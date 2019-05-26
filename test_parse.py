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

# --------------------------------Basic Functionality tests----------------------------------------
def test_read_symbol():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/read_symbol.txt"
    parser =create_parser(file_path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.KEYWORD
    assert parser.symbol.id == parser.scanner.DEVICES_ID

def test_skip_erratic_part():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.skip_erratic_part()
    assert parser.symbol.type == parser.scanner.COMMA

def test_display_error(capfd):
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.display_error(parser.NO_EQUALS)
    out, err = capfd.readouterr()
    assert out == "SyntaxError: Expected an equals sign\n"

def test_display_error(capfd):
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.display_error(parser.NO_EQUALS)
    out, err = capfd.readouterr()
    assert out == "SyntaxError: Expected an equals sign\n"

def test_display_error_device(capfd):
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.display_error_device(parser.devices.BAD_DEVICE)
    out, err = capfd.readouterr()
    assert out == "SemanticError: BAD_DEVICE\n"

def test_display_error_connection(capfd):
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.display_error_connection(parser.network.INPUT_TO_INPUT)
    out, err = capfd.readouterr()
    assert out == "SemanticError: INPUT_TO_INPUT\n"

def test_display_error_monitor(capfd):
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/skip_erratic_part.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    parser.display_error_monitor(parser.monitors.NOT_OUTPUT)
    out, err = capfd.readouterr()
    assert out == "SemanticError: NOT_OUTPUT\n"

def test_check_names():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/check_names.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.NAME
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type != parser.scanner.NAME

def test_check_names():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/check_numbers.txt"
    parser = create_parser(file_path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.NUMBER
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type != parser.scanner.NUMBER

def test_signame():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/signame.txt"
    parser = create_parser(file_path)
    device_id, port_id, syntax_err = parser.signame()
    assert device_id is not None
    assert port_id is not None
    assert syntax_err == 0
    device_id, port_id, syntax_err = parser.signame()
    assert device_id is not None
    assert port_id is None
    assert syntax_err == 0
    device_id, port_id, syntax_err = parser.signame()
    assert device_id is None
    assert port_id is None
    assert syntax_err == 1

def test_get_parameter():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/get_parameter.txt"
    parser = create_parser(file_path)
    param = parser.get_parameter()
    assert param == 80
    param = parser.get_parameter()
    assert param is None

def test_add_device():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/add_device.txt"
    parser = create_parser(file_path)
    flag = parser.add_device()
    assert flag is True
    flag = parser.add_device()
    assert flag is False
    flag = parser.add_device()
    assert flag is False
    flag = parser.add_device()
    assert flag is True
    flag = parser.add_device()
    assert flag is False

def test_parse_devices():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/parse_device.txt"
    parser = create_parser(file_path)
    flag = parser.parse_devices()
    assert flag is True

def test_add_connection():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/add_connection.txt"
    parser = create_parser(file_path)
    flag = parser.parse_devices()
    assert flag is True
    parser.symbol = parser.read_symbol()
    flag = parser.add_connection()
    assert flag is True
    flag = parser.add_connection()
    assert flag is False
    flag = parser.add_connection()
    assert flag is True
    flag = parser.add_connection()
    assert flag is True

    flag = parser.add_connection()
    assert flag is True
    # alternative for this last add_connection():
    # device_id1, port_id1, syntax_err = parser.signame()
    # assert port_id1 is None
    # device_id2, port_id2, syntax_err = parser.signame()
    # assert port_id2 is None
    # err = parser.network.make_connection(device_id1, port_id1, device_id2, port_id2)
    # assert err == parser.network.DEVICE_ABSENT

    flag = parser.add_connection()
    assert flag is False


def test_parse_connections():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/parse_connection.txt"
    parser = create_parser(file_path)
    _ = parser.parse_devices()
    flag = parser.parse_connections()
    assert flag is True

def test_parse_monitors():
    test_file_dir = "test_definition_files/test_functions"
    file_path = test_file_dir + "/parse_monitor.txt"
    parser = create_parser(file_path)
    _ = parser.parse_devices()
    _ = parser.parse_connections()
    flag = parser.parse_monitors()
    assert flag is True

# def test_parse_network():
#     test_file_dir = "test_definition_files/test_functions"
#     file_path = test_file_dir + "/parse_network.txt"
#     parser = create_parser(file_path)
#     flag = parser.parse_network()
#     assert flag is True

# -------------------------------------DEVICE Block tests----------------------------------------
# def test_parse_devices_success():
#     """Test if parse_devices() returns True correctly for a valid file"""
#
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/fully_correct.txt"
#
#     parser =create_parser(file_path)
#     assert parser.parse_devices() is True
#
# def test_DEVICES_missing_devices_keyword(capfd):
#     """Test if parse_devices returns true correctly"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_devices_keyword_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a keyword\n"
#
#
# def test_DEVICES_expected_name_error(capfd):
#     """Test reporting of missing expected Name symbol in DEVICE block"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_name_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a name\n"
#
# def test_DEVICES_resued_name_error(capfd):
#     """Test if reuse of device name is reported in DEVICE block"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/reused_name_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SemanticError: DEVICE_PRESENT\n"
#
#
# def test_DEVICES_expected_comma_error(capfd):
#     """Test if missing expected comma symbol is reported in DEVICE BLOCK"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_comma_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a comma\n"
#
#
# def test_DEVICES_expected_equals_error(capfd):
#     """Test if missing expected equals symbol is reported in DEVICE BLOCK"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_equals_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected an equals sign\n"
#
# def test_DEVICES_expected_number_error(capfd):
#     """Test if a missing expected sumber symbol is reported in DEVICE BLOCK"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_number_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a number\n"
#
# def test_DEVICES_expected_semicolon_error(capfd):
#     """Test if missing expected semicolon symbol is reported in DEVICE BLOCK"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/expected_semicolon_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a semicolon\n"
#
# def test_DEVICES_parameter_error(capfd):
#     """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
#     test_file_dir = "test_definition_files/test_devices"
#     file_path = test_file_dir + "/parameter_error.txt"
#     parser =create_parser(file_path)
#
#     assert parser.parse_devices() is False
#     out,err = capfd.readouterr()
#     assert out == "This specific device needs parameter preceded by a '/'  BUT AT THE MOMENT NOT HANDLED"
#     # not handled
#
# def test_DEVICES_mutliple_errors():
#     """Test that a sequence of known errors are reported indicating proper recovery occurs
#     within DEVICE block"""
#     pass
#
#
# -------------------------------------CONNECTION Block tests----------------------------------------
# test_file_dir = "test_definition_files/test_connections"
#
# def test_parse_connections_success():
#     """Test if parse_devices returns true correctly"""
#
#     file_path = test_file_dir + "/fully_correct.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     assert parser.parse_connections() is True
#
# def test_CONNECTIONS_expected_name_error(capfd):
#     """Test if missing name symbol in CONNECTIONS is reported in CONNECTIONS BLOCK"""
#     test_file_dir = "test_definition_files/test_connections"
#     file_path = test_file_dir + "/expected_name_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     assert parser.parse_connections() is False
#
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a name\n"
#
#
# def test_CONNECTIONS_expected_comma_error(capfd):
#     """Test if missing expected comma symbol is reported in CONNECTIONS BLOCK"""
#     test_file_dir = "test_definition_files/test_connections"
#     file_path = test_file_dir + "/expected_comma_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     assert parser.parse_connections() is False
#
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a comma\n"
#
# def test_CONNECTIONS_expected_dot_error(capfd):
#     test_file_dir = "test_definition_files/test_connections"
#     pass
#
# def test_CONNECTIONS_expected_semicolon_error(capfd):
#     """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
#     test_file_dir = "test_definition_files/test_connections"
#     file_path = test_file_dir + "/expected_semicolon_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     assert parser.parse_connections() is False
#
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a semicolon\n"
#
# def test_CONNECTIONS_mutliple_errors():
#     test_file_dir = "test_definition_files/test_connections"
#     pass
#
# -------------------------------------MONITOR Block tests----------------------------------------
# def test_parse_monitors_success():
#     """Test if parse_monitors returns true correctly"""
#
#     file_path = test_file_dir + "/fully_correct.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     parser.parse_connections()
#
#     assert parser.parse_monitors() is True
#
#
# def test_MONITORS_expected_name_error(capfd):
#     """Test if missing expected name symbol is reported in MONITORS BLOCK"""
#
#     test_file_dir = "test_definition_files/test_monitors"
#     file_path = test_file_dir + "/expected_name_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     parser.parse_connections()
#
#     assert parser.parse_monitors() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a name\n"
#
# def test_MONITORS_expected_comma_error(capfd):
#     """Test if missing expected comma symbol is reported in MONITORS BLOCK"""
#
#     test_file_dir = "test_definition_files/test_monitors"
#     file_path = test_file_dir + "/expected_comma_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     parser.parse_connections()
#     assert parser.parse_monitors() is False
#
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a comma\n"
#
# def test_MONITORS_expected_dot_error(capfd):
#     test_file_dir = "test_definition_files/test_monitors"
#     pass
#
# def test_MONITORS_expected_semicolon_error(capfd):
#     """Test if missing expected ; symbol is reported in MONITORS BLOCK"""
#     test_file_dir = "test_definition_files/test_monitors"
#     file_path = test_file_dir + "/expected_semicolon_error.txt"
#     parser =create_parser(file_path)
#
#     parser.parse_devices()
#     parser.parse_connections()
#
#     assert parser.parse_monitors() is False
#     out,err = capfd.readouterr()
#     assert out == "SyntaxError: Expected a semicolon\n"
#
# def test_MONITORS_mutliple_errors():
#     test_file_dir = "test_definition_files/test_monitors"
#     pass
