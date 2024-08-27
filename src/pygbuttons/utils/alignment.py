import pygame

def align(rect, limits, pos):
    """
    Creates an aligned Rect, with the given size when placed onto a surface with size 'limit_size'.
    Functionally just a wrapper around AlignX and AlignY.

    rect: A pygame.Rect object or size tuple to be aligned.
    limits: A pygame.Rect object or size tuple to which the rect should be aligned.
    pos: The text containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
    """
    if isinstance(limits, pygame.Rect):
        #If the provided 'limit_size' is a Rect, extract its size
        limits = [(limits.left, limits.right), (limits.top, limits.bottom)]
    pos = pos.lower()

    rect = alignX(rect, limits[0], pos)
    rect = alignY(rect, limits[1], pos)

    return rect

def alignX(rect, limits, pos):
    """
    Creates a rectangle that is correctly aligned horizontally.

    rect: A pygame.Rect object or size tuple to be aligned.
    limits: A pygame.Rect object or size tuple (left, right) to which the rect should be aligned.
    pos: The (text) containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
    """
    if isinstance(limits, (float, int)):
        left = 0
        right = limits
    elif isinstance(limits, pygame.Rect):
        left = limits.left
        right = limits.right
    else:
        left = limits[0]
        right = limits[1]

    # Create a pygame.Rect object if required
    if isinstance(rect, pygame.Rect):
        # If the object is already a pygame.Rect, there is nothing to do
        pass
    elif isinstance(rect, int):
        #If only an int (width) is given, create a zero height corresponding pygame.Rect
        rect = pygame.Rect((0, 0), (rect, 0))
    else:
        #If the provided 'rect' argument is not a rect, but just a tuple containing a size, create a new Rect
        rect = pygame.Rect((0, 0), rect)
    pos = pos.lower()

    if "left" in pos:
        rect.left = left
    elif "right" in pos:
        rect.right = right
    else:
        rect.centerx = (left + right) // 2
    return rect

def alignY(rect, limits, pos):
    """
    Creates a rectangle that is correctly aligned vertically.

    rect: A pygame.Rect object or size tuple to be aligned.
    limit_size: A pygame.Rect object or size tuple to which the rect should be aligned.
    pos: The (text) containing the information on how the rect should be aligned (e.g. "top", "midleft", etc.). Defaults to centered if no alignment info is given for an axis, or the given info is invalid.
    """
    if isinstance(limits, (float, int)):
        top = 0
        bottom = limits
    elif isinstance(limits, pygame.Rect):
        top = limits.top
        bottom = limits.bottom
    else:
        top = limits[0]
        bottom = limits[1]

    # Create a pygame.Rect object if required
    if isinstance(rect, pygame.Rect):
        # If the object is already a pygame.Rect, there is nothing to do
        pass
    elif isinstance(rect, int):
        #If only an int (height) is given, create a zero width corresponding pygame.Rect
        rect = pygame.Rect((0, 0), (0, rect))
    else:
        #If the provided 'rect' argument is not a rect, but just a tuple containing a size, create a new Rect
        rect = pygame.Rect((0, 0), rect)
    pos = pos.lower()

    if "top" in pos:
        rect.top = top
    elif "bottom" in pos:
        rect.bottom = bottom
    else:
        rect.centery = (top + bottom) // 2
    return rect
