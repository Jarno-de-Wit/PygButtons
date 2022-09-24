import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame

import math

pygame.font.init() #Required to set a font



class Buttons():
    """
    A class to serve as a base for all Button classes. Also provides interfaces for button-to-button "communication" (e.g. claiming a cursor lock)
    Furthermore, provides certain functionalities that make it easier to implement buttons into a program. (E.G. a way to Click all relevant buttons)

    Capitalisation:
    All actions that can be applied to a button (e.g. LMB_down) are capitalised.
    All attributes and functions that do not directly alter anything about the button itself (e.g. scaling a variable to the Buttons' scale) are not capitalised.

    Available Actions - for more detailed information, see help(Buttons.*function_name*):
    Buttons.Event(pygame.Event, group) - Allows for a pygame.event to be processed completely autonomously, and be diverted to the correct buttons. No further intervention is required if this function is used.
    Buttons.Update(group) - Updates all Buttons in the given group wherever necessary, such as updating the current cursor position for active sliders. Should be called once at the end of each input / event cycle.
    Buttons.Draw(screen, group) - Draw all Buttons in the given group(s) to the given screen / pygame.Surface
    Buttons.Scale(scale, group) - Scales all Buttons in the given group to / by the given factor.
    Buttons.Move(offset, group) - Moves all Buttons in the given group by the given offset.
    Buttons.Clear(group) - Clears all user inputs from Buttons. Note: Does NOT remove the text from Text objects.

    Other Actions (automatically called by Buttons.Event() / Buttons.Update() when required):
    Buttons.LMB_down(pos, group) - Perform a LMB_down (normal mouse click) at a certain position.
    Buttons.LMB_up(pos, group) - Perform a LMB_up (releasing a normal mouse click) at a certain position.
    Buttons.Scroll(value, pos, group) - Perform a Scrolling action at a certain position.
    Buttons.Key_down(event, group) - Perform a Key_down (typing) action.
    Buttons.Set_cursor_pos(pos, group) - Update the cursor position.

    Available functions:
    Buttons.get_group(group) - Will return a list of all Buttons that are in the given group(s). Also used internally when getting all buttons for which an Action should be applied.

    Class attributes:
    Buttons.input_claim - Contains whether or not the last input was fully claimed by a Button. E.G. If a DropdownBox was extended by clicking on  the Arrow button.
    Buttons.input_processed - Contains whether or not the last input was handled by a Button, even if they did not fully claim it. E.G. when exiting a TextBox by clicking outside of the TextBox area.


    Individual Button functions:
    *.get_rect() - Get a pygame.Rect object for the Button.
    *.get_scaled_rect() - Get a pygame.Rect object for the Button at its current scale.
    *.Add_to_group(group) - Add the Button on which this is called to the given group(s).
    """
    #A base class for all buttons
    input_lock = None #Either None, or the currently selected button. Used to give the currently selected button input priority.
    input_claim = False #Set to True if a button has claimed the input, to prevent an input from affecting multiple buttons.
    input_processed = False
    list_all = [] #A list containing all buttons, except those marked as independent. Can be used for debugging, or just to keep a nice list of all buttons.
    groups = {} #Groups to be used for getting certain buttons.
    scroll_factor = 1 #A factor to multiply scrolling with. Should be set based on the target DPI / resolution of the program
    #A framerate variable to help with timing animations
    framerate = 30
    min_scale = 0.05
    max_scale = 5

    def __init__(self, pos, size, font_name = pygame.font.get_default_font(), font_size = 22, groups = None, root = None, independent = False):
        #Tasks that are the same for all sub-classes
        self.updated = True
        self.children = []
        self.scale = 1

        #Tasks that require information from the child class
        self.size = size
        self.topleft = pos
        #Font size has to be set before font name, as setting font name prompts the font object to be built
        self.font_size = font_size
        self.font_name = font_name
        self.Add_to_group(groups)
        self.root = self if root is None else root
        if not independent:
            self.Buttons.list_all.append(self)
        self.independent = independent


    def __str__(self):
        return f"{type(self).__name__} object"
    def __repr__(self):
        return f"<{self.__str__()} at {self.topleft}>"



    @classmethod
    def get_group(cls, group):
        """
        Returns all buttons inside the given group / groups.
        """
        #If a list of groups is given, return the buttons in all the groups combined.
        if type(group) in (tuple, list):
            lst = []
            for grp in group:
                if grp in cls.groups:
                    for button in cls.groups[grp]:
                        #Append all buttons in the group to the original group, if it is not a duplicate
                        if button not in lst:
                            lst.append(button)
                #Else, if the group is already a Button, append that Button to the list instead
                elif isinstance(grp, Buttons):
                    lst.append(grp)
            return lst
        #Select the correct button group
        elif group is all: #If the group is the default 'all', return all buttons
            return cls.list_all
        elif group in cls.groups:
            return cls.groups[group] #Return all buttons in the group.
        elif isinstance(group, Buttons):
            return [group]
        else: #If the group doesn't exist, return an empty list
            return []

    def Add_to_group(self, groups):
        """
        Add a button to a group.
        Allows for assignment of multiple groups simultaniously by passing in a list or tuple of groups.
        """
        if not isinstance(groups, (list, tuple)):
            groups = [groups]
        for grp in groups:
            if grp is None:
                continue
            if grp in self.Buttons.groups:
                #If the group exists, add self to the group, unless self is already in this group.
                if not self in self.Buttons.groups[grp]:
                    self.Buttons.groups[grp].append(self)
            #If the group doesn't exist, make a new group with self as the first list entry.
            else:
                self.Buttons.groups[grp] = [self]

    def Set_lock(self, claim = True):
        """
        Set the input lock (if possible).
        If claim = True, automatically set Buttons.input_claim as well.
        """
        self.Buttons.input_processed = True
        if not self.Buttons.input_lock and not self.independent:
            self.Buttons.input_lock = self
        if claim:
            self.Buttons.input_claim = True

    def Release_lock(self, claim = True):
        """
        Release the input lock (if necessary / possible).
        If claim = True, automatically set Buttons.input_claim as well.
        """
        self.Buttons.input_processed = False
        if self is self.Buttons.input_lock and not self.independent:
            self.Buttons.input_lock = None
        if claim:
            self.Buttons.input_claim = True

    @classmethod
    def Claim_input(cls):
        cls.Buttons.input_claim = True
        cls.Buttons.input_processed = True


    @classmethod
    def Event(cls, event, group = all):
        """
        A method to handle all events a button might need to be informed of.
        """
        #Reset the input_claim and input_processed attributes
        cls.input_claim = False
        cls.input_processed = False

        #Handle the Event appropriately
        if type(event) != pygame.event.EventType:
            raise TypeError(f"Event should be type 'Event', not type {type(event).__name__}")
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cls.LMB_down(event.pos, group)
            elif event.button == 2:
                cls.RMB_down(event.pos, group)
            elif event.button > 3:
                cls.Scroll(cls.convert_scroll(event.button), event.pos, group)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                cls.LMB_up(event.pos, group)
            elif event.button == 2:
                cls.RMB_up(event.pos, group)
        elif event.type == pygame.KEYDOWN:
            cls.Key_down(event, group)


    @classmethod
    def Update(cls, group = all):
        """
        A method that will run any updates that have to be performed each cycle, such as updating the cursor position for sliders.
        """
        if cls.input_lock:
            if "Set_cursor_pos" in cls.input_lock.actions:
                cls.Set_cursor_pos(pygame.mouse.get_pos(), group)


    @classmethod
    def LMB_down(cls, pos, group = all):
        """
        Left Mouse Button down; A.K.A. a normal click.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group)

        #If a button has claimed an input lock
        if cls.input_lock in group_list:
            if "LMB_down" in cls.input_lock.actions:
                cls.input_lock.LMB_down(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "LMB_down" in button.actions and button is not cls.input_lock:
                button.LMB_down(pos)
                if cls.input_claim:
                    return
        return


    @classmethod
    def LMB_up(cls, pos, group = all):
        """
        Left Mouse Button up; A.K.A. releasing a click.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group)

        #If a button has claimed an input lock
        if cls.input_lock in group_list:
            if "LMB_up" in cls.input_lock.actions:
                cls.input_lock.LMB_up(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "LMB_up" in button.actions and button is not cls.input_lock:
                button.LMB_up(pos)
                if cls.input_claim:
                    return
        return


    @classmethod
    def Scroll(cls, value, pos, group):
        """
        Handles all scroll events for all buttons.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group)

        if cls.input_lock in group_list:
            if "Scroll" in cls.input_lock.actions:
                cls.input_lock.Scroll(value, pos)
                if cls.input_claim:
                    return

        for button in group_list:
            #If the button hasn't been processed yet in the input_lock section, and has the "Scroll" attribute:
            if "Scroll" in button.actions and button is not cls.input_lock:
                button.Scroll(value, pos)
                if cls.input_claim:
                    return
        return


    @classmethod
    def Key_down(cls, event, group = all):
        """
        Processes any KEYDOWN events for buttons which require these.
        """
        cls.input_processed = False
        group_list = cls.get_group(group)
        #If any button in the current scope requires keyboard inputs / has focus:
        if cls.input_lock in group_list:
            if "Key_down" in cls.input_lock.actions:
                cls.input_lock.Key_down(event)
        return


    @classmethod
    def Set_cursor_pos(cls, pos, group = all):
        """
        Updates the cursor position. Required for e.g. sliders.
        """
        group_list = cls.get_group(group)
        if not cls.input_lock:
            for button in group_list:
                if "Set_cursor_pos" in button.actions:
                    button.Set_cursor_pos(pos)
        elif cls.input_lock in group_list:
            if "Set_cursor_pos" in cls.input_lock.actions:
                cls.input_lock.Set_cursor_pos(pos)


    @classmethod
    def convert_scroll(cls, value):
        """
        Converts a mouse button value into a scroll value.
        Scrolling down gives negative scroll values.
        """
        if value < 4:
            return 0
        elif value % 2:
            return round((value - 2) / 2) * cls.scroll_factor
        else:
            return round(-(value - 3) / 2) * cls.scroll_factor


    @classmethod
    def Scale(cls, scale, group = all, relative_scale = True, *, center = (0, 0), px_center = None):
        """
        Scales all buttons in the given group by / to a certain scaling factor.

        relative_scale: bool - Determines whether the given scale value is absolute (Button.scale = val), or is a scaling factor relative to their current scale.
        center: tuple - The absolute coordinates around which the scaling should take place.
        px_center: Tuple - The display coordinates around which the scaling should take place. If these are passed in, the 'center' coordinates are ignored.
        """
        if not isinstance(scale, (float, int)):
            raise TypeError(f"scale must be type 'int' or 'float', not type '{type(scale).__name__}'")
        elif scale == 0:
            raise ValueError(f"Cannot scale buttons to scale '0'")

        if px_center:
            px_center = cls.Verify_iterable(px_center, 2)
        else:
            center = cls.Verify_iterable(center, 2)

        for button in cls.get_group(group):
            if not relative_scale:
                scale_factor = cls.Clamp(scale, button.min_scale, button.max_scale) / button.scale
            else:
                scale_factor = cls.Clamp(scale, button.min_scale / button.scale, button.max_scale / button.scale)
            if px_center: #Transform the pixel coordinates to raw coordinates
                center = tuple(i / button.scale for i in px_center)

            #Apply the translation to make sure the given coordinates stay at the same place
            button._move(tuple(i * (1 / scale_factor - 1) for i in center))

            button.scale *= scale_factor

    @classmethod
    def Move(cls, offset, group = all, scale = False):
        """
        Moves all buttons in the given group by a certain offset.

        offset: int / float / tuple - An number, or iterable containing two numbers, for how much the Buttons in the group should be moved. If a number is given, this movement is applied in both directions.
        group: * - The group to which the translation should be applied.
        scale: bool - Determines whether the given values should be scaled to the Buttons' scale before they are applied.
        """
        if hasattr(offset, "__iter__"):
            cls.Verify_iterable(offset, 2, (int, float))
        else:
            offset = (offset, offset)
        #Set the "button_offset" variable to prevent scaling to affect other buttons too.
        b_offset = offset

        for button in cls.get_group(group):
            if scale:
                b_offset = button.scaled(offset, False)
            button._move(b_offset)


    @classmethod
    def Clear(cls, group = all):
        """
        Clears all user inputs from the buttons in the given group.

        group: * - The group of Buttons which should be cleared.
        """
        for button in cls.get_group(group):
            button.Clear()

    @classmethod
    def Draw(cls, screen, group = all):
        """
        Draw all buttons in the specified group to the screen / Surface provided.
        """
        #Select the correct button group
        group_list = cls.get_group(group)
        #Click all buttons without the "Cursor Lock".
        for button in reversed(group_list):
            if button is not cls.input_lock:
                button.Draw(screen)
        #Draw the button with the "Input Lock" last, to make it always appear on top.
        if cls.input_lock:
            if cls.input_lock in group_list:
                cls.input_lock.Draw(screen)


    @classmethod
    def Align(cls, rect, limit_size, pos):
        """
        Creates an aligned Rect, with the given size when placed onto a surface with size 'limit_size'.
        Functionally just a wrapper around AlignX and AlignY.

        rect: A pygame.Rect object or size tuple to be aligned.
        limit_size: A pygame.Rect object or size tuple to which the rect should be aligned.
        pos: The (text) containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
        """
        if isinstance(limit_size, pygame.Rect):
            #If the provided 'limit_size' is a Rect, extract its size
            limit_size = limit_size.size
        pos = pos.lower()

        rect = cls.AlignX(rect, limit_size[0], pos)
        rect = cls.AlignY(rect, limit_size[1], pos)

        return rect

    @staticmethod
    def AlignX(rect, max, pos):
        """
        Creates a rectangle that is correctly aligned horizontally.

        rect: A pygame.Rect object or size tuple to be aligned.
        limit_size: A pygame.Rect object or size tuple to which the rect should be aligned.
        pos: The (text) containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
        """
        if isinstance(rect, pygame.Rect):
            #Make sure the provided Rect is aligned correctly at the start
            rect.left = 0
        elif isinstance(rect, int):
            #If only an int (width) is given, create a zero height corresponding pygame.Rect
            rect = pygame.Rect((0, 0), (rect, 0))
        else:
            #If the provided 'rect' argument is not a rect, but just a tuple containing a size, create a new Rect
            rect = pygame.Rect((0, 0), rect)
        if isinstance(max, pygame.Rect):
            max = max.width
        pos = pos.lower()

        if "left" in pos:
            pass
        elif "right" in pos:
            rect.right = max
        else:
            rect.centerx = math.floor(max / 2)
        return rect

    @staticmethod
    def AlignY(rect, max, pos):
        """
        Creates a rectangle that is correctly aligned vertically.

        rect: A pygame.Rect object or size tuple to be aligned.
        limit_size: A pygame.Rect object or size tuple to which the rect should be aligned.
        pos: The (text) containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
        """
        if isinstance(rect, pygame.Rect):
            #Make sure the provided Rect is aligned correctly at the start
            rect.top = 0
        elif isinstance(rect, int):
            #If only an int (height) is given, create a zero width corresponding pygame.Rect
            rect = pygame.Rect((0, 0), (0, rect))
        else:
            #If the provided 'rect' argument is not a rect, but just a tuple containing a size, create a new Rect
            rect = pygame.Rect((0, 0), rect)
        if isinstance(max, pygame.Rect):
            max = max.height
        pos = pos.lower()

        if "top" in pos:
            pass
        elif "bottom" in pos:
            rect.right = max
        else:
            rect.centery = math.floor(max / 2)

        return rect


    def contains(self, position):
        """
        Tests whether a position is within the current (main) button.
        """
        #Test whether the pos input is valid
        position = self.Verify_iterable(position, 2)
        #If the position is within the corners. Note: Top and left have <=, whereas botom and right have < checks.
        #This is because the bottom / right values are actually just outside of the boxs' actual position
        if self.scaled(self.left) <= position[0] < self.scaled(self.right) and self.scaled(self.top) <= position[1] < self.scaled(self.bottom):
            return True
        else:
            return False

    @staticmethod
    def is_within(position, topleft, bottomright):
        """
        Tests whether a position is within two other corners. Basically a more generalised version of *.contains.
        """
        if topleft[0] <= position[0] < bottomright[0] and topleft[1] <= position[1] < bottomright[1]:
            return True
        else:
            return False


    @classmethod
    def Clamp(cls, value, minimum, maximum):
        """
        Returns a value which is as close to value as possible, but is minimum <= value <= maximum.
        """
        if maximum < minimum:
            raise ValueError(f"Maximum must be >= Minimum {maximum} and {minimum}")
        if hasattr(value, "__iter__"):
            return tuple(cls.Clamp(i, minimum, maximum) for i in value)
        return max(minimum, min(value, maximum))


    def Make_background_surface(self, inp, custom_size = None, scale_custom = False):
        """
        Makes a solid fill background if a colour was provided. If a surface was provided, returns that instead.
        If custom_size is set, will use that size instead of self.true_size.
        If scale_custom is True, and a custom size is given, that custom size will be scaled first.
        """
        if not custom_size:
            size = self.true_size
        elif scale_custom:
            size = self.scaled(custom_size)
        else:
            size = custom_size
        width, height = size
        #Set the background surface for the button. If one is provided, use
        # that one. Otherwise, make a new one with a solid color as given.
        if type(inp) == pygame.Surface:
            return pygame.transform.scale(inp, size)
        elif inp is None:
            return pygame.Surface(size, pygame.SRCALPHA)
        elif hasattr(inp, "__call__"):
            return inp()
        elif hasattr(inp[0], "__call__"): #If it is a tuple/list iterable with a function as its first item
            return inp[0](*(arg if arg != "*self*" else self for arg in inp[1:]))
        else:
            if type(self.style) is int:
                corner_radius = max(0, self.scaled(self.style))
            elif self.style.lower() == "square":
                corner_radius = 0
            elif self.style.lower() == "round":
                corner_radius = min(size)
            elif self.style.lower() == "smooth":
                corner_radius = self.scaled(12)
            else:
                raise ValueError(f"Invalid style value {self.style}")

            surface = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(surface, inp, ((0, 0), size), border_radius = corner_radius)
            return surface


    def Draw_border(self, surface, colour, border_width = 1, border_offset = 0, custom_size = None):
        """
        Draws a border around a surface.
        """
        border_offset = self.scaled(border_offset)
        border_width = self.scaled(border_width)

        if not border_width: #If after scaling, the border width is 0, don't try to draw anything, as doing so would colour the entire button.
            return

        style = self.style
        if custom_size:
            size = custom_size
        else:
            size = self.true_size
        if type(style) is int:
            corner_radius = max(0, self.scaled(style) - border_offset)
        elif style.lower() == "square":
            corner_radius = 0
        elif style.lower() == "round":
            corner_radius = min(size)
        elif style.lower() == "smooth":
            corner_radius = max(0, self.scaled(12) - border_offset)

        pygame.draw.rect(surface, colour, (2*(border_offset,), self.offset(size, 2*(border_offset,), (-2, -2))), border_width, corner_radius)


    @staticmethod
    def Verify_iterable(value, length = 2, data_types = None):
        """
        A function that verifies whether a given iterable has the required length, and whether all items in the iterable are of the correct types.
        """
        if not hasattr(value, "__iter__"):
            raise ValueError("Given value is not iterable")
        value_iterator = value.__iter__()
        #Get the first {length} items from the iterator.
        try:
            output = tuple(next(value_iterator) for _ in range(length))
        #If the iterator doesn't contain enough items, raise a ValueError
        except RuntimeError:
            raise ValueError("Given iterable contains too few items")
        if isinstance(data_types, (type, type(None))):
            data_types = [data_types]
        #If data_types == None,    or    all ites are of an allowed data_type: everything is fine; Else, raise an error.
        if not (data_types[0] is None    or    all(type(item) in data_types for item in output)):
            raise TypeError(f"Incorrect data type for items in iterable")
        #Test if the iterator did not contain more items:
        try:
            next(value_iterator)
        #If a StopIteration error is raised, this means the iterator contained
        #only two items, and thus was the correct size. In that case, return it.
        except StopIteration:
            return output
        else: #Otherwise, the iterator was too long. Raise an error.
            raise ValueError("Given iterable contains too many items")


    @classmethod
    def Verify_colour(cls, value):
        """
        Verifies whether a colour is in the correct format, and within the right range of values.
        """
        value = cls.Verify_iterable(value, 3, int)
        if all(0 <= i <= 255 for i in value):
            return value
        else:
            raise ValueError("All RGB values must be integers between 0 and 255")


    @classmethod
    def Verify_border(cls, border):
        """
        Verifies whether a border is in the correct format, and contains valid values.
        """
        if border:
            cls.Verify_iterable(border, 3)
            border_colour = cls.Verify_colour(border[0])
            if not all(isinstance(i, (int, float)) for i in border[1:]):
                raise TypeError("Border width and Border offset must be type 'int' or 'float'")
            return border_colour, border[1], border[2]
        else:
            return None


    @classmethod
    def Verify_background(cls, background):
        """
        Verifies whether a background is of a correct format / contains valid values.
        """
        if isinstance(background, pygame.Surface): #Pre-existing surface
            return background
        elif not background: #Empty background
            return None
        elif hasattr(background, "__call__"): #If it is itself a function
            return background
        elif isinstance(background, (list, tuple)) and background and hasattr(background[0], "__call__"): #If it is a tuple / list with a function as its first item.
            return background
        else:
            cls.Verify_colour(background)
            return background


    def Verify_functions(cls, functions):
        if not isinstance(functions, dict):
            raise TypeError(f"'functions' must be type 'dict', not type '{type(functions).__name__}'")
        if not all(isinstance(key, str) for key in functions):
            raise TypeError(f"All keys in 'functions' must be type 'str'")
        functions = {key.title(): value for key, value in functions.items()}
        return functions


    def Force_update(self):
        """
        A function that forces a button to get updated. Can be used when an attribute is changed which does not directly cause it to update.
        """
        #Set the updated parameter
        self.updated = True
        #Draw the button to make sure the button surface is updated too.
        self.Draw(pygame.Surface((1,1)))


    @staticmethod
    def offset(pos, offset_vector, scalar_vector = (1, 1)):
        """
        Returns a position with a certain offset.
        Also allows the offset to be multiplied by a scalar vector.
        """
        return tuple(pos[i] + offset_vector[i] * scalar_vector[i] for i in range(len(pos)))


    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, value):
        self.__scale = value
        self.updated = True
        for child in self.children:
            child.scale = value


    def _move(self, value):
        self.left += value[0]
        self.top += value[1]


    @property
    def font(self):
        #If the size of the font has changed, rebuild the font.
        if round(self.scale * self.font_size) != self.__font.get_height():
            self.__Make_font()
        #Return the font object.
        return self.__font


    @property
    def font_name(self):
        return self.__font_name

    @font_name.setter
    def font_name(self, value):
        self.__font_name = value
        self.__Make_font()
        for child in self.children:
            child.font_name = value


    @property
    def font_size(self):
        return self.__font_size

    @font_size.setter
    def font_size(self, value):
        self.__font_size = value
        self.updated = True
        for child in self.children:
            child.font_size = value


    def __Make_font(self):
        """
        Re-builds a font object based on self.font_name and self.font_size, as well as the current self.scale.
        """
        #pygame.font.Font is used in favor of pygame.font.SysFont, as SysFont's font sizes are inconsistent with the value given for the font.
        try:
            self.__font = pygame.font.Font(self.font_name, round(self.scale * self.font_size))
        except FileNotFoundError:
            font = pygame.font.match_font(self.font_name)
            if font is None: #If no matching font was found
                raise FileNotFoundError(f"No such font: '{self.font_name}'")
            self.__font = pygame.font.Font(font, round(self.scale * self.font_size))


    def _Call(self, action):
        """
        Calls a function, if it exists, for the action specified
        """
        if not action in self.functions: #If no function was specified for this action, ignore the fact that this function was called anyway
            return
        if isinstance(self.functions[action], (tuple, list)):
            self.functions[action][0](*(arg if arg != "*self*" else self for arg in self.functions[action][1:]))
        else:
            self.functions[action]()
        return


    @property
    def functions(self):
        return self.__functions
    @functions.setter
    def functions(self, value):
        self.__functions = self.Verify_functions(value)


    @property
    def text_colour(self):
        return self.__text_colour

    @text_colour.setter
    def text_colour(self, value):
        self.__text_colour = self.Verify_colour(value)
        self.updated = True
        for child in self.children:
            child.text_colour = value


    #Properties for all main positions of the button, much like a pygame.rect
    #Positions are not scaled by default. Run button.scaled() on the values to scale them if necessary
    @property
    def center(self):
        return (self.centerx, self.centery)
    @property
    def midbottom(self):
        return (self.centerx, self.bottom)
    @property
    def midtop(self):
        return (self.centerx, self.top)
    @property
    def midleft(self):
        return (self.left, self.centery)
    @property
    def midright(self):
        return (self.right, self.centery)
    @property
    def bottomleft(self):
        return (self.left, self.bottom)
    @property
    def bottomright(self):
        return (self.right, self.bottom)
    @property
    def topleft(self):
        return (self.left, self.top)
    @property
    def topright(self):
        return (self.right, self.top)
    @property
    def size(self):
        return (self.width, self.height)
    @property
    def bottom(self):
        return self.top + self.height
    @property
    def top(self):
        return self.__top
    @property
    def left(self):
        return self.__left
    @property
    def right(self):
        return self.left + self.width
    @property
    def height(self):
        return self.__height
    @property
    def width(self):
        return self.__width
    @property
    def centerx(self):
        return self.left + self.width / 2
    @property
    def centery(self):
        return self.top + self.height / 2

    @property
    def middle(self):
        """
        The middle of the button, pre-scaled.
        """
        return tuple(round(i / 2) for i in self.true_size)


    #Setter for all main positions of the button, much like a pygame.rect
    @center.setter
    def center(self, value):
        value = self.Verify_iterable(value, 2)
        self.centerx, self.centery = value
    @midbottom.setter
    def midbottom(self, value):
        value = self.Verify_iterable(value, 2)
        self.centerx, self.bottom = value
    @midtop.setter
    def midtop(self, value):
        value = self.Verify_iterable(value, 2)
        self.centerx, self.top = value
    @midleft.setter
    def midleft(self, value):
        value = self.Verify_iterable(value, 2)
        self.left, self.centery = value
    @midright.setter
    def midright(self, value):
        value = self.Verify_iterable(value, 2)
        self.right, self.centery = value
    @bottomleft.setter
    def bottomleft(self, value):
        value = self.Verify_iterable(value, 2)
        self.left, self.bottom = value
    @bottomright.setter
    def bottomright(self, value):
        value = self.Verify_iterable(value, 2)
        self.right, self.bottom = value
    @topleft.setter
    def topleft(self, value):
        value = self.Verify_iterable(value, 2)
        self.left, self.top = value
    @topright.setter
    def topright(self, value):
        value = self.Verify_iterable(value, 2)
        self.right, self.top = value
    @size.setter
    def size(self, value):
        value = self.Verify_iterable(value, 2)
        self.width, self.height = value
    @bottom.setter
    def bottom(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'bottom' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.top = value - self.height
    @top.setter
    def top(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'top' must by type 'int' or 'float', not type '{type(value).__name__}'")
        try:
            for child in self.children:
                child._move((0, value - self.top)) #Move children along with the main Button
        except AttributeError: pass #Catch error raised when .top is first set in __init__
        self.__top = value
        self.updated = True #Update button since moving might cause true_size to change
    @left.setter
    def left(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'left' must by type 'int' or 'float', not type '{type(value).__name__}'")
        try:
            for child in self.children:
                child._move((value - self.left, 0)) #Move children along with the main Button
        except AttributeError: pass #Catch error raised when .left is first set in __init__
        self.__left = value
        self.updated = True#Update button since moving might cause true_size to change
    @right.setter
    def right(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'right' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.left = value - self.width
    @centerx.setter
    def centerx(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'centerx' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.left = value - self.width / 2
    @centery.setter
    def centery(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'centery' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.top = value - self.height / 2
    @width.setter
    def width(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'width' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__width = value
        self.updated = True
    @height.setter
    def height(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"'height' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__height = value
        self.updated = True

    #"True" size properties are used to prevent artifacting issues during scaling.
    # Although often the same as self.scaled(self.size), sometimes these will differ by a pixel due to rounding.
    @property
    def true_width(self):
        return self.scaled(self.right) - self.scaled(self.left)
    @property
    def true_height(self):
        return self.scaled(self.bottom) - self.scaled(self.top)
    @property
    def true_size(self):
        return (self.true_width, self.true_height)


    def get_rect(self):
        """
        Returns a pygame.Rect object of the unscaled button rectangle.
        """
        return pygame.Rect(self.topleft, self.size)

    def get_scaled_rect(self):
        """
        Returns a pygame.Rect object of the scaled button rectangle.
        """
        return pygame.Rect(self.scaled(self.topleft), self.true_size)



    def scaled(self, value, rounding = True):
        """
        Returns the scaled version of a value, or tuple of values.
        """
        if isinstance(value, (list, tuple)):
            return tuple(self.scaled(i, rounding) for i in value) #Recursion is amazing!
        elif isinstance(value, (float, int)):
            if rounding:
                return round(value * self.scale)
            else:
                return value * self.scale
        else:
            raise TypeError(f"Cannot scale type '{type(value).__name__}'.")

    def relative(self, pos):
        return self.offset(pos, self.scaled(self.topleft, False), (-1, -1))


#Add an attribute to this class that references itself, so other subclasses can easily acces the parent class object
#This is useful for allowing communications between subclasses
Buttons.Buttons = Buttons
