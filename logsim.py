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
                names, devices, network, monitors = test_gui_1()
            else:
                print("Error: invalid test number.\n")
                sys.exit()
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network,
                      monitors)
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
            gui = Gui("Logic Simulator", path, names, devices, network,
                      monitors)
            gui.Show(True)
            app.MainLoop()

def test_gui_1():
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    devices.make_device(1, devices.SWITCH, 1)
    devices.make_device(2, devices.SWITCH, 1)
    devices.make_device(3, devices.SWITCH, 1)
    devices.make_device(4, devices.SWITCH, 0)
    devices.make_device(5, devices.D_TYPE)
    devices.make_device(6, devices.CLOCK, 2)
    devices.make_device(7, devices.XOR, 2)

    network.make_connection(1, None, 7, names.query("I1"))
    network.make_connection(2, None, 7, names.query("I2"))
    network.make_connection(7, None, 5, names.query("DATA"))
    network.make_connection(6, None, 5, names.query("CLK"))
    network.make_connection(3, None, 5, names.query("SET"))
    network.make_connection(4, None, 5, names.query("CLEAR"))

    monitors.make_monitor(5, names.query("Q"))
    monitors.make_monitor(5, names.query("QBAR"))

    return names, devices, network, monitors

if __name__ == "__main__":
    main(sys.argv[1:])
