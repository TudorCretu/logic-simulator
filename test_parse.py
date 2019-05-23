"""Test the scanner module."""
import builtins

import pytest
import os
from io import StringIO

from names import Names
from scanner import Symbol, Scanner
from parse import Parser
from network import Network
from devices import Device, Devices
from monitors import Monitors

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

names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

# For ease of immediately understanding the contents of the 'test files'
# the use of actual dedicated files is reserved for very large inputs
 
"""DEVICE Block tests"""

def test_parse_devices_success():
    """Test if parse_devices() returns True correctly for a valid file"""
    
    file_path = test_file_dir + "/test_model_2.txt"
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    assert parser.parse_devices() is True 
    
def test_DEVICES_missing_devices_keywords(capfd):
    """Test if parse_devices returns true correctly"""
    
    string_io = StringIO("SKIPKEYWORD CK1 = CLOCK / 1... don't care")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
   
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a keyword\n"
    

def test_DEVICES_expected_name_error(capfd):
    """Test reporting of missing expected Name symbol in DEVICE block"""
    
    string_io = StringIO("DEVICES 1SWITCH = SWITCH/1;...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a name\n"

def test_DEVICES_resued_name_error(capfd):
    """Test if reuse of device name is reported in DEVICE block"""
    
    string_io = StringIO("DEVICES SWITCHe = SWITCH/1, SWITCHe = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SemanticError: DEVICE_PRESENT\n"
   

def test_DEVICES_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in DEVICE BLOCK"""
    
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1 SWITCH2 = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"

def test_DEVICES_expected_number_error(capfd):
    """Test if a missing expected sumber symbol is reported in DEVICE BLOCK"""
    
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/a SWITCH2 = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a number\n"
    
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/ SWITCH2 = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a number\n"

def test_DEVICES_expected_semicolon_error(capfd):
    """Test if missing expected semicolon symbol is reported in DEVICE BLOCK"""
    
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1, SWITCH2 = SWITCH/0 MONITORS")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a semicolon\n"

def test_DEVICES_parameter_error(capfd):
    """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
    
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1, SWITCH2 = SWITCH/0; MONITORS")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "This specific device needs parameter preceded by a '/' "
    # not handled
    
def test_DEVICES_mutliple_errors():
    """Test that a sequence of known errors are reported indicating proper recovery occurs
    within DEVICE block"""
    pass
    
"""CONNECTIONS Block tests""" 

def test_parse_connections_success():
    """Test if parse_devices returns true correctly"""
    
    file_path = test_file_dir + "/test_model_2.txt"
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_devices()
    assert parser.parse_connections() is False
                                   
def test_CONNECTIONS_expected_name_error(capfd):
    pass                                 
                                   
def test_CONNECTIONS_expected_comma_error(capfd):
    pass                                                     

def test_CONNECTIONS_expected_dot_error(capfd):
    pass                  
    
def test_CONNECTIONS_expected_semicolon_error(capfd):
    pass                    
   
def test_DEVICES_mutliple_errors():
    pass

"""Monitors Block tests""" 

def test_MONITORS_expected_name_error(capfd):
    pass                                 
                                   
def test_MONITORS_expected_comma_error(capfd):
    pass                                                     

def test_MONITORS_expected_dot_error(capfd):
    pass                  
    
def test_MONITORS_expected_semicolon_error(capfd):
    pass                    
   
def test_MONITORS_mutliple_errors():
    pass