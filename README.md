# PygButtons
A module made to help in creating a UI by simplifying the creation and handling of basic UI objects (such as Buttons).

## Contents
- [Installation](#Installation)
- [Dependencies](#Dependencies)
- [Usage](#Usage)
- [Support](#Support)

## Installation
To install, run: `pip install pygbuttons`

## Dependencies
- Python => 3.6
- Pygame => 2.0.1

## Usage
To use the Buttons in a program, it is recommended to perform the following steps:
- Setup
  1. Import the module / the contents of the module.
  2. Set the settings for the Buttons module (framerate, scroll factor, scaling limits) where appropriate
  3. Create the required Buttons
- While running
  4. Pass all (relevant) Pygame.Events to the active Buttons in the input loop
  5. Update the Buttons with information which is not event driven (e.g. cursor position)
  6. Draw the Buttons to the active screen
  7. Repeat

Getting an output from a Button can be done either by binding a function to the Button (which is then automatically executed when a certain action takes place), or by polling the Buttons value / status.

For a practical implementation, see the [example.py](https://github.com/Jarno-de-Wit/PygButtons/blob/main/Example.py) file.

## Support
For support / issues, please visit the issue tracker on [GitHub](https://github.com/Jarno-de-Wit/PygButtons/issues).

Source code available at: https://github.com/Jarno-de-Wit/PygButtons
