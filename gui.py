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
import copy
from OpenGL import GL, GLUT
from command_manager import *


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
        self.pan_y = 300
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Simulation instances
        self.devices = devices
        self.monitors = monitors

        # Simulation variables
        self.completed_cycles = 0
        self.clock_display_frequency = 1
        self.monitors_number = len(monitors.monitors_dictionary)

        # Layout variables
        self.monitor_height = 70
        self.monitors_padding = 15
        self.cycle_width = 40
        # 25pt after the longest monitor name
        self.cycle_start_x = 25 + self.text_width("0") * self.monitors.get_margin()
        self.cycle_axis_y = -30
        self.cycle_axis_y_padding = -7
        self.completed_cycles = 10

        # Colors from Tableau 10 and Tableau 10 Medium
        self.blue = self.rgb_to_gl(31, 119, 180)
        self.orange = self.rgb_to_gl(255, 127, 14)
        self.green = self.rgb_to_gl(44, 160, 44)
        self.red = self.rgb_to_gl(214, 39, 40)
        self.purple = self.rgb_to_gl(148, 103, 189)
        self.brown = self.rgb_to_gl(140, 86, 75)
        self.pink = self.rgb_to_gl(227, 119, 194)
        self.olive = self.rgb_to_gl(188, 189, 34)
        self.cyan = self.rgb_to_gl(23, 190, 207)
        self.gray = self.rgb_to_gl(127, 127, 127)
        self.black = (0, 0, 0)
        self.color_cycle = [self.blue, self.orange, self.green,
                            self.red, self.purple, self.brown,
                            self.pink, self.olive, self.cyan]

        self.blue_light = self.rgb_to_gl(114, 158, 206)
        self.orange_light = self.rgb_to_gl(255, 158, 74)
        self.green_light = self.rgb_to_gl(103, 191, 92)
        self.red_light = self.rgb_to_gl(237, 102, 93)
        self.purple_light = self.rgb_to_gl(173, 139, 201)
        self.brown_light = self.rgb_to_gl(168, 120, 110)
        self.pink_light = self.rgb_to_gl(237, 151, 202)
        self.olive_light = self.rgb_to_gl(205, 204, 93)
        self.cyan_light = self.rgb_to_gl(109, 204, 218)
        self.gray_light = self.rgb_to_gl(162, 162, 162)
        self.color_cycle_light = [self.blue_light, self.orange_light, self.green_light,
                                  self.red_light, self.purple_light, self.brown_light,
                                  self.pink_light, self.olive_light, self.cyan_light]

        # Line thicknesses
        self.thin_line = 1
        self.thick_line = 3

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

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if self.completed_cycles < 10:
            self.completed_cycles = 10
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw monitors names
        self.draw_monitors_names()

        # Draw cycles (time)  axis
        self.draw_cycles_axis()

        # Draw signals
        self.draw_monitored_signals()

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
        print(text)
        self.render()

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
            print(text)
            self.render()
        else:
            self.Refresh()  # triggers the paint event

    def draw_monitors_names(self):
        """Handle monitor names drawing operations."""
        for monitor_number, (device_id, output_id) in enumerate(self.monitors.monitors_dictionary):
            self.render_text(self.devices.get_signal_name(device_id, output_id),
                             3, self.cycle_axis_y - self.monitor_height * (0.7+monitor_number))
        return

    def draw_cycles_axis(self):
        """Handle cycles count axis drawing operations."""
        char_width = self.text_width(str(0))

        # Draw title
        self.render_text("Count", 3, self.cycle_axis_y - self.cycle_axis_y_padding/2)

        # Draw numbers
        for i in range(0, self.completed_cycles + 1, self.clock_display_frequency):
            self.render_text(str(i), self.cycle_start_x + i * self.cycle_width, self.cycle_axis_y - self.cycle_axis_y_padding)

        # Draw the horizontal axis
        GL.glPushAttrib(GL.GL_ENABLE_BIT)  # glPushAttrib is done to return everything to normal after drawing
        cycle_axis_x_offset = 15
        GL.glLineWidth(2.0)
        for i in range(1, self.completed_cycles + 1, self.clock_display_frequency):
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (i-1/2)+char_width/2, self.cycle_axis_y)
            GL.glVertex2f(self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (i+1/2)-char_width/2, self.cycle_axis_y)
            GL.glEnd()
        GL.glPopAttrib()

        # Draw the Vertical axis
        GL.glPushAttrib(GL.GL_ENABLE_BIT)  # glPushAttrib is done to return everything to normal after drawing
        cycle_axis_x_offset = 15
        GL.glLineStipple(2, 0x000F)
        GL.glLineWidth(1.0)
        GL.glColor3f(0.4, 0.4, 0.4)  # signal trace is blue
        GL.glEnable(GL.GL_LINE_STIPPLE)
        for i in range(0, self.completed_cycles, self.clock_display_frequency):
            char_width = self.text_width(str(i))
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (i + 1 / 2),
                          self.cycle_axis_y)
            GL.glVertex2f(self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (i + 1 / 2),
                          self.cycle_axis_y - self.monitor_height * self.monitors_number)
            GL.glEnd()
        GL.glPopAttrib()
        return

    def draw_monitored_signals(self):
        """Handle monitors output drawing operations."""
        for monitor_number, (device_id, output_id) in enumerate(self.monitors.monitors_dictionary):
            self.draw_signal(device_id, output_id, monitor_number)

    def draw_signal(self, device_id, output_id, monitor_number):
        """Handle each monitor output drawing operations."""
        monitor_name = self.devices.get_signal_name(device_id, output_id)
        signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
        monitors_start_x = self.cycle_start_x + self.text_width(str(0))/2
        x_0 = monitors_start_x
        y_0 = -self.monitor_height * monitor_number + self.cycle_axis_y - self.monitor_height
        y_low = y_0 + self.monitors_padding
        y_high = y_0  + self.monitor_height - self.monitors_padding

        color = self.color_cycle[monitor_number%len(self.color_cycle)]
        color_light = self.color_cycle_light[monitor_number%len(self.color_cycle_light)]
        signal_thickness = 2

        # Draw thin black horizontal delimiter between monitors
        self.render_line(monitors_start_x, y_0,
                         monitors_start_x + self.cycle_width * self.completed_cycles, y_0,
                         self.black, self.thin_line)

        # Draw thin gray LOW and HIGH
        self.render_line(monitors_start_x, y_low,
                         monitors_start_x + self.cycle_width * self.completed_cycles, y_low,
                         self.gray, self.thin_line)
        self.render_line(monitors_start_x, y_high,
                         monitors_start_x + self.cycle_width * self.completed_cycles, y_high,
                         self.gray, self.thin_line)

        # Draw signals
        prev_signal = self.devices.BLANK
        for signal in signal_list:
            if signal == self.devices.HIGH:
                # Draw light shading
                self.render_rectangle(x_0, y_low, x_0 + self.cycle_width, y_high, color_light)

                # Draw horizontal HIGH line
                self.render_line(x_0, y_high, x_0 + self.cycle_width, y_high, color, signal_thickness)
                if prev_signal == self.devices.LOW:
                    # Draw a rising edge
                    self.render_line(x_0, y_low, x_0, y_high, color, signal_thickness)

                x_0 += self.cycle_width
                print("-", end="")
            elif signal == self.devices.LOW:
                self.render_line(x_0, y_low, x_0 + self.cycle_width, y_low, color, signal_thickness)
                if prev_signal == self.devices.HIGH:
                    # Draw a falling edge
                    self.render_line(x_0, y_high, x_0, y_low, color, signal_thickness)
                x_0 += self.cycle_width
                print("_", end="")
            elif signal == self.devices.RISING:
                self.render_line(x_0, y_low, x_0, y_high, color, signal_thickness)
                print("/", end="")
            elif signal == self.devices.FALLING:
                self.render_line(x_0, y_high, x_0, y_low, color, signal_thickness)
                print("\\", end="")
            elif signal == self.devices.BLANK:
                x_0 += self.cycle_width
                print(" ", end="")
            prev_signal = signal
        print("\n", end="")



    def render_line(self, x_start, y_start, x_end, y_end, color = (0, 0, 1), thickness = 1.0):
        """Handle line drawing operations."""
        GL.glPushAttrib(GL.GL_ENABLE_BIT)  # glPushAttrib is done to return everything to normal after drawing
        GL.glColor3f(*color)
        GL.glLineWidth(thickness)
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(x_start, y_start)
        GL.glVertex2f(x_end, y_end)
        GL.glEnd()
        GL.glPopAttrib()

    def render_rectangle(self, x_bottom_left, y_bottom_left, x_top_right, y_top_right, color = (0, 0, 1)):
        """Handle transparent rectangle drawing operations."""
        GL.glPushAttrib(GL.GL_ENABLE_BIT)  # glPushAttrib is done to return everything to normal after drawing
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA) # enables transparency
        GL.glEnable(GL.GL_BLEND)
        GL.glColor4f(*color, 0.75) # slightly transparent with alpha 0.75
        GL.glBegin(GL.GL_TRIANGLES) # a rectangle made of 2 triangles
        GL.glVertex2f(x_bottom_left, y_top_right)
        GL.glVertex2f(x_bottom_left, y_bottom_left)
        GL.glVertex2f(x_top_right, y_top_right)
        GL.glVertex2f(x_top_right, y_top_right)
        GL.glVertex2f(x_bottom_left, y_bottom_left)
        GL.glVertex2f(x_top_right, y_bottom_left)
        GL.glEnd()
        GL.glPopAttrib()

    def render_text(self, text, x_pos, y_pos, color = (0, 0, 0), font=GLUT.GLUT_BITMAP_HELVETICA_18):
        """Handle text drawing operations."""
        GL.glColor3f(*color)
        GL.glRasterPos2f(x_pos, y_pos)
        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def update_cycle_axis_layout(self):
        """Handle changes in monitors"""
        self.monitors_number = len(self.monitors.monitors_dictionary)
        self.cycle_start_x = 25 + self.text_width("0") * self.monitors.get_margin()
        self.render()

    def text_width(self, text, font=GLUT.GLUT_BITMAP_HELVETICA_18):
        """Calculate the length in pts of a displayed text.

        Return the length of text in pts.
        """
        width = 0
        for character in text:
            if character != '\n':
                width += GLUT.glutBitmapWidth(font, ord(character))
        return width

    def rgb_to_gl(self, r, g, b):
        """Converse an 8bit RGB color to OpenGL format

        Return a list of the RGB float values.
        """
        return [c/256 for c in (r, g, b)]

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

        # Simulation variables
        self.completed_cycles = 0

        # Saving, loading, and undo/redo variables
        self.is_saved = True
        self.command_manager = CommandManager(self, names, devices, network, monitors)
        self.command_history = []
        self.last_command_index = -1

        # Erros
        [self.NO_ERROR, self.INVALID_COMMAND, self.INVALID_ARGUMENT, self.SIGNAL_NOT_MONITORED, self.OSCILLATING_NETWORK,
         self.CANNOT_OPEN_FILE, self.NOTHING_TO_UNDO, self.NOTHING_TO_REDO, self.SIMULATION_NOT_STARTED, self.UNKNOWN_ERROR] = names.unique_error_codes(10)


        # Configure the file menu
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_OPEN, "&Load")
        fileMenu.Append(wx.ID_SAVE, "&Save")
        fileMenu.Append(wx.ID_SAVEAS, "&Save as")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo")
        editMenu.Append(wx.ID_REDO, "&Redo")
        menuBar.Append(editMenu, "&Edit")

        viewMenu = wx.Menu()
        wx.ID_FULLSCREEN = wx.NewId()
        viewMenu.Append(wx.ID_FULLSCREEN, "&Fullscreen")
        viewMenu.Append(wx.ID_ZOOM_100, "&Zoom reset")
        viewMenu.Append(wx.ID_ZOOM_FIT, "&Zoom fit")
        viewMenu.Append(wx.ID_ZOOM_IN, "&Zoom in")
        viewMenu.Append(wx.ID_ZOOM_OUT, "&Zoom out")
        menuBar.Append(viewMenu, "&View")

        runMenu = wx.Menu()
        wx.ID_CONTINUE = wx.NewId()
        runMenu.Append(wx.ID_EXECUTE, "&Run")
        runMenu.Append(wx.ID_CONTINUE, "&Continue")
        menuBar.Append(runMenu, "&Run")

        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_HELP, "&Help")
        helpMenu.Append(wx.ID_HELP_COMMANDS, "&Help commands")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        # Instances of the classes
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.switches = devices.find_devices(devices.SWITCH)

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
        switches_names = [names.get_name_string(switch_id) for switch_id in self.switches]
        self.switches_select = wx.ComboBox(self, wx.ID_ANY, style = wx.CB_SORT, choices=switches_names)
        self.switches_set_button = wx.ToggleButton(self, wx.ID_ANY, "HIGH", style=wx.BORDER_NONE, size=toggle_button_size)
        self.switches_clear_button = wx.ToggleButton(self, wx.ID_ANY, "LOW", style=wx.BORDER_NONE, size=toggle_button_size)
        self.switches_set_button.Disable()
        self.switches_clear_button.Disable()

        #   Monitors
        self.monitors_select = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_SORT,
                                           choices=self.monitors.get_signal_names()[0] + self.monitors.get_signal_names()[1])
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

        #  Exit fullscreen
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

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
            self.quit_command()
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            # Same functionality as load button
            self.on_load_file_button(None)
        if Id == wx.ID_SAVE:
            self.save_file()
        if Id == wx.ID_SAVEAS:
            self.save_file() #TODO
        if Id == wx.ID_UNDO:
            self.last_command_index -= 1
            if self.last_command_index < -1:
                self.raise_error(self.NOTHING_TO_UNDO)
            else:
                self.execute_command_history()
                self.log_text("Undo")
        if Id == wx.ID_REDO:
            self.last_command_index += 1
            if self.last_command_index == len(self.command_history):
                self.raise_error(self.NOTHING_TO_REDO)
            else:
                self.execute_command_history()
                self.log_text("Redo")
        if Id == wx.ID_MAXIMIZE_FRAME:
            self.Maximize(True)
        if Id == wx.ID_FULLSCREEN:
            self.Show()
            self.ShowFullScreen(True)
            pass
        if Id == wx.ID_ZOOM_100:
            pass
        if Id == wx.ID_ZOOM_FIT:
            pass
        if Id == wx.ID_ZOOM_IN:
            pass
        if Id == wx.ID_ZOOM_OUT:
            pass
        if Id == wx.ID_EXECUTE:
            pass
        if Id == wx.ID_CONTINUE:
            pass
        if Id == wx.ID_HELP:
            pass
        if Id == wx.ID_HELP_COMMANDS:
            pass


    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.simulation_cycles_spin.GetValue()
        self.canvas.render()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        cycles = self.simulation_cycles_spin.GetValue()
        self.run_command(cycles)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        cycles = self.simulation_cycles_spin.GetValue()
        self.continue_command(cycles)

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                return False
        self.canvas.Refresh()
        return True

    def update_cycles(self, cycles):
        self.completed_cycles = cycles
        self.canvas.completed_cycles = cycles
        self.canvas.render()

    def on_console(self, event):
        """Handle the event when the user enters a command in the console."""
        command, *args = self.console.GetValue().split()

        if command == "h":
            self.command_manager.execute_command(HelpCommand())
        elif command == "s" and len(args) == 2:
            self.switch_command(*args)
        elif command == "m" and len(args) == 1:
            self.monitor_command(*args)
        elif command == "z" and len(args) == 1:
            self.zap_command(*args)
        elif command == "r" and len(args) == 1:
            self.run_command(*args)
        elif command == "c" and len(args) == 1:
            self.continue_command(*args)
        elif command == "q":
            self.quit_command()
        else:
            wx.MessageBox("Invalid command. Enter 'h' for help.",
                          "Invalid Command Error", wx.ICON_ERROR | wx.OK)

        self.console.SetValue("")
        
    def on_switches_select(self, event):
        """Handle the event when the user types text in switches text box."""
        self.switches_update_toggle()

    def on_switches_set(self, event):
        """Handle the event when the user sets a switch."""
        device_name = self.switches_select.GetValue()
        self.switch_command(device_name, self.devices.HIGH)

    def on_switches_clear(self, event):
        """Handle the event when the user clears a switch."""
        device_name = self.switches_select.GetValue()
        self.switch_command(device_name, self.devices.LOW)

    def on_monitors_select(self, event):
        """Handle the event when the user types text in monitors text box."""
        self.monitors_update_toggle()

    def on_monitors_set(self, event):
        """Handle the event when the user sets a monitor."""
        signal_name = self.monitors_select.GetValue()
        self.monitor_command(signal_name)

    def on_monitors_zap(self, event):
        """Handle the event when the user clears a monitor."""
        signal_name = self.monitors_select.GetValue()
        ids = self.devices.get_signal_ids(signal_name)
        if ids is not None:
            [device_id, output_id] = ids
            self.monitors.remove_monitor(device_id, output_id)
            self.monitors_set_button.Enable()
            self.monitors_zap_button.Disable()
            self.monitors_zap_button.SetValue(False)
            self.canvas.monitors_number = len(self.monitors.monitors_dictionary)
            self.canvas.update_cycle_axis_layout()
            self.log_text("Zap monitor on " + signal_name)

        else:
            text = "DEBUG: ON MONITORS ZAP, ids is None"
            self.canvas.render()

    def on_load_file_button(self, event):
        """Handle the load file button"""
        if not self.is_saved:
            answer = self.ask_to_save("Load file")
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:
                self.save_file()
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
        if not self.is_saved:
            answer = self.ask_to_save("Load file")
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:
                self.save_file()

        # otherwise ask the user what new file to open
        path = self.load_file_text_box.GetValue()
        self.open_file(path)

    def open_file(self, pathname):
        """Create a new network for another definition file"""
        try:
            with open(pathname, 'r') as file:
                self.load_file_text_box.SetValue(pathname)
                # self.doLoadDataOrWhatever(file)
        except IOError:
            self.raise_error(self.CANNOT_OPEN_FILE, "Cannot open file '%s'." % pathname)

    def ask_to_save(self, action_title):
        """Handle the quit or load actions if the state is not save"""
        save_dlg = wx.MessageBox("Current state of the simulation has not been saved! Save changes?", action_title,
                                 wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT, self)
        return save_dlg

    def save_file(self):
        self.is_saved = True
        return

    def log_text(self, text):
        """Handle the logging in activity_log of an event"""
        text = "".join([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S: "), text])
        self.activity_log_text.AppendText(text+'\n')
        self.is_saved=False

    def help_command(self):
        """Print a list of valid commands."""
        text ="User commands:\n" + \
            "r N         - run the simulation for N cycles\n" + \
            "c N         - continue the simulation for N cycles\n" + \
            "s X N     - set switch X to N (0 or 1)\n" + \
            "m X       - set a monitor on signal X\n" + \
            "z X         - zap the monitor on signal X\n" + \
            "h             - help (this command)\n" + \
            "q            - quit the program"
        self.log_text(text)

    def switches_update_toggle(self):
        """Handle a change in switches."""

        # If the text in the switches box matches the name of a switch, then the set
        # and clear buttons enable according to the current value of the switch.
        device_name = self.switches_select.GetValue()
        device_id = self.names.query(device_name)
        if device_id is not None and device_id in self.switches:
            device = self.devices.get_device(device_id)
            if device.switch_state is self.devices.HIGH:
                self.switches_set_button.Disable()
                self.switches_clear_button.Enable()
                self.switches_clear_button.SetValue(False)

            else:
                self.switches_set_button.Enable()
                self.switches_clear_button.Disable()
                self.switches_set_button.SetValue(False)
        else:
            self.switches_set_button.Disable()
            self.switches_clear_button.Disable()

    def monitors_update_toggle(self):
        """Handle a change in monitors"""

        # If the text in the box matches the name of a signal, then the set
        # and zap buttons enable according to if the if it's monitored or not.
        signal_name = self.monitors_select.GetValue()
        monitored, unmonitored = self.monitors.get_signal_names()
        if signal_name in monitored:
            self.monitors_set_button.Disable()
            self.monitors_zap_button.Enable()
            self.monitors_zap_button.SetValue(False)
        elif signal_name in unmonitored:
            self.monitors_set_button.Enable()
            self.monitors_zap_button.Disable()
            self.monitors_set_button.SetValue(False)
        else:
            self.monitors_set_button.Disable()
            self.monitors_zap_button.Disable()

    def switch_command(self, switch_name, value):
        """Set the state of a switch"""
        self.command_manager.execute_command(SwitchCommand(switch_name, value))

    def monitor_command(self, signal_name):
        """Set monitor on a signal"""
        self.command_manager.execute_command(MonitorCommand(signal_name))

    def zap_command(self, signal_name):
        """Zap monitor on a signal"""
        self.command_manager.execute_command(ZapCommand(signal_name))

    def run_command(self, cycles):
        """Run simulation from start for a number of cycles"""
        self.command_manager.execute_command(RunCommand(cycles))

    def continue_command(self, cycles):
        """Continue simulation from start for a number of cycles"""
        self.command_manager.execute_command(ContinueCommand(cycles))

    def quit_command(self):
        """Handle the quit command"""
        if not self.is_saved:
            answer = self.ask_to_save("Quit")
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:

                path = None
                self.command_manager.execute_command(SaveCommand(path))
        self.Close(True)

    def raise_error(self, error, message=None):
        """Handle user's errors in GUI"""
        if error == self.INVALID_COMMAND:
            wx.MessageBox("Invalid command. Enter 'h' for help.",
                          "Invalid Command Error", wx.ICON_ERROR | wx.OK)
        elif error == self.INVALID_ARGUMENT:
            wx.MessageBox(message, "Invalid Argument Error", wx.ICON_ERROR | wx.OK)
        elif error == self.monitors.MONITOR_PRESENT:
            wx.MessageBox(message, "Monitor Present Error", wx.ICON_ERROR | wx.OK)
        elif error == self.SIGNAL_NOT_MONITORED:
            wx.MessageBox(message, "Signal Not Monitored Error", wx.ICON_ERROR | wx.OK)
        elif error == self.monitors.NOT_OUTPUT:
            wx.MessageBox(message, "Monitor On Input Signal Error", wx.ICON_ERROR | wx.OK)
        elif error == self.network.DEVICE_ABSENT:
            wx.MessageBox(message, "Device Absent Error", wx.ICON_ERROR | wx.OK)
        elif error == self.devices.INVALID_QUALIFIER:
            wx.MessageBox(message, "Invalid Argument Error", wx.ICON_ERROR | wx.OK)
        elif error == self.OSCILLATING_NETWORK:
            wx.MessageBox(message, "Oscillating Network Error", wx.ICON_ERROR | wx.OK)
        elif error == self.CANNOT_OPEN_FILE:
            wx.MessageBox(message, "Cannot Open File Error", wx.ICON_ERROR | wx.OK)
        elif error == self.NOTHING_TO_UNDO:
            wx.MessageBox("No command left to undo. This is the initial state of the simulation", "Nothing To Undo",
                          wx.ICON_ERROR | wx.OK)
        elif error == self.NOTHING_TO_REDO:
            wx.MessageBox("No command left to redo. This is the last state of the simulation", "Nothing To Redo",
                          wx.ICON_ERROR | wx.OK)
        elif error == self.SIMULATION_NOT_STARTED:
            wx.MessageBox("Nothing to continue. Run first.", "Simulation Not Started",
                          wx.ICON_ERROR | wx.OK)
        else:
            wx.MessageBox(message, "Unknown Error", wx.ICON_ERROR | wx.OK)

    def on_key(self, event):
        """Handle generic key press. Used for exiting the fullscreen mode by pressing ESCAPE."""
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.ShowFullScreen(False)
        else:
            event.Skip()