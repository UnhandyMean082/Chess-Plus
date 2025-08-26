"""The ADT which stores a chess gamestate.

This module contains the Frame class, and is to be used within the PlayGame and Stack modules.
It holds all aspects of the current gamestate, namely a virtual board and the dead lists.

Classes:
    Frame: The current gamestate storage ADT.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import pygame as pg

import Board as boa


# Create the frame class
class Frame:
    """The gamestate storage device.
    
    This class stores every useful element of a gamestate to allow for it to be returned to upon usage of the undo button.

    Constructor:
        __init__(board (boa.VirtualBoard), dead (list)): Initialise self and attributes.

    Public methods:
        getBoard: Accessor method for the __board attribute.
        getDead: Accessor method for the __dead attribute.
        getAll: Accessor method for both attributes.

    Attributes:
        __board (list): Contains the board list from the Board class.
        __dead (list): Contains the dead pieces list from the PlayGame class.
    """
    
    # Initialise an object of this class when called
    def __init__(self, board: boa.VirtualBoard, dead: list):
        logger.info("Frame created")
        # Define attributes
        self.__board: boa.VirtualBoard = board
        self.__dead: list = dead

    def getBoard(self) -> list:
        """Return the __board attribute."""
        return self.__board
    
    def getDead(self) -> list:
        """Return the __dead attribute."""
        return self.__dead
    
    def getAll(self) -> tuple:
        """Return a tuple of both attributes."""
        logger.debug("Frame retrieved")
        return self.__board, self.__dead
    