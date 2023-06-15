import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame

import math
import sys

pygame.font.init() #Required to set a font



class Buttons():
    """
    A class to serve as a "Command and Control" centre / API for all Buttons

    Capitalisation:
    All actions that can be applied to a button (e.g. LMB_down) are capitalised.
    All attributes and functions that do not directly alter anything about the button itself (e.g. getting all Buttons which are part of a certain group are not capitalised.

    Available Actions - for more detailed information, see help(Buttons.*function_name*):
    Buttons.Event(pygame.Event, group) - Allows for a pygame.event to be processed completely autonomously, and be diverted to the correct buttons. No further intervention is required if this function is used.
    Buttons.Draw(screen, group) - Draw all Buttons in the given group(s) to the given screen / pygame.Surface
    Buttons.Scale(scale, group) - Scales all Buttons in the given group to / by the given factor.
    Buttons.Move(offset, group) - Moves all Buttons in the given group by the given offset.
    Buttons.Clear(group) - Clears all user inputs from Buttons. Note: Does NOT remove the text from Text objects.

    Buttons.Callbacks(enabled [bool]) - Enables or disables function callbacks. Can be used in conjunction with "with" statements.
    Buttons.Update_flags(enabled [bool]) - Enables or disables the update flags for buttons. Can be used in conjuction with "with" statements.

    Other Actions (automatically called by Buttons.Event() when required):
    Buttons.LMB_down(pos, group) - Perform a LMB_down (normal mouse click) at a certain position.
    Buttons.LMB_up(pos, group) - Perform a LMB_up (releasing a normal mouse click) at a certain position.
    Buttons.Scroll(value, pos, group) - Perform a Scrolling action at a certain position.
    Buttons.Key_down(event, group) - Perform a Key_down (typing) action.
    Buttons.Mouse_motion(event or pos, group) - Update the cursor position.

    Available functions:
    Buttons.get_group(group) - Will return a list of all Buttons that are in the given group(s). Also used internally when getting all buttons for which an Action should be applied.

    Class attributes:
    Buttons.input_claim - Contains whether or not the last input / event was fully claimed by a Button. E.G. If a DropdownBox was extended by clicking on the Arrow button.
    Buttons.input_processed - Contains whether or not the last input was used by a Button, even if they did not fully claim it. E.G. when exiting a TextBox by clicking outside of the TextBox area.
    """
    #A base class for all buttons
    _input_lock = None #Either None, or the currently selected button. Used to give the currently selected button input priority.
    input_claim = False #Set to True if a button has claimed the input, to prevent an input from affecting multiple buttons.
    input_processed = False

    list_all = [] #A list containing all buttons, except those marked as independent. Can be used for debugging, or just to keep a nice list of all buttons.
    groups = {} #Groups to be used for getting certain buttons.
    scroll_factor = 1 #A factor to multiply scrolling with. Should be set based on the target DPI / resolution of the program
    #A framerate variable to help with timing animations
    framerate = 30
    min_scale = 0.05
    max_scale = 5


    @classmethod
    def get_group(cls, group, reverse = False):
        """
        Returns all buttons inside the given group / groups.
        """
        #If a list of groups is given, return the buttons in all the groups combined.
        if isinstance(group, (tuple, list)):
            lst = []
            for grp in group:
                if grp in cls.groups:
                    for button in cls.groups[grp]:
                        #Append all buttons in the group to the original group, if it is not a duplicate
                        if button not in lst:
                            lst.append(button)
                #Else, if the group is already a Button, append that Button to the list instead
                elif isinstance(grp, ButtonBase):
                    lst.append(grp)
            if reverse:
                return list(reversed(lst))
            else:
                return lst
        #Select the correct button group
        elif group is all: #If the group is the default 'all', return all buttons
            if reverse:
                return list(reversed(cls.list_all))
            else:
                return cls.list_all
        elif group in cls.groups:
            if reverse:
                return list(reversed(cls.groups[group]))
            else:
                return cls.groups[group] #Return all buttons in the group.
        elif isinstance(group, ButtonBase):
            return [group]
        else: #If the group doesn't exist, return an empty list
            return []

    @classmethod
    def Add_to_group(cls, buttons, groups):
        """
        Add an (array of) button(s) to a group.
        Allows for assignment of multiple groups simultaniously by passing in a list or tuple of groups.
        """
        if not isinstance(button, (list, tuple)):
            buttons = [buttons]
        for button in buttons:
            button.Add_to_group(groups)

    @classmethod
    def Event(cls, event, group = all, reverse = False):
        """
        A method to handle all events a button might need to be informed of.
        """
        #Reset the input_claim and input_processed attributes
        cls.input_claim = False
        cls.input_processed = False

        #Handle the Event appropriately
        if not isinstance(event, pygame.event.EventType):
            raise TypeError(f"Event should be type 'Event', not type {type(event).__name__}")
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cls.LMB_down(event.pos, group, reverse)
            elif event.button == 2:
                cls.MMB_down(event.pos, group, reverse)
            elif event.button == 3:
                cls.RMB_down(event.pos, group, reverse)
            elif event.button > 3:
                cls.Scroll(cls.convert_scroll(event.button), event.pos, group, reverse)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                cls.LMB_up(event.pos, group, reverse)
            elif event.button == 2:
                cls.MMB_up(event.pos, group, reverse)
            elif event.button == 3:
                cls.RMB_up(event.pos, group, reverse)
        elif event.type == pygame.KEYDOWN:
            cls.Key_down(event, group, reverse)
        elif event.type == pygame.MOUSEMOTION:
            cls.Mouse_motion(event, group, reverse)


    @classmethod
    def Update(cls, group = all):
        """
        A method that will run any updates that have to be performed each cycle, such as updating the cursor position for sliders.
        """
        if not hasattr(cls, "depr_update"):
            cls.depr_update = True
            print(f"Update will be deprecated in the next version. All functionality has been taken over by the MOUSEMOTION event. It is safe to remove Update() as long as the MOUSEMOTION event is not filtered.", file = sys.stderr)
        if cls._input_lock:
            if "Set_cursor_pos" in cls._input_lock.actions:
                cls.Set_cursor_pos(pygame.mouse.get_pos(), group)


    @classmethod
    def LMB_down(cls, pos, group = all, reverse = False):
        """
        Left Mouse Button down; A.K.A. a normal click.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "LMB_down" in cls._input_lock.actions:
                cls._input_lock.LMB_down(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "LMB_down" in button.actions and button is not cls._input_lock:
                button.LMB_down(pos)
                if cls.input_claim:
                    return


    @classmethod
    def LMB_up(cls, pos, group = all, reverse = False):
        """
        Left Mouse Button up; A.K.A. releasing a click.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "LMB_up" in cls._input_lock.actions:
                cls._input_lock.LMB_up(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "LMB_up" in button.actions and button is not cls._input_lock:
                button.LMB_up(pos)
                if cls.input_claim:
                    return


    @classmethod
    def RMB_down(cls, pos, group = all, reverse = False):
        """
        Right Mouse Button down.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "RMB_down" in cls._input_lock.actions:
                cls._input_lock.RMB_down(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "RMB_down" in button.actions and button is not cls._input_lock:
                button.RMB_down(pos)
                if cls.input_claim:
                    return


    @classmethod
    def RMB_up(cls, pos, group = all, reverse = False):
        """
        Right Mouse Button up.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "RMB_up" in cls._input_lock.actions:
                cls._input_lock.RMB_up(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "RMB_up" in button.actions and button is not cls._input_lock:
                button.RMB_up(pos)
                if cls.input_claim:
                    return


    @classmethod
    def MMB_down(cls, pos, group = all, reverse = False):
        """
        Middle Mouse Button down.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "MMB_down" in cls._input_lock.actions:
                cls._input_lock.MMB_down(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "MMB_down" in button.actions and button is not cls._input_lock:
                button.MMB_down(pos)
                if cls.input_claim:
                    return


    @classmethod
    def MMB_up(cls, pos, group = all, reverse = False):
        """
        Middle Mouse Button up.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        #If a button has claimed an input lock
        if cls._input_lock in group_list:
            if "MMB_up" in cls._input_lock.actions:
                cls._input_lock.MMB_up(pos)
                if cls.input_claim:
                    return

        for button in group_list:
            if "MMB_up" in button.actions and button is not cls._input_lock:
                button.MMB_up(pos)
                if cls.input_claim:
                    return


    @classmethod
    def Scroll(cls, value, pos, group = all, reverse = False):
        """
        Handles all scroll events for all buttons.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)

        if cls._input_lock in group_list:
            if "Scroll" in cls._input_lock.actions:
                cls._input_lock.Scroll(value, pos)
                if cls.input_claim:
                    return

        for button in group_list:
            #If the button hasn't been processed yet in the input_lock section, and has the "Scroll" attribute:
            if "Scroll" in button.actions and button is not cls._input_lock:
                button.Scroll(value, pos)
                if cls.input_claim:
                    return


    @classmethod
    def Key_down(cls, event, group = all, reverse = False):
        """
        Processes any KEYDOWN events for buttons which require these.
        """
        cls.input_claim = False
        cls.input_processed = False
        group_list = cls.get_group(group, reverse)
        #If any button in the current scope requires keyboard inputs / has focus:
        if cls._input_lock in group_list:
            if "Key_down" in cls._input_lock.actions:
                cls._input_lock.Key_down(event)
                if cls.input_claim:
                    return

        for button in group_list:
            #If the button hasn't been processed yet in the input_lock section, and has the "Key_down" attribute:
            if "Key_down" in button.actions and button is not cls._input_lock:
                button.Key_down(event)
                if cls.input_claim:
                    return

    @classmethod
    def Mouse_motion(cls, event, group = all, reverse = False):
        """
        Updates the cursor position. Required for e.g. sliders.
        Only active for the button which currently holds the _input_lock to prevent excessive function call overhead.
        """
        group_list = cls.get_group(group, reverse)
        if cls._input_lock in group_list:
            if "Mouse_motion" in cls._input_lock.actions:
                cls._input_lock.Mouse_motion(event)


    @classmethod
    def Set_cursor_pos(cls, pos, group = all):
        """
        Updates the cursor position. Required for e.g. sliders.
        """
        if not hasattr(cls, "depr_update"):
            cls.depr_update = True
            print(f"Set_cursor_pos will be deprecated in the next version. All functionality has been taken over by the MOUSEMOTION event. Please replace all direct calls to Buttons.Set_cursor_pos with Buttons.Mouse_motion.", file = sys.stderr)
        group_list = cls.get_group(group)
        if not cls._input_lock:
            for button in group_list:
                if "Set_cursor_pos" in button.actions:
                    button.Set_cursor_pos(pos)
        elif cls._input_lock in group_list:
            if "Set_cursor_pos" in cls._input_lock.actions:
                cls._input_lock.Set_cursor_pos(pos)


    @classmethod
    def convert_scroll(cls, value):
        """
        Converts a mouse button value into a scroll value.
        Scrolling down gives negative scroll values.
        """
        if value < 4:
            return 0
        elif value % 2:
            return round((value - 3) / 2) * cls.scroll_factor
        else:
            return round(-(value - 2) / 2) * cls.scroll_factor


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
    def Draw(cls, screen, group = all, reverse = True):
        """
        Draw all buttons in the specified group to the screen / Surface provided.
        """
        #Select the correct button group
        group_list = cls.get_group(group, reverse)
        #Click all buttons without the "Cursor Lock".
        for button in group_list:
            if button is not cls._input_lock:
                button.Draw(screen)
        #Draw the button with the "Input Lock" last, to make it always appear on top.
        if cls._input_lock:
            if cls._input_lock in group_list:
                cls._input_lock.Draw(screen)


    @classmethod
    def Force_update(cls, group):
        """
        A function that forces a button to get updated. Can be used when an attribute is changed which does not directly cause it to update.
        """
        for button in cls.get_group(group):
            # Querry the button for a re-draw
            button.updated = True
            # Finish the re-draw / update
            button.Draw(pygame.Surface((1, 1)))


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
        #If data_types == None,    or    all items are of an allowed data_type: everything is fine; Else, raise an error.
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


    class Callbacks:
        """
        Whether Buttons should trigger function callbacks on events

        value: Whether function calls should be enabled. Can be any of:
            True / Truthy - All state changes trigger function calls.
            False / Falsy (except None) - No functions are called, regardless of the originator.
            None (Default behavior): Disables enforcement, meaning only event based changes trigger functions.

        enforce: Whether the rule should be enforced for all nested statements. Note: nested statements with enforce = True will still overwrite this.
        """
        suppressor = None #A reference to the currently enforcing flag
        def __init__(self, value, enforce = True, /):
            #Store the initial value and suppressor to set them back upon __exit__ (if called)
            self.__prev_value = ButtonBase._callbacks
            self.__prev_suppressor = Buttons.Callbacks.suppressor
            #Clearing the flag (set to default)
            if value is None:
                Buttons.Callbacks.suppressor = None
                ButtonBase._callbacks = False #False by default, unless set to true by events' with statement
            #Setting the flag as enforcer
            elif enforce:
                ButtonBase._callbacks = value
                Buttons.Callbacks.suppressor = self
            #Setting the flag, without becoming the enforcer
            elif Buttons.Callbacks.suppressor is None:
                ButtonBase._callbacks = value
            #else: Do nothing. This instance is not enforcing, and a pre-existing instance is, so that one takes precedence.
        def __enter__(self):
            #Don't do anything inside __enter__(). All actions are already done in __init__().
            pass
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self is Buttons.Callbacks.suppressor or Buttons.Callbacks.suppressor is None:
                ButtonBase._callbacks = self.__prev_value
                #Remove self as the suppressor, since we exit the scope of this with value
                Buttons.Callbacks.suppressor = self.__prev_suppressor


    class Update_flags:
        """
        Whether Buttons should update the event flags

        value: Whether event flag updates should be enabled. Can be any of:
            True / Truthy - All state changes trigger function calls.
            False / Falsy (except None) - No functions are called, regardless of the originator.
            None (Default behavior): Disables enforcement, meaning only event based changes trigger functions.

        enforce: Whether the rule should be enforced for all nested statements. Note: nested statements with enforce = True will still overwrite this.
        """
        suppressor = None #A reference to the currently enforcing flag
        def __init__(self, value, enforce = True, /):
            self.__prev_value = ButtonBase._update_flags
            self.__prev_suppressor = Buttons.Update_flags.suppressor
            #Clearing the flag (set to default)
            if value is None:
                Buttons.Update_flags.suppressor = None
                ButtonBase._update_flags = False #False by default, unless set to true by events' with statement
            #Setting the flag as enforcer
            elif enforce:
                ButtonBase._update_flags = value
                Buttons.Update_flags.suppressor = self
            #Setting the flag, without becoming the enforcer
            elif Buttons.Update_flags.suppressor is None:
                ButtonBase._update_flags = value
            #else: Do nothing. This instance is not enforcing, and a pre-existing instance is, so that one takes precedence.
        def __enter__(self):
            #Don't do anything inside __enter__(). All actions are already done in __init__().
            pass
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self is Buttons.Update_flags.suppressor or Buttons.Update_flags.suppressor is None:
                ButtonBase._update_flags = self.__prev_value
                #Remove self as the suppressor, since we exit the scope of this with value
                Buttons.Update_flags.suppressor = self.__prev_suppressor

    #Easy access for generally shared properties, while still allowing individual settings by setting the value directly to button.{property_name}
    @property
    def min_scale(self):
        return ButtonBase.min_scale
    @min_scale.setter
    def min_scale(self, value):
        ButtonBase.min_scale = value
    @property
    def max_scale(self):
        return ButtonBase.max_scale
    @min_scale.setter
    def max_scale(self, value):
        ButtonBase.max_scale = value
