"""Test the scanner module."""
import builtins

import pytest
import os
from io import StringIO

from names import Names
from scanner import Scanner


# Function to make "open" function to work with StringIo objects
def replace_open():
    # The next line redefines the open function
    old_open, builtins.open = builtins.open, lambda *args, **kwargs: args[0] if isinstance(args[0], StringIO) else old_open(*args, **kwargs)

    # The methods below have to be added to the StringIO class in order for the "with" statement to work
    # StringIO.__enter__ = lambda self: self
    # StringIO.__exit__= lambda self, a, b, c: None


replace_open()
# Folder to keep test definition files
test_file_dir = "test_definition_files"


@pytest.fixture
def new_definition_file():
    """Return a new instance of the Devices class."""
    new_names = Names()


def test_initial_whitespace():
    """Test if initial white space is ignored."""
    names = Names()
    string_io = StringIO("  \f  \t  \n \t \r \n \v symbol")
    scanner = Scanner(string_io, names)
    assert scanner.get_symbol() == "symbol"


def test_middle_whitespace():
    """Test if final white space is ignored."""
    names = Names()
    string_io = StringIO("symbol  \f  \t  \n \t \r \n \v next")
    scanner = Scanner(string_io, names)
    assert scanner.get_symbol() == "symbol"
    assert scanner.get_symbol() == "next"


def test_final_whitespace():
    """Test if final white space is ignored."""
    names = Names()
    string_io = StringIO("symbol  \f \n\r  \t  \n \t \r \n \v ")
    scanner = Scanner(string_io, names)
    assert scanner.get_symbol() == "symbol"
    assert scanner.get_symbol() == ""


def test_comment():
    """Test if definition_file_1 is scanned correctly."""
    names = Names()
    string_io = StringIO("Some ")
    scanner = Scanner(string_io, names)
    print(scanner.get_symbol())


def test_definition_file_1():
    """Test if definition_file_1 is scanned correctly."""
    names = Names()
    scanner = Scanner(os.path.join(test_file_dir, "test_model_1.txt"), names)
    assert scanner.get_symbol() == "DEVICES"
    assert scanner.get_symbol() == "SW1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "SWITCH"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "SWITCH"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW3"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "SWITCH"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW4"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "SWITCH"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "0"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "DTYPE"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "CLOCK"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ";"

    assert scanner.get_symbol() == "CONNECTIONS"
    assert scanner.get_symbol() == "SW1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "XOR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "XOR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "XOR1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "DATA"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "CLK"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW3"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "SET"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "SW4"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "CLEAR"
    assert scanner.get_symbol() == ";"

    assert scanner.get_symbol() == "MONITORS"
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "Q"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "D1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "QBAR"
    assert scanner.get_symbol() == ";"


def test_definition_file_2():
    """Test if definition_file_2 is scanned correctly."""
    names = Names()
    scanner = Scanner(os.path.join(test_file_dir, "test_model_2.txt"), names)
    assert scanner.get_symbol() == "DEVICES"
    assert scanner.get_symbol() == "CK1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "CLOCK"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "CLOCK"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "AND1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "AND"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "NAND1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NAND"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "OR1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "OR"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "NOR1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NOR"
    assert scanner.get_symbol() == "/"
    assert scanner.get_symbol() == "2"
    assert scanner.get_symbol() == ";"

    assert scanner.get_symbol() == "CONNECTIONS"
    assert scanner.get_symbol() == "CK1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "AND1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "AND1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NAND1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "OR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "CK2"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NOR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I2"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "AND1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NAND1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "NAND1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "OR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I1"
    assert scanner.get_symbol() == ","
    assert scanner.get_symbol() == "OR1"
    assert scanner.get_symbol() == "="
    assert scanner.get_symbol() == "NOR1"
    assert scanner.get_symbol() == "."
    assert scanner.get_symbol() == "I1"
    assert scanner.get_symbol() == ";"

    assert scanner.get_symbol() == "MONITORS"
    assert scanner.get_symbol() == "NOR1"
    assert scanner.get_symbol() == ";"
