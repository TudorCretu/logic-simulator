"""
Test the parser module.

Testing of the parser mainly consists of 2 parts: basic functionality testing and more complicated case testing.

Basic functionality testing in this file is finished by Dongcheng Jiang (dj346), the person who implemented parse.py as well.

The other file test_parse.py which contains case testing is made by Shakthivel Ravichandran (sr795).

"""

import builtins
import pytest
import os

from names import Names
from scanner import Symbol, Scanner
from parse import Parser
from network import Network
from devices import Device, Devices
from monitors import Monitors

def create_parser(path):
    """Create a new parser for every test"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    return parser

# --------------------------------Basic Functionality tests----------------------------------------
def test_read_symbol():
    """Test the Parser.read_symbol() function"""
    file_dir = "test_functions"
    path = file_dir + "/read_symbol.txt"
    parser =create_parser(path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.KEYWORD
    assert parser.symbol.id == parser.scanner.DEVICES_ID

def test_skip_erratic_part():
    """Test the Parser.skip_erratic_part() function"""
    file_dir = "test_functions"
    path = file_dir + "/skip_erratic_part.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.skip_erratic_part()
    assert parser.symbol.type == parser.scanner.COMMA

def test_display_error(capfd):
    """Test the Parser.display_error() function"""
    file_dir = "test_functions"
    path = file_dir + "/skip_erratic_part.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.display_error(parser.NO_EQUALS)
    out, err = capfd.readouterr()
    assert out == "SyntaxError: Expected an equals sign\n"

def test_display_error_device(capfd):
    """Test the Parser.display_error_device() function"""
    file_dir = "test_functions"
    path = file_dir + "/skip_erratic_part.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.display_error_device(parser.devices.BAD_DEVICE)
    out, err = capfd.readouterr()
    assert out == "SemanticError: BAD_DEVICE\n"

def test_display_error_connection(capfd):
    """Test the Parser.display_error_connection() function"""
    file_dir = "test_functions"
    path = file_dir + "/skip_erratic_part.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.display_error_connection(parser.network.INPUT_TO_INPUT)
    out, err = capfd.readouterr()
    assert out == "SemanticError: INPUT_TO_INPUT\n"

def test_display_error_monitor(capfd):
    """Test the Parser.display_error_monitor() function"""
    file_dir = "test_functions"
    path = file_dir + "/skip_erratic_part.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.display_error_monitor(parser.monitors.NOT_OUTPUT)
    out, err = capfd.readouterr()
    assert out == "SemanticError: NOT_OUTPUT\n"

def test_check_names():
    """Test the Parser.check_names() function"""
    file_dir = "test_functions"
    path = file_dir + "/check_names.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.NAME
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type != parser.scanner.NAME

def test_check_numbers():
    """Test the Parser.check_numbers() function"""
    file_dir = "test_functions"
    path = file_dir + "/check_numbers.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type == parser.scanner.NUMBER
    parser.symbol = parser.read_symbol()
    assert parser.symbol.type != parser.scanner.NUMBER

def test_check_side():
    """Test the Parser.check_side() function"""
    file_dir = "test_functions"
    path = file_dir + "/check_side.txt"
    parser = create_parser(path)
    parser.symbol = parser.read_symbol()
    parser.symbol = parser.read_symbol()
    assert parser.check_side(0) is True
    parser.symbol = parser.read_symbol()
    parser.symbol = parser.read_symbol()
    assert parser.check_side(1) is True

def test_signame():
    """Test the Parser.signame() function"""
    file_dir = "test_functions"
    path = file_dir + "/signame.txt"
    parser = create_parser(path)
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
    """Test the Parser.get_parameter() function"""
    file_dir = "test_functions"
    path = file_dir + "/get_parameter.txt"
    parser = create_parser(path)
    param = parser.get_parameter()
    assert param == 80
    param = parser.get_parameter()
    assert param is None

def test_add_device():
    """Test the Parser.add_device() function"""
    file_dir = "test_functions"
    path = file_dir + "/add_device.txt"
    parser = create_parser(path)
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
    """Test the Parser.parse_devices() function"""
    file_dir = "test_functions"
    path = file_dir + "/parse_device.txt"
    parser = create_parser(path)
    flag = parser.parse_devices()
    assert flag is True

def test_add_connection():
    """Test the Parser.add_connection() function"""
    file_dir = "test_functions"
    path = file_dir + "/add_connection.txt"
    parser = create_parser(path)
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
    # alternative for this add_connection():
    # device_id1, port_id1, syntax_err = parser.signame()
    # assert port_id1 is None
    # device_id2, port_id2, syntax_err = parser.signame()
    # assert port_id2 is None
    # err = parser.network.make_connection(device_id1, port_id1, device_id2, port_id2)
    # assert err == parser.network.DEVICE_ABSENT

    flag = parser.add_connection()
    assert flag is False

def test_parse_connections():
    """Test the Parser.parse_connections() function"""
    file_dir = "test_functions"
    path = file_dir + "/parse_connection.txt"
    parser = create_parser(path)
    _ = parser.parse_devices()
    flag = parser.parse_connections()
    assert flag is True

def test_add_monitor():
    """Test the Parser.add_monitor() function"""
    file_dir = "test_functions"
    path = file_dir + "/add_monitor.txt"
    parser = create_parser(path)
    flag = parser.parse_devices()
    assert flag is True
    flag = parser.parse_connections()
    assert flag is True
    parser.symbol = parser.read_symbol()
    flag = parser.add_monitor()
    assert flag is True
    flag = parser.add_monitor()
    assert flag is False
    flag = parser.add_monitor()
    assert flag is False
    flag = parser.add_monitor()
    assert flag is True
    flag = parser.add_monitor()
    assert flag is True
    flag = parser.add_monitor()
    assert flag is False

def test_parse_monitors():
    """Test the Parser.parse_monitors() function"""
    file_dir = "test_functions"
    path = file_dir + "/parse_monitor.txt"
    parser = create_parser(path)
    _ = parser.parse_devices()
    _ = parser.parse_connections()
    flag = parser.parse_monitors()
    assert flag is True

def test_parse_network():
    """Test the Parser.parse_network() function"""
    file_dir = "test_functions"
    path = file_dir + "/parse_network.txt"
    parser = create_parser(path)
    flag = parser.parse_network()
    assert flag is True