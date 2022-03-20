import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"


from Buttons2 import *


import pygame
import math

def Main():
    framerate = 30
    Buttons.framerate = framerate
    pygame.init()
    pygame.key.set_repeat(500, 50)
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    running = True
    global a, b, c, d, e, f, g, h, i, j, k
    #a = DropdownBox((100, 100), (200, 50), display_length = 3, options = ["1", "2", "3", "4"])
    a = Button((100, 25 ), (200, 50), text = "0", mode = "Count")#, background = Arrow_bg, accent_background = None, func_data = ((255, 255, 255), (220, 220, 220)))
    b = Button((100, 100), (200, 50), text = "Toggle", mode = "Toggle")
    c = Button((100, 175), (200, 50), text = "Hold", mode = "Hold")
    d = Button((600, 450), (100, 50), text = "Quit")#, border = ((63, 63, 63), 1, 2))
    e = Button((100, 400), (200, 50), text = "Drag", mode = "Hold", dragable = (True, True), limits = (100, 550, 400, 600))#, snap = ((200,), (), 40))
    f = TextBox((400, 25),(200, 50), hint = "Type here")
    g = Slider((400, 125), (200, 10), slider_size = (51, 25), style = "square", slider_feature_text = "|||")
    h = TextBox((400, 174), (200, 50))
    i = Slider((650, 25), (10, 200), slider_size = 25, style = "round")
    j = Text((700, 25), (200, 100), text = 2 * "How How How How How How How How How", border = ((10, 10, 10), 1, 0), scroll_bar = 2)
    k = DropdownBox((700, 225), (200, 50), options = ["a", "b", "c", "d"], scroll_bar = 2)

    #Buttons.Scale(1.2)
    #Buttons.Scale(0.5)
    #Buttons.Scale(0.9)
    while running:
        running = Handle_input()
        Draw_screen(screen)
        if a.clicked:
            a.text = str(a.value)
        if d.clicked:
            running = False
        if b.clicked:
            g.Set_slider_primary(51 + (149 * b.value))
            i.value_range = (0, b.value)
            #i.Set_slider_primary(100)
            #g.Set_range(0, 5)
            pass
            #Buttons.Scale(0.95)
        if c.clicked:
            a.value = 0
            a.text = 0
            pass
            #Buttons.Scale(1.0526315789473684)
        if g.moved:
            #h.text = f"{g.value:.2f}"
            print(f"{g.value:.2f}", file = j)
        if i.moved:
            pass
            #j.text = f"Value is now a grand total of {i.value:.2f}"
        Buttons.Update(all)
        clock.tick(framerate)

def Handle_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return(False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return(False)
        Buttons.Event(event)
                
    return(True)

def Draw_screen(screen):
    scr_rect = screen.get_rect()
    scr_surf = pygame.Surface(scr_rect.size)
    scr_surf.fill((63, 127, 191))
    screen.blit(scr_surf, scr_rect)
    pygame.draw.rect(screen, (127, 127, 127), ((100, 400),(450, 200)) )
    Buttons.Draw(screen)
    pygame.display.flip()
    return()

if __name__ == "__main__" and True:
    try:
        Main()
    except Exception as e:
        raise(e)
    finally:
        pygame.quit()
        pass
