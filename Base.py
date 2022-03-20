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

    def __init__(self, pos, size, font_name = pygame.font.get_default_font(), font_size = 20, groups = None, independent = False):
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
        if not independent:
            self.Buttons.list_all.append(self)
        self.independent = independent


    def __str__(self):
        return f"{type(self).__name__} object"
    def __repr__(self):
        return f"{self.__str__()} at {self.topleft}"



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
            return lst
        #Select the correct button group
        elif group is all: #If the group is the default 'all', return all buttons
            return cls.list_all
        elif group in cls.groups:
            return cls.groups[group] #Return all buttons in the group.
        else: #If the group doesn't exist, return an empty list
            return []

    def Add_to_group(self, groups):
        """
        Add a button to a group.
        Allows for assignment of multiple groups simultaniously by passing in a list or tuple of groups.
        """
        if type(groups) not in (list, tuple):
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
    def Scale(cls, scale, group = all, relative_scale = True):
        """
        Scales all buttons in the given group by / to a certain scaling factor.
        """
        for button in cls.get_group(group):
            if relative_scale:
                button.scale *= scale
            else:
                button.scale = scale


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


    def Make_background_surface(self, inp, custom_size = None):
        """
        Makes a solid fill background if a colour was provided. If a surface was provided, returns that instead.
        If custom_size is set, will use that size instead of self.size. (scaling will still be applied to custom_size).
        """
        if not custom_size:
            size = self.size
            width, height = self.size
        else:
            size = custom_size
            width, height = custom_size
        #Set the background surface for the button. If one is provided, use
        #that one. Otherwise, make a new one with a solid color as given.
        if type(inp) == pygame.Surface:
            return pygame.transform.scale(inp, self.scaled(size))
            #return(inp)
        elif inp is None:
            return pygame.Surface(self.scaled(size), pygame.SRCALPHA)
            #return(pygame.Surface((1,1), pygame.SRCALPHA))
        elif hasattr(inp, "__call__"):
            return inp(self)
        else:
            if type(self.style) is int:
                corner_radius = max(0, self.scaled(self.style))
            elif self.style.lower() == "square":
                corner_radius = 0
            elif self.style.lower() == "round":
                corner_radius = self.scaled(min(width, height) / 2)
            elif self.style.lower() == "smooth":
                corner_radius = 12
            else:
                raise ValueError(f"Invalid style value {self.style}")

            surface = pygame.Surface(self.scaled(size), pygame.SRCALPHA)
            pygame.draw.rect(surface, inp, ((0, 0), self.scaled(size)), border_radius = corner_radius)
            return surface


    def Draw_border(self, surface, colour, border_width = 1, border_offset = 0):
        """
        Draws a border around a surface.
        """
        style = self.style
        if type(style) is int:
            corner_radius = max(0, self.scaled(style - border_offset))
        elif style.lower() == "square":
            corner_radius = 0
        elif style.lower() == "round":
            corner_radius = self.scaled(min(self.width, self.height) / 2)
        elif style.lower() == "smooth":
            corner_radius = 10

        border_width = self.scaled(border_width)
        if not border_width: #If after scaling, the border width is 0, don't try to draw it, as doing so would colour the entire button.
            return
        border_offset = self.scaled(border_offset)
        corner_radius = self.scaled(corner_radius)

        pygame.draw.rect(surface, colour, (self.scaled((border_offset, border_offset)), self.scaled(self.offset(self.size, (border_offset, border_offset), (-2, -2)))), border_width, corner_radius)


    @staticmethod
    def Verify_iterable(value, length = 2, data_types = None):
        """
        A function that verifies whether a given iterable has the required length, and whether all items in the iterable are of the correct types.
        """
        if not(hasattr(value, "__iter__")):
            raise ValueError("Given value is not iterable")
        value_iterator = value.__iter__()
        #Get the first {length} items from the iterator.
        try:
            output = tuple(next(value_iterator) for _ in range(length))
        #If the iterator doesn't contain enough items, raise a ValueError
        except RuntimeError:
            raise ValueError("Given iterable contains too few items")
        if type(data_types) in (type, type(None)):
            data_types = [data_types]
        #If data_types == None,    or    all ites are of an allowed data_type: everything is fine; Else, raise an error.
        if not (data_types[0] == None    or    all(type(item) in data_types for item in output)):
            raise TypeError(f"Incorrect data type for items in iterable")
        #Test if the iterator did not contain more items:
        try:
            next(value_iterator)
        #If a StopIteration error is raised, this means the iterator contained
        #only two items, and thus was the correct size. In that case, return it.
        except StopIteration:
            return output
        else: #Otherwise, the iterator was too long. Raise an error.
            raise ValueError("Given value contains too many items")


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
            if not all(type(i) in [int, float] for i in border[1:]):
                raise TypeError("Border width and Border offset must be type 'int' or 'float'")
            return border_colour, border[1], border[2]
        else:
            return None


    @classmethod
    def Verify_background(cls, background):
        """
        Verifies whether a background is of a correct format / contains valid values.
        """
        if type(background) is pygame.Surface: #Pre-existing surface
            return background
        elif not background: #Empty background
            return(None)
        elif hasattr(background, "__call__"): #Allows the user to pass in a custom function to draw the background / Surface
            return background
        else:
            cls.Verify_colour(background)
            return background


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
        self.__font = pygame.font.Font(self.font_name, round(self.scale * self.font_size))


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
        return self.scaled(tuple(i / 2 for i in self.size))


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
        if not type(value) in (int, float):
            raise TypeError(f"'bottom' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__top = value - self.height
    @top.setter
    def top(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'top' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__top = value
    @left.setter
    def left(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'left' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__left = value
    @right.setter
    def right(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'right' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__left = value - self.width
    @centerx.setter
    def centerx(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'centerx' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__left = value - self.width / 2
    @centery.setter
    def centery(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'centery' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__top = value - self.height / 2
    @width.setter
    def width(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'width' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__width = value
        self.updated = True
    @height.setter
    def height(self, value):
        if not type(value) in (int, float):
            raise TypeError(f"'height' must by type 'int' or 'float', not type '{type(value).__name__}'")
        self.__height = value
        self.updated = True


    def get_rect(self):
        """
        Returns a pygame.Rect object of the unscaled button rectangle.
        """
        return pygame.Rect(self.topleft, self.size)

    def get_scaled_rect(self):
        """
        Returns a pygame.Rect object of the scaled button rectangle.
        """
        return pygame.Rect(self.scaled(self.topleft), self.scaled(self.size))



    def scaled(self, value, rounding = True):
        """
        Returns the scaled version of a value, or tuple of values.
        """
        if type(value) in (list, tuple):
            return(tuple(self.scaled(i, rounding) for i in value)) #Recursion is amazing!
        elif type(value) in (float, int):
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