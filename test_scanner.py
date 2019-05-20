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
    old_open, builtins.open = builtins.open, lambda *args, **kwargs: args[0] \
                                if isinstance(args[0], StringIO) \
                                else old_open(*args, **kwargs)

    # The methods below have to be added to the StringIO class in order for the "with" statement to work
    # StringIO.__enter__ = lambda self: self
    # StringIO.__exit__= lambda self, a, b, c: None


replace_open()
# Folder to keep test definition files
test_file_dir = "test_definition_files"


@pytest.fixture
def names():
    """Return a new instance of the Devices class."""
    return Names()


def assert_symbol(symbol, expected_type, expected_id):
    assert symbol.type == expected_type
    assert symbol.id == expected_id


def test_eof_symbol(names):
    """Test if eof is handled correctly."""
    string_io = StringIO("")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_string_symbol(names):
    """Test if name is handled correctly."""
    string_io = StringIO("symbol")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_backslash_symbol(names):
    """Test if backslash is handled correctly."""
    string_io = StringIO("/")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_comma_symbol(names):
    """Test if comma is handled correctly."""
    string_io = StringIO(",")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_semicolon_symbol(names):
    """Test if semicolon is handled correctly."""
    string_io = StringIO(";")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_equals_symbol(names):
    """Test if equals is handled correctly."""
    string_io = StringIO("=")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_dot_symbol(names):
    """Test if dot is handled correctly."""
    string_io = StringIO(".")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_keyword_symbol(names):
    """Test if keywords are handled correctly."""
    string_io = StringIO("CONNECTIONS")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("CONNECTIONS"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)

    string_io = StringIO("DEVICES")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("DEVICES"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)

    string_io = StringIO("MONITORS")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("MONITORS"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_number_symbol(names):
    """Test if number is handled correctly."""
    string_io = StringIO("1234")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1234")
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_unknown_symbol(names):
    """Test if unknown symbol is handled correctly."""
    string_io = StringIO("%")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), None, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_string_punctuation_sequence(names):
    """Test if string, punctuation sequence is handled correctly."""
    string_io = StringIO("symbol/other")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("other"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_string_punctuation_number_symbol(names):
    """Test if string, punctuation, number sequence is handled correctly."""
    string_io = StringIO("symbol/1234/other")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1234")
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("other"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_keywords_in_sequence_symbol(names):
    """Test if the keywords DEVICES, CONNECTIONS, MONITORS are recognised correctly."""
    string_io = StringIO("DEVICES symbol/1234,CONNECTIONS connec/5678.MONITORS monitor/90;")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("DEVICES"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1234")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("CONNECTIONS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("connec"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "5678")
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("MONITORS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("monitor"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "90")
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_initial_whitespace(names):
    """Test if initial white space is ignored."""
    string_io = StringIO("  \f  \t  \n \t \r \n \v symbol")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_interior_whitespace(names):
    """Test if interior white space is ignored."""
    string_io = StringIO("symbol  \f  \t  \n \t \r \n \v / \n \t next")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("next"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_final_whitespace(names):
    """Test if final white space is ignored."""
    string_io = StringIO("symbol  \f \n\r  \t  \n \t \r \n \v ")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_comment(names):
    """Test if comments are ignored correctly."""
    string_io = StringIO("Some / symbol # some comment 1234 / " + os.linesep
                         + "Some / other / symbols # some other comments / ; ")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("Some"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("Some"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("other"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbols"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_comment_between_sections(names):
    """Test if comments are ignored correctly."""
    string_io = StringIO("Some / symbol " + os.linesep + os.linesep + " # some comment 1234 / "
                         + os.linesep + os.linesep + "Some / other / symbols # some other comments / ; ")
    scanner = Scanner(string_io, names)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("Some"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbol"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("Some"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("other"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("symbols"))
    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_definition_file_1(names):
    """Test if definition_file_1 is scanned correctly."""
    scanner = Scanner(os.path.join(test_file_dir, "test_model_1.txt"), names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("DEVICES"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SWITCH"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SWITCH"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW3"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SWITCH"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW4"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SWITCH"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "0")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("DTYPE"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CLOCK"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("XOR1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("XOR"))
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("CONNECTIONS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("XOR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I1"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("XOR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I2"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("XOR1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("DATA"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CLK"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW3"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SET"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("SW4"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CLEAR"))
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("MONITORS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("Q"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("D1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("QBAR"))
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.EOF, None)


def test_definition_file_2(names):
    """Test if definition_file_2 is scanned correctly."""
    scanner = Scanner(os.path.join(test_file_dir, "test_model_2.txt"), names)
    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("DEVICES"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CLOCK"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CLOCK"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "1")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("AND1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("AND"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NAND1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NAND"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("OR1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("OR"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NOR1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NOR"))
    assert_symbol(scanner.get_symbol(), scanner.BACKSLASH, None)
    assert_symbol(scanner.get_symbol(), scanner.NUMBER, "2")
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("CONNECTIONS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("AND1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I1"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("AND1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I2"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NAND1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I2"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("OR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I2"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("CK2"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NOR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I2"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("AND1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NAND1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I1"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NAND1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("OR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I1"))
    assert_symbol(scanner.get_symbol(), scanner.COMMA, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("OR1"))
    assert_symbol(scanner.get_symbol(), scanner.EQUALS, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NOR1"))
    assert_symbol(scanner.get_symbol(), scanner.DOT, None)
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("I1"))
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.KEYWORD, names.query("MONITORS"))
    assert_symbol(scanner.get_symbol(), scanner.NAME, names.query("NOR1"))
    assert_symbol(scanner.get_symbol(), scanner.SEMICOLON, None)

    assert_symbol(scanner.get_symbol(), scanner.EOF, None)
