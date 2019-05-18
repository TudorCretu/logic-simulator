import builtins
import pytest
import os
from io import StringIO
from names import Names

def test_unique_error_codes():
    n = Names()
    assert n.unique_error_codes(3) == [0,1,2]
    assert n.error_code_count == 3
    with pytest.raises(TypeError):
        n.unique_error_codes(-1)
        n.unique_error_codes("name")

def test_query():
    n = Names()
    n.names = ["name1", "name2", "name3"]
    assert n.query("name1") == 0
    assert n.query("name4") is None

def test_lookup():
    """Test the look_up method"""
    n = Names()
    assert n.lookup(["name1"]) == [0]
    assert n.lookup(["name2"])  == [1]
    assert n.lookup(["name2","name3","name1"]) == [1,2,0]

def test_get_name_string():
    n = Names()
    _ = n.lookup(["name1","name2","name3"])
    assert n.get_name_string(1) == "name2"
    assert n.get_name_string(5) is None
