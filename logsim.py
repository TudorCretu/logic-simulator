#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hct:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    # names = Names()
    # devices = Devices(names)
    # network = Network(names, devices)
    # monitors = Monitors(names, devices, network)
    names = None
    devices = None
    network = None
    monitors = None

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()
        elif option == "-t":  # manually create the devices, network, and monitors for testing
            if path == "1":
                names, devices, network, monitors = test_1()
            elif path == "2":
                names, devices, network, monitors = test_2()
            elif path == "3":
                names, devices, network, monitors = test_3()
            elif path == "4":
                names, devices, network, monitors = test_4()
            else:
                print("Error: invalid test number.\n")
                sys.exit()
            # userint = UserInterface(names, devices, network, monitors)
            # userint.command_interface()

            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network, monitors)
            gui.Show(True)
            app.MainLoop()


    if not options:  # no option given, use the graphical user interface

        if len(arguments) != 1:  # wrong number of arguments
            print("Error: one file path required\n")
            print(usage_message)
            sys.exit()

        [path] = arguments
        # scanner = Scanner(path, names)
        # parser = Parser(names, devices, network, monitors, scanner)
        if parser.parse_network():
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network, monitors)
            gui.Show(True)
            app.MainLoop()

def test_1():
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


if __name__ == "__main__":
    main(sys.argv[1:])
