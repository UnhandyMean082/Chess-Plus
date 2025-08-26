"""A slightly custom stack ADT.

This module contains the Stack class, and is to be used within the PlayGame module.
It is similar to a regular stack with the key difference being that if an entity is pushed
while the stack is at its maximum size, the oldest entity is removed to maintain size.

Classes:
    Stack: The custom stack class.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger

import Frame as fme


# Create the stack class
class Stack:
    """The custom stack, which cycles if pushed to at max size.
    
    This stack is meant to facilitate the function of the undo button, meaning that it stores all entities of previous gamestates
    up till a certain point, before removing them to reduce the space complexity as gamestate frames are not that small.

    Constructor:
        __init__(maxSize (int)): Initialise self and attributes.

    Public methods:
        getMaxSize: Accessor method for the __maxSize attribute.
        setMaxSize: Mutator method for the __maxSize attribute.
        getList: Accessor method for the __list attribute.
        isEmpty: Return whether the length of the __list attribute is 0.
        isFull: Return whether the length of the __list attribute is equal to the max length.
        push: Append an entity to the stack, removing any entities from the bottom where necessary.
        peek: Return the entity at the top of the stack.
        pop: Delete and return the entity at the top of the stack.

    Attributes:
        __maxSize (int): The maximum size of the stack.
        __list (list): The list of previous gamestate frames.
    """
    
    # Initialise an object of this class when called
    def __init__(self, maxSize: int):
        logger.info("Stack created")
        # Define attributes
        self.__maxSize: int = maxSize
        self.__list: list = []

    def getMaxSize(self) -> int:
        """Return the __maxSize attribute."""
        return self.__maxSize
    
    def setMaxSize(self, newMaxSize: int) -> None:
        """Set the __maxSize attribute."""
        self.__maxSize = newMaxSize
    
    def getList(self) -> list:
        """Return the __list attribute."""
        return self.__list
    
    def isEmpty(self) -> bool:
        """Return whether the __list attribute is empty."""
        return len(self.__list) == 0

    def isFull(self) -> bool:
        """Return whether the __list attribute's length is equal to the maximum size."""
        return len(self.__list) == self.__maxSize
    
    def push(self, newItem) -> None:
        """Append an entity to the stack."""
        logger.debug("Pushed to stack")
        self.__list.append(newItem)
        if len(self.__list) > self.__maxSize:
            while len(self.__list) != self.__maxSize:
                del(self.__list[0])

    def peek(self) -> None | fme.Frame:
        """Return the entity at the top of the stack."""
        if len(self.__list) != 0:
            return self.__list[-1]

    def pop(self) -> None | fme.Frame:
        """Remove the entity at the top of the stack and return it."""
        logger.debug("Popped from stack")
        if len(self.__list) != 0:
            return self.__list.pop()
    