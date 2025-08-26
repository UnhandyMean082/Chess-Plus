"""All of the pieces and their assosciated methods within a chess game.

This module contains the Piece abstract base class and classes of each chess piece which inherit from it,
and is to be used within the PlayGame and Board modules for move generation and piece storage.
These all inherit from the Switch class in the Input module, since they function similarly to switches.

Classes:
    Piece: The abstract base class from which the other six inherit.
    King: The chess king, which additionally stores the _movedEver and _threatened attributes, and whose value is 5.
    Queen: The chess queen, whose value is 4.
    Bishop: The chess bishop, whose value is 3.
    Knight: The chess knight, whose value is 2.
    Rook: The chess rook, which additionally stores the _movedEver attributes, and whose value is 1.
    Pawn: The chess pawn, which additionally stores the _movedEver and _doubleMoved attributes, and whose value is 0.

Functions:
    onBoard: Return whether or not a square, given in vector form, is on the board or not.
    infDist: Return a list of all possible moves based on an unlimited distance move.
    updateRegularMoves: Return a list of all possible moves which can be made by any non-pawn pieces.
    updateCastle: Return a list containing the possible castle moves (if any)
    freeCheck: Return whether or not an input list of board squares are all free.
    updatePawnMoves: Return a list containing all possible moves which can be made by a pawn.
    decodeInt: Decode an integer representation of a piece back into, and then return, a copy of the original piece.
"""

# Import modules and libraries
from loguru import logger
import os
import pygame as pg

import Input as inp


# Create the piece abstract class
class Piece(inp.Switch):
    """The abstract base class which dictates the overall behaviour of all piece classes.

    Defines the shared basics, such as all shared accessors and mutators, as well as defining shared attributes
    and containing other useful shared methods such as encoding, updating and moving the pieces.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), idle (pg.surface.Surface), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Mutator method for the _legalMoves attribute to update it by calling the module functions.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, idle: pg.surface.Surface, team: bool) -> None:
        logger.info(f"{type(self)} created")
        # Define the image filters depending on the team
        midGrey = pg.surface.Surface(size, pg.SRCALPHA)
        midGrey.fill((50, 50, 50))
        pieceReddenerWhite = pg.surface.Surface(size, pg.SRCALPHA)
        pieceReddenerWhite.fill((255, 100, 100))
        pieceReddenerBlack = pg.surface.Surface(size, pg.SRCALPHA)
        pieceReddenerBlack.fill((155, 0, 0))
        imageReddener = pg.surface.Surface(size, pg.SRCALPHA)
        imageReddener.fill((255, 0, 0, 50))
        # Create an anonymous function to change the greyscale depending on team
        greyBlender = lambda base, team: base if (base.blit(midGrey, pg.Vector2(0, 0), special_flags=pg.BLEND_ADD) if team else base.blit(midGrey, pg.Vector2(0, 0), special_flags=pg.BLEND_SUB)) else None
        
        # Create the hovering and clicked forms of the base idle image
        hovering = greyBlender(idle.copy(), team)
        clicked = greyBlender(hovering.copy(), team)
        
        # Create the red idle selected image
        idleSelectedPiece = idle.copy()
        if team:
            idleSelectedPiece.blit(pieceReddenerBlack, pg.Vector2(0, 0), special_flags=pg.BLEND_ADD)
        else:
            idleSelectedPiece.blit(pieceReddenerWhite, pg.Vector2(0, 0), special_flags=pg.BLEND_MIN)
        # Create its hovering and clicked forms
        hoveringSelectedPiece = greyBlender(idleSelectedPiece.copy(), team)
        clickedSelectedPiece = greyBlender(hoveringSelectedPiece.copy(), team)
        
        # Blit these onto a semitransparent red background
        idleSelected = imageReddener.copy()
        idleSelected.blit(idleSelectedPiece, pg.Vector2(0, 0))
        hoveringSelected = imageReddener.copy()
        hoveringSelected.blit(hoveringSelectedPiece, pg.Vector2(0, 0))
        clickedSelected = imageReddener.copy()
        clickedSelected.blit(clickedSelectedPiece, pg.Vector2(0, 0))

        # Define the arrays of each state as the normal and selected versions
        idle = [idle, idleSelected]
        hovering = [hovering, hoveringSelected]
        clicked = [clicked, clickedSelected]

        super().__init__(size, square.elementwise() * size, idle, hovering, clicked)
        # Define the attributes
        self._squareSize: pg.Vector2 = size
        self._team: bool = team
        self._square: pg.Vector2 = square
        self._legalMoves: list = []

    def getTeam(self) -> bool:
        """Return the _team attribute."""
        return self._team
    
    def getValue(self) -> int:
        """Return the _value attribute."""
        return self._value
    
    def baseImage(self) -> None:
        """Reset the state to 0 and the image to the default idle image."""
        self._state = 0
        self.image = self._images["idle"][0]
    
    def getSquare(self) -> pg.Vector2:
        """Return the _square attribute."""
        return self._square
    
    def getMovedEver(self) -> None | bool:
        """Return the _movedEver attribute."""
        # Use a try-except clause in case this attribute does not exist for this object
        try:
            return self._movedEver
        except NameError:
            return 
    
    def movedEverTrue(self) -> None:
        """Set the _movedEver attribute to True."""
        # Use a try-except clause in case this attribute does not exist for this object
        try:
            self._movedEver = True
        except NameError:
            return
    
    def getLegalMoves(self) -> list:
        """Return the _legalMoves attribute."""
        return self._legalMoves
    
    def updateLegalMoves(self, moveList: list, board: list, turn: bool) -> None:
        """Update the _legalmoves attribute by calling static functions based on the piece type."""
        self._legalMoves = updateRegularMoves(self._team, self._square, self, moveList[self._value], board)

    def removeLegalMove(self, square: pg.Vector2) -> None:
        """Remove a move from the _legalmoves attribute if its destination matches the square passed as a parameter."""
        for i, move in enumerate(self._legalMoves):
            if move[0][0] == square.x and move[0][1] == square.y:
                del(self._legalMoves[i])
    
    def move(self, newSquare: pg.Vector2) -> None:
        """Set the _square and _pos attributes to new values."""
        self._square = newSquare
        super().setPos(newSquare.elementwise() * self._squareSize)

    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool, turn: bool) -> None:
        """Call the Switch update method if it is this piece's turn."""
        if self._team == turn:
            super().update(events, mousePos, leftMousePressed)

    def encodeInt(self) -> int:
        """Encode the piece state into an integer.
        
        Encodes all data needed to replicate the piece into an integer, which is effectively
        a compressed method of storing the piece without all of the unnecessary attributes such as image.
        In order from the least to most significant digit, the code is determined as follows:
        - Digit 1 is a combination of the team, moved ever (if it exists) and double moved (also if it exists)
            Team 0 is white and 1 is black, and the three are stored using digits 0-7 as 3 bit binary,
            with most to least significant being: double moved, moved ever, team
        - Digit 2 is the piece value
            0-5 in order mean: pawn, rook, knight, bishop, queen, king
        
        Args:
            None

        Kwargs:
            None

        Returns:
            Returns the integer which was created to store the piece data.
        """
        code = (self._value * 10) + self._team
        # Use a try-except clause since not all pieces have the moved ever and double moved attributes
        try:
            if self._movedEver:
                code += 2
                if self._doubleMoved:
                    code += 4
        except AttributeError:
            pass
        return code


# Create the king class
class King(Piece):
    """The chess king.

    Stores the _movedEver and _threatened attributes on top of the common ones, and is the most important piece in the game,
    with limited mobility but the castle special move and the property that the game is decided by whether it is checkmated or not.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Overwritten from the Piece class to include checking for castle.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.
        getThreatened: Accessor method for the _threatened attribute.
        threatenedTrue: Mutator method for the _threatened attribute to set it to True.
        threatenedFalse: Mutator method for the _threatened attribute to set it to False.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
        _movedEver (bool): Whether this piece has ever moved.
        _threatened (bool): Whether this piece is currently under attack from a piece on the opposing team.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 5
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White King.png", "\\Assets\\Black King.png"][team]).convert_alpha(), size), team)
        # Define the moved ever attribute to allow for castling
        self._movedEver: bool = False
        # Define the threatened attribute to allow for check checking
        self._threatened: bool = False

    def getThreatened(self) -> bool:
        """Return the threatened attribute."""
        return self._threatened
    
    def threatenedTrue(self) -> None:
        """Set the threatened attribute to True."""
        self._threatened = True

    def threatenedFalse(self) -> None:
        """Set the threatened attribute to False."""
        self._threatened = False

    def updateLegalMoves(self, moveList: list, board: list, turn: bool) -> None:
        """Overwrite the update legal moves method to include checking whether castling is legal."""
        self._legalMoves = updateRegularMoves(self._team, self._square, self, moveList[self._value], board)
        if not (self._movedEver or self._threatened):
            # Find whether the piece is active by checking the turn against the team
            self._legalMoves += updateCastle(self._team == turn, turn, self, board)


# Create the queen class
class Queen(Piece):
    """The chess queen.

    Is the most powerful piece in the game, with the highest mobility.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Mutator method for the _legalMoves attribute to update it by calling the module functions.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 4
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White Queen.png", "\\Assets\\Black Queen.png"][team]).convert_alpha(), size), team)


# Create the bishop class
class Bishop(Piece):
    """The chess bishop.

    Is the minor piece which specialises in the endgame, with higher mobility than the knight when unhindered.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Mutator method for the _legalMoves attribute to update it by calling the module functions.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 3
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White Bishop.png", "\\Assets\\Black Bishop.png"][team]).convert_alpha(), size), team)


# Create the knight class
class Knight(Piece):
    """The chess knight.

    Is the minor piece which specialises in the early game, as it is the only piece which can move over other pieces.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Mutator method for the _legalMoves attribute to update it by calling the module functions.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 2
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White Knight.png", "\\Assets\\Black Knight.png"][team]).convert_alpha(), size), team)

# Create the rook class
class Rook(Piece):
    """The chess knight.

    Stores the _movedEver attribute on top of the common ones, and is the best piece for the endgame besides the queen,
    as it is the (second) best at area denial. Is the other piece which can make the castle special move with the king.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Mutator method for the _legalMoves attribute to update it by calling the module functions.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Call the Switch update method if it is this piece's turn.
        encodeInt: Encode and return the piece as an integer.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
        _movedEver (bool): Whether this piece has ever moved.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 1
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White Rook.png", "\\Assets\\Black Rook.png"][team]).convert_alpha(), size), team)
        # Define the moved attribute to allow for castling
        self._movedEver: bool = False


# Create the pawn class
class Pawn(Piece):
    """The chess pawn.

    Stores the _movedEver and _doubleMoved attributes on top of the common ones, and is the least valuable piece in the game.
    However, it has the double and en passant special moves, and if it reaches the opponent's home rank it can promote into any piece other than the king.
    
    Constructor:
        __init__(size (pg.Vector2), square (pg.Vector2), team (bool)): Initialise self and attributes.

    Public Methods:
        getTeam: Accessor method for the _team attribute.
        getValue: Accessor method for the _value attribute.
        baseimage: Reset the image and state.
        getSquare: Accessor method for the _square attribute.
        getMovedEver: Accessor method for the _movedEver attribute.
        movedEverTrue: Mutator method for the _movedEver attribute to set it to True.
        getLegalMoves: Accessor method for the _legalMoves attribute.
        updateLegalMoves: Overwritten from the Piece class to call the pawn-specific function.
        removeLegalMove: Mutator method for the _legalMoves attribute to remove any moves which have the same destination as the parameter.
        move: Set the _square and _pos attributes to reflect a piece movement.
        update: Overwritten from the Piece class to also reset the _doubleMoved attribute.
        encodeInt: Encode and return the piece as an integer.
        getDoubleMoved: Accessor method for the _doubleMoved attribute.
        doubleMovedTrue: Mutator method for the _doubleMoved attribute to set it to True.

    Attributes:
        _size (pg.Vector2): The size of the button - the shape will be a rect based on this.
        _pos (pg.Vector2): The position on the screen of the button, used for detecting whether the mouse position intersects with the button.
        rect (pg.Rect): The rect object holding the size and position of the button.
        _pressed (bool): Whether the button has been pressed/clicked on.
        _images (dict): A dictionary containing the images of the button for every state.
        image (pg.surface.Surface): The current image of the button.
        _state (int): The index of the currently relevant idle image in the idle images value of the _images dictionary.
        _squareSize (pg.Vector2): The size of each board square, and thus the piece as well.
        _team (bool): False for white team and True for black team.
        _square (pg.Vector2): The board square (i.e. index of the board array) which this piece inhabits.
        _legalMoves (list): A list of all legal moves this piece can make.
        _value (int): The piece type's arbitrary integer value.
        _movedEver (bool): Whether this piece has ever moved.
        _doubleMoved (bool): Whether this piece just made a double move.
    """

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, square: pg.Vector2, team: bool) -> None:
        # Define attributes
        self._value: int = 0
        super().__init__(size, square, pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + ["\\Assets\\White Pawn.png", "\\Assets\\Black Pawn.png"][team]).convert_alpha(), size), team)
        # Define the moved ever attribute to allow for the double size first move
        self._movedEver: bool = False
        # Define the double moved attribute to allow for en passant
        self._doubleMoved: bool = False

    def getDoubleMoved(self) -> bool:
        """Return the double moved attribute."""
        return self._doubleMoved
    
    def doubleMovedTrue(self) -> None:
        """Set the double moved attribute to True."""
        self._doubleMoved = True

    # Overwrite the update method to reset double moved
    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool, turn: bool) -> None:
        """Set the _doubleMoved attribute to False if it is the pawn's turn, and then call the Piece class update method."""
        if self._doubleMoved and turn == self._team:
            self._doubleMoved = False
        super().update(events, mousePos, leftMousePressed, turn)

    def updateLegalMoves(self, moveList: list, board: list, turn: bool) -> None:
        """Overwrite the update legal moves method to run the pawn-specific one."""
        self._legalMoves = updatePawnMoves(self._team, turn, self._square, self, board)


# Define static methods to handle piece move generation
def onBoard(square: pg.Vector2) -> bool:
    """Return whether a square is on the board or not."""
    return (0 <= square.x <= 7) and (0 <= square.y <= 7)

def infDist(team: bool, square: pg.Vector2, agent: int | Queen | Bishop | Rook, move: tuple, board: list) -> list:
    """Find a list of all possible moves based on a move option with unlimited distance.

    Use indefinite iteration to find all possible moves given a move option with unlimited distance.

    Args:
        team (bool): The team of the piece whose moves are being checked.
        square (pg.Vector2): The current position of moving piece.
        agent (int | Queen | Bishop | Rook): The piece whose moves are being checked.
        move (tuple): The specific move whose possibilities are being evaluated.
        board (list): The board list, containing all pieces at their positions.

    Kwargs:
        None

    Returns:
        A list of possible moves.
    """
    # Define anonymous functions depending on whether the function is dealing with real pieces or integer representations
    if isinstance(agent, int):
        getTeam = lambda target: target % 2
        addMove = lambda dest: moves.append((square, dest))
    else:
        getTeam = lambda target: target.getTeam()
        addMove = lambda dest: moves.append((dest, agent))

    moves = []
    # Repeat this moving in both positive and negative directions
    for changer in [(lambda base: base + 1), (lambda base: base - 1)]:
        validMove = True
        x = 0
        y = 0
        inf = 0

        # Repeat while the move can still be valid
        while validMove:
            inf = changer(inf)
            # If that component of the move is x, replace it with the infinite move variable, and if the x component is mx, subtract the infinite variable instead
            if move[0] == "x":
                x = int(square.x + inf)
            elif move[0] == "mx":
                x = int(square.x - inf)
            else:
                x = int(square.x + move[0])
            if move[1] == "x":
                y = int(square.y + inf)
            else:
                y = int(square.y + move[1])

            # Only bother target checking if the move is within bounds
            if onBoard(pg.Vector2(x, y)):
                target = board[x][y]

                # The decision to append this move and keep going with the next depends on the target
                if target == None:
                    addMove(pg.Vector2(x, y))

                elif getTeam(target) != team:
                    addMove(pg.Vector2(x, y))
                    if isinstance(target, King):
                        target.threatenedTrue()
                    validMove = False

                else:
                    validMove = False
            else:
                validMove = False
    return moves

def updateRegularMoves(team: bool, square: pg.Vector2, agent: int | King | Queen | Bishop | Knight | Rook, moveList: list, board: list) -> list:
    """Find a list of all possible moves for all non-pawn pieces.

    Use the piece's move list to check which moves are valid and return all of those at the end.

    Args:
        team (bool): The team of the piece whose moves are being checked.
        square (pg.Vector2): The current position of moving piece.
        agent (int | Queen | Bishop | Rook): The piece whose moves are being checked.
        moveList (list): The list of all of that piece's moves.
        board (list): The board list, containing all pieces at their positions.

    Kwargs:
        None

    Returns:
        A list of possible moves.
    """
    # Define anonymous functions depending on whether the function is dealing with real pieces or integer representations
    if isinstance(agent, int):
        getTeam = lambda target: target % 2
        addMove = lambda dest: moves.append((square, dest))
    else:
        getTeam = lambda target: target.getTeam()
        addMove = lambda dest: moves.append((dest, agent))

    moves = []
    for move in moveList:

        # Iterate through all valid squares if the move value is an x, otherwise simply add the moves to the list
        if move[0] == "x" or move[1] == "x":
            moves += infDist(team, square, agent, move, board)
        else:
            toAdd = (int(square.x + move[0]), int(square.y + move[1]))

            # Only check the target if the move is within bounds
            if onBoard(pg.Vector2(toAdd)):
                target = board[toAdd[0]][toAdd[1]]
                
                # If the space is free for the purposes of movement, add that to the move list
                if target == None or getTeam(target) != team:
                    addMove(pg.Vector2(toAdd))
                    if isinstance(target, King):
                        target.threatenedTrue()
    return moves

def updateCastle(active: bool, turn: bool, agent: int | King, board: list) -> list:
    """Return the legal castle moves (if any).

    Check for possible castle moves on both sides, checking against the criteria:
    - Has the rook never moved.
    - Are there no pieces in the way.

    Args:
        active (bool): Whether it is currently the turn of the king in question.
        turn (bool): The current turn in the game.
        agent (int | Queen | Bishop | Rook): The piece whose moves are being checked.
        board (list): The board list, containing all pieces at their positions.

    Kwargs:
        None

    Returns:
        A list of possible castle moves.
    """
    # Define anonymous functions depending on whether the function is dealing with real pieces or integer representations
    if isinstance(agent, int):
        isRookNeverMoved = lambda piece: (piece // 10 == 4) and ((piece % 10) % 4 == (0 or 1))
        addMove = lambda dest: moves.append((pg.Vector2(4 - turn, activeRow), pg.Vector2(dest[0], dest[1]), dest[2]))
    else:
        isRookNeverMoved = lambda piece: isinstance(piece, Rook) and not piece.getMovedEver()
        addMove = lambda dest: moves.append((dest, agent))

    moves = []
    activeRow = active * 7
    lEnd = 6 - (turn + (active * 4))
    rEnd = 6 - (turn + ((not active) * 4))

    # Check left side castling
    if isRookNeverMoved(board[7 - activeRow][activeRow]): # The rook in question will be the piece at the bottom left or top right square
        # Check whether the squares on the left hand side of the king are free
        # List comprehension for greater efficiency iterates between all squares between the king and rook checking that they are empty.
        if not [None for x in range((((not active) * 4) + bool((not turn) + active)), (((not active) * 4) + 3 + (not turn) * active)) if board[x][activeRow] != None]:
            addMove((lEnd, activeRow, "lc"))

    # Check right side castling
    if isRookNeverMoved(board[activeRow][activeRow]): # The rook in question will be the piece at the bottom right or top left square
        # Check whether the squares on the left hand side of the king are free
        # List comprehension for greater efficiency iterates between all squares between the king and rook checking that they are empty.
        if not [None for x in range((active * 4 + (not (turn * active))), (active * 4 + 3 + (not (turn + active)))) if board[x][activeRow] != None]:
            addMove((rEnd, activeRow, "rc"))
    return moves

def freeCheck(squares: list, board: list) -> bool:
    """Return whether a list of board squares are empty."""
    return not [None for square in squares if board[square[0]][square[1]] != None]

def updatePawnMoves(team: bool, turn: bool, square: pg.Vector2, agent: int | Pawn, board: list) -> list:
    """Find a list of all possible moves able to be made by a pawn.

    Find all moves, including special ones, which can be made by a pawn and return them.
    First, check the normal single move, and then double move, followed by diagonal taking and finally orthogonal en passant.

    Args:
        team (bool): The team of the pawn whose moves are being checked.
        turn (bool): The current turn in the game.
        square (pg.Vector2): The current position of moving piece.
        agent (int | Queen | Bishop | Rook): The piece whose moves are being checked.
        board (list): The board list, containing all pieces at their positions.

    Kwargs:
        None

    Returns:
        A list of all possible moves.
    """
    # Define anonymous functions depending on whether the function is dealing with real pieces or integer representations
    if isinstance(agent, int):
        getTeam = lambda target: target % 2
        getMovedEver = lambda target: (target // 2) % 2 != 0
        isPawn = lambda target: target // 10 == 5
        doubleMoved = lambda target: (target % 10) // 4
        addMove = lambda dest: moves.append((square, dest)) if isinstance(dest, pg.Vector2) else moves.append((square, pg.Vector2(dest[0], dest[1]), dest[2]))
    else:
        getTeam = lambda target: target.getTeam()
        getMovedEver = lambda target: target.getMovedEver()
        isPawn = lambda target: isinstance(target, Pawn)
        doubleMoved = lambda target: target.getDoubleMoved()
        addMove = lambda dest: moves.append((dest, agent))

    moves = []

    # Make turn positive if the piece is active and negative if not
    if team == turn:
        turn = -1
    else:
        turn = 1

    # Check that the regular move is valid
    toAdd = (int(square.x), int(square.y + turn))
    if onBoard(pg.Vector2(toAdd)) and freeCheck([toAdd], board):
        addMove(pg.Vector2(toAdd))

        # Check the double move
        if not getMovedEver(agent):
            toAdd = (int(square.x), int(square.y + (2 * turn)))
            if onBoard(pg.Vector2(toAdd)) and freeCheck([toAdd], board):
                toAdd = tuple(toAdd) + tuple("d")
                addMove(toAdd)

    # Check for taking on both sides at the same time as en passant
    for toAdd in [(int(square.x - 1), int(square.y + turn)), (int(square.x + 1), int(square.y + turn))]:
        if 0 <= toAdd[0] <= 7 and 0 <= toAdd[1] <= 7:
            target = board[toAdd[0]][toAdd[1]]

            # If there is a piece at a diagonal to the pawn, add that square to the move list
            if target != None:
                if getTeam(target) != team:
                    addMove(pg.Vector2(toAdd))
                    if isinstance(target, King):
                        target.threatenedTrue()

            # Check for pawns orthogonally adjacent to the subject pawn which have just moved twice, as an en passant can occur here
            else:
                target = board[toAdd[0]][toAdd[1] - turn]
                if target != None and isPawn(target) and doubleMoved(target) and getTeam(target) != team:
                    toAdd += tuple("e")
                    addMove(toAdd)
    return moves

# This is a static method instead of a piece method since this will be called when there is not yet any piece to call it.
def decodeInt(code: int, square: pg.Vector2, squareSize: pg.Vector2) -> Piece:
    """Decode an integer representation of a piece back into that piece.
    
    Decodes the integer representation back into that integer.
    In order from the least to most significant digit, the attributes are deteermined from the code as follows:
    - Digit 1 is a combination of the team, moved ever (if it exists) and double moved (also if it exists)
        Team 0 is white and 1 is black, and the three are stored using digits 0-7 as 3 bit binary,
        with most to least significant being: double moved, moved ever, team
    - Digit 2 is the piece value
        0-5 in order mean: pawn, rook, knight, bishop, queen, king
    
    Args:
        code (int): The piece code.
        square (pg.Vector2): The square where the piece is located.
        squareSize (pg.Vector2): The size of each board square, and thus the piece as well.

    Kwargs:
        None

    Returns:
        Returns a copy of the original piece.
    """
    # Isolate the digits
    value = code // 10
    bools = code % 10

    # Decode the booleans using division and modular arithmetic
    team = bools % 2
    movedEver = bool((bools - team) % 4)
    doubleMoved = bools // 4

    # Depending on the value, create the piece
    piece = [Pawn, Rook, Knight, Bishop, Queen, King][value](squareSize, square, team)

    # Adjust with the decoded booleans, checking first if they are True since the default for them is False but they may not exist for that piece
    if movedEver:
        piece.movedEverTrue()
    if doubleMoved:
        piece.doubleMovedTrue()

    return piece
