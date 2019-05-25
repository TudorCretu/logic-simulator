"""Test the scanner module."""
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
    scanner = scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    return parser
"""DEVICE Block tests"""

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
    assert out == "SyntaxError: Expected a keyword\n"
    

def test_DEVICES_expected_name_error(capfd):
    """Test reporting of missing expected Name symbol in DEVICE block"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_name_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a name\n"

def test_DEVICES_resued_name_error(capfd):
    """Test if reuse of device name is reported in DEVICE block"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/reused_name_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SemanticError: DEVICE_PRESENT\n"
   

def test_DEVICES_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"
    
    
def test_DEVICES_expected_equals_error(capfd):
    """Test if missing expected equals symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_equals_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected an equals sign\n"

def test_DEVICES_expected_number_error(capfd):
    """Test if a missing expected sumber symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_number_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a number\n"
       

def test_DEVICES_expected_semicolon_error(capfd):
    """Test if missing expected semicolon symbol is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)

    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a semicolon\n"

def test_DEVICES_parameter_error(capfd):
    """Test if lack of parameter labelling is reported in DEVICE BLOCK"""
    test_file_dir = "test_definition_files/test_devices"
    file_path = test_file_dir + "/parameter_error.txt"
    parser =create_parser(file_path)
    
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "This specific device needs parameter preceded by a '/'  BUT AT THE MOMENT NOT HANDLED"
    # not handled
    
def test_DEVICES_mutliple_errors():
    """Test that a sequence of known errors are reported indicating proper recovery occurs
    within DEVICE block"""
    pass

    
"""CONNECTIONS Block tests""" 
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
    assert out == "SyntaxError: Expected a name\n"
                                   
                                   
def test_CONNECTIONS_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)
    
    parser.parse_devices()
    assert parser.parse_connections() is False
                                   
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"                                                     

def test_CONNECTIONS_expected_dot_error(capfd):
    test_file_dir = "test_definition_files/test_connections"
    pass                
    
def test_CONNECTIONS_expected_semicolon_error(capfd):
    """Test if missing expected ; symbol is reported in CONNECTIONS BLOCK"""
    test_file_dir = "test_definition_files/test_connections"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)
    
    parser.parse_devices()
    assert parser.parse_connections() is False
                                   
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a semicolon\n"                    
   
def test_CONNECTIONS_mutliple_errors():
    test_file_dir = "test_definition_files/test_connections"
    pass

"""Monitors Block tests""" 



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
    assert out == "SyntaxError: Expected a name\n"
                                   
 
                                 
def test_MONITORS_expected_comma_error(capfd):
    """Test if missing expected comma symbol is reported in MONITORS BLOCK"""
    
    test_file_dir = "test_definition_files/test_monitors"
    file_path = test_file_dir + "/expected_comma_error.txt"
    parser =create_parser(file_path)
    
    parser.parse_devices()
    parser.parse_connections()
    assert parser.parse_monitors() is False
                                
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a comma\n"                                                     

def test_MONITORS_expected_dot_error(capfd):
    test_file_dir = "test_definition_files/test_monitors"
    pass                
    



def test_MONITORS_expected_semicolon_error(capfd):
    """Test if missing expected ; symbol is reported in MONITORS BLOCK"""
    test_file_dir = "test_definition_files/test_monitors"
    file_path = test_file_dir + "/expected_semicolon_error.txt"
    parser =create_parser(file_path)
    
    parser.parse_devices() 
    parser.parse_connections()
    
    assert parser.parse_monitors() is False
    
                                 
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a semicolon\n"                    
  
def test_MONITORS_mutliple_errors():
    test_file_dir = "test_definition_files/test_monitors"
    pass
