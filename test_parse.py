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


 
"""DEVICE Block tests"""

def test_parse_devices_success():
    """Test if parse_devices returns true correctly"""
    
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
    string_io = StringIO("DEVICES 1SWITCH = SWITCH/1;...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a name\n"

def test_DEVICES_resued_name_error(capfd):
    string_io = StringIO("DEVICES SWITCHe = SWITCH/1, SWITCHe = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"
    
   

def test_DEVICE_expected_comma_error(capfd):
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1 SWITCH2 = SWITCH/0 ; ...")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"

def test_DEVICE_expected_number_error(capfd):
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

def test_DEVICE_semicolon_absense(capfd):
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1, SWITCH2 = SWITCH/0 MONITOR")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a semicolon"
    

def test_DEVICE_parameter_error(capfd):
    string_io = StringIO("DEVICES SWITCH1 = SWITCH/1, SWITCH2 = SWITCH/0; MONITOR")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "This specific device needs parameter preceded by a '/' "

    
def test_DEVICE_mutliple_errors():
    pass
    
"""CONNECTIONS Block tests""" 

def test_parse_parse_connections_success():
    """Test if parse_devices returns true correctly"""
    
    file_path = test_file_dir + "/test_model_2.txt"
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_devices()
    assert parser.parse_connections() is True 


    
  
   
