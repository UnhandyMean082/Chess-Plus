"""The menu of a chess game, which allows the user to play and choose their opponent or quit.

This module contains the Menu class, and is to be used within the Game class in the Game module.
It displays a main menu screen, with the title of the game and
both a play button, which signals the Game class to switch to the play game state,
and a quit button, which closes the program.
There is also an opponent selection screen, where the player decides whether to play against a human or the computer.

Classes:
    Menu: The class which displays the game's menu and handles its buttons.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import os
import pygame as pg

import Input as inp


# Create the menu class
class Menu:
    """The chess game menu, which displays the menu screen and handles switching state and quitting.
    
    This class displays the coloured background of the game's main menu, as well as its title,
    and contains two Button objects from the Input module, one of which signals the state switch,
    the other of which quits the program, and both of which are updated every time this class is.

    Constructor:
        __init__(screenSize (pg.Vector2)): Initialise self and attributes, and create images and filters.

    Public Methods:
        getPlayGame: Accessor method for the __playGame attribute.
        playGameFalse: Mutator method to set the __playGame attribute to False.
        update: Update the buttons, handle their outputs and draw the menu screen.

    Attributes:
        __playGame (bool): False means the game is in the menu state and True means it should switch to play game.
        __screenSize (pg.Vector2): The (x, y) size, in pixels, of the screen.
        __image (pg.surface.Surface): The main menu image which is to be drawn on the display screen.
        __title (pg.surface.Surface): The game name image.
        __vs (pg.surface.Surface): The VS image.
        __state (bool): False means the menu is the in the main state, and True means it is in the opponent selector.
        __mainButtons (pg.sprite.Group): A sprite group containing both buttons which will be contained by the main menu.
        __oppButtons (pg.sprite.Group): A sprite group containing the buttons which will be contained by the opponent selector.
        __transOffset (int): The offset of buttons and logo during the transition animation.
        __opponent (bool): False if the opponent is a human and True if it is the computer.
        __playGameButton (inp.Button): The button which controls state change to play game.
        __exitButton (inp.Button): The button which controls quitting the program.
        __humanButton (inp.Button): The button to play the game against another human.
        __computerButton (inp.Button): The button to play the game against the computer.
        __backButton (inp.Button): The button to go back to the main menu.
    """
    
    # Initialise an object of this class when called
    def __init__(self, screenSize: pg.Vector2):
        logger.info("Menu created")
        # Define attributes
        self.__playGame: bool = False
        self.__screenSize: pg.Vector2 = screenSize
        self.__image: pg.surface.Surface = pg.surface.Surface(self.__screenSize)
        self.__title: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Title.png").convert_alpha(), self.__screenSize.elementwise() / pg.Vector2(4, 10/3))
        self.__vs: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\VS.png").convert_alpha(), self.__screenSize.elementwise() / pg.Vector2(4, 10/3))
        self.__state: bool = False
        self.__mainButtons: pg.sprite.Group = pg.sprite.Group()
        self.__oppButtons: pg.sprite.Group = pg.sprite.Group()
        self.__transOffset: int = 0
        self.__opponent = False

        # Define the variables for changing the surfaces
        mainButtonSize = self.__screenSize.elementwise() / pg.Vector2(2, 5)
        oppButtonSize = mainButtonSize / 1.5
        buttonDarkener = pg.surface.Surface(mainButtonSize, pg.SRCALPHA)
        buttonDarkener.fill((100, 100, 100))

        # Create the buttons based on previously defined surfaces
        playGameButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Play Button.png").convert_alpha(), mainButtonSize)
        playGameButtonHovering = playGameButtonIdle.copy()
        playGameButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        playGameButtonClicked = playGameButtonHovering.copy()
        playGameButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__playGameButton: inp.Button = inp.Button(mainButtonSize, (self.__screenSize.elementwise() / pg.Vector2(4, 2.5)), playGameButtonIdle, playGameButtonHovering, playGameButtonClicked)
        self.__mainButtons.add(self.__playGameButton)
        exitButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Exit Button.png").convert_alpha(), mainButtonSize)
        exitButtonHovering = exitButtonIdle.copy()
        exitButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        exitButtonClicked = exitButtonHovering.copy()
        exitButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__exitButton: inp.Button = inp.Button(mainButtonSize, (self.__screenSize.elementwise() / pg.Vector2(4, 13/9)), exitButtonIdle, exitButtonHovering, exitButtonClicked)
        self.__mainButtons.add(self.__exitButton)
        humanButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Human Button.png").convert_alpha(), oppButtonSize)
        humanButtonHovering = humanButtonIdle.copy()
        humanButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        humanButtonClicked = humanButtonHovering.copy()
        humanButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__humanButton: inp.Button = inp.Button(oppButtonSize, (self.__screenSize.elementwise() / pg.Vector2(3, 2.5)), humanButtonIdle, humanButtonHovering, humanButtonClicked)
        self.__oppButtons.add(self.__humanButton)
        computerButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Computer Button.png").convert_alpha(), oppButtonSize)
        computerButtonHovering = computerButtonIdle.copy()
        computerButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        computerButtonClicked = computerButtonHovering.copy()
        computerButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__computerButton: inp.Button = inp.Button(oppButtonSize, (self.__screenSize.elementwise() / pg.Vector2(3, 1.7)), computerButtonIdle, computerButtonHovering, computerButtonClicked)
        self.__oppButtons.add(self.__computerButton)
        backButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Back Button.png").convert_alpha(), oppButtonSize)
        backButtonHovering = backButtonIdle.copy()
        backButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        backButtonClicked = backButtonHovering.copy()
        backButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__backButton: inp.Button = inp.Button(oppButtonSize, (self.__screenSize.elementwise() / pg.Vector2(3, 1.3)), backButtonIdle, backButtonHovering, backButtonClicked)
        self.__oppButtons.add(self.__backButton)

    def getPlayGame(self) -> bool:
        """Return the __playGame attribute."""
        return self.__playGame
    
    def playGameFalse(self) -> None:
        """Set the __playGame attribute to False."""
        self.__playGame = False

    def getOpponent(self) -> bool:
        """Return the __opponent attribute."""
        return self.__opponent
    
    def opponentFalse(self) -> None:
        """Set the __opponent attribute to False."""
        self.__opponent = False
    
    def __stateTrans(self) -> pg.surface.Surface:
        """Transitions the screen from the main menu to the opposition selection screen.

        Depending on the current state, this method moves the main menu image in such a way
        as to end up showing the image of the target state. The opponent selector menu will always appear the same,
        as the main menu is the only thing whose appearance change, so this will be drawn first no matter what.
        Then, depending on the target state, the main menu's parts are either moved together or apart.
        
        Args:
            None

        Kwargs:
            None
            
        Returns:
            Returns the image of the current frame of the changing animation.
        """
        logger.debug(f"Menu state transition to {self.__state}")
        # Define the method of change depending on the target state
        if self.__state:
            offset = self.__transOffset
        else:
            offset = self.__screenSize.y - self.__transOffset

        # Draw the screen which is underneath
        self.__image.fill("gold1")
        # Draw a trapezium going from 3/4 down the screen on the left to 1/4 down on the right
        pg.draw.polygon(self.__image, "cornflowerblue", [pg.Vector2(0, (self.__screenSize.y * 0.75)), pg.Vector2(0, self.__screenSize.y), self.__screenSize, pg.Vector2(self.__screenSize.x, (self.__screenSize.y * 0.25))])
        self.__image.blit(self.__vs, self.__screenSize.elementwise() / pg.Vector2(8/3, 20))
        self.__oppButtons.draw(self.__image)

        # Draw the above screen separating until it is not there anymore
        # Top half
        # Draw a trapezium going from 3/4 down the screen on the left to 1/4 down on the right moved based on the offset
        pg.draw.polygon(self.__image, "chartreuse1", [pg.Vector2(0, 0), pg.Vector2(0, ((self.__screenSize.y * 0.75) - offset)), pg.Vector2(self.__screenSize.x, ((self.__screenSize.y * 0.25) - offset)), pg.Vector2(self.__screenSize.x, 0)])
        self.__image.blit(self.__title, (self.__screenSize.elementwise() / pg.Vector2(8/3, 20)) - pg.Vector2(0, offset))
        self.__playGameButton.setPos(pg.Vector2(self.__screenSize.x // 4, (self.__screenSize.y / 2.5) - offset))

        # Bottom half
        # Draw a trapezium going from 3/4 down the screen on the left to 1/4 down on the right moved based on the offset
        pg.draw.polygon(self.__image, "coral1", [pg.Vector2(0, ((self.__screenSize.y * 0.75) + offset)), pg.Vector2(0, self.__screenSize.y), self.__screenSize, pg.Vector2(self.__screenSize.x, ((self.__screenSize.y * 0.25) + offset))])
        self.__exitButton.setPos(pg.Vector2(self.__screenSize.x // 4, (self.__screenSize.y / (13/9)) + offset))

        # Draw the buttons whose positions have been updated
        self.__mainButtons.draw(self.__image)

    def __mainReset(self) -> None:
        """Reset the main menu state to base settings."""
        self.__state = False
        self.__playGameButton.setPos(self.__screenSize.elementwise() / pg.Vector2(4, 2.5))
        self.__exitButton.setPos(self.__screenSize.elementwise() / pg.Vector2(4, 13/9))
        self.__transOffset = 0

    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> pg.surface.Surface:
        """Draw the main screen, title card, and update and then draw the relevant buttons.

        Process the user inputs, update then draw the relevant buttons, executing their functionality if any of them are pressed,
        handle the drawing of the screen image regardless of state and check whether, and if so handle, a state transition animation.
        
        Args:
            events (list): The event queue of the current cycle.
            mousePos (pg.Vector2): The current mouse cursor position.
            leftMousePressed (bool): Whether the left mouse button is currently being pressed.

        Kwargs:
            None

        Returns:
            Returns the overall menu image.
        """
        # Check whether there is currently a state transition happening
        if self.__transOffset != 0:
            self.__transOffset = min(self.__screenSize.y, int((self.__transOffset + 1) * 1.25))
            self.__stateTrans()
            if self.__transOffset == self.__screenSize.y:
                self.__transOffset = 0

        # Check whether the state is currently main menu or opponent choosing
        elif self.__state:
            
            # Update the opposition selection buttons
            self.__oppButtons.update(events, mousePos, leftMousePressed)

            # Handle the next action based on which (if any) button was pressed
            # Play the game if either of these two are pressed, but set the opponent differently
            if self.__humanButton.getPressed():
                self.__playGame = True
                self.__mainReset()
                self.__humanButton.pressedFalse()
            elif self.__computerButton.getPressed():
                self.__opponent = True
                self.__playGame = True
                self.__mainReset()
                self.__computerButton.pressedFalse()

            # Return to the main screen if back is pressed
            elif self.__backButton.getPressed():
                self.__state = False
                self.__transOffset = 1
                self.__backButton.pressedFalse()
                
            # Set the menu image
            self.__image.fill("gold1")
            # Draw a trapezium going from 3/4 down the screen on the left to 1/4 down on the right
            pg.draw.polygon(self.__image, "cornflowerblue", [pg.Vector2(0, (self.__screenSize.y * 0.75)), pg.Vector2(0, self.__screenSize.y), self.__screenSize, pg.Vector2(self.__screenSize.x, (self.__screenSize.y * 0.25))])
            self.__image.blit(self.__vs, self.__screenSize.elementwise() / pg.Vector2(8/3, 20))
            self.__oppButtons.draw(self.__image)

        else:
            # Update the main menu buttons
            self.__mainButtons.update(events, mousePos, leftMousePressed)

            # Handle the next action based on which (if any) button was pressed
            if self.__playGameButton.getPressed():
                self.__state = True
                self.__transOffset = 1
                self.__playGameButton.pressedFalse()

            elif self.__exitButton.getPressed():
                quit("Thanks for playing!")
                
            # Set the menu image
            self.__image.fill("chartreuse1")
            # Draw a trapezium going from 3/4 down the screen on the left to 1/4 down on the right
            pg.draw.polygon(self.__image, "coral1", [pg.Vector2(0, (self.__screenSize.y * 0.75)), pg.Vector2(0, self.__screenSize.y), self.__screenSize, pg.Vector2(self.__screenSize.x, (self.__screenSize.y * 0.25))])
            self.__image.blit(self.__title, self.__screenSize.elementwise() / pg.Vector2(8/3, 20))
            self.__mainButtons.draw(self.__image)
        return self.__image
