#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface with a blank circuit: logsim.py
Graphical user interface with a predefined test circuit: logsim.py -t <circuit_number>
Graphical user interface with loading a file: logsim.py <file path>
"""
import getopt
import sys

import wx

from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui
from networks_lib import *


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface with a blank circuit: logsim.py\n"
                     "Graphical user interface with a predefined test circuit: logsim.py -t <circuit_number>\n"
                     "Graphical user interface with loading a file: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hct:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    import app_base as ab
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

            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", path, names, devices, network, monitors,"en")
            gui.Show(True)
            app.MainLoop()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) == 0:  # Open the blank gui
            # Initialise an instance of the gui.Gui() class
            app = wx.App()
            gui = Gui("Logic Simulator", None, names, devices, network, monitors,"en")
            gui.Show(True)
            app.MainLoop()

        elif len(arguments) == 1:
            [path] = arguments
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the gui.Gui() class
                app = wx.App()
                gui = Gui("Logic Simulator", path, names, devices, network, monitors,"en")
                gui.Show(True)
                app.MainLoop()

        else:  # wrong number of arguments
            print("Error: Too many arguments given\n")
            print(usage_message)
            sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
