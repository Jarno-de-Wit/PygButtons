from .Base import Buttons
from .Button import Button

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame


class Slider(Buttons):
    """
    Creates a Slider, which allows the user to input a value within a given range.

    pos: (left, top) - The topleft position before scaling.
    size: (width, height) - The size before scaling.
    value_range: (a, b) - The range between which values the slider should (linearly) interpolate.
    orientation: "auto", int - The orientation of the Slider. In case orientation == "auto", the longest direction will be seen as the primary direction. If orientation == 0, the Slider will be horizontal; if orientation == 1, the Slider will be vertical.
    style: "Square", "Round", int - Defines the radius of curvature of the buttons' corners.
    background: pygame.Surface, (R, G, B), None, function - The background of the button if it is not selected.
    border: ((R, G, B), width, offset), None - The border that appears around the Sliders' background.
    markings: int - The amount of markings to be drawn to the background. Set to 0 to disable all markings.
    edge_markings: bool - Whether or not markings should be present at the edges too, or should be spaced equally over the entire text_box. Can not be enabled when markings < 2.
    marking_colour: (R, G, B) - The colour the markings will have when drawn onto the Slider background.
    snap_radius: int, float - The radius (in pixels) in which the slider should snap towards any markings.
    slider_background: pygame.Surface, (R, G, B), None, function - The background of the slider if it is not selected.
    slider_border: ((R, G, B), width, offset), None - The border that appears around the slider.
    accent background: pygame.Surface, (R, G, B), None, function - The background of the slider if it is_selected. If set to None, will be the same as normal background.
    slider_feature_font: str - The name of the font that should be used for the slider feature.
    slider_feature_size: int - The size (in px) of the sliders' feature text.
    slider_feature_colour: (R, G, B) - The colour of the feature / text on the slider.
    slider_feature_align: The alignment of the feature text on the slider Button.
    slider_feature_text: str - The feature / text that will be rendered to the slider.
    slider_size: "auto", int, (width, height) - The size of the slider. If set to "auto", will automatically fit the slider to the direction orthogonal to the orientation.
    functions: dict - Contains functions that should be called when a specific event occurs. The values should either be {"Click": func,} to call a function without arguments, or {"Click": (func, arg1, arg2, ...)} to call a function with arguments. If the Button itself is to be passed in as an argument, that argument can be passed in as '*self*'. This argument will automatically replaced when the function is actually called.
                    - "Click": Called when the Slider is clicked.
                    - "Release": Called when the Slider is released.
                    - "Move": Called when the Slider is moved to a new location. Only called by user input.
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
    root: None, Button - The Button that is considered the 'root element' for this Button. Any function calls that need to include a 'self' Button, will include this root Button instead.
    independent: bool - Determines whether or not the button is allowed to set the input_lock, and is added to buttons.list_all. Mostly important for buttons which are part of another button.

    Inputs:
    *.value: int, float - The current value of the Slider.
    *.Set_range: (a, b) - Sets the range between which values the slider should (linearly) interpolate. See help(*.Set_range) for more information.
    *.Set_slider_primary(*) - Sets the primary size of the slider. Mainly useful when the slider is used as a scrollbar. See help(*.Set_slider_primary) for more information.

    Outputs:
    *.value: float - The current value of the slider.
    *.moved: bool - Whether the slider has been moved since the last time this property has been checked. Automatically resets once it is querried.

    *.is_selected: bool - Whether this Slider object is selected at this point in time. I.E. Whether the user is currently moving the Slider.
    """
    actions = ["LMB_down", "LMB_up", "Set_cursor_pos"]
    def __init__(self, pos, size,
                 value_range = (0, 1),
                 start_value = 0,
                 orientation = "auto", #0 for horizontal, 1 for vertical
                 style = "Square",
                 #Background settings
                 background = (255, 255, 255), #Colour or pygame.Surface
                 border = ((63, 63, 63), 1, 0),
                 #Marking settings:
                 markings = 0, #The amount of markings that should be made. 0 to disable all markings.
                 edge_markings = False,
                 marking_colour = (127, 127, 127),
                 snap_radius = 0, #The distance for which the slider should snap to markings (in pixels).
                 #Settings for the slider button. Provide Button object for custom sliders.
                 slider_background = (220, 220, 220),
                 slider_border = ((63, 63, 63), 1, 0),
                 slider_accent_background = (191, 191, 191),
                 slider_feature_font = pygame.font.get_default_font(),
                 slider_feature_size = 22,
                 slider_feature_colour = (63, 63, 63),
                 slider_feature_align = "center",
                 slider_feature_text = "",
                 slider_size = "Auto",
                 #Other (miscelaneous) settings
                 functions = {},
                 group = None,
                 root = None,
                 independent = False,
                 ):
        """
        Create a Slider Button object. See help(type(self)) for more detailed information.
        """
        #Note: 'Slider' (captialised) in commments etc. refers to the main object (self)
        #      'slider' (non-capitalised) refers to the button that moves along the Slider (self.slider)
        super().__init__(pos, size, groups = group, root = root, independent = independent) #We don't care about the font, as this Button will not contain any text
        #Initialise the basic parameters of the Slider
        self.__value_range = self.Verify_iterable(value_range, 2) #Directly written to the private property, to prevent a chicken - egg problem with self.value
        if type(orientation) is int:
            self.orientation = orientation
        elif orientation.lower() == "auto":
            self.orientation = int(self.width < self.height)
        self.style = style
        #Set the background parameters for the Slider
        self.bg = self.Buttons.Verify_background(background)
        self.border = self.Verify_border(border)

        #Initialise any markers - Has to be done before making the slider object
        if markings == 1 and edge_markings:
            raise ValueError("Edge markings require at least 2 markings to be present")
        self.markings = markings
        self.edge_markings = edge_markings
        self.marking_colour = marking_colour

        #Create the sliding object (from now on referred to as "slider" (lower case))
        self.tmp_slider_size = slider_size
        self.slider = Make_slider(self, style, slider_size, slider_background, slider_accent_background, slider_border, markings, edge_markings, snap_radius, slider_feature_text, slider_feature_colour, slider_feature_align, slider_feature_font, slider_feature_size, self.orientation)
        self._value = self.start_value = start_value
        del self.tmp_slider_size
        self.children.append(self.slider)

        #Other
        self.is_selected = False
        self.moved = True #Indicates whether there is a chance the slider has moved. If so, the user can take action (if necessary).
        self.functions = functions
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are set-up correctly


    def LMB_down(self, pos):
        if self.slider.contains(pos):
            self.is_selected = True
            self.slider.LMB_down(pos)
            self.Set_lock()
            self.moved = True
            self._moved = True #Instruct the button that value is no longer equal to the value stored in __value
        elif self.contains(pos):
            self.is_selected = True
            #Move the slider to where we clicked (within limits of course)
            self.slider.LMB_down(self.slider.scaled(self.slider.center))
            self.Set_cursor_pos(pos)
            self.Set_lock()
        return

    def LMB_up(self, pos):
        if self.is_selected:
            self.slider.LMB_up(pos)
            self.is_selected = False
            self.moved = True #To make sure the button get's re-drawn correctly with the right background
            self._moved = True
        return

    def Set_cursor_pos(self, pos):
        if self.is_selected:
            slider_pos = self.slider.topleft
            self.slider.Set_cursor_pos(pos)
            if self.slider.topleft != slider_pos:
                self.moved = True
                self._moved = True


    def Scale(self, scale, relative_scale = True, *, center = (0, 0), px_center = None):
        super().Scale(scale, self, relative_scale, center = center, px_center = px_center)


    def Move(self, offset, scale = False):
        super().Move(offset, self, scale)


    def Clear(self):
        #Reset the slider position to its inital value
        self._value = self.start_value
        self.is_selected = False
        #Lock is automatically released in property setter


    def Draw(self, screen, pos = None):
        """
        Draw the button to the screen.
        """
        #Set draw positions for when a custom location is given
        if pos is not None:
            slider_pos = self.offset(self.slider.scaled(self.slider.topleft), self.offset(pos, self.scaled(self.topleft), (-1, -1)))
        else:
            pos = self.scaled(self.topleft)
            slider_pos = None

        #Update the button surface (if necessary)
        if self.updated:
            #Now, let's actually construct the surface
            self.surface = self.Make_background_surface(self.bg)
            if self.border:
                self.Draw_border(self.surface, *self.border)

            if self.markings:
                #Set up the information of the marking itself
                marking_height = self.rotated(self.true_size)[1] - 2*(self.scaled(self.border[1]) + self.scaled(self.border[2]) if self.border else 0)
                marking_width = self.scaled(1)
                marking_rect = pygame.Rect((0,0), self.rotated((marking_width, marking_height)))

                #Iterate over all markings, and draw them
                for coord in self.Marking_coords():
                    coord = self.scaled(coord)
                    marking_rect.center = self.rotated(coord, self.rotated(self.true_size)[1] / 2)
                    pygame.draw.rect(self.surface, self.marking_colour, marking_rect)

            self.updated = False

        screen.blit(self.surface, pos)
        self.slider.Draw(screen, slider_pos)
        return




    def rotated(self, value, other = None):
        """
        Returns a rotated version of a 2-item list / tuple, such that the primary dimension is always first in the tuple.
        In case the orientation is horizontal, it stays the same.
        In case the orientation is vertical, it becomes reversed.
        """
        if other is not None:
            value = (value, other)
        if self.orientation % 2:
            return tuple(reversed(value))
        else:
            return value

    def Marking_coords(self):
        try:
            slider_size = self.slider.size
        except AttributeError: #During setup, the coords are required to construct the slider object. Therefore, when slider does not exist, instead take the size from the temporary value.
            if type(self.tmp_slider_size) is int:
                slider_size = 2 * (self.tmp_slider_size,)
            elif type(self.tmp_slider_size) is not str:
                slider_size = self.tmp_slider_size
            elif self.tmp_slider_size.lower() == "auto":
                slider_size = 2 * (min(self.size),)
        coord_range = self.rotated(self.size)[0] - self.rotated(slider_size)[0] #The available pixels for the slider to move in
        offset = self.rotated(slider_size)[0] / 2 #The offset due to the slider having to fit within the sliders' width (to some degree)
        for i in range(self.markings):
            if self.edge_markings:
                yield(coord_range / (self.markings - 1) * i + offset)
            else:
                yield(coord_range / (self.markings + 1) * (i + 1) + offset)

    def Set_range(self, range, *args):
        """
        Set a new range for the slider. Can be done as either:
        set_range([min, max]) or
        set_range(min, max)
        """
        if args: #If the user passed the values in as two separate values, combine them into one tuple
            range = (range, args[0])
        self._value #Flush any _moved arguments, in case they haven't been processed yet.
        self.value_range = tuple(range) #Update the slider range
        self.value = self.Clamp(self._value, *sorted(self.value_range)) #Reset the value, to update the sliders' position

    def Set_slider_primary(self, value, limit_size = True):
        """
        Set the sliders' primary dimension / size (in the direction of travel).
        Set_slider_primary(value).
        If limit_size == True, the primary dimension cannot go below 1/2 the secondary dimension. This is to prevent the slider from disappearing completely if the primary is set too low.
        """
        if limit_size:
            #Make sure the slider primary can not accidentally be set too low.
            value = max(value, round(self.rotated(self.slider.size)[1] / 2))
        self._value #Flush any _moved arguments, in case they haven't been processed yet.
        if self.orientation % 2: #Update the sliders' size
            if self.slider.height != value:
                self.slider.height = value
        else:
            if self.slider.width != value:
                self.slider.width = value
        self._value = self._value #Reset the value to update the sliders' position
        #Update the sliders' snap points
        self.slider.snap = self.rotated(tuple(self.rotated(self.topleft)[0] - value / 2 + coord for coord in self.Marking_coords()), ()) + (self.slider.snap[2],)
        self.updated = True


    @property
    def is_selected(self):
        return self.__is_selected

    @is_selected.setter
    def is_selected(self, value):
        if value: #If the user selects the text box:
            self.__is_selected = True
            self.Set_lock()
        else: #If the user deselects the box:
            self.__is_selected = False
            self.Release_lock()

    @property
    def _value(self):
        #Note: No need to run ._Call() anywhere in this code. The fact that the .__value is only updated here isn't important. It was already called when the slider was actually moved.
        if self._moved: #If the user clicked on the slider, the value should be re-calculated from the slider position. If not, the value should be exactly what the user set.
            pos = round(self.rotated(self.offset(self.slider.topleft, self.topleft, (-1, -1)))[0])
            coord_range = self.rotated(self.size)[0] - self.rotated(self.slider.size)[0] #The available pixels for the slider to move in
            if coord_range == 0: #If the slider is the same size as the overall button, pre-emptively catch it to prevent a ZeroDivisionError
                self.__value = sum(self.value_range) / 2
            else:
                self.__value = self.Clamp(self.value_range[0] + pos / coord_range * (self.value_range[1] - self.value_range[0]), *sorted(self.value_range))
            self._moved = False
        return self.__value

    @_value.setter
    def _value(self, val):
        val = self.Clamp(val, *sorted(self.value_range))
        if self.value_range[0] == self.value_range[1]:
            self.slider.center = self.center
        else:
            coord_range = self.rotated(self.size)[0] - self.rotated(self.slider.size)[0] #The available pixels for the slider to move in
            self.slider.topleft = self.rotated(self.rotated(self.topleft)[0] + (val - self.value_range[0]) / (self.value_range[1] - self.value_range[0]) * coord_range, self.rotated(self.center)[1] - self.rotated(self.slider.size)[1] / 2)
        self.__value = val
        self._moved = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.root._Call("Move")

    @property
    def value_range(self):
        return self.__value_range

    @value_range.setter
    def value_range(self, value):
        self.__value_range = self.Verify_iterable(value, 2)
        self._value += 0

    @property
    def moved(self):
        moved = self.__moved
        self.__moved = False
        return moved

    @moved.setter
    def moved(self, value):
        self.__moved = value


def Make_slider(self, style, size, background, accent_background, border, markings, edge_markings, snap_radius, feature_text, feature_colour, feature_align, feature_font, feature_size, orientation):
    """
    Make a slider Button.
    For internal use only. This function is therefore also not imported by __init__.py
    """
    if type(size) is int:
        size = 2 * (size,)
    elif type(size) is not str:
        pass
    elif size.lower() == "auto":
        #Primary direction: min(self.size)
        #Secondary direction: the Sliders' height in the secondary direction
        size = self.rotated((min(self.size), self.rotated(self.size)[1]))

    if self.orientation % 2:
        limits = (self.left - size[0], self.right + size[0], self.top, self.bottom)
    else:
        limits = (self.left, self.right, self.top - size[1], self.bottom + size[1])
    #pos is irrelevant, as it is set by the value setter anyway
    return Button((0, 0), size, mode = "Hold", style = style,
                background = background,
                text = feature_text,
                text_colour = feature_colour,
                text_align = feature_align,
                font_name = feature_font,
                font_size = feature_size,
                orientation = orientation,
                accent_background = accent_background,
                border = border,
                dragable = self.rotated((True, False)),
                limits = limits,
                snap = self.rotated(tuple(self.rotated(self.topleft)[0] - (self.rotated(size)[0] / 2) + coord for coord in self.Marking_coords()), ()) + (snap_radius,),
                root = self.root,
                independent = True,
                )
