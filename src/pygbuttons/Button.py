from .Base import ButtonBase
from .Control import Buttons

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
import math


class Button(ButtonBase):
    """
    Creates a Button, an object which can detect Left Mouse Button inputs from the user.

    pos: (left, top) - The topleft position before scaling.
    size: (width, height) - The size before scaling.
    text: str - The text to be displayed on the Button.
    mode: str - "None": Does not change *.value when clicked. Will set *.clicked and execute any assigned functions.
              - "Count": Count the number of inputs that have occured.
              - "Toggle": Toggle value from True to False and back.
              - "Hold": Stays True until the Mouse Button is released.
    orientation: int - The orientation of the text. If orientation == 0, the text will be horizontal; if orientation == 1, the text will be vertical.
    style: "Square", "Round", int - Defines the radius of curvature of the buttons' corners.
    font_name: str - The name of the font that should be used for the Button.
    font_size: int - The size (in px) of the text.
    text_colour: (R, G, B) - The colour of the text the user types.
    text_align: The alignment of the text on the Button.
    background: pygame.Surface, (R, G, B), None, function - The background of the button if it is not selected.
    border: ((R, G, B), width, offset), None - The border that appears around the TextBox.
    accent background: pygame.Surface, (R, G, B), None, function - The background of the Button if *.value. If set to None, will be the same as normal background.
    dragable: (horizotal, vertical) - A tuple of two booleans defining whether the Button is allowed to be moved in either the horizontal and / or vertical direction repectively. Requires mode == "Hold".
    limits: (left, right, top, bottom) - The coordinate limits between which the Button is to be draggable.
    snap: ((x snap coords, ___), (y snapc coords, ___), snap_range) - If the button is dragable / movable, the positions to which the Button should snap, as well as the range (in px) within which the Button should snap to these locations.
    functions: dict - Contains functions that should be called when a specific event occurs. The values should either be {"Click": func,} to call a function without arguments, or {"Click": (func, arg1, arg2, ...)} to call a function with arguments. If the Button itself is to be passed in as an argument, that argument can be passed in as '*self*'. This argument will automatically replaced when the function is actually called.
                    - "Click": Called when the Button is clicked.
                    - "Release": Called when the Button is released. Available only when mode == "Hold" or mode == "Toggle".
                    - "Move": Called when the Button is dragged to a new location. Only available if any(dragable).
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
    root: None, Button - The Button that is considered the 'root element' for this Button. Any function calls that need to include a 'self' Button, will include this root Button instead.
    independent: bool - Determines whether or not the button is allowed to set the input_lock, and is added to buttons.list_all. Mostly important for buttons which are part of another button.

    Inputs:
    *.value: int, bool - The current state of the button.

    Outputs:
    *.value: int, bool - The current state in the Button. If mode == "count", the amount of times (int) the Button was clicked. If mode == "Toggle" or "hold", whether the button is currently in the pressed / down state (bool).
    *.clicked: bool - Whether the Button has been set to a new state since the last time this variable was checked. Automatically resets once it is querried.
    *.moved: bool - Whether the Button has been dragged to a different location since the last time this variable was checked. Automatically resets once it is querried.
    """
    actions = ["LMB_down", "LMB_up", "Set_cursor_pos", "Mouse_motion"]
    def __init__(self, pos, size,
                 text = "",
                 mode = "None",
                 orientation = 0,
                 style = "Square",
                 font_name = pygame.font.get_default_font(),
                 font_size = 22,
                 text_colour = (0, 0, 0),
                 text_align = "Center",
                 text_offset = "auto",
                 background = (255, 255, 255),
                 border = ((63, 63, 63), 1, 0),
                 accent_background = (220, 220, 220),
                 dragable = (False, False),
                 limits = (None, None, None, None),
                 snap = ((), (), 0),
                 functions = {},
                 group = None,
                 root = None,
                 independent = False
                 ):
        """
        Create a Button Button object. See help(type(self)) for more detailed information.
        """
        super().__init__(pos, size, font_name, font_size, group, root, independent)
        self.orientation = orientation
        self.style = style
        self.functions = functions
        if not isinstance(mode, str):
            raise TypeError(f"mode must be type 'str', not type {type(mode).__name__}")
        elif mode.lower() == "count":
            self.value = 0
        elif mode.lower() in ("none", "toggle", "hold"):
            self.value = False
        else:
            raise ValueError(f"Unsupported button mode '{mode}'")
        self.mode = mode.lower()
        self.text = text
        self.text_colour = self.Verify_colour(text_colour)
        self.text_align = text_align
        self.bg = self.Verify_background(background)
        if accent_background:
            self.accent_bg = self.Verify_background(accent_background)
        else:
            self.accent_bg = self.bg
        self.border = self.Verify_border(border)

        #Set the offset the text has from the sides of the text_box
        if isinstance(text_offset, int):
            self.text_offset = 2 * (text_offset,)
        elif not isinstance(text_offset, str):
            self.text_offset = self.Verify_iterable(text_offset, 2)
        elif text_offset.lower() == "auto":
            #The automatic offset is calculated as 0.25 * font_size + (border_width + border_offset if there is a border)
            #Offset is not 0 if no border is given, to be consistent with TextBox Buttons
            #It can of course still be 0 if the user sets text_offset = 0
            self.text_offset = 2 * (round(self.font_size / 4) + ((self.border[1] + self.border[2]) if self.border else 0),)

        self.dragable = self.Verify_iterable(dragable, 2, bool)
        limits = self.Verify_iterable(limits, 4)
        self.limits = list(value if value is not None else ( (-1) ** (i + 1) * math.inf) for i, value in enumerate(limits))
        self.snap = self.Verify_iterable(snap, 3)
        self.moved = False
        self.clicked = False
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are prepared and set-up correctly


    def LMB_down(self, pos):
        if self.contains(pos):
            with Buttons.Callbacks(True, False), Buttons.Update_flags(True, False):
                if self.mode == "none":
                    self._Call("Click") #Call "Click" separately since "none" does not change self.value
                    if self._update_flags:
                        self.clicked = True
                elif self.mode == "count":
                    self.value += 1
                elif self.mode == "toggle":
                    self.value = not self.value
                elif self.mode == "hold":
                    self.Set_lock()
                    self.value = True
                    if any(self.dragable):
                        self.drag_pos = self.relative(pos)
                self.Claim_input()
            return

    def LMB_up(self, pos):
        if self.mode == "hold" and self.value:
            with Buttons.Callbacks(True, False), Buttons.Update_flags(True, False):
                self.value = False
                self.Release_lock()
        return

    def Mouse_motion(self, event):
        """
        If the button supports dragging, this function is used to move the button to a new position.

        event: pygame.event.EventType, tuple - The event or global position the cursor moved to.
        """
        # If required, extract the position from the event
        if isinstance(event, pygame.event.EventType):
            pos = event.pos
        else:
            pos = event

        if self.value:
            if any(self.dragable):
                hori, verti = self.offset(self.relative(pos), self.drag_pos, (-1, -1)) #Determine the offsets of the cursor from where the user originally clicked

                left = self.left + hori / self.scale * self.dragable[0] #Scale the offsets down to the original scale
                top = self.top + verti / self.scale * self.dragable[1]
                #Perform snapping
                distances = sorted(zip((abs(left - snap_point) for snap_point in self.snap[0]), self.snap[0]))
                if distances: #If there are any snap point:
                    closest = distances[0]
                    if closest[0] <= self.snap[2]: #If the distance <= the snapping range
                        left = round(closest[1]) #Snap!
                #Also, vertical snapping
                distances = sorted(zip((abs(top - snap_point) for snap_point in self.snap[1]), self.snap[1]))
                if distances: #If there are any snap point:
                    closest = distances[0]
                    if closest[0] <= self.snap[2]: #If the distance <= the snapping range
                        top = round(closest[1]) #Snap!
                #Confine the button within the limits
                self.left = self.Clamp(left, self.limits[0], self.limits[1] - self.width)
                self.top = self.Clamp(top, self.limits[2], self.limits[3] - self.height)
                with Buttons.Callbacks(True, False), Buttons.Update_flags(True, False):
                    self._Call("Move")
                    if self._update_flags:
                        self.moved = True

    def Set_cursor_pos(self, pos):
        self.Mouse_motion(pos)


    def Scale(self, scale, relative_scale = True, *, center = (0, 0), px_center = None):
        super().Scale(scale, self, relative_scale, center = center, px_center = px_center)


    def Move(self, offset, scale = False):
        super().Move(offset, self, scale)


    def Clear(self):
        self.value = 0 if self.mode.lower() == "count" else False
        self.Release_lock()


    def Draw(self, screen, pos = None):
        """
        Draw the button to the screen.
        """
        if self.updated:
            #Build the correct background for the surface
            if not self.value:
                self.surface = self.Make_background_surface(self.bg)
            else:
                self.surface = self.Make_background_surface(self.accent_bg)
            #Draw a border, if it is enabled
            if self.border:
                self.Draw_border(self.surface, *self.border)
            #Draw the text onto the surface
            if self.text:
                #Make a surface that fits within the border
                text_offset = self.scaled(self.text_offset)
                text_limiter = pygame.Surface(self.Clamp(self.offset(self.true_size, text_offset, (-2, -2)), 0, math.inf), pygame.SRCALPHA)
                limiter_rect = text_limiter.get_rect()
                text_surface = self.font.render(self.text, True, self.text_colour)

                if self.orientation:
                    text_surface = pygame.transform.rotate(text_surface, -90 * self.orientation)
                text_rect = text_surface.get_rect()
                if not "bottom" in self.text_align:
                    text_rect.height = self.font.get_height()
                #Align the text properly
                self.Align(text_rect, limiter_rect, self.text_align)
                #Blit the text to the limiter surface, and then onto the screen
                text_limiter.blit(text_surface, text_rect)
                limiter_rect.center = self.middle
                self.surface.blit(text_limiter, limiter_rect)

            #Clear self.updated again, as the surface has been remade.
            self.updated = False
        screen.blit(self.surface, pos or self.scaled(self.topleft))
        return

    def _move(self, value):
        self.left += value[0]
        self.top += value[1]
        self.limits[0] += value[0]
        self.limits[1] += value[0]
        self.limits[2] += value[1]
        self.limits[3] += value[1]



    @property
    def text(self):
        return self.__text
    @text.setter
    def text(self, value):
        self.__text = str(value)
        self.updated = True

    @property
    def text_align(self):
        return self.__text_align
    @text_align.setter
    def text_align(self, value):
        self.__text_align = value
        self.updated = True

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value):
        self.__value = value
        if value:
            self._Call("Click")
        else:
            self._Call("Release")
        self.updated = True
        if self._update_flags:
            self.clicked = True

    @property
    def clicked(self):
        clicked_ = self.__clicked
        self.__clicked = False
        return clicked_
    @clicked.setter
    def clicked(self, value):
        self.__clicked = value

    @property
    def moved(self):
        moved = self.__moved
        self.__moved = False
        return moved
    @moved.setter
    def moved(self, value):
        self.__moved = value
