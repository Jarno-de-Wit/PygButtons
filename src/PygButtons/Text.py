from .Base import Buttons
from .Slider import Slider

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame


class Text(Buttons):
    """
    A simple (multi-line) text object, with scrolling support.

    pos: (left, top) - The topleft position before scaling.
    size: (width, height) - The size before scaling.
    text: str - The text that will be rendered to the surface.
    style: "Square", "Round", int - Defines the radius of curvature of the buttons' corners.
    font_name: str - The name of the font that should be used for the Text.
    font_size: int - The size (in px) of the text.
    text_colour: (R, G, B) - The colour of the text in the Text object.
    text_align: The alignment of the text on the Button surface.
    text_offset: "auto", int, (x, y) - The offset the text should have from the sides of the Text object. Prevents the text from overlapping with borders, and touching the edges.
    scroll_bar: None, int, Slider - The type of scrollbar to be included. Default styles 1 and 2 are available.
    background: pygame.Surface, (R, G, B), None, function - The background of the button.
    border: ((R, G, B), width, offset), None - The border that appears around the TextBox.
    functions: dict - Contains functions that should be called when a specific event occurs. The values should either be {"Click": func,} to call a function without arguments, or {"Click": (func, arg1, arg2, ...)} to call a function with arguments. If the Button itself is to be passed in as an argument, that argument can be passed in as '*self*'. This argument will automatically replaced when the function is actually called.
                    - "Move": Called whenever the Text object is scrolled.
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
    root: None, Button - The Button that is considered the 'root element' for this Button. Any function calls that need to include a 'self' Button, will include this root Button instead.
    independent: bool - Determines whether or not the button is allowed to set the input_lock, and is added to buttons.list_all. Mostly important for buttons which are part of another button.

    Inputs:
    *.value: str - Can be used synonymously with *.text.
    *.text: str - Allows the user to set a new value for the Text objects' displayed text.
    *.lines: tuple - Allows the user to set a new value for 'lines' (the text as it is split to fit properly accros the lines).
    *.write(value) - Appends text to self.text. Allows this button to be used as an output for e.g. the print() function.

    Outputs:
    *.value: str - Synonymous with *.text.
    *.text: str - The current text being rendered to the surface.
    *.lines: tuple - The current text being rendered to the surface, as it is split to prevent it from exceeding the Surface borders.
    """
    actions = ["Scroll", "LMB_down", "LMB_up", "Set_cursor_pos"]
    def __init__(self, pos, size,
                 text = "",
                 style = "Square",
                 font_name = pygame.font.get_default_font(),
                 font_size = 22,
                 text_colour = (0, 0, 0),
                 text_align = "topleft",
                 text_offset = "auto",
                 scroll_bar = None,
                 background = None,
                 border = None,
                 functions = {},
                 group = None,
                 root = None,
                 independent = False,
                 ):
        """
        Create a Text Button object. See help(type(self)) for more detailed information.
        """
        super().__init__(pos, size, font_name, font_size, group, root, independent)
        self.style = style
        self.text_colour = self.Verify_colour(text_colour)
        self.text_align = text_align

        self.bg = self.Verify_background(background)
        self.border = self.Verify_border(border)

        #Set the offset the text has from the sides of the text_box
        if type(text_offset) is int:
            self.text_offset = 2 * (text_offset,)
        elif type(text_offset) is not str:
            self.text_offset = self.Verify_iterable(text_offset, 2)
        elif text_offset.lower() == "auto":
            #The automatic offset is calculated as 0.25 * font_size + (border_width + border_offset if there is a border)
            #Offset is not 0 if no border is given, to be consistent with TextBox Buttons
            #It can of course still be 0 if the user sets text_offset = 0
            self.text_offset = 2 * (round(self.font_size / 4) + ((border[1] + border[2]) if self.border else 0),)

        if scroll_bar:
            self.scroll_bar = Make_scroll_bar(self, scroll_bar)
            self.children.append(self.scroll_bar)
        else:
            self.scroll_bar = None
        self.__scrolled = 0
        self.functions = functions
        self.text = text
        self.Build_lines()
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are set-up correctly


    def LMB_down(self, pos):
        if self.scroll_bar:
            self.scroll_bar.LMB_down(pos)
            if self.Buttons.input_claim: #If the slider contained the position, and now claimed the input, set self as the lock
                self.Set_lock()


    def LMB_up(self, pos):
        if self.scroll_bar:
            self.scroll_bar.LMB_up(pos)
            if self.Buttons.input_claim:
                self.Release_lock()


    def Set_cursor_pos(self, pos):
        if self.scroll_bar:
            self.scroll_bar.Set_cursor_pos(pos)


    def Scroll(self, value, pos):
        if not self.contains(pos): #If the mouse was not within the text box:
            return
        self.scrolled_px += self.Buttons.scroll_factor * value
        self.Claim_input()


    def Scale(self, scale, relative_scale = True, *, center = (0, 0), px_center = None):
        super().Scale(scale, self, relative_scale, center = center, px_center = px_center)


    def Move(self, offset, scale = False):
        super().Move(offset, self, scale)


    def Clear(self):
        self.scrolled = 0
        self.Release_lock()
        #Does not do anything to the contained text, since that is not created directly through user input.


    def Draw(self, screen, pos = None):
        """
        Draw the button to the screen.
        """
        self.scrolled #Update the scrolled position quickly, so that any .moved = True are set
        pos = pos or self.scaled(self.topleft)

        if self.updated:
            self.Build_lines()
            self.moved = True

            #Make the background surface
            self.bg_surface = self.Make_background_surface(self.bg)
            if self.border:
                self.Draw_border(self.bg_surface, *self.border)

            font_height = self.font.get_height()
            if self.px_height >= len(self.lines) * font_height:
                #If the text fully fits within the available space, calculate the vertical offset to get the right alignment
                vert_offset = self.AlignY(len(self.lines) * font_height, self.px_height, self.text_align).top
            else:
                #If the text requires scrolling, vertical alignment doesn't matter anymore (all vertical alignment is taken over by the scrolled value)
                vert_offset = 0

            #Build the surface containing ALL lines of text
            self.text_surface =  pygame.Surface((self.px_width, font_height * len(self.lines) + vert_offset), pygame.SRCALPHA)

            for line_nr, line in enumerate(self.lines):
                line_surf = self.font.render(line, True, self.text_colour)
                line_rect = line_surf.get_rect()
                line_rect.top = line_nr * font_height + vert_offset
                line_rect = self.AlignX(line_rect, self.px_width, self.text_align)
                self.text_surface.blit(line_surf, line_rect)

            self.updated = False

        if self.moved:
            #Blit the fully rendered text surface onto a limiter surface.
            text_limiter = pygame.Surface((self.px_width, self.true_height - 2 * self.scaled(self.text_offset[1])), pygame.SRCALPHA)
            text_limiter.blit(self.text_surface, (0, -self.scrolled_px))

            #Blit the text surface onto the actual background
            self.surface = self.bg_surface.copy()
            self.surface.blit(text_limiter, self.scaled(self.text_offset))

            if self.scroll_bar:
                self.scroll_bar.Draw(self.surface, tuple(round(i) for i in self.relative(self.scroll_bar.scaled(self.scroll_bar.topleft))))
            self.moved = False

        screen.blit(self.surface, pos)
        return


    def write(self, value):
        """
        Append value to self.text.
        Allows for a Text object to be used as an output "file" for e.g. print.
        """
        self.text += value


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

        return

    @property
    def scrolled_px(self):
        #Calculate the required height (in px)
        req_height = self.font.get_height() * len(self.lines)
        #Calculate the required height change that has to be accomodated by scrolling (in px)
        max_scroll_height = max(0, req_height - self.true_height + 2 * self.scaled(self.text_offset[1])) #Get the total distance (in px) the surface must be scrolled

        return round(max_scroll_height * self.scrolled)

    @scrolled_px.setter
    def scrolled_px(self, value):
        #Calculate the required height (in px)
        req_height = self.font.get_height() * len(self.lines)
        #Calculate the required height change that has to be accomodated by scrolling (in px)
        max_scroll_height = max(0, req_height - self.true_height + 2 * self.scaled(self.text_offset[1])) #Get the total distance (in px) the surface must be scrolled

        if max_scroll_height:
            self.scrolled = value / max_scroll_height


    @property
    def value(self):
        return self.text

    @value.setter
    def value(self, val):
        self.text = val


    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        if type(value) is not str:
            raise TypeError(f"Text should be type str, not type {type(value).__name__}.")

        self.__text = value
        self.updated = True


    @property
    def lines(self):
        return self.__lines

    @lines.setter
    def lines(self, value):
        """

        """
        #For external use only. Internally, all writing calls are directly to self.__lines
        if type(value) not in (tuple, list,):
            raise TypeError(f"Lines must be type 'tuple' or type 'list', not type {type(value).__name__}")
        self.__lines = tuple(value)
        self.__text = "\n".join(self.__lines)
        self.updated = True


    def Build_lines(self):
        """
        (Re-)builds the '*.lines' tuple based on the current value of self.text, such that the text will automatically wrap around to the next line if it won't fit on the current line anymore.
        Called automatically in *.Draw, after *.text is set / changed.
        """
        max_width = self.px_width
        #Split the text into lines, ignoring any trailing newlines.
        text_lines = self.text.rstrip("\n").split("\n")
        lines = []
        for line in text_lines:
            words = line.split(" ")
            line_string = words[0]
            for word in words[1:]:
                if self.font.size(" ".join([line_string, word]))[0] <= max_width: #If the next word still fits on this line:
                    line_string = " ".join([line_string, word]) #Join it together with the existing text
                else: #If the word is too long to fit on the line:
                    lines.append(line_string)
                    line_string = word #Place it on the next line.
            #Once all words are exhausted, append the remaining string to lines as well
            lines.append(line_string)
        self.__lines = tuple(lines)

        if self.scroll_bar:
            self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(1, (self.height - 2 * self.text_offset[1]) / (len(self.lines) * self.font_size))))

        self.scrolled += 0 #Update the 'scrolled' value, to take into account that after rebuilding, the length of 'lines' might be different

    @property
    def px_width(self):
        """
        The maximum width (in px) the text may have. In other words, the horizontal space available for text.
        """
        return self.true_width - 2 * self.scaled(self.text_offset[0]) - (self.scroll_bar.true_width + self.scaled(self.text_offset[0]) if self.scroll_bar else 0)

    @property
    def px_height(self):
        """
        The maximum height (in px) the text may have. In other words, the horizontal space available for text.
        """
        return self.true_height + 2 * self.scaled(self.text_offset[1])

def Make_scroll_bar(self, scroll_bar):
    """
    Make a scroll_bar for a Text object.
    For internal use only. This function is therefore also not imported by __init__.py
    """
    if isinstance(scroll_bar, Slider):
        scroll_bar.right = self.right - self.text_offset[0]
        scroll_bar.top = self.top + self.text_offset[1]
        if scroll_bar.height > self.height - 2 * self.text_offset[1]:
            scroll_bar.height = self.height - 2 * self.text_offset[1]
        return scroll_bar
    if scroll_bar == 1:
        size = (15, self.height - 2 * self.text_offset[1])
        pos = (self.right - size[0] - self.text_offset[0], self.top + self.text_offset[1])
        style = "Round"
        background = None
        border = None
        slider_bg = (220, 220, 220)
        slider_accent_bg = (127, 127, 127)
        slider_border = None
        return Slider(pos, size, style = style, background = background, border = border, slider_background = slider_bg, slider_border = slider_border, root = self.root, independent = True)
    elif scroll_bar == 2:
        size = (15, self.height - 2 * self.text_offset[1])
        pos = (self.right - size[0] - self.text_offset[0], self.top + self.text_offset[1])
        slider_feature_text = "|||"
        slider_feature_size = 9
        return Slider(pos, size, slider_feature_text = slider_feature_text, slider_feature_size = slider_feature_size, root = self.root, independent = True)
    else:
        raise ValueError(f"Unsupported scroll_bar style: {repr(scroll_bar)}")
