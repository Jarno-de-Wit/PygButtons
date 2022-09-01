#Import all Buttons from pygbuttons
from pygbuttons import *

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
import pygame


def Main():
    # Set-up of basic parameters
    global running
    framerate = 30
    Buttons.framerate = framerate #Optional, but recommended in case TextBoxes are used
    pygame.init()
    pygame.key.set_repeat(500, 50)
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()

    #Setup of the Buttons - Note: The name of the button variables is not
    # important. You could also store them in a list, or not store them anywhere
    # at all, and just use the Buttons' groups to organise all buttons
    button_quit = Button((450, 450), (100, 50), text = "Quit", mode = "Count")

    button_count = Button((50, 25 ), (200, 50), text = "Count", mode = "Count")
    button_toggle = Button((50, 100), (200, 50), text = "Toggle", mode = "Toggle")
    button_hold = Button((50, 175), (200, 50), text = "Hold", mode = "Hold")
    Button_func = Button((50, 250), (200, 50), text = "Function (print)", mode = "None", functions = {"Click": (print, "Clicked")})

    button_tb = TextBox((350, 25),(200, 50), hint = "Type here")
    button_text = Text((300, 125), (300, 100), text = "This is a Text object. You can scroll through the text if you want, although this text isn't really that interesting.", border = ((31, 31, 31), 1, 0), scroll_bar = 2)

    button_slider_1 = Slider((920, 25), (10, 200), slider_size = 25, style = "round")
    button_slider_2 = Slider((650, 37), (200, 10), slider_size = (51, 25), style = "square", slider_feature_text = "|||")

    button_dd = DropdownBox((650, 100), (200, 50), options = ["a", "b", "c", "d"], scroll_bar = 2, display_length = 3.2)

    running = True
    while running:
        #Handle the inputs / events for the program
        Handle_input()
        if button_quit.clicked:
            running = False
        if button_count.clicked:
            button_count.text = str(button_count.value)

        #Perform updates on the Buttons
        Buttons.Update(all)
        Draw_screen(screen)
        #Let pygame's framerate limiter do its thing of limiting the framerate to the framerate we set
        clock.tick(framerate)


def Handle_input():
    """
    Handles the input events.
    """
    global running
    for event in pygame.event.get():
        #Let the buttons handle the Event
        Buttons.Event(event)
        if Buttons.input_processed:
            #If a Button accepted the Event, don't process it further
            continue
        elif event.type == pygame.QUIT:
            running = False
            return
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                return
    return


def Draw_screen(screen):
    """
    Re-draws the screen.
    """
    #Draw the background
    screen.fill((63, 127, 191))
    #Draw the buttons
    Buttons.Draw(screen)
    #Update the frame buffer to display the new Surface
    pygame.display.flip()
    #Done
    return

if __name__ == "__main__":
    try:
        Main()
    except Exception:
        raise
    finally:
        pygame.quit()
        pass
