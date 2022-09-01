from .Base import Buttons
from .Button  import Button
from .Slider import Slider

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame


class DropdownBox(Buttons):
    """
    Creates a DropdownBox, in which a user can select an input from a list of options.

    pos: (left, top) - The topleft position before scaling.
    size: (width, height) - The size before scaling.
    options: list, tuple - A list containing the values of all options to be added to the DropdownBox.
    hint: str - The text that is displayed in the main box when no option is selected.
    option_align: The alignment of the text on the dropped down 'option' buttons.
    value_align: The alignment of the current value on the main Button.
    hint_align: The alignment of the hint on the main Button.
    display_length: int - 0: unlimited (show all items regardless of how many there are).
                          +: Show up to n items, but if there are less, limit the length to the amount of items.
                          -: Show n items. If there are less items, show an empty area at the bottom of the list.
    button_spacing: int, (x, y) - The spacing between the buttons inside the Dropdown Box.
    style: "Square", "Round", int - Defines the radius of curvature of the buttons' corners.
    font_name: str - The name of the font that should be used for the DropdownBox.
    font_size: int - The size (in px) of the text.
    text_colour: (R, G, B) - The colour of the text in the DropdownBox.
    scroll_bar: None, int, Slider - The type of scrollbar to be included. Default styles 1 and 2 are available.
    background: pygame.Surface, (R, G, B), None, function - The background of the button if it is not selected.
    border: ((R, G, B), width, offset), None - The border that appears around the buttons in the DropdownBox.
    accent_background: pygame.Surface, (R, G, B), None, function - The background of the button if it is_selected. If set to None, will be the same as normal background.
    dropdown_background: pygame.Surface, (R, G, B), None, function - The background that is rendered behind the buttons on the dropdown section of the DropdownBox.
    functions: dict - Contains functions that should be called when a specific event occurs. The values should either be {"Click": func,} to call a function without arguments, or {"Click": (func, arg1, arg2, ...)} to call a function with arguments. If the Button itself is to be passed in as an argument, that argument can be passed in as '*self*'. This argument will automatically replaced when the function is actually called.
                    - "Select": Called whenever the DropdownBox is selected (dropped down).
                    - "Deselect": Called whenever the DropdownBox is deselected.
                    - "Update": Called whenever the state is changed.
                    - "Move": Called whenever the dropdown area is scrolled.
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
    root: None, Button - The Button that is considered the 'root element' for this Button. Any function calls that need to include a 'self' Button, will include this root Button instead.
    independent: bool - Determines whether or not the button is allowed to set the input_lock, and is added to buttons.list_all. Mostly important for buttons which are part of another button.


    Inputs:
    *.state: int - Sets the index of the currently selected option. Set negative to deselect all options
    *.Add_option(*) - Adds an option to the list of possible options. See help(*.Add_option) for more information.
    *.Del_option(*) - Removes an option from the list of possible options. See help(*.Del_option) for more information.

    Outputs:
    *.value: * - The value of the currently selected item. Type can be wathever was given as the value.
    *.state: int - The index of the currently selected option. Is -1 if no option is selected.
    *.new_state: bool - Whether the DropdownBox has been set to a new state since the last time this variable was checked. Automatically resets once it is querried.

    *.is_selected: bool - Whether this DropdownBox object is selected at this point in time. I.E. Whether DropdownBox is expanded.
    """
    actions = ["LMB_down", "LMB_up", "Set_cursor_pos", "Scroll"]
    def __init__(self, pos, size,
                 options = [],
                 hint = "",
                 option_align = "center",
                 value_align = "left",
                 hint_align = "left", #Align left for consistency with text boxes
                 display_length = 0,
                 button_spacing = (0, 0),
                 style = "Square",
                 font_name = pygame.font.get_default_font(),
                 font_size = 22,
                 text_colour = (0, 0, 0),
                 hint_colour = (128, 128, 128),
                 scroll_bar = None,
                 background = (255, 255, 255),
                 border = ((63, 63, 63), 1, 0),
                 accent_background = (220, 220, 220),
                 dropdown_background = None,
                 functions = {},
                 group = None,
                 root = None,
                 independent = False
                 ):
        """
        Create a DropdownBox Button object. See help(type(self)) for more detailed information.
        """
        super().__init__(pos, size, font_name, font_size, group, root, independent)
        self.option_align = option_align
        self.hint = hint
        self.hint_align = hint_align
        self.value_align = value_align
        #Storing information required for later child buttons
        self.bg = self.Verify_background(background)
        self.accent_bg = self.Verify_background(accent_background)
        self.border = border
        self.style = style

        self.options = []
        self.button_list = []
        self.__state = -1
        self.__scrolled = 0
        self.new_state = False
        self.moved = True

        if type(button_spacing) in (int, float):
            self.spacing = (button_spacing, button_spacing)
        elif hasattr(button_spacing, "__iter__"):
            self.spacing = self.Verify_iterable(button_spacing, 2)
        else:
            raise ValueError("Incorrect spacing type")

        self.dropdown_bg = self.Verify_background(dropdown_background)
        self.display_length = display_length
        #Create the arrow button
        self.arrow = Button((self.right - self.height, self.top), (self.height, self.height), border = border, background = (Arrow_bg, "*self*", self.bg, self.accent_bg), accent_background = None, style = style, mode = "Toggle", root = self.root, independent = True)
        self.children.append(self.arrow)

        #Make the button containing the information about the currently selected option.
        self.main_button = Button(self.topleft, (self.width - self.height - self.spacing[0], self.height), font_name = font_name, font_size = font_size, border = border, background = background, accent_background = accent_background, style = style, root = self.root, independent = True)
        self.children.append(self.main_button)

        if scroll_bar:
            self.scroll_bar = Make_scroll_bar(self, scroll_bar)
            self.scroll_bar.Set_slider_primary(self.scroll_bar.height)
            self.children.append(self.scroll_bar)
        else:
            self.scroll_bar = None

        self.text_colour = self.Verify_colour(text_colour)
        self.hint_colour = self.Verify_colour(hint_colour)

        self.functions = functions
        #Add in all the options
        for option in options:
            self.Add_option(option)
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are set-up correctly


    def LMB_down(self, pos):
        #Test if any of the two header boxes was clicked:
        if self.main_button.contains(pos):
            self.Claim_input()
            self.is_selected = not self.is_selected
            self.updated = True
        elif self.arrow.contains(pos):
            self.Claim_input()
            self.is_selected = not self.is_selected
            self.updated = True
        #Test if the scroll_bar (if any) contained the location
        elif self.scroll_bar and self.scroll_bar.contains(pos):
            self.scroll_bar.LMB_down(pos)
            self.Set_lock()
        #Test if the any of the buttons in the dropdown space contain the clicking point
        elif self.is_selected and self.is_within(pos, (self.scaled(self.left), self.scaled(self.bottom) + self.scaled(self.spacing[1])), (self.scaled(self.right), self.scaled(self.bottom) + self.scaled(self.spacing[1]) + self._true_pixel_length)):
            #Claim the input. Even if no button is "hit", it was within the surface of the dropdown box
            self.Claim_input()
            #Calculate the new relative pos, when it is taken relative to the dropdown spaces' coordinates
            for button_nr, button in enumerate(self.button_list):
                if button.contains((pos[0], pos[1] + self.scrolled_px)):
                    self.state = button_nr
                    self.is_selected = False
                    #Stop checking from here, as no buttons overlap, thus no other buttons will .contain(rel_pos)
                    return
        elif self.is_selected:
            self.is_selected = False

    def LMB_up(self, pos):
        if self.scroll_bar:
            self.scroll_bar.LMB_up(pos)

    def Set_cursor_pos(self, pos):
        if self.scroll_bar:
            self.scroll_bar.Set_cursor_pos(pos)


    def Scroll(self, value, pos):
        if self.arrow.value: #If self is selected / the menu is expanded downwards
            if self.contains(pos):
                pass
            elif self.is_within(pos, (self.scaled(self.left), self.scaled(self.bottom) + self.scaled(self.spacing[1])), (self.scaled(self.right), self.scaled(self.bottom) + self.scaled(self.spacing[1]) + self._true_pixel_length)): #If the position lies withing the expanded section, perform scrolling.
                self.scrolled_px += self.Buttons.scroll_factor * value
                self.Claim_input()


    def Scale(self, scale, relative_scale = True, *, center = (0, 0), px_center = None):
        super().Scale(scale, self, relative_scale, center = center, px_center = px_center)


    def Move(self, offset, scale = False):
        super().Move(offset, self, scale)


    def Clear(self):
        self.is_selected = False
        self.state = -1
        #Lock is automatically released in property setter


    def Draw(self, screen, pos = None):
        """
        Draw the button to the screen.
        """
        #Set the correct position for the dropdown_surface
        dropdown_pos = (self.scaled(self.left), self.scaled(self.bottom) + self.scaled(self.spacing[1]))
        if pos is not None:
            offset = self.offset(pos, self.scaled(self.topleft), (-1, -1))
            dropdown_pos = self.offset(dropdown_pos, offset)

        self.scrolled
        #If the box has been updated, re-draw this stuff:
        if self.updated:
            #Set self.moved to True to make sure the dropdown_surface also gets updated to the latest state
            self.moved = True
            #Draw the main / header surface
            #Re-draw self.surface (containing the header and the arrow)
            self.surface = self.Make_background_surface(None)
            self.main_button.Draw(self.surface, (0, 0))
            self.arrow.Draw(self.surface, (self.true_width - self.arrow.true_width, 0))

            #Re-build the button surface
            #Re-draw self.button_surface (the pre-rendered surface containing ALL buttons stacked underneath each other)
            self.button_surface = pygame.Surface((self.true_width - (self.scroll_bar.true_width if self.scroll_bar else 0), self.scaled(self.button_list[-1].bottom) - self.scaled(self.button_list[0].top) if self.button_list else 0), pygame.SRCALPHA)
            for button in self.button_list:
                button.Draw(self.button_surface, (0, button.scaled(button.top) - self.scaled(self.button_list[0].top)))

            self.updated = False

        if self.moved:
            #re-draw self.dropdown_surface (The cut-to-size version of self.button_surface), including the potential scroll_bar
            self.dropdown_surface = self.Make_background_surface(self.dropdown_bg, (self.true_width, self._true_pixel_length))
            self.dropdown_surface.blit(self.button_surface, (0, -self.scrolled_px))
            if self.scroll_bar:
                self.scroll_bar.Draw(self.dropdown_surface, (self.true_width - self.scroll_bar.true_width, 0))

            self.moved = False


        if self.is_selected:
            screen.blit(self.dropdown_surface, dropdown_pos)
        screen.blit(self.surface, pos or self.scaled(self.topleft))
        return


    def Add_option(self, value, sort = False, set_to = False):
        """
        Add an option to the dropdown lists' options.
        sort: bool - Whether the new value should be sorted between old values. If False, the value is simply appended to the end.
        set_to: bool - Whether the new value should be automatically switched to as the currently selected option.
        """
        #Save and clear the state, as it can change by inserting a new button in between
        state = self._state
        self._state = -1
        if sort:
            #The index is the first item, for which value sorts before the item
            index = min([ind for ind, option in enumerate(self.options) if value == sorted([value, option])[0]], default = len(self.options))
        else:
            index = len(self.options)
        self.options.insert(index, value)
        new_button = Button((self.left, self.bottom + self.spacing[1] + index * (self.height + self.spacing[1])),
                            (self.width - (self.scroll_bar.width + self.spacing[0] if self.scroll_bar else 0), self.height),
                            text = str(value),
                            text_align = self.option_align,
                            style = self.style,
                            background = self.bg,
                            accent_background = self.accent_bg,
                            text_colour = self.text_colour,
                            font_name = self.font_name,
                            font_size = self.font_size,
                            border = self.border,
                            root = self.root,
                            independent = True
                            )
        self.button_list.insert(index, new_button)
        self.children.append(new_button)
        new_button.scale = self.scale

        #Move all following buttons down (if necessary) to make space for the new button
        for button in self.button_list[index + 1:]:
            button.top += self.height + self.spacing[1]

        #Set self.state to the correct value again
        if set_to:
            self.state = index #Set the new state, including running ._Call
        elif index <= self._state: #If the new item is before the current one, shift the index by 1 as well, and don't run ._Call
            self._state = state + 1
        else: #Otherwise, set the state back to what it was already
            self._state = state

        #Update the scroll_bar size if present
        if self.scroll_bar:
            self.scroll_bar.height = self._display_pixel_length
            if self.display_length == 0:
                self.scroll_bar.Set_slider_primary(self.scroll_bar.height)
            elif self.display_length > 0:
                self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(len(self.options), self.display_length) / len(self.options)))
            else:
                self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(1, -self.display_length / len(self.options))))
            self.scroll_bar.slider.limits[3] = self.scroll_bar.bottom
        return


    def Del_option(self, option = None, index = None):
        """
        Allows an option to be removed from the dropdown list. The option can be indicated either by the options' value (option = value), or the options' index (index = value).
        If the provided option does not exist, the function will cancel the operation gracefully.

        Returns:
        True if deletion was successful.
        False if deletion was unsuccessful.
        """
        #Determine the index of the item to be removed, or cancel the operation if the given value is invalid
        if isinstance(index, int):
            if index >= len(self.options) or -index > len(self.options): #If the index is invalid (too big positive, or too small negative)
                return False
            index %= len(self.options)
        else:
            #Try to find the index of the specified item
            try:
                index = self.options.index(option)
            except ValueError: #If the option is not inside the list:
                return False

        #Save and clear the state, as it can change by removing a button
        state = self._state
        self._state = -1

        #Remove all references to the button / option from this butttons' lists
        self.children.remove(self.button_list[index])
        self.options.pop(index)
        self.button_list.pop(index)

        #Move the relevant buttons upwards again
        for button in self.button_list[index:]:
            button.top -= self.height + self.spacing[1]

        #Reduce the state by 1, if the selected button came after the current button
        if state > index:
            self._state = state - 1
        elif state < index:
            self._state = state
        else:
            #If state == index, don't change self.state again. In that case, the selected item was the one which was removed, so we shouldn't set a new item.
            #._Call should still be run though as the state did change.
            self.root._Call("Update")

        #Update the scroll_bar size if present
        if self.scroll_bar:
            self.scroll_bar.height = self._display_pixel_length
            if self.display_length == 0:
                self.scroll_bar.Set_slider_primary(self.scroll_bar.height)
            elif self.display_length > 0:
                self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(len(self.options), self.display_length) / max(1, len(self.options))))
            else:
                self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(1, -self.display_length / max(1, len(self.options)))))
            self.scroll_bar.slider.limits[3] = self.scroll_bar.bottom #Update the bottom limit of the scroll_bar slider

        return True


    @property
    def value(self):
        if self._state >= 0:
            return self.options[self._state]
        else:
            return None
    @value.setter
    def value(self, value):
        if value in self.options:
            self.state = self.options.index(value)
        elif value is None:
            self.state = -1
        else:
            raise ValueError("Value not in options list")

    #_state is for internal use only. It allows the Button to update the state, without accidentally triggering the ._Call.
    # In doing so, it allows any user-set values to still run ._Call, and perform all required checks with minimal code duplicates.
    @property
    def _state(self):
        return self.__state
    @_state.setter
    def _state(self, value):
        #Verify that the index is not too big to prevent getting into an unrecoverable state if the state is out of bounds.
        if value >= len(self.options):
            raise IndexError("Index out of range")
        #Clear the currently selected button (if any)
        if self.__state >= 0:
            self.button_list[self.__state].value = False
        #If the new value selects an actual button:
        if value >= 0:
            self.__state = value
            self.button_list[value].value = True
            self.main_button.text = self.button_list[value].text
            self.main_button.text_colour = self.text_colour
            self.main_button.text_align = self.value_align
        else:
            self.__state = -1
            self.main_button.text = self.hint
            self.main_button.text_colour = self.hint_colour
            self.main_button.text_align = self.hint_align
        self.new_state = True
        self.updated = True
        self.moved = True


    @property
    def state(self):
        return self.__state
    @state.setter
    def state(self, value):
        self._state = value
        self.root._Call("Update")

    @property
    def new_state(self):
        new_state = self.__new_state
        self.__new_state = False
        return new_state
    @new_state.setter
    def new_state(self, value):
        self.__new_state = True


    @property
    def scrolled(self):
        if self.scroll_bar and self.scroll_bar.moved:
            self.__scrolled = self.scroll_bar.value
            self.moved = True
        return self.__scrolled

    @scrolled.setter
    def scrolled(self, value):
        #Make sure the scrolled value cannot exceed the limits of the space in the box
        value = self.Clamp(value, 0, 1)
        self.moved = True

        self.__scrolled = value
        if self.scroll_bar:
            self.scroll_bar.value = value

    @property
    def scrolled_px(self):
        #Calculate the required height (in px)
        req_height = 0 if not self.options else self.scaled(self.button_list[-1].bottom) - self.scaled(self.button_list[0].top)
        #Calculate the required height change that has to be accomodated by scrolling (in px)
        max_scroll_height = max(0, req_height - self._true_pixel_length) #Get the total distance (in px) the surface must be scrolled

        return round(max_scroll_height * self.scrolled)

    @scrolled_px.setter
    def scrolled_px(self, value):
        #Calculate the required height (in px)
        req_height = 0 if not self.options else self.scaled(self.button_list[-1].bottom) - self.scaled(self.button_list[0].top)
        #Calculate the required height change that has to be accomodated by scrolling (in px)
        max_scroll_height = max(0, req_height - self._true_pixel_length) #Get the total distance (in px) the surface must be scrolled

        #Only update the scrolled value, if the DD can be scrolled
        if max_scroll_height:
            self.scrolled = value / max_scroll_height


    @property
    def is_selected(self):
        return self.arrow.value

    @is_selected.setter
    def is_selected(self, value):
        if value == self.arrow.value:
            if value:
                self.Set_lock()
            else:
                self.Release_lock(False)
            return
        elif value:
            self.arrow.value = True
            self.Set_lock()
            self.root._Call("Select")
        else:
            self.arrow.value = False
            self.scrolled = 0
            self.moved = True
            self.Release_lock(False)
            self.root._Call("Deselect")
        self.updated = True


    @property
    def _display_pixel_length(self):
        """
        The length of the dropdown_surface in pixels (before scaling).
        """
        if self.display_length == 0:
            return max(0, len(self.options) * (self.height + self.spacing[1]) - self.spacing[1])
        elif self.display_length > 0:
            return max(0, min(self.display_length, len(self.options)) * (self.height + self.spacing[1]) - self.spacing[1])
        else:
            return abs(self.display_length) * (self.height + self.spacing[1]) - self.spacing[1]

    @property
    def _true_pixel_length(self):
        """
        The true / scaled pixel length of the dropdown_surface.
        """
        if self.scroll_bar:
            return self.scroll_bar.true_height
        else:
            return self.scaled(self.bottom + self.spacing[1] + self._display_pixel_length) - self.scaled(self.bottom + self.spacing[1])

def Arrow_bg(self, bg, accent_bg):
    """
    The function that will create the background for the dropdown arrow button.
    For internal use only. This function is therefore also not imported by __init__.py
    """
    #Just leave the making of the buttons background to the default function. Not gonna bother re-doing that here (because why would I?)
    if self.value:
        surface = self.Make_background_surface(accent_bg)
    else:
        surface = self.Make_background_surface(bg)

    #Draw the arrow so characteristic to dropdown boxes
    if not self.value:
        arrow_coords = (
            (round(self.true_width * 1/6), round(self.true_height * 1/3)), #Top left
            (round(self.true_width * 1/2), round(self.true_height * 2/3)), #Bottom
            (round(self.true_width * 5/6), round(self.true_height * 1/3)), #Top right
            )
    else:
        arrow_coords = (
            (round(self.true_width * 1/6), round(self.true_height * 2/3)), #Bottom left
            (round(self.true_width * 1/2), round(self.true_height * 1/3)), #Top
            (round(self.true_width * 5/6), round(self.true_height * 2/3)), #Bottom right
            )
    pygame.draw.polygon(surface, self.border[0] if self.border else (63, 63, 63), arrow_coords)

    return surface


def Make_scroll_bar(self, scroll_bar):
    """
    Makes a scroll_bar for a DropdownBox.
    For internal use only. This function is therefore also not imported by __init__.py
    """
    if isinstance(scroll_bar, Slider):
        scroll_bar.right = self.right
        scroll_bar.height = self._display_pixel_length
        scroll_bar.top = self.bottom
        scroll_bar.root = self.root
        return scroll_bar
    if scroll_bar == 1:
        size = (15, self._display_pixel_length)
        pos = (self.right - size[0], self.bottom)
        style = "Round"
        background = None
        border = None
        slider_bg = (220, 220, 220)
        slider_accent_bg = (127, 127, 127)
        slider_border = None
        return Slider(pos, size, style = style, background = background, border = border, slider_background = slider_bg, slider_border = slider_border, orientation = 1, root = self.root, independent = True)
    elif scroll_bar == 2:
        size = (15, self._display_pixel_length)
        pos = (self.right - size[0], self.bottom)
        slider_feature_text = "|||"
        slider_feature_size = 9
        return Slider(pos, size, slider_feature_text = slider_feature_text, slider_feature_size = slider_feature_size, orientation = 1, root = self.root, independent = True)
    else:
        raise ValueError(f"Unsupported scroll_bar style: {repr(scroll_bar)}")
