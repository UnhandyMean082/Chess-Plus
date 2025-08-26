"""The overall chess game, which handles the screen and game state.

This module contains the Game class, and is to be used within a basic pygame game loop.
In this case, it is specifically meant to be imported by the main module to allow the game to be played.

Classes:
    Game: The class which updates the screen and handles the game states.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import pygame as pg

import Menu as men
import PlayGame as pla


# Create the game class
class Game:
    """The overall chess game, which stores and updates the game state and updates the screen.
    
    This class stores an object of each game state, created using the classes in the Menu and PlayGame modules.
    It also handles resetting and switching between the two while being updated every cycle of the game loop.

    Constructor:
        __init__(screenSize (pg.Vector2)): Initialise self and attributes.

    Public methods:
        update: Updates the current state class and screen image.

    Attributes:
        __state (bool): False means the game is in the menu state and True means it is in play game.
        __screenSize (pg.Vector2): The (x, y) size, in pixels, of the screen.
        __menu (men.Menu): The menu state object.
        __playGame (pla.PlayGame): The play game state object.
    """

    # Initialise an object of this class when called
    def __init__(self, screenSize: pg.Vector2) -> None:
        logger.info("Game created")
        # Define attributes
        self.__state: bool = False
        self.__screenSize: pg.Vector2 = screenSize
        self.__menu: men.Menu = men.Menu(self.__screenSize)
        self.__playGame: pla.PlayGame = pla.PlayGame(self.__screenSize)

    def __swapFromMenu(self):
        """Check for, and if so, action a swap from the menu to play game state."""
        # If the menu signals to switch state, change the state and reset the play game state
        if self.__menu.getPlayGame():
            logger.info("Menu to game state")
            self.__state = True
            self.__menu.playGameFalse()
            self.__playGame.restart()
            self.__playGame.setOpp(self.__menu.getOpponent())
            self.__menu.opponentFalse()

    def __swapFromPlayGame(self):
        """Check for, and if so, action a swap from the play game to menu state."""
        # If the play game state signals to switch state, change the state
        if self.__playGame.getGameOver():
            logger.info("Game to menu state")
            self.__state = False
            self.__playGame.gameOverFalse()

    def update(self, events: list, screen: pg.surface.Surface) -> None:
        """Handle the updating and switching of game states, as well as drawing their image onto the screen.

        Args:
            events (list): The event queue of the current cycle.
            screen (pg.surface.Surface): The screen that will be displayed in the current cycle.

        Kwargs:
            None
        
        Returns:
            None
        """
        # Decide which set of state and swapper are used based on the current state
        if self.__state:
            state = self.__playGame
            swapper = self.__swapFromPlayGame
        else:
            state = self.__menu
            swapper = self.__swapFromMenu

        # Update the current state and check for any changes
        screen.blit(state.update(events, pg.mouse.get_pos(), pg.mouse.get_pressed()[0]), (0, 0))
        swapper()
