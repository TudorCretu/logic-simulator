"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import sys
import os

import wx.glcanvas as wxcanvas
import datetime
import numpy as np
import math
from OpenGL import GL, GLU, GLUT
from command_manager import *
import builtins
builtins.__dict__['_'] = wx.GetTranslation

import app_const as appC

from wx.lib.mixins.inspection import InspectionMixin

def _displayHook(obj):
    if obj is not None:
        print (repr(obj))

class My2DGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------save
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

    draw_monitors_names(self): Handles monitor names drawing operations.

    draw_cycles_axis(self): Handles cycles axis drawing operations.

    draw_monitored_signals(self): Handles monitors records drawing operations.

    draw_signal(self, device_id, output_id, monitor_number): Handles each
    monitor record drawing operations

    render_line(self, x_start, y_start, x_end, y_end, color=(0, 0, 1),
    thickness=1.0): Handle line drawing operations.

    render_rectangle(self, x_bottom_left, y_bottom_left, x_top_right,
    y_top_right, color=(0, 0, 1)): Handle transparent rectangle drawing.

    render_text(self, text, x_pos, y_pos): Handles text drawing operations.

    zoom_in(self): Zooms in by 25%.

    zoom_out(self): Zooms out by 25%.

    set_zoom(self, zoom): Sets zoom to a specific value.

    set_pan_x(self, scroll_x): Sets pan x to a specific value.

    set_pan_y(self, scroll_x): Sets pan y to a specific value.

    reset_pan(self, scroll_x): Resets pan to the start of the signals.

    pan_to_right_end(self, scroll_x): Pans to the right of the signals.

    update_cycle_axis_layout(self): Handle changes in monitors or cycles
    counter.

    text_width(self, text, font=GLUT.GLUT_BITMAP_HELVETICA_18): Return the
    length of the text in pts.

    rgb_to_gl(self, r, g, b): Converse an 8bit RGB colour to OpenGL format
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
        size = self.GetClientSize()
        self.display_width = size.width
        self.display_height = size.height
        self.pan_x = 0
        self.pan_y = 300
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position
        self.width = 100
        self.height = 100

        # Initialise variables for zooming
        self.zoom = 1
        self.zoom_min = 0.5
        self.zoom_max = 2.5

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Simulation instances
        self.gui = parent
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
        margin = self.monitors.get_margin()
        if margin is None:
            longest_monitor = int(len("Cycles") * 12 / 18)
        else:
            longest_monitor = max(int(len("Cycles") * 12 / 18), margin)
        self.cycle_start_x = 25 + self.text_width("0") * longest_monitor
        self.cycle_axis_y = 0
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
        self.white = (1, 1, 1)
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
        self.color_cycle_light = [self.blue_light, self.orange_light,
                                  self.green_light, self.red_light,
                                  self.purple_light, self.brown_light,
                                  self.pink_light, self.olive_light,
                                  self.cyan_light]

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
        self.cap_pan()
        self.update_cycle_axis_layout()

        self.SetCurrent(self.context)
        if self.completed_cycles < 30:
            self.completed_cycles = 30
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw signals
        self.draw_monitored_signals()

        # Draw cycles (time)  axis
        self.draw_cycles_axis()

        # Draw monitors names
        self.draw_monitors_names()

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
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.cap_pan()
        self.update_cycle_axis_layout()
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() > 0:  # zoom in
            if self.zoom < self.zoom_max:
                self.zoom /= (1.0 - (event.GetWheelRotation() /
                                     (40 * event.GetWheelDelta())))
                self.zoom = min(self.zoom, self.zoom_max)
            else:
                self.zoom = self.zoom_max
            self.init = False
            self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)

        if event.GetWheelRotation() < 0:  # zoom out
            if self.zoom > self.zoom_min:
                self.zoom /= (1.0 - (event.GetWheelRotation() /
                                     (40 * event.GetWheelDelta())))
                self.zoom = max(self.zoom, self.zoom_min)
            else:
                self.zoom = self.zoom_min
            self.init = False
            self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)

        self.render()  # triggers the paint event

    def draw_monitors_names(self):
        """Handle monitor names drawing operations."""
        pan_offset = (self.pan_y - self.display_height) / self.zoom

        # Draw background
        self.render_rectangle(-self.pan_x / self.zoom,
                              self.cycle_axis_y - pan_offset,
                              self.cycle_start_x - self.pan_x / self.zoom,
                              self.cycle_axis_y - self.monitor_height *
                              (1 + len(self.monitors.monitors_dictionary)),
                              color=self.white,
                              alpha=1.0)

        # Draw monitor names text
        for monitor_number, (device_id, output_id) in enumerate(
                self.monitors.monitors_dictionary):
            self.render_text(self.devices.get_signal_name(device_id,
                                                          output_id),
                             -self.pan_x / self.zoom + 3 / self.zoom,
                             self.cycle_axis_y - self.monitor_height *
                             (0.7 + monitor_number))

        # Draw title
        self.render_rectangle(-self.pan_x / self.zoom,
                              self.cycle_axis_y - pan_offset,
                              self.cycle_start_x - self.pan_x / self.zoom,
                              self.cycle_axis_y - pan_offset -
                              self.monitor_height / 2,
                              color=self.white, alpha=1.0)
        self.render_text("Count", (-self.pan_x + 5) / self.zoom,
                         self.cycle_axis_y -
                         self.cycle_axis_y_padding / 2 / self.zoom -
                         pan_offset - 18 / self.zoom, color=self.gray,
                         font=GLUT.GLUT_BITMAP_HELVETICA_12)

        return

    def draw_cycles_axis(self):
        """Handle cycles count axis drawing operations."""
        char_width = self.text_width(str(0))
        pan_offset = (self.pan_y + 18 - self.display_height) / self.zoom

        # Draw background
        self.render_rectangle(0, self.cycle_axis_y - pan_offset,
                              self.cycle_start_x + self.cycle_width * (
                                  self.completed_cycles + 1), 30,
                              color=self.white,
                              alpha=1.0)

        # Draw numbers
        for i in range(0, self.completed_cycles + 1,
                       self.clock_display_frequency):
            self.render_text(str(i), self.cycle_start_x + i * self.cycle_width,
                             self.cycle_axis_y - self.cycle_axis_y_padding /
                             self.zoom - pan_offset, color=self.gray,
                             font=GLUT.GLUT_BITMAP_HELVETICA_12)

        # Draw the horizontal axis
        GL.glPushAttrib(GL.GL_ENABLE_BIT)
        cycle_axis_x_offset = 15
        GL.glLineWidth(1.0)
        GL.glColor4f(*self.gray_light, 0.6)
        for i in range(1, self.completed_cycles + 1,
                       self.clock_display_frequency):
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(
                self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (
                    i - 1 / 2) + char_width / 2,
                self.cycle_axis_y - pan_offset)
            GL.glVertex2f(
                self.cycle_start_x - cycle_axis_x_offset + self.cycle_width * (
                    i + 1 / 2) - char_width / 2,
                self.cycle_axis_y - pan_offset)
            GL.glEnd()
        GL.glPopAttrib()

        # Draw the Vertical axis
        GL.glPushAttrib(GL.GL_ENABLE_BIT)
        cycle_axis_x_offset = 15
        GL.glLineStipple(2, 0x000F)
        GL.glLineWidth(1.0)
        GL.glColor4f(*self.gray_light, 0.6)
        GL.glEnable(GL.GL_LINE_STIPPLE)
        for i in range(0, self.completed_cycles, self.clock_display_frequency):
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(
                self.cycle_start_x - cycle_axis_x_offset +
                self.cycle_width * (i + 1 / 2),
                self.cycle_axis_y - pan_offset)
            GL.glVertex2f(
                self.cycle_start_x - cycle_axis_x_offset +
                self.cycle_width * (i + 1 / 2),
                self.cycle_axis_y - self.monitor_height * self.monitors_number)
            GL.glEnd()
        GL.glPopAttrib()
        return

    def draw_monitored_signals(self):
        """Handle monitors output drawing operations."""
        for monitor_number, (device_id, output_id) in enumerate(
                self.monitors.monitors_dictionary):
            self.draw_signal(device_id, output_id, monitor_number)

    def draw_signal(self, device_id, output_id, monitor_number):
        """Handle each monitor output drawing operations."""
        signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
        monitors_start_x = self.cycle_start_x + self.text_width(str(0)) / 2
        x_0 = monitors_start_x
        y_0 = -self.monitor_height * monitor_number + self.cycle_axis_y - \
            self.monitor_height
        y_low = y_0 + self.monitors_padding
        y_high = y_0 + self.monitor_height - self.monitors_padding

        color = self.color_cycle[monitor_number % len(self.color_cycle)]
        color_light = self.color_cycle_light[monitor_number % len(
            self.color_cycle_light)]
        signal_thickness = 2

        # Draw thin black horizontal delimiter between monitors
        self.render_line(monitors_start_x, y_0,
                         monitors_start_x + self.cycle_width *
                         self.completed_cycles, y_0,
                         self.black, self.thin_line)

        # Draw thin gray LOW and HIGH
        self.render_line(monitors_start_x, y_low,
                         monitors_start_x + self.cycle_width *
                         self.completed_cycles, y_low,
                         self.gray, self.thin_line)
        self.render_line(monitors_start_x, y_high,
                         monitors_start_x + self.cycle_width *
                         self.completed_cycles, y_high,
                         self.gray, self.thin_line)

        # Draw signals
        prev_signal = self.devices.BLANK
        for signal in signal_list:
            if signal == self.devices.HIGH:
                # Draw light shading
                self.render_rectangle(
                    x_0, y_low, x_0 + self.cycle_width, y_high, color_light)

                # Draw horizontal HIGH line
                self.render_line(x_0, y_high, x_0 + self.cycle_width, y_high,
                                 color,
                                 signal_thickness)
                if prev_signal == self.devices.LOW:
                    # Draw a rising edge
                    self.render_line(x_0, y_low, x_0, y_high,
                                     color, signal_thickness)

                x_0 += self.cycle_width
                # print("-", end="")
            elif signal == self.devices.LOW:
                self.render_line(x_0, y_low, x_0 + self.cycle_width, y_low,
                                 color, signal_thickness)
                if prev_signal == self.devices.HIGH:
                    # Draw a falling edge
                    self.render_line(x_0, y_high, x_0, y_low,
                                     color, signal_thickness)
                x_0 += self.cycle_width
                # print("_", end="")
            elif signal == self.devices.RISING:
                self.render_line(x_0, y_low, x_0, y_high,
                                 color, signal_thickness)
                # print("/", end="")
            elif signal == self.devices.FALLING:
                self.render_line(x_0, y_high, x_0, y_low,
                                 color, signal_thickness)
                # print("\\", end="")
            elif signal == self.devices.BLANK:
                x_0 += self.cycle_width
                # print(" ", end="")
            prev_signal = signal
        # print("\n", end="")

    def render_line(self, x_start, y_start, x_end, y_end, color=(0, 0, 1),
                    thickness=1.0):
        """Handle line drawing operations."""
        GL.glPushAttrib(
            GL.GL_ENABLE_BIT)
        GL.glColor3f(*color)
        GL.glLineWidth(thickness)
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(x_start, y_start)
        GL.glVertex2f(x_end, y_end)
        GL.glEnd()
        GL.glPopAttrib()

    def render_rectangle(self, x_bottom_left, y_bottom_left, x_top_right,
                         y_top_right,
                         color=(0, 0, 1), alpha=0.75):
        """Handle transparent rectangle drawing operations."""
        GL.glPushAttrib(
            GL.GL_ENABLE_BIT)
        # enables transparency
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glColor4f(*color, alpha)  # slightly transparent with alpha 0.75
        GL.glBegin(GL.GL_TRIANGLES)  # a rectangle made of 2 triangles
        GL.glVertex2f(x_bottom_left, y_top_right)
        GL.glVertex2f(x_bottom_left, y_bottom_left)
        GL.glVertex2f(x_top_right, y_top_right)
        GL.glVertex2f(x_top_right, y_top_right)
        GL.glVertex2f(x_bottom_left, y_bottom_left)
        GL.glVertex2f(x_top_right, y_bottom_left)
        GL.glEnd()
        GL.glPopAttrib()

    def render_text(self, text, x_pos, y_pos, color=(0, 0, 0),
                    font=GLUT.GLUT_BITMAP_HELVETICA_18):
        """Handle text drawing operations."""
        GL.glColor3f(*color)
        GL.glRasterPos2f(x_pos, y_pos)
        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def zoom_in(self):
        """Zoom in by 25%"""

        self.zoom *= 1.25
        self.zoom = min(self.zoom, self.zoom_max)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def zoom_out(self):
        """Zoom out by 25%"""

        self.zoom /= 1.25
        self.zoom = max(self.zoom, self.zoom_min)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def set_zoom(self, zoom):
        """Set zoom to a specific value"""

        self.zoom = zoom
        self.zoom = min(self.zoom, self.zoom_max)
        self.zoom = max(self.zoom, self.zoom_min)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def set_pan_x(self, scroll_x):
        """Set pan x to a specific value"""
        self.pan_x = -scroll_x
        self.init = False
        self.render()

    def set_pan_y(self, scroll_y):
        """Set pan y to a specific value"""
        self.pan_y = scroll_y + self.display_height - 18
        self.init = False
        self.render()

    def cap_pan(self):
        """Cap pan to not wander outside drawn borders"""
        # Don't allow panning outside the drawn area
        self.pan_x = max(-(self.width - self.display_width), self.pan_x)
        self.pan_x = min(0, self.pan_x)
        self.pan_y = min(self.height - 50, self.pan_y)
        self.pan_y = max(self.display_height - 18, self.pan_y)

    def reset_pan(self):
        """Reset pan to start of displayed signals"""
        self.pan_x = 0
        self.pan_y = self.display_height - 18
        self.init = False
        self.render()

    def pan_to_right_end(self):
        """Pan to the right of the signals"""

        x_at_end_of_signal = self.pan_x + self.zoom * (
            self.cycle_start_x + self.completed_cycles * self.cycle_width)
        self.pan_x -= x_at_end_of_signal - self.GetClientSize().width + 50
        if self.pan_x > 0:
            self.pan_x = 0
        self.init = False
        self.render()

    def update_cycle_axis_layout(self):
        """Handle changes in monitors"""
        self.monitors_number = len(self.monitors.monitors_dictionary)
        margin = self.monitors.get_margin()
        if margin is None:
            longest_monitor = int(len("Cycles") * 12 / 18)
        else:
            longest_monitor = max(int(len("Cycles") * 12 / 18), margin)
        self.cycle_start_x = (25 + self.text_width("0")
                              * longest_monitor) / self.zoom
        self.width = (self.cycle_start_x + self.completed_cycles *
                      self.cycle_width + 30) * self.zoom
        self.height = ((self.monitors_number + 1) *
                       self.monitor_height + 30) * self.zoom
        size = self.GetClientSize()
        self.display_width = size.width
        self.display_height = size.height
        self.gui.update_scrollbars()

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
        return [c / 256 for c in (r, g, b)]


class My3DGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------save
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

    draw_monitors_names(self): Handles monitor names drawing operations.

    draw_cycles_axis(self): Handles cycles axis drawing operations.

    draw_monitored_signals(self): Handles monitors records drawing operations.

    draw_signal(self, device_id, output_id, monitor_number): Handles each
    monitor record drawing operations

    render_line(self, x_start, y_start, x_end, y_end, color=(0, 0, 1),
    thickness=1.0): Handle line drawing operations.

    render_rectangle(self, x_bottom_left, y_bottom_left, x_top_right,
    y_top_right, color=(0, 0, 1)): Handle transparent rectangle drawing
    operations.

    render_text(self, text, x_pos, y_pos): Handles text drawing operations.

    zoom_in(self): Zooms in by 25%.

    zoom_out(self): Zooms out by 25%.

    set_zoom(self, zoom): Sets zoom to a specific value.

    set_pan_x(self, scroll_x): Sets pan x to a specific value.

    set_pan_y(self, scroll_x): Sets pan y to a specific value.

    reset_pan(self, scroll_x): Resets pan to the start of the signals.

    pan_to_right_end(self, scroll_x): Pans to the right of the signals.

    update_cycle_axis_layout(self): Handle changes in monitors or cycles
    counter.

    text_width(self, text, font=GLUT.GLUT_BITMAP_HELVETICA_18): Return the
    length of the text in pts.

    rgb_to_gl(self, r, g, b): Converse an 8bit RGB colour to OpenGL format
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
        
        

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.default_rotate = np.array([[0, 0, 1, 0],
                               [0, -1, 0, 0],
                               [1, 0, 0, 0],
                               [0, 0, 0, 1]], 'f')
        self.scene_rotate = self.default_rotate

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Initialise variables for panning
        size = self.GetClientSize()
        self.display_width = size.width
        self.display_height = size.height
        self.width = 100
        self.height = 100

        # Initialise variables for zooming
        self.zoom = 1
        self.zoom_min = 0.1
        self.zoom_max = 5.0

        # Simulation instances
        self.gui = parent
        self.devices = devices
        self.monitors = monitors

        # Simulation variables
        self.completed_cycles = 0
        self.clock_display_frequency = 1
        self.monitors_number = len(monitors.monitors_dictionary)

        # Layout variables
        self.monitor_width = 55
        self.monitors_padding = 10
        self.signal_height = 40
        self.cycle_width = 80
        # 25pt after the longest monitor name
        margin = self.monitors.get_margin()
        if margin is None:
            longest_monitor = int(len("Cycles") * 12 / 18)
        else:
            longest_monitor = max(int(len("Cycles") * 12 / 18), margin)
        self.cycle_start_x = 25 + self.text_width("0") * longest_monitor
        self.cycle_axis_y = 0
        self.cycle_axis_y_padding = -7
        self.completed_cycles = 0

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
        self.white = (1, 1, 1)
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
        self.color_cycle_light = [self.blue_light, self.orange_light,
                                  self.green_light,
                                  self.red_light, self.purple_light,
                                  self.brown_light,
                                  self.pink_light, self.olive_light,
                                  self.cyan_light]

        # Line thicknesses
        self.thin_line = 1
        self.thick_line = 3
        
        self.Refresh()

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        self.cap_pan()
        self.update_cycle_axis_layout()

        self.SetCurrent(self.context)

        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw signals
        self.draw_monitored_signals()

        # Draw cycles (time)  axis
        self.draw_cycles_axis()

        # Draw monitors names
        self.draw_monitors_names()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_monitored_signals(self):
        """Handle monitors output drawing operations."""
        for monitor_number, (device_id, output_id) in enumerate(
                self.monitors.monitors_dictionary):
            self.draw_signal(device_id, output_id, monitor_number)

    def draw_signal(self, device_id, output_id, monitor_number):
        """Handle each monitor output drawing operations."""
        signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
        monitors_start_x = self.cycle_start_x + self.text_width(str(0)) / 2
        x_0 = monitors_start_x - self.cycle_width * self.completed_cycles / 2
        y_0 = self.monitor_width * (
            monitor_number + 1 - len(
                self.monitors.monitors_dictionary) / 2)
        z_low = -6
        z_high = z_low + self.signal_height
        y_start = y_0 + self.monitors_padding
        y_end = y_0 + self.monitor_width - self.monitors_padding

        color = self.color_cycle[monitor_number % len(self.color_cycle)]
        color_light = self.color_cycle_light[monitor_number % len(
            self.color_cycle_light)]
        signal_thickness = 8
        alpha = 0.6

        # Draw signals
        prev_signal = self.devices.BLANK
        for signal in signal_list:
            if signal == self.devices.HIGH:
                # Draw light shading
                self.render_cuboid(x_0, y_start, z_low, x_0 + self.cycle_width,
                                   y_end, z_high,
                                   color_light, alpha)

                # Draw horizontal HIGH line
                self.render_cuboid(x_0, y_start, z_high,
                                   x_0 + self.cycle_width, y_end,
                                   z_high + signal_thickness, color)
                if prev_signal == self.devices.LOW:
                    # Draw a rising edge
                    self.render_cuboid(x_0, y_start, z_low + signal_thickness,
                                       x_0 + signal_thickness, y_end, z_high,
                                       color)
                    pass
                x_0 += self.cycle_width
                # print("-", end="")
            elif signal == self.devices.LOW:
                self.render_cuboid(x_0, y_start, z_low, x_0 + self.cycle_width,
                                   y_end,
                                   z_low + signal_thickness, color_light)
                if prev_signal == self.devices.HIGH:
                    # Draw a falling edge
                    self.render_cuboid(x_0 - signal_thickness, y_start,
                                       z_low + signal_thickness,
                                       x_0, y_end, z_high + signal_thickness,
                                       color)
                    pass
                x_0 += self.cycle_width
                # print("_", end="")
            elif signal == self.devices.RISING:
                self.render_cuboid(x_0, y_start, z_low + signal_thickness,
                                   x_0 + signal_thickness, y_end, z_high,
                                   color)
                # print("/", end="")
            elif signal == self.devices.FALLING:
                self.render_cuboid(x_0 - signal_thickness, y_start,
                                   z_low + signal_thickness,
                                   x_0, y_end,
                                   z_high + signal_thickness, color)
                # print("\\", end="")
            elif signal == self.devices.BLANK:
                x_0 += self.cycle_width
                # print(" ", end="")
            prev_signal = signal
        # print("\n", end="")

    def render_cuboid(self, z_start, y_start, x_start, z_end, y_end, x_end,
                      color, alpha=1.0):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glPushAttrib(GL.GL_ENABLE_BIT)
        GL.glColor4f(*color, alpha)
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_start, y_start, z_start)
        GL.glVertex3f(x_end, y_start, z_start)
        GL.glVertex3f(x_end, y_start, z_end)
        GL.glVertex3f(x_start, y_start, z_end)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_end, y_end, z_start)
        GL.glVertex3f(x_start, y_end, z_start)
        GL.glVertex3f(x_start, y_end, z_end)
        GL.glVertex3f(x_end, y_end, z_end)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_start, y_end, z_start)
        GL.glVertex3f(x_start, y_start, z_start)
        GL.glVertex3f(x_start, y_start, z_end)
        GL.glVertex3f(x_start, y_end, z_end)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_end, y_start, z_start)
        GL.glVertex3f(x_end, y_end, z_start)
        GL.glVertex3f(x_end, y_end, z_end)
        GL.glVertex3f(x_end, y_start, z_end)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_start, y_start, z_start)
        GL.glVertex3f(x_start, y_end, z_start)
        GL.glVertex3f(x_end, y_end, z_start)
        GL.glVertex3f(x_end, y_start, z_start)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_start, y_end, z_end)
        GL.glVertex3f(x_start, y_start, z_end)
        GL.glVertex3f(x_end, y_start, z_end)
        GL.glVertex3f(x_end, y_end, z_end)
        GL.glEnd()
        GL.glPopAttrib()

    def draw_cycles_axis(self):
        """Handle cycles count axis drawing operations."""
        char_width = self.text_width(str(0))
        if self.completed_cycles == 0:
            return
        # Draw numbers
        for i in range(0, self.completed_cycles + 1,
                       self.clock_display_frequency):
            self.render_text(str(i), self.cycle_start_x + (
                i - self.completed_cycles / 2) * self.cycle_width,
                self.monitor_width *
                (len(self.monitors.monitors_dictionary) / 2 + 1),
                0, font=GLUT.GLUT_BITMAP_HELVETICA_12)

        for i in range(0, self.completed_cycles + 1,
                       self.clock_display_frequency):
            self.render_text(str(i), self.cycle_start_x + (
                i - self.completed_cycles / 2) * self.cycle_width,
                -self.monitor_width *
                (len(self.monitors.monitors_dictionary) / 2 - 1),
                0, font=GLUT.GLUT_BITMAP_HELVETICA_12)

        # Draw the horizontal axis
        GL.glPushAttrib(
            GL.GL_ENABLE_BIT)
        cycle_axis_x_offset = 15
        GL.glLineWidth(3.0)
        GL.glColor4f(*self.white, 0.6)
        for i in np.linspace(-self.completed_cycles / 2 + 0.5,
                             self.completed_cycles / 2 - 0.5,
                             self.completed_cycles):
            GL.glBegin(GL.GL_LINES)
            GL.glVertex3f(0,
                          self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 + 1),
                          self.cycle_start_x - cycle_axis_x_offset / 2 +
                          self.cycle_width * (i - 1 / 2) + char_width / 2)
            GL.glVertex3f(0,
                          self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 + 1),
                          self.cycle_start_x - cycle_axis_x_offset / 2 +
                          self.cycle_width * (i + 1 / 2) - char_width / 2)
            GL.glEnd()
            GL.glBegin(GL.GL_LINES)
            GL.glVertex3f(0,
                          -self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 - 1),
                          self.cycle_start_x - cycle_axis_x_offset / 2 +
                          self.cycle_width * (i - 1 / 2) + char_width / 2)
            GL.glVertex3f(0,
                          -self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 - 1),
                          self.cycle_start_x - cycle_axis_x_offset / 2 +
                          self.cycle_width * (i + 1 / 2) - char_width / 2)
            GL.glEnd()
        GL.glPopAttrib()

        # # Draw the Vertical axis
        GL.glPushAttrib(GL.GL_ENABLE_BIT)
        cycle_axis_x_offset = 15
        GL.glLineStipple(2, 0x000F)
        GL.glLineWidth(3.0)
        GL.glColor4f(*self.white, 0.6)
        GL.glEnable(GL.GL_LINE_STIPPLE)
        for i in np.linspace(-self.completed_cycles / 2 - 0.5,
                             self.completed_cycles / 2 - 0.5,
                             self.completed_cycles + 1):
            GL.glBegin(GL.GL_LINES)
            GL.glVertex3f(0, -self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 - 1),
                          self.cycle_start_x - cycle_axis_x_offset / 2 +
                          self.cycle_width * (i + 1 / 2))
            GL.glVertex3f(0, self.monitor_width *
                          (len(self.monitors.monitors_dictionary) / 2 + 1),
                          self.cycle_start_x - cycle_axis_x_offset +
                          self.cycle_width * (i + 1 / 2))
            GL.glEnd()
        GL.glPopAttrib()
        # return

    def draw_monitors_names(self):
        for monitor_number, (device_id, output_id) in enumerate(
                self.monitors.monitors_dictionary):
            self.render_text(
                self.devices.get_signal_name(device_id, output_id),
                -self.pan_x / self.zoom + 3 / self.zoom,
                self.cycle_axis_y - self.monitor_width * (
                    monitor_number - 0.5 - len(
                        self.monitors.monitors_dictionary) / 2),
                self.signal_height + 5 + self.cycle_start_x/2)

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            if not wx.GetKeyState(wx.WXK_CONTROL):
                # if CTRL is not pushed, rotate
                GL.glMatrixMode(GL.GL_MODELVIEW)
                GL.glLoadIdentity()
                x = event.GetX() - self.last_mouse_x
                y = event.GetY() - self.last_mouse_y
                if event.LeftIsDown():
                    GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
                if event.MiddleIsDown():
                    GL.glRotatef((x + y), 0, 0, 1)
                if event.RightIsDown():
                    self.pan_x += x * self.zoom
                    self.pan_y -= y * self.zoom
                GL.glMultMatrixf(self.scene_rotate)
                GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)

                self.last_mouse_x = event.GetX()
                self.last_mouse_y = event.GetY()
                self.init = False
            else:
                # if CTRL is pushed, pan
                self.pan_x += (event.GetX() - self.last_mouse_x) * self.zoom
                self.pan_y -= (event.GetY() - self.last_mouse_y) * self.zoom
                self.last_mouse_x = event.GetX()
                self.last_mouse_y = event.GetY()
                self.init = False

        if event.GetWheelRotation() > 0:  # zoom in
            if self.zoom < self.zoom_max:
                self.zoom /= (1.0 - (event.GetWheelRotation() /
                                     (40 * event.GetWheelDelta())))
                self.zoom = min(self.zoom, self.zoom_max)
            else:
                self.zoom = self.zoom_max
            self.init = False
            self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)

        if event.GetWheelRotation() < 0:  # zoom out
            if self.zoom > self.zoom_min:
                self.zoom /= (1.0 - (event.GetWheelRotation() /
                                     (40 * event.GetWheelDelta())))
                self.zoom = max(self.zoom, self.zoom_min)
            else:
                self.zoom = self.zoom_min
            self.init = False
            self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)

        self.Refresh()  # triggers the paint event

    def render_text(self, text, z_pos, y_pos, x_pos,
                    font=GLUT.GLUT_BITMAP_HELVETICA_18):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glColor3f(*self.white)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def zoom_in(self):
        """Zoom in by 25%"""

        self.zoom *= 1.25
        self.zoom = min(self.zoom, self.zoom_max)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def zoom_out(self):
        """Zoom out by 25%"""

        self.zoom /= 1.25
        self.zoom = max(self.zoom, self.zoom_min)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def set_zoom(self, zoom):
        """Set zoom to a specific value"""

        self.zoom = zoom
        self.zoom = min(self.zoom, self.zoom_max)
        self.zoom = max(self.zoom, self.zoom_min)
        self.init = False
        self.gui.zoom_slider.SetValue(self.zoom * self.gui.zoom_resolution)
        self.render()

    def set_pan_x(self, scroll_x):
        """Set pan x to a specific value"""
        self.pan_x = scroll_x + self.width/2
        self.pan_y = 0
        self.scene_rotate = self.default_rotate
        self.init = False
        self.render()

    def set_pan_y(self, scroll_y):
        """Set pan y to a specific value"""
        self.pan_y = scroll_y + self.display_height - 18
        self.scene_rotate = self.default_rotate
        self.init = False
        self.render()

    def cap_pan(self):
        """Cap pan to not wander outside drawn borders"""
        # Don't allow panning outside the drawn area
        # self.pan_x = max(-(self.width - self.display_width), self.pan_x)
        # self.pan_x = min(0, self.pan_x)
        # self.pan_y = min(self.height - 50, self.pan_y)
        # self.pan_y = max(self.display_height - 18, self.pan_y)
        pass

    def reset_pan(self):
        """Reset pan to center of displayed signals"""
        self.gui.zoom_slider.SetValue(1*self.gui.zoom_resolution)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        # Reset pan to center
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1

        # Reset to identity matrix
        GL.glLoadIdentity()

        # Reset to default view
        GL.glRotatef(*[90, 0, -1, 0])
        GL.glRotatef(*[180, 1, 0, 0])

        # a = (GL.GLfloat * 16)()
        GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
        self.init = False

        self.render()

    def pan_to_right_end(self):
        """Pan to the right of the signals"""
        self.reset_pan()
        self.set_pan_x(-self.width-self.cycle_width)
        self.init = False
        self.render()

    def update_cycle_axis_layout(self):
        """Handle changes in monitors"""
        self.monitors_number = len(self.monitors.monitors_dictionary)
        margin = self.monitors.get_margin()
        if margin is None:
            longest_monitor = int(len("Cycles") * 12 / 18)
        else:
            longest_monitor = max(int(len("Cycles") * 12 / 18), margin)
        self.cycle_start_x = (25 + self.text_width("0")
                              * longest_monitor) / self.zoom
        self.width = (self.cycle_start_x + self.completed_cycles *
                      self.cycle_width + 30) * self.zoom
        self.height = ((self.monitors_number + 1) *
                       self.monitor_width + 30) * self.zoom
        size = self.GetClientSize()
        self.display_width = size.width
        self.display_height = size.height
        self.gui.update_scrollbars()

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
        return [c / 256 for c in (r, g, b)]


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.
    path: initial path of the file loaded
    names - instance of the names.Names() class.
    devices - instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors - instance of the monitors.Monitors() class.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
    control value.

    on_run_button(self, event): Event handler for when the user clicks the run
    button.

    on_continue_button(self, event): Event handler for when the user clicks the
    continue button.

    on_console(self, event): Event handler for when the user types in the
    console.

    on_switches_select(self, event): Event handler for when the user types in
    the switches box.

    on_switches_set(self, event): Event handler for when the user clicks the
    switches set button.

    on_switches_clear(self, event): Event handler for when the user clicks the
    switches clear button.

    on_monitors_select(self, event): Event handler for when the user types in
    the monitors text box.

    on_monitors_set(self, event): Event handler for when the user clicks the
    monitors set button.

    on_monitors_zap(self, event): Event handler for when the user clicks the
    monitors zap button.

    on_load_file_button(self, event): Event handler for when the user clicks
    the load file button.

    on_load_file_text_box(self, event): Event handler for when the user enters
    a filepath into load file text box.

    on_scrollbar_ver(self, event): Event handler for when the user scrolls the
    vertical scrollbar

    on_scrollbar_hor(self, event): Event handler for when the user scrolls the
    horizontal scrollbar

    on_zoom_minus_button(self, event): Event handler for when the user clicks
    the zoom minus button

    on_zoom_plus_button(self, event): Event handler for when the user clicks
    the zoom plus button

    on_zoom_scroll(self, event): Event handler for when the user scrolls the
    zoom slider

    open_file(self, pathname): Creates a new network for another definition
    file.

    ask_to_save(self, action_title): Opens a save message box.

    save_file(self): Open a save file dialog and executes the save command.

    log_text(self, text): Writes text along with timestamp in activity log.

    help_command(self): Prints a list of valid commands in activity log.

    switches_update_toggle(self): Updates the visibility of the set/clear
    switch buttons when switches change.

    monitors_update_toggle(self): Updates the visibility of the set/zap monitor
    buttons when monitors change.

    update_toolbar(self): Update undo/redo visibility buttons in toolbar
    display when a command is undone or redone.

    update_scrollbars(self): Updates the canvas' scrollbars position, size,
    visibility when the users pans/zooms.

    update_cycles(self, cycles): Updates the number of completed cycles in both
     the gui and the canvas.

    switch_command(self, switch_name, value): Set the value state to a switch.

    monitor_command(self, signal_name): Set a monitor on a signal.

    zap_command(self, signal_name): Zap a monitor on a signal.

    run_command(self, cycles): Run the simulation for a number of cycles.

    continue_command(self, cycles): Continue the simulation for a number of
    cycles.

    quit_command(self): Handle the quit command.

    raise_error(self, error, message=None): Display a message box with the
    error to the user.

    on_key(self, event): Event handler for when the user presses a key.

    """
    
    def __init__(self, title, path, names, devices, network, monitors,lang_code):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title =title, size=(800, 600))
        # set attributte for language code eg. "en" for English, "el"
        # for Greek 
        self.lang_code = lang_code
        self.path_name = path
        
        sys.displayhook = _displayHook
        
        self.appName = "I18N sample application"
        
        self.doConfig()
        
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.lang_code = lang_code

        self.updateLanguage(lang_code)

        # Simulation variables
        self.completed_cycles = 0

        # Saving, loading, and undo/redo variables
        self.is_saved = True
        self.command_manager = CommandManager(
            self, names, devices, network, monitors)

        # Configure the menu
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, _("&New"))
        fileMenu.Append(wx.ID_OPEN, _("&Load"))
        fileMenu.Append(wx.ID_SAVE, _("&Save"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&File"))

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, _("&Undo\tCTRL+Z"))
        editMenu.Append(wx.ID_REDO, _("&Redo\tCTRL+SHIFT+Z"))
        menuBar.Append(editMenu, _("&Edit"))

        viewMenu = wx.Menu()
        wx.ID_FULLSCREEN = wx.NewId()
        viewMenu.Append(wx.ID_FULLSCREEN, _("&Fullscreen"))
        viewMenu.Append(wx.ID_ZOOM_100, _("&Actual Size"))
        viewMenu.Append(wx.ID_ZOOM_IN, _("Zoom &In\tCTRL++"))
        viewMenu.Append(wx.ID_ZOOM_OUT, _("Zoom &Out\tCTRL+-"))
        menuBar.Append(viewMenu, _("&View"))

        runMenu = wx.Menu()
        wx.ID_CONTINUE = wx.NewId()
        runMenu.Append(wx.ID_EXECUTE, _("&Run"))
        runMenu.Append(wx.ID_CONTINUE, _("&Continue"))
        menuBar.Append(runMenu, _("&Run"))

        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, _("&About"))
        helpMenu.Append(wx.ID_HELP, _("&Help"))
        helpMenu.Append(wx.ID_HELP_COMMANDS, _("&Help Commands"))
        menuBar.Append(helpMenu, _("&Help"))

        LangMenu = wx.Menu()
        self.ENGLISH_BUTTON_ID = 10001
        self.GREEK_BUTTON_ID = 10002
        LangMenu.Append(self.ENGLISH_BUTTON_ID, "&ENGLISH")
        LangMenu.Append(self.GREEK_BUTTON_ID, "&ΕΛΛΗΝΙΚΑ")
        menuBar.Append(LangMenu, u"&LANGUAGE / Γλώσσα")
        self.SetMenuBar(menuBar)
        

        # Configure the tooblar
        self.toolbar = wx.ToolBar(self)
        self.toolbar.AddTool(wx.ID_NEW, 'New file',
                             wx.ArtProvider.GetBitmap(wx.ART_NEW))
        self.toolbar.AddTool(wx.ID_OPEN, 'Load',
                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        self.toolbar.AddTool(wx.ID_SAVE, 'Save',
                             wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        self.toolbar.AddTool(wx.ID_UNDO, 'Undo',
                             wx.ArtProvider.GetBitmap(wx.ART_UNDO))
        self.toolbar.AddTool(wx.ID_REDO, 'Redo',
                             wx.ArtProvider.GetBitmap(wx.ART_REDO))
        self.toolbar.AddTool(wx.ID_EXIT, 'Exit',
                             wx.ArtProvider.GetBitmap(wx.ART_QUIT))

        self.toolbar.Realize()
        self.toolbar.EnableTool(wx.ID_UNDO, False)
        self.toolbar.EnableTool(wx.ID_REDO, False)
        self.SetToolBar(self.toolbar)

        # Configure the hotkeys
        self.accel_tbl = wx.AcceleratorTable(
            [(wx.ACCEL_CTRL, ord('N'), wx.ID_NEW),
             (wx.ACCEL_CTRL, ord(
                 'O'), wx.ID_OPEN),
             (wx.ACCEL_CTRL, ord(
                 'S'), wx.ID_SAVE),
             (wx.ACCEL_CTRL, ord(
                 'Z'), wx.ID_UNDO),
             (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('Z'),
              wx.ID_REDO),
             (wx.ACCEL_CTRL, ord(
                 'Y'), wx.ID_REDO),
             (wx.ACCEL_CTRL, ord(
                 'H'), wx.ID_HELP),
             (wx.ACCEL_CTRL, ord(
                 '+'), wx.ID_ZOOM_IN),
             (wx.ACCEL_CTRL, ord(
                 '-'), wx.ID_ZOOM_OUT)
             ])
        self.SetAcceleratorTable(self.accel_tbl)

        # Instances of the classes
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.switches = devices.find_devices(devices.SWITCH)

        # Configure the widgets
        #  Canvas for drawing signals
        self.canvas_2D = My2DGLCanvas(self, devices, monitors)
        self.canvas_3D = My3DGLCanvas(self, devices, monitors)
        self.canvas = self.canvas_2D
        self.canvas_scrollbar_hor = wx.ScrollBar(self, wx.ID_ANY)
        self.canvas_scrollbar_ver = wx.ScrollBar(
            self, wx.ID_ANY, style=wx.SB_VERTICAL)
        self.update_scrollbars()

        #  Top sizer
        self.load_file_button = wx.Button(self, wx.ID_ANY, _("Load file"))
        self.load_file_text_box = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        if path is not None:
            self.load_file_text_box.SetValue(path.split('/')[-1])

        #  Activity log sizer
        self.activity_log_title = wx.StaticText(
            self, wx.ID_ANY, _("Activity log"))
        self.activity_log_text = wx.TextCtrl(self, wx.ID_ANY, "",
                                             style=wx.TE_MULTILINE |
                                             wx.TE_READONLY |
                                             wx.ALIGN_TOP)
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL)
        self.activity_log_text.SetFont(font)

        #  Console sizer
        self.console = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)

        #  Side Sizer
        #   Switches
        toggle_button_size = wx.Size(50, wx.DefaultSize.GetHeight())
        switches_names = [names.get_name_string(
            switch_id) for switch_id in self.switches]
        self.switches_select = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_SORT,
                                           choices=switches_names)
        self.switches_set_button = wx.ToggleButton(self, wx.ID_ANY, _("HIGH"),
                                                   style=wx.BORDER_NONE,
                                                   size=toggle_button_size)
        self.switches_clear_button = wx.ToggleButton(self, wx.ID_ANY, _("LOW"),
                                                     style=wx.BORDER_NONE,
                                                     size=toggle_button_size)
        self.switches_set_button.Disable()
        self.switches_clear_button.Disable()

        #   Monitors
        monitor_names = self.monitors.get_signal_names()[0] + \
            self.monitors.get_signal_names()[1]
        self.monitors_select = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_SORT,
                                           choices=monitor_names)
        self.monitors_set_button = wx.ToggleButton(self, wx.ID_ANY, _("SET"),
                                                   style=wx.BORDER_NONE,
                                                   size=toggle_button_size)
        self.monitors_zap_button = wx.ToggleButton(self, wx.ID_ANY, _("ZAP"),
                                                   style=wx.BORDER_NONE,
                                                   size=toggle_button_size)
        self.monitors_set_button.Disable()
        self.monitors_zap_button.Disable()

        #   Simulation
        self.simulation_cycles_spin = wx.SpinCtrl(
            self, wx.ID_ANY, "10", max=10 ** 10)
        self.simulation_run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.simulation_continue_button = wx.Button(
            self, wx.ID_ANY, _("Continue"))

        #   Zoom
        zoom_button_size = wx.Size(25, 25)
        self.zoom_resolution = 100
        self.zoom_slider = wx.Slider(self, wx.ID_ANY,
                                     value=1 * self.zoom_resolution,
                                     minValue=self.zoom_resolution *
                                     self.canvas.zoom_min,
                                     maxValue=self.zoom_resolution *
                                     self.canvas.zoom_max,
                                     style=wx.SL_LABELS | wx.SL_TICKS,
                                     name=_("Zoom"))
        self.zoom_slider.SetTickFreq(250)
        if wx.Platform == '__WXGTK__':  # If available, use zoom bitmaps
            plus = wx.ArtProvider.GetBitmap(
                "gtk-zoom-in", wx.ART_MENU, size=zoom_button_size)
            self.zoom_plus_button = wx.BitmapButton(
                self, wx.ID_ANY, plus, size=zoom_button_size)
            minus = wx.ArtProvider.GetBitmap(
                "gtk-zoom-out", wx.ART_MENU, size=zoom_button_size)
            self.zoom_minus_button = wx.BitmapButton(self, wx.ID_ANY, minus,
                                                     size=zoom_button_size)

        else:  # otherwise, just use +/- string
            self.zoom_plus_button = wx.Button(
                self, wx.ID_ANY, "+", size=zoom_button_size)
            self.zoom_minus_button = wx.Button(
                self, wx.ID_ANY, "-", size=zoom_button_size)

        #   Pan
        self.pan_left_button = wx.Button(self, wx.ID_ANY, _(" <- To Start"))
        self.pan_reset_button = wx.Button(self, wx.ID_ANY, _(" Reset View"))
        self.pan_right_button = wx.Button(self, wx.ID_ANY, _(" To End ->"))

        #   2D/3D
        self.two_dim_button = wx.Button(self, wx.ID_ANY, _("3D"))

        #  Static Strings
        console_title = wx.StaticText(self, wx.ID_ANY, _("Console"))
        side_title = wx.StaticText(self, wx.ID_ANY, _("Properties"))
        switches_title = wx.StaticText(
            self, wx.ID_ANY, _("Change State of Switch"))
        monitors_title = wx.StaticText(self, wx.ID_ANY, _("Set or Zap Monitors"))
        run_simulation_title = wx.StaticText(self, wx.ID_ANY, _("Simulate"))
        zoom_title = wx.StaticText(self, wx.ID_ANY, _("Zoom"))
        pan_title = wx.StaticText(self, wx.ID_ANY, _("Pan"))
        two_dim_title = wx.StaticText(self, wx.ID_ANY, _("2D/3D View"))

        #  Lines
        line_side = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_switches = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_switches_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_monitors = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_monitors_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_run_simulation = wx.StaticLine(
            self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_run_simulation_end = wx.StaticLine(
            self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_zoom = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_zoom_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_pan = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_pan_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_two_dim = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)
        line_two_dim_end = wx.StaticLine(self, wx.ID_ANY, style=wx.HORIZONTAL)

        # Bind events to widgets
        #  Menu
        self.Bind(wx.EVT_MENU, self.on_menu)

        #  Exit fullscreen
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        #  Load file
        self.load_file_button.Bind(wx.EVT_BUTTON, self.on_load_file_button)
        self.load_file_text_box.Bind(
            wx.EVT_TEXT_ENTER, self.on_load_file_text_box)

        #  Scrollbars
        self.canvas_scrollbar_ver.Bind(wx.EVT_SCROLL, self.on_scrollbar_ver)
        self.canvas_scrollbar_hor.Bind(wx.EVT_SCROLL, self.on_scrollbar_hor)

        #  Console
        self.console.Bind(wx.EVT_TEXT_ENTER, self.on_console)

        #  Switches
        self.switches_select.Bind(wx.EVT_TEXT, self.on_switches_select)
        self.switches_set_button.Bind(
            wx.EVT_TOGGLEBUTTON, self.on_switches_set)
        self.switches_clear_button.Bind(
            wx.EVT_TOGGLEBUTTON, self.on_switches_clear)

        #  Monitors
        self.monitors_select.Bind(wx.EVT_TEXT, self.on_monitors_select)
        self.monitors_set_button.Bind(
            wx.EVT_TOGGLEBUTTON, self.on_monitors_set)
        self.monitors_zap_button.Bind(
            wx.EVT_TOGGLEBUTTON, self.on_monitors_zap)

        #  Run simulation
        self.simulation_cycles_spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.simulation_run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.simulation_continue_button.Bind(
            wx.EVT_BUTTON, self.on_continue_button)

        #  Zoom
        self.zoom_minus_button.Bind(wx.EVT_BUTTON, self.on_zoom_minus_button)
        self.zoom_slider.Bind(wx.EVT_SCROLL, self.on_zoom_scroll)
        self.zoom_plus_button.Bind(wx.EVT_BUTTON, self.on_zoom_plus_button)

        #  Pan
        self.pan_left_button.Bind(wx.EVT_BUTTON, self.on_pan_left_button)
        self.pan_reset_button.Bind(wx.EVT_BUTTON, self.on_pan_reset_button)
        self.pan_right_button.Bind(wx.EVT_BUTTON, self.on_pan_right_button)

        # 2D
        self.two_dim_button.Bind(wx.EVT_BUTTON, self.on_two_dim_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        central_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_scrollbar_ver_sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        zoom_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zoom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pan_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pan_sizer = wx.BoxSizer(wx.HORIZONTAL)
        two_dim_title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        two_dim_sizer = wx.BoxSizer(wx.HORIZONTAL)

        line_sizer_side = wx.BoxSizer(wx.VERTICAL)
        line_sizer_switches = wx.BoxSizer(wx.VERTICAL)
        line_sizer_monitors = wx.BoxSizer(wx.VERTICAL)
        line_sizer_run_simulation = wx.BoxSizer(wx.VERTICAL)
        line_sizer_zoom = wx.BoxSizer(wx.VERTICAL)
        line_sizer_pan = wx.BoxSizer(wx.VERTICAL)
        line_sizer_two_dim = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(top_sizer, 0, wx.EXPAND, 5)
        main_sizer.Add(central_sizer, 10, wx.EXPAND, 5)
        main_sizer.Add(activity_log_sizer, 3, wx.LEFT |
                       wx.RIGHT | wx.EXPAND, 5)
        main_sizer.Add(console_sizer, 1, wx.LEFT |
                       wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)

        top_sizer.Add(self.load_file_button, 0, wx.LEFT, 5)
        top_sizer.Add(self.load_file_text_box, 1, wx.LEFT | wx.RIGHT, 5)

        central_sizer.Add(self.canvas_sizer, 5, wx.EXPAND |
                          wx.TOP | wx.LEFT | wx.BOTTOM, 5)
        central_sizer.Add(canvas_scrollbar_ver_sizer, 0,
                          wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, 5)
        central_sizer.Add(side_sizer, 1, wx.ALL, 5)

        self.canvas_sizer.Add(self.canvas_2D, 5, wx.EXPAND, 0)
        self.canvas_sizer.Add(self.canvas_3D, 5, wx.EXPAND, 0)
        self.canvas_sizer.Hide(self.canvas_3D, True)
        self.canvas_sizer.Add(self.canvas_scrollbar_hor, 0, wx.EXPAND, 0)

        canvas_scrollbar_ver_sizer.Add(
            self.canvas_scrollbar_ver, 0, wx.EXPAND | wx.BOTTOM, 15)

        activity_log_sizer.Add(self.activity_log_title, 0, wx.TOP, 10)
        activity_log_sizer.Add(self.activity_log_text, 1, wx.EXPAND, 5)

        console_sizer.Add(console_title, 1, wx.TOP, 5)
        console_sizer.Add(self.console, 1, wx.EXPAND, 5)

        side_sizer.Add(side_title_sizer, 0, wx.TOP | wx.EXPAND, 1)
        side_sizer.Add(switches_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(switches_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_switches_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(monitors_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(monitors_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_monitors_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(simulation_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(simulation_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(line_run_simulation_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(zoom_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(zoom_sizer, 0, wx.ALL | wx.EXPAND, 0)
        side_sizer.Add(line_zoom_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(pan_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(pan_sizer, 0, wx.ALL | wx.EXPAND, 0)
        side_sizer.Add(line_pan_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        side_sizer.Add(two_dim_title_sizer, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        side_sizer.Add(two_dim_sizer, 0, wx.ALL | wx.EXPAND, 0)
        side_sizer.Add(line_two_dim_end, 0, wx.TOP |
                       wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        side_title_sizer.Add(side_title, 0, wx.TOP, 0)
        side_title_sizer.Add(line_sizer_side, 1, wx.TOP |
                             wx.RIGHT | wx.EXPAND, 3)

        switches_title_sizer.Add(switches_title, 0, wx.LEFT | wx.TOP, 10)
        switches_title_sizer.Add(
            line_sizer_switches, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        switches_sizer.Add(self.switches_select, 2,
                           wx.TOP | wx.LEFT | wx.EXPAND, 12)
        switches_sizer.Add(self.switches_set_button, 0, wx.TOP | wx.LEFT, 12)
        switches_sizer.Add(self.switches_clear_button,
                           0, wx.TOP | wx.RIGHT, 12)

        monitors_title_sizer.Add(monitors_title, 0, wx.LEFT | wx.TOP, 10)
        monitors_title_sizer.Add(
            line_sizer_monitors, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        monitors_sizer.Add(self.monitors_select, 2,
                           wx.TOP | wx.LEFT | wx.EXPAND, 12)
        monitors_sizer.Add(self.monitors_set_button, 0, wx.TOP | wx.LEFT, 12)
        monitors_sizer.Add(self.monitors_zap_button, 0, wx.TOP | wx.RIGHT, 12)

        simulation_title_sizer.Add(
            run_simulation_title, 0, wx.LEFT | wx.TOP, 10)
        simulation_title_sizer.Add(line_sizer_run_simulation, 1,
                                   wx.TOP | wx.RIGHT | wx.EXPAND,
                                   10)

        simulation_sizer.Add(self.simulation_cycles_spin,
                             4, wx.LEFT | wx.TOP | wx.EXPAND, 12)
        simulation_sizer.Add(self.simulation_run_button,
                             0, wx.LEFT | wx.TOP, 12)
        simulation_sizer.Add(
            self.simulation_continue_button, 0, wx.LEFT | wx.TOP, 12)

        zoom_title_sizer.Add(zoom_title, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        if wx.Platform == '__WXGTK__':
            bmp = wx.ArtProvider.GetBitmap("gtk-find", wx.ART_MENU)
            zoom_bmp = wx.StaticBitmap(self, wx.ID_ANY, bmp)
            zoom_title_sizer.Add(zoom_bmp, 0, wx.Left | wx.TOP, 10)
        zoom_title_sizer.Add(line_sizer_zoom, 1, wx.TOP |
                             wx.RIGHT | wx.EXPAND, 10)

        zoom_sizer.Add(self.zoom_minus_button, 0, wx.LEFT | wx.TOP, 20)
        zoom_sizer.Add(self.zoom_slider, 1, wx.EXPAND, 0)
        zoom_sizer.Add(self.zoom_plus_button, 0, wx.RIGHT | wx.TOP, 20)

        pan_title_sizer.Add(pan_title, 0, wx.LEFT | wx.TOP, 10)
        pan_title_sizer.Add(line_sizer_pan, 1,
                                wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        pan_sizer.Add(self.pan_left_button, 1, wx.ALL | wx.EXPAND, 5)
        pan_sizer.Add(self.pan_reset_button, 1, wx.ALL | wx.EXPAND, 5)
        pan_sizer.Add(self.pan_right_button, 1, wx.ALL | wx.EXPAND, 5)

        two_dim_title_sizer.Add(two_dim_title, 0, wx.LEFT | wx.TOP, 10)
        two_dim_title_sizer.Add(line_sizer_two_dim, 1,
                                wx.TOP | wx.RIGHT | wx.EXPAND, 10)

        two_dim_sizer.Add(self.two_dim_button, 1, wx.ALL | wx.EXPAND, 10)

        line_sizer_side.Add(line_side, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_switches.Add(line_switches, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_monitors.Add(line_monitors, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_run_simulation.Add(
            line_run_simulation, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_zoom.Add(line_zoom, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_pan.Add(line_pan, 0, wx.ALL | wx.EXPAND, 5)
        line_sizer_two_dim.Add(line_two_dim, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizeHints(900, 600)
        self.SetSizer(main_sizer)
        self.update_scrollbars()
        self.Show()
        self.Maximize(True)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        print(Id)
        if Id == self.ENGLISH_BUTTON_ID:
            new_gui = Gui("Logic Simulator", self.path_name, self.names, self.devices, self.network, self.monitors,"en")
            new_gui.Show(True)
            self.Close(True)
			
        if Id == self.GREEK_BUTTON_ID:
            new_gui = Gui("Λογική Προσομοιωτής", self.path_name, self.names, self.devices, self.network, self.monitors,"el")
            new_gui.Show(True)
            self.Close(True)
			
			
        if Id == wx.ID_NEW:
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            app = wx.App()
            gui = Gui(_("Logic Simulator"), None, names,
                      devices, network, monitors, self.lang_code)
            gui.Show(True)
            app.MainLoop()
        if Id == wx.ID_EXIT:
            self.quit_command()
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator\nCreated by Team 05\n2019"),
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            # Same functionality as load button
            self.on_load_file_button(None)
        if Id == wx.ID_SAVE:
            self.save_file()
        if Id == wx.ID_UNDO:
            error_code, error_message = self.command_manager.undo_command()
            if error_code != self.command_manager.NO_ERROR:
                self.raise_error(error_code, error_message)
            else:
                self.log_text(_("Undo"))
        if Id == wx.ID_REDO:
            error_code, error_message = self.command_manager.redo_command()
            if error_code != self.command_manager.NO_ERROR:
                self.raise_error(error_code, error_message)
            else:
                self.log_text(_("Redo"))
        if Id == wx.ID_MAXIMIZE_FRAME:
            self.Maximize(True)
        if Id == wx.ID_FULLSCREEN:
            self.Show()
            self.ShowFullScreen(True)
        if Id == wx.ID_ZOOM_100:
            self.canvas.set_zoom(1)
        if Id == wx.ID_ZOOM_FIT:
            pass
        if Id == wx.ID_ZOOM_IN:
            self.canvas.zoom_in()
        if Id == wx.ID_ZOOM_OUT:
            self.canvas.zoom_out()
        if Id == wx.ID_EXECUTE:
            # Same functionality as load button
            self.on_run_button(None)
        if Id == wx.ID_CONTINUE:
            # Same functionality as continue button
            self.on_continue_button(None)
        if Id == wx.ID_HELP:
            self.display_help()
        if Id == wx.ID_HELP_COMMANDS:
            self.help_command()
            
    def doConfig(self):
        """Setup an application configuration file"""
        # configuration folder
        sp = wx.StandardPaths.Get()
        self.configLoc = sp.GetUserConfigDir()
        self.configLoc = os.path.join(self.configLoc, self.appName)
        # win: C:\Users\userid\AppData\Roaming\appName
        # nix: \home\userid\appName

        if not os.path.exists(self.configLoc):
            os.mkdir(self.configLoc)

        # AppConfig stuff is here
        self.appConfig = wx.FileConfig(appName=self.appName,
                                       vendorName=u'who you wish',
                                       localFilename=os.path.join(
                                       self.configLoc, "AppConfig"))
    
        if not self.appConfig.HasEntry(u'Language'):
            # on first run we default to German
            self.appConfig.Write(key=u'Language', value=u'de')
            
        self.appConfig.Flush()
        
    def updateLanguage(self, lang):
        """
        Update the language to the requested one.
        
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.
        
        :param string `lang`: one of the supported language codes
        
        """
        # if an unsupported language is requested default to English
        if lang in appC.supLang:
            selLang = appC.supLang[lang]
        else:
            selLang = wx.LANGUAGE_ENGLISH
            
            
        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale
        
        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
        else:
            self.locale = None
            
    
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

    def on_two_dim_button(self, event):
        """Handle the event when the user click the 2D/3D button"""
        if self.two_dim_button.GetLabelText() == _("2D"):
            self.two_dim_button.SetLabel(_("3D"))
            self.canvas_sizer.Show(self.canvas_2D, recursive=True)
            self.canvas_sizer.Hide(self.canvas_3D, recursive=True)
            self.canvas = self.canvas_2D
        else:
            self.two_dim_button.SetLabel(_("2D"))
            self.canvas_sizer.Hide(self.canvas_2D, recursive=True)
            self.canvas_sizer.Show(self.canvas_3D, recursive=True)
            self.canvas = self.canvas_3D
        self.zoom_slider.SetMin(self.canvas.zoom_min * self.zoom_resolution)
        self.zoom_slider.SetMax(self.canvas.zoom_max * self.zoom_resolution)
        self.canvas.completed_cycles = self.completed_cycles
        self.canvas.init = False
        self.canvas_sizer.Layout()
        self.canvas.render()

    def on_console(self, event):
        """Handle the event when the user enters a command in the console."""
        commands = self.console.GetValue().strip().split('\n')
        for command_arg in commands:
            command, *args = command_arg.split()
            # try:
            #     command, *args = command_arg.split()
            # except ValueError:  # Command is
            #     break
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
                self.raise_error(self.command_manager.INVALID_COMMAND,
                                 _("Command ") + command_arg +
                                 _(" is invalid. Enter 'h' for help."))
                break

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
        self.zap_command(signal_name)

    def on_load_file_button(self, event):
        """Handle the load file button"""
        if not self.is_saved:
            answer = self.ask_to_save(_("Load file"))
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:
                self.save_file()
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, _("Open another definition file"),
                           wildcard="Definiton file (*.def)|*.def|"
                                    "Network file (*.defb)|*.defb|"
                                    "Text file (*.txt)|*.txt|All files (*)|*",
                           style=wx.FD_OPEN |
                                 wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            path = fileDialog.GetPath()
            self.open_file(path)

    def on_load_file_text_box(self, event):
        """Handle the event when user enters filepath into load_text_box"""
        if not self.is_saved:
            answer = self.ask_to_save(_("Load file"))
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:
                self.save_file()

        # otherwise ask the user what new file to open
        path = self.load_file_text_box.GetValue()
        self.open_file(path)

    def on_scrollbar_ver(self, event):
        """Handle the event when users scroll the vertical scrollbar"""
        scroll_ver = self.canvas_scrollbar_ver.GetThumbPosition()
        self.canvas.set_pan_y(scroll_ver)
        pass

    def on_scrollbar_hor(self, event):
        """Handle the event when users scroll the horizontal scrollbar"""
        scroll_hor = self.canvas_scrollbar_hor.GetThumbPosition()
        self.canvas.set_pan_x(scroll_hor)

    def on_zoom_minus_button(self, event):
        """Handle the event when users press the zoom minus button"""
        self.canvas.zoom_out()

    def on_zoom_plus_button(self, event):
        """Handle the event when users press the zoom plus button"""
        self.canvas.zoom_in()

    def on_zoom_scroll(self, event):
        """Handle the event when users scroll the zoom slider"""
        zoom_value = self.zoom_slider.GetValue() / self.zoom_resolution
        self.canvas.set_zoom(zoom_value)

    def on_pan_left_button(self, event):
        """Handle the event when users press the pan left button"""
        self.canvas.reset_pan()
        self.canvas.set_pan_x(0)

    def on_pan_reset_button(self, event):
        """Handle the event when users press the pan Reset button"""
        self.canvas.reset_pan()

    def on_pan_right_button(self, event):
        """Handle the event when users press the pan Right button"""
        self.canvas.pan_to_right_end()

    def open_file(self, pathname):
        """Create a new network for another definition file"""
        try:
            with open(pathname, 'r') as _:
                self.command_manager.execute_command(LoadCommand(pathname))
                self.path_name = pathname
        except IOError:
            self.raise_error(self.command_manager.CANNOT_OPEN_FILE,
                             "Cannot open file " + pathname)

    def ask_to_save(self, action_title):
        """Handle the quit or load actions if the state is not save"""
        save_dlg = wx.MessageBox(
            _("Current state of the simulation has not been saved! ")
            + _("Save changes?"),
            action_title,
            wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT, self)
        return save_dlg

    def save_file(self):
        """Handle file dialog for choosing the saving file destination"""
        with wx.FileDialog(self, _("Choose where to save the file"),
                           wildcard="Network files (*.defb)|*.defb",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                error_code, error_message = \
                    self.command_manager.execute_command(
                        SaveCommand(pathname))
                if error_code == self.command_manager.NO_ERROR:
                    self.is_saved = True
                else:
                    self.raise_error(error_code, error_message)
            except IOError:
                wx.LogError(
                    _("Cannot save current data in file ") + pathname)
                return
        return

    def log_text(self, text):
        """Handle the logging in activity_log of an event"""
        text = "".join([datetime.datetime.now().strftime("%H:%M:%S: "), text])
        self.activity_log_text.AppendText(text + '\n')
        self.is_saved = False

    def display_help(self):
        with open(_("logsim_help.txt"), 'r') as help_fp:
            wx.MessageBox(help_fp.read(), _("Help"), wx.ICON_INFORMATION | wx.OK)

    def help_command(self):
        """Print a list of valid commands."""
        text = _("User commands:\n") + \
               _("r N         - run the simulation for N cycles\n") + \
               _("c N         - continue the simulation for N cycles\n") + \
               _("s X N     - set switch X to N (0 or 1)\n") + \
               _("m X       - set a monitor on signal X\n") + \
               _("z X         - zap the monitor on signal X\n") + \
               _("h             - help (this command)\n") + \
               _("q            - quit the program")
        wx.MessageBox(text, _("Help on Commands"), wx.ICON_INFORMATION | wx.OK)

    def switches_update_toggle(self):
        """Handle a change in switches."""

        # If the text in the switches box matches the name of a switch,
        # then the set and clear buttons enable according to the current
        # value of the switch.
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

    def update_toolbar(self):
        """Handle an undo/redo action in toolbar display"""
        # Enable or disable UNDO arrow
        if len(self.command_manager.undo_stack) == 0:
            self.toolbar.EnableTool(wx.ID_UNDO, False)
        else:
            self.toolbar.EnableTool(wx.ID_UNDO, True)

        # Enable or disable REDO arrow
        if len(self.command_manager.redo_stack) == 0:
            self.toolbar.EnableTool(wx.ID_REDO, False)
        else:
            self.toolbar.EnableTool(wx.ID_REDO, True)

    def update_scrollbars(self):
        """Handle a change in pan or zoom"""

        # Update horizontal scrollbar
        range_x = self.canvas.width
        thumb_x = self.canvas.display_width
        position_x = self.canvas.pan_x
        self.canvas_scrollbar_hor.SetScrollbar(
            -position_x, thumb_x, range_x, thumb_x, True)

        # Update vertical scrollbar
        position_y = self.canvas.pan_y - self.canvas.display_height + 18
        range_y = self.canvas.height - 50
        thumb_y = self.canvas.display_height
        self.canvas_scrollbar_ver.SetScrollbar(
            position_y, thumb_y, range_y, thumb_y, True)

    def update_cycles(self, cycles):
        """Update the number of completed cycles"""
        self.completed_cycles = cycles
        self.canvas.completed_cycles = cycles

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
            answer = self.ask_to_save(_("Quit"))
            if answer == wx.CANCEL:
                return
            elif answer == wx.YES:
                self.save_file()
        self.Close(True)

    def raise_error(self, error,
                    message="Unknown error. Send an email to group 05 for support"):
        """Handle user's errors in GUI"""
        if error == self.command_manager.INVALID_COMMAND:
            wx.MessageBox(message, _("Invalid Command Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.INVALID_ARGUMENT:
            wx.MessageBox(message, _("Invalid Argument Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.monitors.MONITOR_PRESENT:
            wx.MessageBox(message, _("Monitor Present Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.SIGNAL_NOT_MONITORED:
            wx.MessageBox(message, _("Signal Not Monitored Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.monitors.NOT_OUTPUT:
            wx.MessageBox(message, _("Monitor On Input Signal Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.network.DEVICE_ABSENT:
            wx.MessageBox(message, _("Device Absent Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.devices.INVALID_QUALIFIER:
            wx.MessageBox(message, _("Invalid Argument Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.OSCILLATING_NETWORK:
            wx.MessageBox(message, _("Oscillating Network Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.CANNOT_OPEN_FILE:
            wx.MessageBox(message, _("Cannot Open File Error"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.NOTHING_TO_UNDO:
            wx.MessageBox(
                "No command left to undo. This is the initial state of the "
                + _("simulation."),
                + _("Nothing To Undo"),
                wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.NOTHING_TO_REDO:
            wx.MessageBox(
                _("No command left to redo. This is the last state of the ")
                +_("simulation."),
                _("Nothing To Redo"),
                wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.SIMULATION_NOT_STARTED:
            wx.MessageBox(_("Nothing to continue. Run first."),
                          _("Simulation Not Started"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.NO_FILE:
            wx.MessageBox(_("No network avilable. Load a valid definition file."),
                          _("No network available"),
                          wx.ICON_ERROR | wx.OK)
        elif error == self.command_manager.INVALID_DEFINITION_FILE:
            wx.MessageBox(
                message + _("\nPlease check the activity log or the terminal."),
                _("Invalid definition file"),
                wx.ICON_ERROR | wx.OK)
        else:
            wx.MessageBox(message, _("Unknown Error"), wx.ICON_ERROR | wx.OK)

    def on_key(self, event):
        """Handle generic key press. Used for exiting the fullscreen mode by
        pressing ESCAPE."""
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.ShowFullScreen(False)
        else:
            event.Skip()
