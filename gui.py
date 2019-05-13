"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
import datetime
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):  
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        self.completed_cycles = 0

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_SAVE, "&Save")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # List of switches
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        # self.switches = devices.find_devices("SWITCH") #TODO Uncomment when devices is implemented

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        #  Top sizer
        self.load_file_button = wx.Button(self, wx.ID_ANY, "Load file")
        self.load_file_text_box = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.load_file_text_box.SetValue(path)

        #  Activity log sizer
        self.activity_log_title = wx.StaticText(self, wx.ID_ANY, "Activity log")
        self.activity_log_text = wx.TextCtrl(self, wx.ID_ANY, "", style= wx.TE_MULTILINE | wx.TE_READONLY | wx.ALIGN_TOP)

        #  Console sizer
        self.console = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)

        #  Side Sizer
        #   Switches
        toggle_button_size = wx.Size(50, wx.DefaultSize.GetHeight())
        self.switches_select = wx.ComboBox(self, wx.ID_ANY, style = wx.CB_SORT)
        self.switches_set_button = wx.ToggleButton(self, wx.ID_ANY, "HIGH", style=wx.BORDER_NONE, size=toggle_button_size)
        self.switches_clear_button = wx.ToggleButton(self, wx.ID_ANY, "LOW", style=wx.BORDER_NONE, size=toggle_button_size)
        self.switches_set_button.Disable()
        self.switches_clear_button.Disable()

        #   Monitors
        self.monitors_select = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_SORT)
        self.monitors_set_button = wx.ToggleButton(self, wx.ID_ANY, "SET", style=wx.BORDER_NONE, size=toggle_button_size)
        self.monitors_zap_button = wx.ToggleButton(self, wx.ID_ANY, "ZAP", style=wx.BORDER_NONE, size=toggle_button_size)
        self.monitors_set_button.Disable()
        self.monitors_zap_button.Disable()

        #   Simulation
        self.simulation_cycles_spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.simulation_run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.simulation_continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        #  StatiROWSc Strings
        console_title = wx.StaticText(self, wx.ID_ANY, "Console")
        side_title = wx.StaticText(self, wx.ID_ANY, "Properties")
        switches_title = wx.StaticText(self, wx.ID_ANY, "Change State of Switch")
        monitors_title = wx.StaticText(self, wx.ID_ANY, "Set or Zap Monitors")
        run_simulation_title = wx.StaticText(self, wx.ID_ANY, "Simulate")

        #  Lines
        line_side = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_switches = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_switches_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_monitors = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_monitors_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_run_simulation = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_run_simulation_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)

        # Bind events to widgets
        #  Menu
        self.Bind(wx.EVT_MENU, self.on_menu)

        #  Load file
        self.load_file_button.Bind(wx.EVT_BUTTON, self.on_load_file_button)
        self.load_file_text_box.Bind(wx.EVT_TEXT_ENTER, self.on_load_file_text_box)

        #  Console
        self.console.Bind(wx.EVT_TEXT_ENTER, self.on_console)

        #  Switches
        self.switches_select.Bind(wx.EVT_TEXT, self.on_switches_select)
        self.switches_set_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_switches_set)
        self.switches_clear_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_switches_clear)

        #  Monitors
        self.monitors_select.Bind(wx.EVT_TEXT, self.on_monitors_select)
        self.monitors_set_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_monitors_set)
        self.monitors_zap_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_monitors_zap)

        #  Run simulation
        self.simulation_cycles_spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.simulation_run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.simulation_continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        central_sizer = wx.BoxSizer(wx.HORIZONTAL)
        activity_log_sizer = wx.BoxSizer(wx.VERTICAL)
        console_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        side_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        switches_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        switches_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitors_sizer = wx.BoxSizer(wx.HORIZONTAL)
        simulation_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        simulation_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line_sizer_side = wx.BoxSizer(wx.VERTICAL)
        line_sizer_switches = wx.BoxSizer(wx.VERTICAL)
        line_sizer_monitors = wx.BoxSizer(wx.VERTICAL)
        line_sizer_run_simulation = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(top_sizer, 0, wx.TOP | wx.EXPAND, 5)
        main_sizer.Add(central_sizer, 10, wx.EXPAND, 5)
        main_sizer.Add(activity_log_sizer, 5, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(console_sizer, 1, wx.ALL | wx.EXPAND, 5)
        
        top_sizer.Add(self.load_file_button, 0, wx.LEFT| wx.TOP, 5)
        top_sizer.Add(self.load_file_text_box, 1, wx.ALL , 5)

        central_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        central_sizer.Add(side_sizer, 1, wx.ALL, 5)
        
        activity_log_sizer.Add(self.activity_log_title, 0, wx.TOP| wx. BOTTOM, 10)
        activity_log_sizer.Add(self.activity_log_text, 2, wx.EXPAND, 5)

        console_sizer.Add(console_title, 1, wx.TOP, 5)
        console_sizer.Add(self.console, 1, wx.EXPAND, 5)

        side_sizer.Add(side_title_sizer, 0, wx.TOP | wx.EXPAND, 1)
        side_sizer.Add(switches_title_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(switches_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_switches_end, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(monitors_title_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(monitors_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_monitors_end, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(simulation_title_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(simulation_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_run_simulation_end, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        side_title_sizer.Add(side_title, 0, wx.TOP, 0)
        side_title_sizer.Add(line_sizer_side, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 3)

        switches_title_sizer.Add(switches_title, 0, wx.LEFT | wx.TOP, 10)
        switches_title_sizer.Add(line_sizer_switches, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        switches_sizer.Add(self.switches_select, 2, wx.TOP | wx.LEFT | wx.EXPAND, 12)
        switches_sizer.Add(self.switches_set_button, 0, wx.TOP | wx.LEFT, 12)
        switches_sizer.Add(self.switches_clear_button, 0, wx.TOP | wx.RIGHT, 12)

        monitors_title_sizer.Add(monitors_title, 0, wx.LEFT | wx.TOP, 10)
        monitors_title_sizer.Add(line_sizer_monitors, 1,  wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        monitors_sizer.Add(self.monitors_select, 2, wx.TOP | wx.LEFT | wx.EXPAND, 12)
        monitors_sizer.Add(self.monitors_set_button, 0, wx.TOP | wx.LEFT, 12)
        monitors_sizer.Add(self.monitors_zap_button, 0, wx.TOP | wx.RIGHT, 12)

        simulation_title_sizer.Add(run_simulation_title, 0, wx.LEFT | wx.TOP, 10)
        simulation_title_sizer.Add(line_sizer_run_simulation, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        simulation_sizer.Add(self.simulation_cycles_spin, 4, wx.LEFT| wx.TOP | wx.EXPAND, 12)
        simulation_sizer.Add(self.simulation_run_button, 0, wx.LEFT| wx.TOP, 12)
        simulation_sizer.Add(self.simulation_continue_button, 0, wx.LEFT| wx.TOP, 12)

        line_sizer_side.Add(line_side, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_switches.Add(line_switches, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_monitors.Add(line_monitors, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_run_simulation.Add(line_run_simulation, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizeHints(900, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.simulation_cycles_spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.completed_cycles = int(self.simulation_cycles_spin.GetValue())
        self.canvas.render(text)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        self.completed_cycles += int(self.simulation_cycles_spin.GetValue())
        self.canvas.render(text)

    def on_console(self, event):
        """Handle the event when the user enters a command in the console."""
        text_box_value = self.console.GetValue()
        text = "".join([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S: "), text_box_value])
        self.activity_log_text.AppendText(text+'\n')
        self.console.SetValue("")
        
    def on_switches_select(self, event):
        """Handle the event when the user types text in switches text box.
        If the text in the box matches the name of a switch, then the set
        and clear buttons enable according to the current value of the switch.
        """
        device_name = self.switches_select.GetValue()
        device_id = self.names.query(device_name)
        if device_id is not None and device_id in self.switches:
            device = self.devices.get_device(device_id)
            if device.switch_state is self.devices.HIGH:
                self.switches_set_button.Disable()
                self.switches_clear_button.Enable()
            else:
                self.switches_set_button.Enable()
                self.switches_clear_button.Disable()
        else:
            self.switches_set_button.Disable()
            self.switches_clear_button.Disable()

    def on_switches_set(self, event):
        """Handle the event when the user sets a switch."""
        device_name = self.switches_select.GetValue()
        device_id = self.names.query(device_name)
        if device_id is not None and device_id in self.switches:
            self.devices.set_switch(device_id, self.devices.HIGH)
            self.switches_set_button.Disable()
            self.switches_clear_button.Enable()
        else:
            self.canvas.render("DEBUG: ON SWITCHES SET, device_id not in switches")

    def on_switches_clear(self, event):
        """Handle the event when the user clears a switch."""
        device_name = self.switches_select.GetValue()
        device_id = self.names.query(device_name)
        if device_id is not None and device_id in self.switches:
            self.devices.set_switch(device_id, self.devices.HIGH)
            self.switches_set_button.Enable()
            self.switches_clear_button.Disable()
        else:
            self.canvas.render("DEBUG: ON SWITCHES CLEAR, device_id not in switches")


    def on_monitors_select(self, event):
        """Handle the event when the user types text in monitors text box.
        If the text in the box matches the name of a signal, then the set
        and zap buttons enable according to if the if it's monitored or not.
        """
        signal_name = self.switches_select.GetValue()
        monitored, unmonitored = self.monitors.get_signal_names()
        if signal_name in monitored:
            self.monitors_set_button.Disable()
            self.monitors_zap_button.Enable()
        elif signal_name in unmonitored:
            self.monitors_set_button.Enable()
            self.monitors_zap_button.Disable()
        else:
            self.monitors_set_button.Disable()
            self.monitors_zap_button.Disable()

    def on_monitors_set(self, event):
        """Handle the event when the user sets a monitor."""
        signal_name = self.switches_select.GetValue()
        ids = self.devices.get_signal_ids(self, signal_name)
        if ids is not None:
            [device_id, output_id] = ids
            self.monitors.make_monitor(self, device_id, output_id, cycles_completed=0)
        else:
            self.canvas.render("DEBUG: ON MONITORS SET, ids is None")

    def on_monitors_zap(self, event):
        """Handle the event when the user clears a monitor."""
        signal_name = self.switches_select.GetValue()
        ids = self.devices.get_signal_ids(self, signal_name)
        if ids is not None:
            [device_id, output_id] = ids
            self.monitors.remove_monitor(self, device_id, output_id)
        else:
            self.canvas.render("DEBUG: ON MONITORS ZAP, ids is None")

    def on_load_file_button(self, event):
        """Handle the load file button"""
        # if self.contentNotSaved:
        #     if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
        #                      wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         return

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open another definition file", wildcard="*.def",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            path = fileDialog.GetPath()
            self.open_file(path)

    def on_load_file_text_box(self, event):
        """Handle the event when user enters a filepath into load_file_text_box"""
        # if self.contentNotSaved:
        #     if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
        #                      wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         return

        # otherwise ask the user what new file to open
        path = self.load_file_text_box.GetValue()
        self.open_file(path)

    def open_file(self, pathname):
        try:
            with open(pathname, 'r') as file:
                self.load_file_text_box.SetValue(pathname)
                # self.doLoadDataOrWhatever(file)
        except IOError:
            wx.LogError("Cannot open file '%s'." % pathname)
