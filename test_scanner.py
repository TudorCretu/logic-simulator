"""Test the scanner module."""
import pytest
import os
from io import StringIO

from names import Names
from scanner import Scanner

test_file_dir = ""

@pytest.fixture
def new_definition_file():
    """Return a new instance of the Devices class."""
    new_names = Names()


def test_definition_file_1():
    """Test if definition_file_1 is scanned correctly."""
    names = Names()
    scanner = Scanner()
    