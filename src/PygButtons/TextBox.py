from .Base import Buttons

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame


class TextBox(Buttons):
    """
    Creates a TextBox, in which a user can input text.

    pos: (left, top) - The topleft position before scaling.
    size: (width, height) - The size before scaling.
    hint: str - The text that will be shown if no text is input by the user.
    style: "Square", "Round", int - Defines the radius of curvature of the buttons' corners.
    font_name: str - The name of the font that should be used for the TextBox.
    font_size: int - The size (in px) of the text.
    text_colour: (R, G, B) - The colour of the text the user types.
    hint_colour: (R, G, B) - The colour of the hint.
    text_align: The alignment of the text on the Button. Vertical alignment is always active. Horizontal alignment only if the width of the text is less than the available space.
    text_offset: "auto", int, (x, y) - The offset the text should have from the sides of the TextBox. Prevents the text from overlapping with borders, and touching the edges.
    background: pygame.Surface, (R, G, B), None, function - The background of the button if it is not selected.
    border: ((R, G, B), width, offset), None - The border that appears around the TextBox.
    accent background: pygame.Surface, (R, G, B), None, function - The background of the button if it is_selected. If set to None, will be the same as normal background.
    accent_border: ((R, G, B), width, offset), None - An additional border that can be drawn when the TextBox is selected.
    functions: dict - Contains functions that should be called when a specific event occurs. The values should either be {"Click": func,} to call a function without arguments, or {"Click": (func, arg1, arg2, ...)} to call a function with arguments. If the Button itself is to be passed in as an argument, that argument can be passed in as '*self*'. This argument will automatically replaced when the function is actually called.
                    - "Select": Called whenever the TextBox is selected.
                    - "Deselect": Called whenever the TextBox is deselected.
                    - "Type": Called every time a valid Key_down (one which could alter the contents of the TextBox) is recorded while this TextBox is selected.
    groups: None, [___, ___] - A list of all groups to which a button is to be added.
    root: None, Button - The Button that is considered the 'root element' for this Button. Any function calls that need to include a 'self' Button, will include this root Button instead.
    independent: bool - Determines whether or not the button is allowed to set the input_lock, and is added to buttons.list_all. Mostly important for buttons which are part of another button.

    Inputs:
    *.value: str - Sets the current text in the TextBox.
    *.text: str - Synonymous to *.value. Can be used to keep code clearer / more readable, depending on the context of where this button is used.

    Outputs:
    *.value: str - The current value in the TextBox. I.E. the text input by the user into the input field.
    *.text: str - Synonymous to *.value. Can be used instead to keep code clearer / more readable, depending on the context of where this button is used.
    *.new_input: bool - Whether the TextBox has received any new text inputs since the last time this variable was checked. Automatically resets once it is querried.
    *.deselected: bool - Whether the TextBox was deselected since the last time this variable was checked. Automatically resets once it is querried.

    *.is_selected: bool - Whether this TextBox object is selected at this point in time. I.E. Whether the user is currently typing in this TextBox.
    """
    actions = ["LMB_down", "Key_down"]
    def __init__(self, pos, size,
                 hint = "",
                 style = "Square",
                 font_name = pygame.font.get_default_font(),
                 font_size = 22,
                 text_colour = (0, 0, 0),
                 hint_colour = (128, 128, 128),
                 text_align = "left",
                 text_offset = "auto",
                 background = (255, 255, 255),
                 border = ((63, 63, 63), 1, 0),
                 accent_background = None,
                 accent_border = ((0, 0, 0), 1, 2), #Set to None or False to disable
                 functions = {},
                 group = None,
                 root = None,
                 independent = False,
                 ):
        """
        Create a TextBox Button object. See help(type(self)) for more detailed information.
        """
        super().__init__(pos, size, font_name, font_size, group, root, independent)
        #Set up of basic TextBox properties
        self.text = ""
        self.new_input = False
        self.hint = hint
        self.style = style
        self.text_colour = self.Verify_colour(text_colour)
        self.hint_colour = self.Verify_colour(hint_colour)
        self.text_align = text_align
        self.bg = self.Verify_background(background)
        if accent_background:
            self.accent_bg = self.Verify_background(accent_background)
        else:
            self.accent_bg = self.bg

        #Verify and set the border variables
        self.border = self.Verify_border(border)
        self.accent_border = self.Verify_border(accent_border)

        #Set the offset the text has from the sides of the text_box. In the end,
        #text_offset should be a tuple (x_offset, y_offset)
        if type(text_offset) is int:
            self.text_offset = 2 * (text_offset,)
        elif type(text_offset) is not str:
            self.text_offset = self.Verify_iterable(text_offset, 2)
        elif text_offset.lower() == "auto":
            #The automatic offset is calculated as 0.25 * font_size + max(border_width + border_offset for any of the borders)
            self.text_offset = 2 * (round(self.font_size / 4) + max([brdr[1] + brdr[2] for brdr in (self.border, self.accent_border) if brdr], default = 0),)

        #Settting the initial state for certain default variables
        self.text_scroll = 0
        self.cursor = 0
        self.__is_selected = False
        self.deselected = False
        self.functions = functions
        self.Draw(pygame.Surface((1, 1))) #Makes sure all attributes are set-up correctly


    def LMB_down(self, pos):
        if self.contains(pos):
            self.Claim_input()
            if self.is_selected:
                pos = self.relative(pos)
                #If there is any text: (Check required since for loop has to run at least once to not crash)
                if self.text:
                    #Iterate over all letters, to find which letter was closest to
                    #the position at which the user clicked
                    pixel_offset = - self.text_scroll + self.scaled(max(self.border[1] + self.border[2] + round(self.font_size / 4), self.accent_border[1] + self.accent_border[2] + round(self.font_size / 4)), True)
                    for letter_nr, letter in enumerate(self.text):
                        pixel_length = self.font.size(self.text[:letter_nr + 1])[0]
                        if (pixel_length + pixel_offset) >= pos[0]:
                            break
                    #Calculate the horizontal distance from the cursor to the text box
                    distance = pixel_length + pixel_offset - pos[0]
                    #Get the size of the last letter in the list
                    letter_size = self.font.size(letter)[0]
                    #If the cursor is more than halfway back before the end of this letter
                    #put the cursor in front of the letter.
                    if distance >= (0.5 * letter_size):
                        self.cursor = letter_nr
                    #Else, put it after the letter
                    else:
                        self.cursor = letter_nr + 1
                #If there is no text:
                else:
                    self.cursor = 0
            else:
                self.is_selected = True
                self.cursor = len(self.text)
        elif self.is_selected:
            self.is_selected = False
            self.Buttons.input_processed = True

        return


    def Key_down(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.is_selected = False
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:max(self.cursor - 1, 0)] + self.text[self.cursor:]
            #Move the cursor back one item
            self.cursor -= 1
        elif event.key == pygame.K_DELETE:
            self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
        elif event.key == pygame.K_LEFT:
            self.cursor -= 1
        elif event.key == pygame.K_RIGHT:
            self.cursor += 1
        elif event.unicode:
            self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
            #Scroll the item sideways
            #self.text_scroll += self.font.size(event.unicode)[0]
            self.cursor += 1
        else:
            return
        #Inform Buttons that the input has been processed / used
        self.Buttons.input_processed = True
        #Call "type" if the Key_down event was one which could have altered the text contents.
        if event.key not in (pygame.K_RETURN, pygame.K_RIGHT, pygame.K_LEFT):
            self.root._Call("Type")
        return


    def Scale(self, scale, relative_scale = True, *, center = (0, 0), px_center = None):
        super().Scale(scale, self, relative_scale, center = center, px_center = px_center)


    def Move(self, offset, scale = False):
        super().Move(offset, self, scale)


    def Clear(self):
        self.value = ""
        self.is_selected = False
        #Lock is automatically released in property setter


    def Draw(self, screen, pos = None):
        """
        Draw the button to the screen.
        """
        pos = pos or self.scaled(self.topleft)
        if self.updated:
            self.update_scroll()
            #Draw the correct background onto the surface
            if not self.is_selected:
                self.surface = self.Make_background_surface(self.bg)
            else:
                self.surface = self.Make_background_surface(self.accent_bg)
            #Draw a border, if it is enabled
            if self.border:
                self.Draw_border(self.surface, *self.border)
            #Draw a accent border, if it is enabled:
            if self.accent_border and self.is_selected:
                self.Draw_border(self.surface, *self.accent_border)
            #Copy the surface to allow the cursor to be drawn
            self.cursor_surface = self.surface.copy()

            #Add the text to the surface
            text_limiter = pygame.Surface(self.offset(self.true_size, self.scaled(self.text_offset), (-2, -2)), pygame.SRCALPHA)
            limiter_rect = text_limiter.get_rect()
            if self.text:
                text_surface = self.font.render(self.text, True, self.text_colour)
            else:
                text_surface = self.font.render(self.hint, True, self.hint_colour)
            text_rect = text_surface.get_rect()
            #Align the text rect
            text_rect = self.AlignY(text_rect, limiter_rect, self.text_align)
            if text_rect.width <= limiter_rect.width:
                #If the text is smaller than the limiter, perform alignment in the X direction
                self.AlignX(text_rect, limiter_rect, self.text_align)
            else:
                #If the text is wider than the limiter, all alignment is taken care of inside text_scroll
                text_rect.left = - self.text_scroll
            text_limiter.blit(text_surface, text_rect)
            #Blit the limiter onto the button
            limiter_rect.center = self.middle #middle is scaled(width / 2, height / 2)
            self.surface.blit(text_limiter, limiter_rect)

            #Make the cursor surface
            cursor_rect = pygame.Rect((0, 0), (max(1, self.scaled(1)), self.font.get_height()))
            #Align cursor vertically
            cursor_rect.centery = text_rect.centery
            #Align cursor horizontally. (if-else statement is required to prevent the hint from changing the Cursor location.)
            cursor_rect.left = self.font.size(self.text[:self.cursor])[0] + (text_rect.left if self.text else self.AlignX(cursor_rect.width, limiter_rect, self.text_align).left)
            #Draw the cursor to the text limiter
            pygame.draw.rect(text_limiter, self.text_colour,  cursor_rect)
            self.cursor_surface.blit(text_limiter, limiter_rect)

            #Clear self.updated again, as the surface has been remade.
            self.updated = False

        if self.is_selected:
            #Update the cursor animation
            self.cursor_animation = (self.cursor_animation + 1) % self.framerate
        if self.cursor_animation < round(self.framerate / 2):
            screen.blit(self.cursor_surface, pos)
        else:
            screen.blit(self.surface, pos)
        return


    @property
    def is_selected(self):
        return self.__is_selected

    @is_selected.setter
    def is_selected(self, value):
        #If the user selects the text box:
        if value:
            self.__is_selected = True
            self.cursor = len(self.text)
            self.Set_lock()
            self.root._Call("Select")
        else:
            self.__is_selected = False
            self.deselected = True
            self.cursor = 0
            self.cursor_animation = self.framerate
            self.Release_lock(False) #Release without claiming the input
            self.root._Call("Deselect")


    @property
    def deselected(self):
        deselected_ = self.__deselected
        self.__deselected = False
        return deselected_

    @deselected.setter
    def deselected(self, value):
        self.__deselected = value


    @property
    def cursor(self):
        return self.__cursor

    @cursor.setter
    def cursor(self, value):
        #Make sure the cursor cannot be set to negative points, nor can it go further than directly after the last character.
        self.__cursor = self.Clamp(int(value), 0, len(self.text))
        self.cursor_animation = self.framerate - 1
        self.updated = True
        self.update_scroll()


    @property
    def text_scroll(self):
        return self.__text_scroll

    @text_scroll.setter
    def text_scroll(self, value):
        self.__text_scroll = value
        self.updated = True


    @property
    def text(self):
        return self.__value

    @text.setter
    def text(self, value):
        self.__value = value
        self.updated = True
        self.new_input = True


    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = val
        self.updated = True
        self.new_input = True


    @property
    def new_input(self):
        new_input_ = self.__new_input
        self.__new_input = False
        return new_input_

    @new_input.setter
    def new_input(self, value):
        self.__new_input = value


    def update_scroll(self):
        """
        Update the value of the scrolling (within limits).
        """
        #Get the width of the text box; +1 to account for a possible cursor at the end.
        #Always add this +1, to prevent annoying 1-pixel shifts when moving the cursor to the final position.
        text_width = self.font.size(self.text)[0] + 1
        #Get the width of the text limiter surface
        limiter_width = self.true_width - self.scaled(2 * self.text_offset[0])
        #Get the cursor pixel index; +1 not required since 'size' already includes index 0 as width 1
        cursor_pos = self.font.size(self.text[:self.cursor])[0]
        #If all text fits in the view window:
        if text_width <= limiter_width:
            #Reset any scroll. No need to scroll if it fits anyway
            self.text_scroll = 0
        #If the text is bigger than the scroll window
        else:
            self.text_scroll = self.Clamp(self.text_scroll, 0, text_width - limiter_width)
            #If the cursor is before the view window:
            if cursor_pos < self.text_scroll:
                self.text_scroll = cursor_pos
            #If the cursor is after the view window:
                # => because the cursor is 1 pixel wide, and thus ends at pos+1
            elif cursor_pos >= self.text_scroll + limiter_width:
                self.text_scroll = cursor_pos - limiter_width + 1
            #If the cursor is already inside of the view window:
            else:
                pass
