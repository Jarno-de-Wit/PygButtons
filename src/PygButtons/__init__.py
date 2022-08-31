import os
import sys
#Exctract the path of this file
path = os.path.dirname(__file__)
#Insert the path to the start of sys.path, to make sure importing goes correctly at all times
sys.path.insert(0, path)

from Base import Buttons

from Button import Button
from TextBox import TextBox
from Slider import Slider
from DropdownBox import DropdownBox
from Text import Text

#Remove the path that has been added as to not contaminate the namespace
sys.path.remove(path)

#Delete the path variable again to prevent accidental namespace cluttering
del path
