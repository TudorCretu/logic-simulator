"""Test the scanner module."""
import builtins

import pytest
import os
from io import StringIO

from names import Names
from scanner import Scanner
from parse import Parser
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
devices =None
network= None
monitors =None

def test_parse_devices_success():
    """Test if parse_devices returns true correctly"""
    
    file_path = test_file_dir + "/test_model_2.txt"
    scanner = Scanner(file_path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    assert parser.parse_devices() is True 
    
def test_detects_missing_devices_keywords(capfd):
    """Test if parse_devices returns true correctly"""
    
    string_io = StringIO("SKIPKEYWORD CK1 = CLOCK / 1")
    scanner = Scanner(string_io, names)
    parser = Parser(names, devices, network, monitors, scanner)
   
    assert parser.parse_devices() is False
    out,err = capfd.readouterr()
    assert out == "SyntaxError: Expected a keyword\n"
    
  
   