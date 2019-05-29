import builtins
import pytest
import os
from io import StringIO
from names import Names


def test_unique_error_codes():
    """Test the unique_error_codes method"""
    n = Names()
    codes = n.unique_error_codes(3)
    assert [codes[0], codes[1], codes[2]] == [0, 1, 2]
    with pytest.raises(TypeError):
        n.unique_error_codes(-1)
    with pytest.raises(TypeError):
        n.unique_error_codes("s")


def test_query():
    """Test the query method"""
    n = Names()
    n.names = ["name1", "name2", "name3"]
    assert n.query("name1") == 0
    assert n.query("name4") is None


def test_lookup():
    """Test the look_up method"""
    n = Names()
    assert n.lookup(["name1"]) == [0]
    assert n.lookup(["name2"]) == [1]
    assert n.lookup(["name2", "name3", "name1"]) == [1, 2, 0]


def test_get_name_string():
    """Test the get_name_string method"""
    n = Names()
    _ = n.lookup(["name1", "name2", "name3"])
    assert n.get_name_string(1) == "name2"
    assert n.get_name_string(5) is None
