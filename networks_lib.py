"""Define test networks of the test definition files.

These functions build the network of a test definition file to be used for testing the gui whenever
scanner or parse module is not in a working state.
"""

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors


def test_1():
    """Create network that matches test definition file 1"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    [SW1, SW2, SW3, SW4, D1, CK1, XOR1] = \
        names.lookup(["SW1", "SW2", "SW3", "SW4", "D1", "CK1", "XOR1"])
    print(names.query("SW1"))
    devices.make_device(SW1, devices.SWITCH, 1)
    devices.make_device(SW2, devices.SWITCH, 1)
    devices.make_device(SW3, devices.SWITCH, 1)
    devices.make_device(SW4, devices.SWITCH, 0)
    devices.make_device(D1, devices.D_TYPE)
    devices.make_device(CK1, devices.CLOCK, 2)
    devices.make_device(XOR1, devices.XOR)

    network.make_connection(SW1, None, XOR1, names.query("I1"))
    network.make_connection(SW2, None, XOR1, names.query("I2"))
    network.make_connection(XOR1, None, D1, names.query("DATA"))
    network.make_connection(CK1, None, D1, names.query("CLK"))
    network.make_connection(SW3, None, D1, names.query("SET"))
    network.make_connection(SW4, None, D1, names.query("CLEAR"))

    monitors.make_monitor(D1, names.query("Q"))
    monitors.make_monitor(D1, names.query("QBAR"))

    return names, devices, network, monitors


def test_2():
    """Create network that matches test definition file 2"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    CK1, CK2, AND1, NAND1, OR1, NOR1 = names.lookup(["CK1", "CK2", "AND1", "NAND1", "OR1", "NOR1"])
    devices.make_device(CK1, devices.CLOCK, 2)
    devices.make_device(CK2, devices.CLOCK, 1)
    devices.make_device(AND1, devices.AND, 2)
    devices.make_device(NAND1, devices.NAND, 2)
    devices.make_device(OR1, devices.OR, 2)
    devices.make_device(NOR1, devices.NOR, 2)

    network.make_connection(CK1, None, AND1, names.query("I1"))
    network.make_connection(CK2, None, AND1, names.query("I2"))
    network.make_connection(CK2, None, NAND1, names.query("I2"))
    network.make_connection(CK2, None, OR1, names.query("I2"))
    network.make_connection(CK2, None, NOR1, names.query("I2"))
    network.make_connection(AND1, None, NAND1, names.query("I1"))
    network.make_connection(NAND1, None, OR1, names.query("I1"))
    network.make_connection(OR1, None, NOR1, names.query("I1"))

    monitors.make_monitor(NOR1, None)
    return names, devices, network, monitors


def test_3():
    """Create network that matches test definition file 3"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    S, R, CK, D = names.lookup(["S", "R", "CK", "D"])
    devices.make_device(S, devices.SWITCH, 0)
    devices.make_device(R, devices.SWITCH, 0)
    devices.make_device(CK, devices.CLOCK, 1)
    devices.make_device(D, devices.D_TYPE)

    network.make_connection(CK, None, D, names.query("CLK"))
    network.make_connection(S, None, D, names.query("SET"))
    network.make_connection(R, None, D, names.query("CLEAR"))
    network.make_connection(D, names.query("QBAR"), D, names.query("DATA"))

    monitors.make_monitor(CK, None)
    monitors.make_monitor(D, names.query("Q"))
    monitors.make_monitor(S, None)
    monitors.make_monitor(R, None)

    return names, devices, network, monitors


def test_4():
    """Create network that matches test definition file 4, a 4-bit ripple counter"""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    SW, CK, D1, D2, D3, D4 = names.lookup(["SW", "CK", "D1", "D2", "D3", "D4"])
    devices.make_device(SW, devices.SWITCH, 0)
    devices.make_device(CK, devices.CLOCK, 1)
    devices.make_device(D1, devices.D_TYPE)
    devices.make_device(D2, devices.D_TYPE)
    devices.make_device(D3, devices.D_TYPE)
    devices.make_device(D4, devices.D_TYPE)

    network.make_connection(SW, None, D1, names.query("SET"))
    network.make_connection(SW, None, D1, names.query("CLEAR"))
    network.make_connection(SW, None, D2, names.query("SET"))
    network.make_connection(SW, None, D2, names.query("CLEAR"))
    network.make_connection(SW, None, D3, names.query("SET"))
    network.make_connection(SW, None, D3, names.query("CLEAR"))
    network.make_connection(SW, None, D4, names.query("SET"))
    network.make_connection(SW, None, D4, names.query("CLEAR"))
    network.make_connection(CK, None, D1, names.query("CLK"))
    network.make_connection(D1, names.query("QBAR"), D2, names.query("CLK"))
    network.make_connection(D2, names.query("QBAR"), D3, names.query("CLK"))
    network.make_connection(D3, names.query("QBAR"), D4, names.query("CLK"))
    network.make_connection(D1, names.query("QBAR"), D1, names.query("DATA"))
    network.make_connection(D2, names.query("QBAR"), D2, names.query("DATA"))
    network.make_connection(D3, names.query("QBAR"), D3, names.query("DATA"))
    network.make_connection(D4, names.query("QBAR"), D4, names.query("DATA"))

    monitors.make_monitor(CK, None)
    monitors.make_monitor(D1, names.query("Q"))
    monitors.make_monitor(D2, names.query("Q"))
    monitors.make_monitor(D3, names.query("Q"))
    monitors.make_monitor(D4, names.query("Q"))

    return names, devices, network, monitors
