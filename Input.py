"""A pygame implementation of buttons and switches for GUI-based programs.

This module contains the Input abstract base class and the Button and Switch classes which inherit from it,
and is to be used within the PlayGame, Board and Menu modules for user input handling,
and the classes in the Piece module inherit from the Switch class. These are standard buttons and switches
whose dimensions and images in each state must be passed upon creation. They inherit from the pygame Sprite class.

Classes:
    Input: The abstract base class from which the other two inherit.
    Button: An interactable screen-object with two states: pressed and released.
    Switch: An interactable screen-object with many states: a pressed state, and multiple released states which are cycled through upon press and release.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import pygame as pg


# Create the input abstract class
class Input(pg.sprite.Sprite):
    """The abstract base class which dictates the overall behaviour of the Button and Switch.

    Defines the shared basics, such as all shared accessors and mutators, as well as defining shared attributes and containing the abstract update class.
    
    Constructor:
        __init__(size (pg.Vector2), pos (pg.Vector2), idle (pg.surface.Surface | list), hovering (pg.surface.Surface), clicked (pg.surface.Surface)): Initialise self and attributes.

    Public Methods:
        getPos: Accessor method for the _pos attribute.
        setPos: Mutator method for the _pos attribute.
        updateRect: Mutator method for the rect attribute to update it based on the _pos and _size attributes.
        getPressed: Accessor method for the _pressed attribute.
        pressedFalse: Mutator method to set the _pressed attribute to False.
        setImage: Abstract method to select the image attribute.
        update: Abstract method for updating the input method itself.

    Attributes:
        _size (pg.Vector2): The size of the input method - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the input method, used for detecting whether the mouse position intersects with the input method.
        rect (pg.Rect): The rect object holding the size and position of the input method.
        _pressed (bool): Whether the input method has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the input method for every state.
        image (pg.surface.Surface): The current image of the input method.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, pos: pg.Vector2, idle: pg.surface.Surface | list, hovering: pg.surface.Surface, clicked: pg.surface.Surface) -> None:
        logger.info(f"{type(self)} created")
        super().__init__()
        # Define attributes
        self._size: pg.Vector2 = size
        self._pos: pg.Vector2 = pos
        self.rect: pg.Rect = pg.Rect(self._pos, self._size)
        self._pressed: bool = False
        self._images: dict = {
            "idle": idle,
            "hovering": hovering,
            "clicked": clicked
        }
        if isinstance(self._images["idle"], list):
            self.image: pg.surface.Surface = self._images["idle"][0]
        else:
            self.image: pg.surface.Surface = self._images["idle"]

    def getPos(self) -> pg.Vector2:
        """Return the _pos attribute."""
        return self._pos
    
    def setPos(self, newPos: pg.Vector2) -> None:
        """Set the _pos attribute to a new value."""
        self._pos = newPos
        self.updateRect()

    def updateRect(self) -> None:
        """Update the rect attribute based on the position and size attributes."""
        self.rect = pg.Rect(self._pos, self._size)

    def getPressed(self) -> bool:
        """Return the _pressed attribute."""
        return self._pressed
    
    def pressedFalse(self) -> None:
        """Set the _pressed attribute to False."""
        self._pressed = False

    def setImage(self, state: str) -> None:
        """Abstract method to select the image."""
        pass

    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> None:
        """Abstract update method."""
        pass


# Create the button class
class Button(Input):
    """A button with two states - pressed and not pressed.

    Overwrites the method to set the image based on a parameter and the update method to function as a typical button.
    
    Constructor:
        __init__(size (pg.Vector2), pos (pg.Vector2), idle (pg.surface.Surface), hovering (pg.surface.Surface), clicked (pg.surface.Surface)): Initialise self and attributes.

    Public Methods:
        getPos: Accessor method for the _pos attribute.
        setPos: Mutator method for the _pos attribute.
        updateRect: Mutator method for the rect attribute to update it based on the _pos and _size attributes.
        getPressed: Accessor method for the _pressed attribute.
        pressedFalse: Mutator method to set the _pressed attribute to False.
        setImage: Mutator method for the image attribute to set the image based on a state parameter.
        update: Process whether the button has been clicked or not, and use this to decide its _pressed and image attributes.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
    """
    
    # Overwrite the setImage method
    def setImage(self, state: str) -> None:
        """Set the image attribute to an image from the images dictionary depending on state."""
        self.image = self._images[state]

    # Overwrite the update method
    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> None:
        """Update the _pressed and image attributes based on mouse position, mouse pressed, and the events queue.

        Use the events queue, mouse position and mouse pressed parameters to decide whether the button has been pressed,
        as well as which state it should appear in, out of possible options idle, hovering and clicked.

        Args:
            events (list): The current frame's events queue.
            mosePos (pg.Vector2): The position of the mouse as a vector.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed down.

        Kwargs:
            None

        Returns:
            None
        """
        # If the mouse is hovering over the button, its state should either be clicked or hovering
        if self.rect.collidepoint(mousePos):
            # If the mouse is clicked, change state, and if it is released, assign the pressed attribute to True
            for event in events:

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        self.setImage("clicked")
                        return
                    
                elif event.type == pg.MOUSEBUTTONUP and self.image == self._images["clicked"]:
                    if event.button == pg.BUTTON_LEFT:
                        self._pressed = True

            # Ensure that if the mouse button is held down, the state does not just default back to hovering
            if leftMousePressed and self.image == self._images["clicked"]:
                return
            self.setImage("hovering")
            return
        
        # If the button was clicked but then the player moved their mouse off the button, ensure that it stays in the clicked state untill they release the mouse still
        if self.image == self._images["clicked"]:
            for event in events:
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == pg.BUTTON_LEFT:
                        self._pressed = True

        # If either the mouse is depressed or the previous state was not clicked, change the state to idle
        if not (leftMousePressed and self.image == self._images["clicked"]):
            self.setImage("idle")


# Create the switch class
class Switch(Input):
    """A switch with two state categories - pressed and not pressed, where not pressed can consist of a list of states.

    Overwrites the method to set the image based on a parameter and the update method to function as a typical switch.
    Adds methods to get and cycle the state attribute.
    
    Constructor:
        __init__(size (pg.Vector2), pos (pg.Vector2), idle (pg.surface.Surface | list), hovering (pg.surface.Surface), clicked (pg.surface.Surface)): Initialise self and attributes.

    Public Methods:
        getPos: Accessor method for the _pos attribute.
        setPos: Mutator method for the _pos attribute.
        updateRect: Mutator method for the rect attribute to update it based on the _pos and _size attributes.
        getPressed: Accessor method for the _pressed attribute.
        pressedFalse: Mutator method to set the _pressed attribute to False.
        setImage: Mutator method for the image attribute to set the image based on a state parameter.
        update: Process whether the button has been clicked or not, and use this to decide its _pressed and image attributes.
        getState: Accessor method for the _state attribute.
        cycleState: Mutator method to cycle the state attribute based on the length of the idle images value in the _images dictionary.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, pos: pg.Vector2, idle: pg.surface.Surface | list, hovering: pg.surface.Surface, clicked: pg.surface.Surface) -> None:
        super().__init__(size, pos, idle, hovering, clicked)
        # Define attribute
        self._state: int = 0
    
    # Overwrite the setImage method
    def setImage(self, state: str) -> None:
        """Set the image attribute to an image from the images dictionary depending on state."""
        self.image = self._images[state]
        if isinstance(self.image, list):
            self.image = self.image[self._state]

    def getState(self) -> int:
        """Return the _state attribute."""
        return self._state
    
    def cycleState(self) -> None:
        """Increment the _state attribute and then set it to zero if it exceeds the length of the idle images value."""
        self._state += 1
        if self._state == len(self._images["idle"]):
            self._state = 0

    # Overwrite the update method
    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> None:
        """Update the _pressed, image and _state attributes based on mouse position, mouse pressed, and the events queue.

        Use the events queue, mouse position and mouse pressed parameters to decide whether the button has been pressed,
        as well as which state it should appear in, out of possible options idle, hovering and clicked.
        Also, cycle the state for the idle image every time the switch is released from being pressed.

        Args:
            events (list): The current frame's events queue.
            mosePos (pg.Vector2): The position of the mouse as a vector.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed down.

        Kwargs:
            None

        Returns:
            None
        """
        # Define an anonymous function which dictates how the image is checked against being clicked
        clicked = lambda image, clickedImage: image == clickedImage if isinstance(clickedImage, pg.surface.Surface) else image in clickedImage
        # If the mouse is hovering over the switch, its state should either be clicked or hovering
        if self.rect.collidepoint(mousePos):
            # If the mouse is clicked, change and cycle state, and if it is released, assign the pressed attribute to True
            for event in events:

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        self.setImage("clicked")
                        self.cycleState()
                        self._pressed = True
                        return
                    
                elif event.type == pg.MOUSEBUTTONUP and clicked(self.image, self._images["clicked"]):
                    if event.button == pg.BUTTON_LEFT:
                        self._released = True

            # Ensure that if the mouse button is held down, the state does not just default back to hovering
            if leftMousePressed and clicked(self.image, self._images["clicked"]):
                return
            self.setImage("hovering")
            return
        
        # If the switch was clicked but then the player moved their mouse off the switch, ensure that it stays in the clicked state untill they release the mouse still
        if clicked(self.image, self._images["clicked"]):
            for event in events:
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == pg.BUTTON_LEFT:
                        self._released = True
                        
        # If either the mouse is depressed or the previous state was not clicked, change the state to idle
        if not (leftMousePressed and clicked(self.image, self._images["clicked"])):
            self.setImage("idle")
