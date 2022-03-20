from Base import Buttons
from Slider import Slider

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
    font_name: str - The name of the font that should be used for the Text. Must lead to a valid font when used in pygame.font.Font().
    font_size: int - The size (in px) of the text.
    text_colour: (R, G, B) - The colour of the text in the Text object.
    text_offset: "auto", int, (x, y) - The offset the text should have from the sides of the Text object. Prevents the text from overlapping with borders, and touching the edges.
    scroll_bar: None, int, Slider - The type of scrollbar to be included. Default styles 1 and 2 are available.
    background: pygame.Surface, (R, G, B), None, function - The background of the button. If a function is given, it will be called in Make_background as function(self).
    border: ((R, G, B), width, offset), None - The border that appears around the TextBox.
    func_data: dict - Contains potential additional data for use by custom background drawing functions.
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
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
                 font_size = 20,
                 text_colour = (0, 0, 0),
                 text_offset = "auto",
                 scroll_bar = None,
                 background = None,
                 border = None,
                 func_data = {},
                 group = None,
                 independent = False,
                 ):
        """
        Create a Text Button object. See help(type(self)) for more detailed information.
        """
        super().__init__(pos, size, font_name, font_size, group, independent)
        self.style = style
        self.text_colour = self.Verify_colour(text_colour)

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
        self.text = text
        self.__scrolled = 0
        self.Build_lines()
        self.func_data = func_data
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are set-up correctly


    def LMB_down(self, pos):
        pos = self.relative(pos)
        if self.scroll_bar:
            self.scroll_bar.LMB_down(pos)
            if self.Buttons.input_claim: #If the slider contained the position, and now claimed the input, set self as the lock
                self.Set_lock()


    def LMB_up(self, pos):
        pos = self.relative(pos)
        if self.scroll_bar:
            self.scroll_bar.LMB_up(pos)
            if self.Buttons.input_claim:
                self.Release_lock()


    def Set_cursor_pos(self, pos):
        pos = self.relative(pos)
        if self.scroll_bar:
            self.scroll_bar.Set_cursor_pos(pos)


    def Scroll(self, value, pos):
        if not self.contains(pos): #If the mouse was not within the text box:
            return
        self.scrolled += value
        self.Buttons.input_claim = True
        self.Buttons.input_processed = True


    def Draw(self, screen):
        """
        Draw the button to the screen.
        """
        self.scrolled #Update the scrolled position quickly

        if self.updated:
            self.Build_lines()
            self.moved = True

            #Make the background surface
            self.bg_surface = self.Make_background_surface(self.bg)
            if self.border:
                self.Draw_border(self.bg_surface, *self.border)

            #Build the surface containing ALL lines of text
            font_height = self.font.get_height()
            self.text_surface =  pygame.Surface(self.scaled((self.width - 2 * self.text_offset[0] - (self.scroll_bar.width if self.scroll_bar else 0), font_height * len(self.lines))), pygame.SRCALPHA)
            for line_nr, line in enumerate(self.lines):
                self.text_surface.blit(self.font.render(line, True, self.text_colour), (0, line_nr * font_height))

            self.updated = False

        if self.moved:
            #Blit the fully rendered text surface onto a limiter surface.
            text_limiter = pygame.Surface(self.scaled((self.width - 2 * self.text_offset[0] - (self.scroll_bar.width + self.text_offset[0] if self.scroll_bar else 0), self.height - 2 * self.text_offset[1])), pygame.SRCALPHA)
            text_limiter.blit(self.text_surface, (0, -self.scaled(self.scrolled)))

            #Blit the text surface onto the actual background
            self.surface = self.bg_surface.copy()
            self.surface.blit(text_limiter, self.scaled(self.text_offset))

            if self.scroll_bar:
                self.scroll_bar.Draw(self.surface)
            self.moved = False

        screen.blit(self.surface, self.scaled(self.topleft))
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
            self.scrolled = round(self.scroll_bar.value)
        return(self.__scrolled)

    @scrolled.setter
    def scrolled(self, value):
        text_height = self.font_size * len(self.lines) #Get the total height of all text in the text box

        #Make sure the scrolled value cannot exceed the limits of the space in the box
        value = round(self.Clamp(value, 0, max(0, text_height - self.height + 2 * self.text_offset[1])))

        self.moved = True

        #Return if the scroll value has not been updated
        if value == self.__scrolled:
            return

        self.__scrolled = value

        if self.scroll_bar:
            self.scroll_bar.value = value

        return


    @property
    def value(self):
        return self.text

    @value.setter
    def value(self, val):
        self.text = val


    @property
    def text(self):
        return(self.__text)

    @text.setter
    def text(self, value):
        if type(value) is not str:
            raise TypeError(f"Text should be type str, not type {type(value).__name__}.")

        self.__text = value
        self.updated = True


    @property
    def lines(self):
        return(self.__lines)

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
        Called automatically after *.text is set.
        """
        max_width = self.scaled(self.width - 2 * self.text_offset[0] - (self.scroll_bar.width + self.text_offset[0] if self.scroll_bar else 0))
        text_lines = self.text.split("\n")
        lines = []
        for line in text_lines:
            line_string = ""
            words = line.split(" ")
            for word in words:
                if line_string == "": #If the line is still empty:
                    line_string = word #Simply place the word at the start of the string.
                elif self.font.size(" ".join([line_string, word]))[0] <= max_width: #If the next word still fits on this line:
                    line_string = " ".join([line_string, word]) #Join it together with the existing text
                else: #If the word is too long to fit on the line:
                    lines.append(line_string)
                    line_string = word #Place it on the next line.
            #Once all words are exhausted, append the remaining string to lines as well
            lines.append(line_string)
        self.__lines = tuple(lines)

        if self.scroll_bar:
            self.scroll_bar.Set_slider_primary(round(self.scroll_bar.height * min(1, (self.height - 2 * self.text_offset[1]) / (len(self.lines) * self.font_size))))
            self.scroll_bar.value_range = (0, max(0, len(self.lines) * self.font_size - self.height + 2 * self.text_offset[1]))

        self.scrolled += 0 #Update the 'scrolled' value, to take into account that after rebuilding, the length of 'lines' might be different


def Make_scroll_bar(self, scroll_bar):
    """
    Make a scroll_bar for a Text object.
    For internal use only. This function is therefore also not imported by __init__.py
    """
    if isinstance(scroll_bar, Slider):
        scroll_bar.right = self.width - self.text_offset[0]
        scroll_bar.centery = math.floor(self.height)
        if scroll_bar.height > self.height - 2 * text_offset:
            scroll_bar.height = self.height - 2 * text_offset
        return(scroll_bar)
    if isinstance(scroll_bar, int) and int(scroll_bar) == 1:
        size = (15, self.height - 2 * self.text_offset[1])
        pos = (self.width - size[0] - self.text_offset[0], self.text_offset[1])
        style = "Round"
        background = None
        border = None
        slider_bg = (220, 220, 220)
        slider_accent_bg = (127, 127, 127)
        slider_border = None
        return(Slider(pos, size, style = style, background = background, border = border, slider_background = slider_bg, slider_border = slider_border, independent = True))
    elif isinstance(scroll_bar, int) and int(scroll_bar) == 2:
        size = (15, self.height - 2 * self.text_offset[1])
        pos = (self.width - size[0] - self.text_offset[0], self.text_offset[1])
        slider_feature_text = "|||"
        slider_feature_size = 9
        return(Slider(pos, size, slider_feature_text = slider_feature_text, slider_feature_size = slider_feature_size, independent = True))
    else:
        raise ValueError(f"Unsupported scroll_bar style: {repr(scroll_bar)}")
