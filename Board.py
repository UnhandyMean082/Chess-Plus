"""A chess board which handles a lot of piece logic and UI functions.

This module contains the Board and VirtualBoard classes, and is to be used within the PlayGame class in the Playgame module,
and the NegaMax class in the NegaMax module. It displays the board, along with handling all pieces on it,
and creates and operates the movement buttons, as well as turn swapping and checking whether the game is over.

Classes:
    Board: The class which contains all of the pieces and handles a lot of the inter-piece and UI functionality.
    VirtualBoard: A much lighter-weight class which stores all of the logically necessary components of Board.

Functions:
    algebraicNotation: Process a move and return the algebraic notation representation of it.
"""

# Import modules and libraries
import copy
from loguru import logger
import os
import pygame as pg

import Input as inp
import Piece as pie


# Create the board class
class Board:
    """The chess board.

    This class stores and organises all pieces, contains and displays the board image, creates and operates the movement buttons,
    handles turn swaps by rotating the board and notifying the PlayGame class, notifies it of any dead pieces and checks whether the game is over.

    Constructor:
        __init__(size (pg.Vector2), pos (pg.Vector2)): Initialise self and attributes.

    Public methods:
        getBoard: Accessor method for the __board attribute.
        setBoard: Mutator method for the __board attribute.
        getSquareSize: Accessor method for the __squareSize attribute.
        getImage: Accessor method for the __image attribute.
        getPieces: Accessor method for the __pieces attribute.
        setPieces: Mutator method for the __pieces attribute.
        getKings: Accessor method for the __kings attribute.
        setKings: Mutator method for the __kings attribute.
        createVBoard: Return a virtual board made from the current board.
        getMoved: Accessor method for the __moved attribute.
        movedFalse: Mutator method for the __moved attribute to set it to False.
        getToPromote: Accessor method for the __toPromote attribute.
        toPromoteNone: Mutator method for the __toPromote attribute to set it to None.
        getDead: Accessor method for the __dead attribute.
        deadNone: Mutator method for the __dead attribute to set it to None.
        getCheck: Return whether either king is being threatened.
        getCheckmate: Return whether there are no legal moves left and the current king is in check.
        getStalemate: Return whether there are no legal moves left and the current king is not in check.
        rotateBoard: Rotate the board array.
        promoteTo: Promote a pawn to another piece.
        updateMoves: Update the _legalMoves attribute of all pieces followed by the __allMoves attribute.
        update: Process the user input, update the pieces and any present move buttons, and return the output image.

    Attributes:
        __pieceMoves (dict): A dictionary containing all possible moves for each piece.
        __board (list): The board list, which stores all pieces at their positions.
        __size (pg.Vector2): The board size in pixels.
        __pos (pg.Vector2): The board position in pixels.
        __squareSize (pg.Vector2): The size of each square, adn therefore piece as well.
        __image (pg.surface.Surface): The board image.
        __chessboard (pg.surface.Surface): The image of the simple checkered chessboard.
        __pieces (pg.sprite.Group): A sprite group containing all of the pieces.
        __kings (pg.sprite.Group): A sprite group containing both of the kings.
        __moveButtonIdle (pg.surface.Surface): The image of the move button in its idle state.
        __moveButtonHovering (pg.surface.Surface): The image of the move button in its hovering state.
        __moveButtonClicked (pg.surface.Surface): The image of the move button in its clicked state.
        __specialMoves (list): A list of all special moves available to the selected piece.
        __moveButtons (pg.sprite.Group): A sprite group containing all move buttons.
        __selectedPiece (None | pie.King | pie.Queen | pie.Bishop | pie.Knight | pie.Rook | pie.Pawn): The piece which is currently selected.
        __allMoves (list): A list of all current legal moves.
        __moved (bool): Whether or not a move has occurred yet this turn.
        __toPromote (None | pie.Pawn): A pawn to be promoted, if there is one.
        __dead (None | tuple | list): All pieces which have died this turn.
    """

    # The moves of each piece should remain static, so it is being defined as a class attribute
    # Where x means any non-zero number in that direction and mx means its negative
    __pieceMoves: dict = {
        5: [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)],
        4: [("x", "x"), ("mx", "x"), (0, "x"), ("x", 0)],
        3: [("x", "x"), ("mx", "x")],
        2: [(x + z, y) if x == 0 else (x, y + z) for x in [-2, 0, 2] for y in [-2, 0, 2] if (x + y == 2 or x + y == -2) for z in [-1, 1]],
        1: [("x", 0), (0, "x")]
    }

    # Initialise an object of this class when called
    def __init__(self, size: pg.Vector2, pos: pg.Vector2) -> None:
        logger.info("Board created")
        # Define the basic attributes
        self.__board: list = [[None] * 8 for y in range(8)] # Note that a y-index of 0 means the top, and the array is indexed [x][y]
        self.__size: pg.Vector2 = size
        self.__pos: pg.Vector2 = pos
        self.__squareSize: pg.Vector2 = self.__size / 8
        self.__image: pg.surface.Surface = pg.surface.Surface(self.__size)
        self.__chessboard: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Chessboard.png").convert_alpha(), self.__size)

        # Define all attributes related to the pieces, as well as populating these sprite groups with their objects
        # Define the sprite groups
        self.__pieces: pg.sprite.Group = pg.sprite.Group()
        self.__kings: pg.sprite.Group = pg.sprite.Group()

        # List comprehension for greater efficiency, iterate through piece list and populate sprite groups
        # Populate them first with pieces of the relevant type, given by iterating through a list of types
        # Then, add a row of pawns to both sides
        [[self.__pieces.add(piece(self.__squareSize, pg.Vector2(xSquare, ySquare), team)) for xSquare, piece
          in enumerate([pie.Rook, pie.Knight, pie.Bishop, pie.Queen, pie.King, pie.Bishop, pie.Knight, pie.Rook])] for team, ySquare in enumerate([7, 0])]
        [[self.__pieces.add(pie.Pawn(self.__squareSize, pg.Vector2(xSquare, ySquare), team)) for xSquare in range(8)] for team, ySquare in enumerate([6, 1])]
        
        # Go through and populate the board, as well as the kings group with the kings
        for piece in self.__pieces:
            square = piece.getSquare()
            self.__board[int(square[0])][int(square[1])] = piece
            if isinstance(piece, pie.King):
                self.__kings.add(piece)

        # Define the move button image attributes
        self.__moveButtonIdle: pg.surface.Surface = pg.surface.Surface(self.__squareSize, pg.SRCALPHA)
        self.__moveButtonIdle.fill((255, 0, 0, 50))
        self.__moveButtonHovering: pg.surface.Surface = pg.surface.Surface(self.__squareSize, pg.SRCALPHA)
        self.__moveButtonHovering.fill((255, 0, 0, 100))
        self.__moveButtonClicked: pg.surface.Surface = pg.surface.Surface(self.__squareSize, pg.SRCALPHA)
        self.__moveButtonClicked.fill((255, 0, 0, 150))

        # Define all specific and miscellaneous attributes mainly to do with the actual turns
        self.__specialMoves: list = []
        self.__moveButtons: pg.sprite.Group = pg.sprite.Group()
        self.__selectedPiece: None | pie.King | pie.Queen | pie.Bishop | pie.Knight | pie.Rook | pie.Pawn = None
        self.__allMoves: list = []
        self.__moved: bool = False
        self.__toPromote: None | pie.Pawn = None
        self.__dead: None | tuple | list = None
        
        # Call the method to update the legal moves of all pieces
        self.updateMoves(False)

    def getBoard(self) -> list:
        """Return the board attribute."""
        # As __board is multidimensional, return a deep copy so that there are no array modifying side effects
        return [column.copy() for column in self.__board]
    
    def setBoard(self, newBoard: list) -> None:
        """Set the board attribute to a new board."""
        self.__board = [column.copy() for column in newBoard]

    def getSquareSize(self) -> pg.Vector2:
        """Return the square size attribute."""
        return self.__squareSize
    
    def getImage(self) -> pg.surface.Surface:
        """Return the image attribute."""
        return self.__image
    
    def getPieces(self) -> pg.sprite.Group:
        """Return the pieces attribute."""
        return self.__pieces
    
    def setPieces(self, newPieces: pg.sprite.Group) -> None:
        """Set the board attribute to the new board parameter."""
        self.__pieces = newPieces
    
    def getKings(self) -> pg.sprite.Group:
        """Return the kings attribute."""
        return self.__kings
    
    def setKings(self, newKings: pg.sprite.Group) -> None:
        """Set the board attribute to the new board parameter."""
        self.__kings = newKings

    def createVBoard(self, turn: bool):
        """Return a virtual board made from the current board."""
        vBoard = VirtualBoard(turn)

        # Encode all pieces into integers and place them on the virtual board array in their original positions
        [vBoard.placePiece(piece.getSquare(), piece.encodeInt()) for piece in self.__pieces]

        return vBoard

    def __updateAllMoves(self, turn: bool) -> None:
        """Set the all moves attribute to the list of all moves of the current team."""
        moveList = []
        # Append moves to move lists respective of piece team
        [moveList.append(piece.getLegalMoves()) for piece in self.__pieces if piece.getTeam() == turn]
        self.__allMoves = [move for moveset in moveList for move in moveset]

        # Remove moves from allmoves if they are illegal/would lead to the king being in check
        # Start by creating a virtual board
        vBoard = self.createVBoard(turn)
        illegal = []
        # Iterate through every move and decide whether or not to remove each
        for move in self.__allMoves:
            if isinstance(move[0], pg.Vector2) and vBoard.getCheck(vBoard.fakeMove((move[1].getSquare(), move[0])), True):
                move[1].removeLegalMove(move[0])
                illegal.append(move)
            elif isinstance(move[0], tuple) and vBoard.getCheck(vBoard.fakeMove((move[1].getSquare(), pg.Vector2(move[0][0], move[0][1]), move[0][2])), True):
                move[1].removeLegalMove(pg.Vector2(move[0][0], move[0][1]))
                illegal.append(move)
        [self.__allMoves.remove(move) for move in illegal]
        logger.debug(f"All legal moves are: {self.__allMoves}")

    def getMoved(self) -> bool:
        """Return the moved attribute."""
        return self.__moved
    
    def movedFalse(self) -> None:
        """Set the moved attribute to False."""
        self.__moved = False

    def getToPromote(self) -> None | pie.Pawn:
        """Return the to promote attribute."""
        return self.__toPromote
    
    def toPromoteNone(self) -> None:
        """Set the to promote attribute to none."""
        self.__toPromote = None

    def getDead(self) -> None | tuple | list:
        """Return the dead attribute."""
        return self.__dead
    
    def deadNone(self) -> None:
        """Set the dead attribute to none."""
        self.__dead = None
    
    def getCheck(self, turn: bool) -> bool:
        """Return whether either king is in check."""
        return bool([None for king in self.__kings if king.getThreatened() and king.getTeam() == turn])

    def getCheckmate(self, turn: bool) -> bool:
        """Return whether there are no legal moves left and the current king is in check."""
        logger.debug(f"Checkmate is checked: {len(self.__allMoves) == 0 and self.getCheck(turn)}")
        return len(self.__allMoves) == 0 and self.getCheck(turn)
    
    def getStalemate(self, turn: bool) -> bool:
        """Return whether there are no legal moves left and the current king is not in check."""
        logger.debug(f"Stalemate is checked: {len(self.__allMoves) == 0 and not self.getCheck(turn)}")
        return len(self.__allMoves) == 0 and not self.getCheck(turn)

    def __spaceToPixel(self, square: pg.Vector2) -> pg.Vector2:
        """Return the pixel position which corresponds to the input board position."""
        return self.__squareSize.elementwise() * square
    
    def rotateBoard(self) -> None:
        """Reverse the board array and its sub-arrays to give the effect of rotation."""
        logger.debug("Board rotated")
        # List comprehension for greater efficiency, iterate through and rotate the position of every piece
        [piece.move(pg.Vector2(7, 7) - piece.getSquare()) for piece in self.__pieces]
        
        # Reverse the rows and then columns (equivalent to a rotation) of the board list
        [row.reverse() for row in self.__board]
        self.__board.reverse()

    def promoteTo(self, value: int) -> None:
        """Promote a pawn to another piece."""
        destSquare = self.__toPromote.getSquare()
        team = self.__toPromote.getTeam()
        self.__toPromote.kill()
        pieceValues = [pie.Queen, pie.Bishop, pie.Knight, pie.Rook]
        logger.debug(f"Promote {self.__toPromote} to {pieceValues[value]}")
        promoted = pieceValues[value](self.__squareSize, destSquare, team)
        self.__pieces.add(promoted)
        self.__board[int(destSquare[0])][int(destSquare[1])] = promoted

    # Define a method to handle the special moves
    def __handleSpecialMoves(self, sourceSquare: pg.Vector2, destSquare: pg.Vector2, piece: pie.Piece) -> None:
        """Execute any unique processes if the move that has been made is a special one.
        
        If the move is a castle, then move the rook depending on the side.
        If it is a pawn double move, then set this attribute of the pawn to True.
        If it is a pawn en passant, kill the piece directly behind the pawn
        (on the assumption that it was a valid en passant, and thus this piece should be another pawn).
        
        Args:
            sourceSquare (pg.Vector2): The source square of the move which is currently being executed.
            destSquare (pg.Vector2): The destination square of the move which is currently being executed.
            piece (pie.Piece): The piece which is currently moving.

        Kwargs:
            None

        Returns:
            None
        """
        inSpecial = False
        for specMove in self.__specialMoves:
            if destSquare == pg.Vector2(specMove[0][0], specMove[0][1]):

                # If the move is a castle, also move the corresponding rook
                if specMove[0][2] == "lc":
                    logger.debug("Move the rook in the left castle")
                    logger.success(f"{["White", "Black"][piece.getTeam()]} played {algebraicNotation(sourceSquare, destSquare, piece, "lc")}")
                    inSpecial = True
                    # The rook in question will be the piece at the bottom left square
                    self.__board[0][7].move(pg.Vector2(specMove[0][0] + 1, 7))
                    self.__board[specMove[0][0] + 1][7] = self.__board[0][7]
                    self.__board[0][7] = None

                elif specMove[0][2] == "rc":
                    logger.debug("Move the rook in the right castle")
                    logger.success(f"{["White", "Black"][piece.getTeam()]} played {algebraicNotation(sourceSquare, destSquare, piece, "rc")}")
                    inSpecial = True
                    # The rook in question will be the piece at the bottom right square
                    self.__board[7][7].move(pg.Vector2(specMove[0][0] - 1, 7))
                    self.__board[specMove[0][0] - 1][7] = self.__board[7][7]
                    self.__board[7][7] = None

                # If the move was a pawn double move, set this attribute to True
                elif specMove[0][2] == "d":
                    logger.debug("Set the doubleMoved attribute to True")
                    self.__selectedPiece.doubleMovedTrue()

                # Otherwise, it was an en passant so kill the passed pawn
                else:
                    logger.debug("Kill the passed pawn in en passant")
                    logger.success(f"{["White", "Black"][piece.getTeam()]} played {algebraicNotation(sourceSquare, destSquare, piece, "e")}")
                    inSpecial = True
                    target = self.__board[int(destSquare.x)][int(destSquare.y) + 1]
                    self.__dead = (target.getTeam(), target.getValue())
                    target.kill()
                    self.__board[int(destSquare.x)][int(destSquare.y) + 1] = None

        if not inSpecial:
            logger.success(f"{["White", "Black"][piece.getTeam()]} played {algebraicNotation(sourceSquare, destSquare, piece)}")

    # Define a method to handle the selected piece
    def __handleSelectedPiece(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool, turn: bool) -> None:
        """If a piece is selected, update move buttons and if any are pressed, trigger the turn change.

        Update the selectedd piece's move buttons, and if any are pressed, change the turn.
        Update attributes, check whether the move needs to be handled specially, and rotate the board.

        Args:
            events (list): The current frame's events queue.
            mousePos (pg.Vector2): The current position of the mouse.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed.
            turn (bool): The team whose turn it currently is.

        Kwargs:
            None

        Returns:
            None
        """
        # Update the piece"s move buttons
        self.__moveButtons.update(events, mousePos - self.__pos, leftMousePressed)
        # Check if any were pressed, and if so, handle a piece move
        for button in self.__moveButtons:
            if button.getPressed():
                logger.debug(f"Selected piece button at {button.getPos()} was pressed")

                # Define and update attributes and variables
                selectedPieceSquare = self.__selectedPiece.getPos().elementwise() / self.__squareSize
                destSquare = button.getPos().elementwise() / self.__squareSize
                self.__selectedPiece.move(destSquare)
                self.__selectedPiece.movedEverTrue()
                self.__selectedPiece.baseImage()
                self.__moved = True
                self.__moveButtons = pg.sprite.Group()

                # Kill the piece at that spot (if any) and add it to the dead pieces list
                target = self.__board[int(destSquare.x)][int(destSquare.y)]
                if target != None and target.getTeam() != turn:
                    self.__dead = (target.getTeam(), target.getValue())
                    target.kill()

                # Call the method to handle the special moves list
                self.__handleSpecialMoves(selectedPieceSquare, destSquare, self.__selectedPiece)

                # Move the piece on the board array as well
                self.__board[int(selectedPieceSquare.x)][int(selectedPieceSquare.y)] = None
                self.__board[int(destSquare.x)][int(destSquare.y)] = self.__selectedPiece

                # If a piece has been moved, check if any on the farthest row are friendly pawns, and if so, put them up for promotion
                for piece in range(len(self.__board)):
                    endPiece = self.__board[piece][0]
                    if isinstance(endPiece, pie.Pawn) and endPiece.getTeam() == turn:
                        self.__toPromote = endPiece
            
                # Rotate the board unless there is a promotion
                if self.__toPromote == None:
                    self.rotateBoard()
                    
                    # Call the method to update all piece moves of the opposing team
                    self.updateMoves(not turn)

                self.__selectedPiece = None

    def updateMoves(self, turn: bool) -> None:
        """Update the _legalMoves attributes of all pieces, followed by the __allMoves attribute."""
        # Set each king's threatened attribute back to False
        [king.threatenedFalse() for king in self.__kings]
        # Update every piece"s legal move list
        [piece.updateLegalMoves(self.__pieceMoves, self.__board, turn) for piece in self.__pieces]
        # Compile a list of all moves which might block castling from occurring
        castleBlockers = [move[0] for piece in self.__pieces for move in piece.getLegalMoves() if ((move[0][1] == 0) and (piece.getTeam() == turn)) or ((move[0][1] == 7) and (piece.getTeam() != turn))]
        # Remove any castle moves if they pass through attacked squares
        for king in self.__kings:
            castles = [move[0] for move in king.getLegalMoves() if isinstance(move[0], tuple)]
            [king.removeLegalMove(pg.Vector2(castle[0], castle[1])) for castle in castles for x in range(int(min(castle[0], king.getSquare().x)), int(max(castle[0], king.getSquare().x) + 1)) if pg.Vector2(x, castle[1]) in castleBlockers]
        self.__updateAllMoves(turn)

    # Define a method to create move buttons if any need to be created
    def __createMoveButtons(self) -> None:
        """If a piece has been selected, get its move list and create a move button for each one."""
        for piece in self.__pieces:
            if piece.getState() and piece.getPressed():
                piece.pressedFalse()
                self.__selectedPiece = piece

                # Each entity within this move options list is a tuple which holds the move at index 0 and the piece at index 1
                moveOptions = piece.getLegalMoves()
                self.__specialMoves = []

                # Define an anonymous function to get the square as a vector and add any special moves to the special moves list
                squareVector = lambda move: move[0] if isinstance(move[0], pg.Vector2) else pg.Vector2(move[0][0], move[0][1]) if (self.__specialMoves.append(move) == None) else None
                # List comprehension for greater efficiency, iterate through every move adding buttons
                [self.__moveButtons.add(
                    inp.Button(self.__squareSize, self.__spaceToPixel(squareVector(move)), self.__moveButtonIdle, self.__moveButtonHovering, self.__moveButtonClicked))
                  for move in moveOptions]

    # Define a method to update the board
    def update(self, turn: bool, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> pg.surface.Surface:
        """Process the user input, update the pieces and any present move buttons, alter some attributes and return the output image.

        Draw the board, take care of any potential promotions, update all selected pieces, and if none are selected then update every piece,
        call the method to handle a selected piece if one is selected, and draw everything else onto the board and return the resulting image.

        Args:
            turn (bool): The team whose turn it currently is.
            events (list): The current frame's events queue.
            mousePos (pg.Vector2): The current position of the mouse.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed.

        Kwargs:
            None

        Returns:
            The board image to be displayed on the PlayGame object's image.
        """
        # Draw the chessboard base before handling all of the pieces
        self.__image.blit(self.__chessboard, pg.Vector2(0, 0))

        # If there is to be a promotion, do not update anything until the promotion has been decided
        if self.__toPromote == None:
            # If a piece has just been selected, create its move buttons
            self.__createMoveButtons()

            # Update all selected pieces, and if nothing is updated, update all pieces
            if not [piece.update(events, mousePos - self.__pos, leftMousePressed, turn) for piece in self.__pieces if (piece.getState())]:
                self.__pieces.update(events, mousePos - self.__pos, leftMousePressed, turn)
                self.__specialMoves = []
                self.__moveButtons = pg.sprite.Group()
                self.__selectedPiece = None

            else:
                # Call the method to handle the selected piece
                self.__handleSelectedPiece(events, mousePos, leftMousePressed, turn)
                
        # Draw the pieces
        self.__pieces.draw(self.__image)
        # Draw the piece"s move buttons
        self.__moveButtons.draw(self.__image)
        return self.__image
    

# Create the virtual board class
class VirtualBoard:
    """A lightweight virtual version of the chess board.

    This class stores and organises all piece integer codes, and allows useful operations to be performed upon them.

    Constructor:
        __init__(turn (bool)): Initialise self and attributes.

    Public methods:
        getBoard: Accessor method for the __board attribute.
        setBoard: Mutator method for the __board attribute.
        getTurn: Accessor method for the __turn attribute.
        getAllMoves: Return a list of all possible moves.
        getAllLegalMoves: Return a list of all possible legal moves.
        placePiece: Place a piece at the specified board index.
        rotateBoard: Rotate the board array.
        fakeMove: Return the results of a move made on the current board.
        makeMove: Make a move on the current board.
        getPieces: Return a list of all pieces.
        getCheck: Return whether the active king is being threatened.

    Attributes:
        __pieceMoves (dict): A dictionary containing all possible moves for each piece.
        __board (list): The board list which stores all piece integers at their positions.
        __turn (bool): The current turn.
    """

    # The moves of each piece should remain static, so it is being defined as a class attribute
    # Where x means any non-zero number in that direction and mx means its negative
    __pieceMoves: dict = {
        5: [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)],
        4: [("x", "x"), ("mx", "x"), (0, "x"), ("x", 0)],
        3: [("x", "x"), ("mx", "x")],
        2: [(x + z, y) if x == 0 else (x, y + z) for x in [-2, 0, 2] for y in [-2, 0, 2] if (x + y == 2 or x + y == -2) for z in [-1, 1]],
        1: [("x", 0), (0, "x")]
    }

    # Initialise an object of this class when called
    def __init__(self, turn: bool) -> None:
        logger.info("VirtualBoard created")
        # Define attributes
        self.__board: list = [[None] * 8 for y in range(8)]
        self.__turn: bool = turn

    def getBoard(self) -> list:
        """Return the board attribute."""
        # As __board is multidimensional, return a deep copy so that there are no array modifier side effects
        return copy.deepcopy(self.__board)
    
    def setBoard(self, newBoard: list) -> None:
        """Set the board attribute to a new board."""
        self.__board = copy.deepcopy(newBoard)
    
    def getTurn(self) -> bool:
        """Return the turn attribute."""
        return self.__turn
    
    def getAllMoves(self, turn: None | bool=None, board: bool | list=False) -> list:
        """Return a list of all possible moves."""
        # If board was not passed, use the board attribute
        if not board:
            board = copy.deepcopy(self.__board)
        # If turn was not passed, use the turn attribute
        if turn == None:
            turn = self.__turn
        allMoves = []
        # Iterate through every board square and append the results of running either update piece moves or update regular moves
        [allMoves.append(pie.updateRegularMoves(turn, pg.Vector2(x, y), piece, self.__pieceMoves[piece // 10], board)) if piece >= 10 else allMoves.append(pie.updatePawnMoves(turn, turn, pg.Vector2(x, y), piece, board)) for x, column in enumerate(board) for y, piece in enumerate(column) if piece != None and piece % 2 == turn]
        return [move for moveset in allMoves for move in moveset]
    
    def getAllLegalMoves(self, turn: None | bool=None, board: bool | list=False) -> list:
        """Return a list of all legal moves."""
        # If board was not passed, use the board attribute
        if not board:
            board = copy.deepcopy(self.__board)
        # If turn was not passed, use the turn attribute
        if turn == None:
            turn = self.__turn
        # First, get all moves, and then eliminate them based on which lead to an attacked king
        allMoves = self.getAllMoves(turn, board)

        toDel = []
        [toDel.append(move) for move in allMoves if self.getCheck(self.fakeMove(move), True)]
        [allMoves.remove(move) for move in toDel]
        return allMoves
    
    def placePiece(self, square: pg.Vector2, piece: int | pie.Piece) -> None:
        """Place a piece at the specified index on the board."""
        self.__board[int(square.x)][int(square.y)] = piece

    def rotateBoard(self) -> None:
        """Rotate the board array if it is a different player's turn."""
        logger.debug("Virtual board array rotated")
        # Reverse the rows and then columns (equivalent to a rotation) of the board list
        [row.reverse() for row in self.__board]
        self.__board.reverse()

    def fakeMove(self, move: tuple, promote: int=4) -> list:
        """Return the results of a move made on the current board.
        
        The format of the move parameter is a tuple, containing first the starting position,
        then the ending position, and finally any special flags where necessary.
        The move is assumed to be acting on a piece whose turn it currently is, but there are no checks for this.

        Args:
            move (tuple): The move which is to be processed and returned.

        Kwargs:
            promote (int) = 4: The piece value to which the pawn should be promoted.

        Returns:
            The new board list after this move has been made.
        """
        # Take a deep copy, since this is a 2D list, meaning that a simple shallow copy would contain the component lists still as pointers
        board = copy.deepcopy(self.__board)

        # Deal with the simplest part - moving the piece in question
        board[int(move[1].x)][int(move[1].y)] = board[int(move[0].x)][int(move[0].y)]
        board[int(move[0].x)][int(move[0].y)] = None

        # If the piece has a moved ever attribute, add 2 if it has not already been moved
        if (board[int(move[1].x)][int(move[1].y)] // 10 in (0, 1, 5)) and (((board[int(move[1].x)][int(move[1].y)] % 10) // 2) % 2 == 0):
            board[int(move[1].x)][int(move[1].y)] += 2

        # Reset all double moved attributes
        for x, column in enumerate(board):
            for y, piece in enumerate(column):
                if piece != None and piece // 10 == 0:
                    board[x][y] %= 4

        # Deal with any specialty if there is any
        if len(move) == 3:
            # Left castle
            if move[2] == "lc":
                board[int(move[1].x) + 1][7] = board[0][7]
                board[0][7] = None

            # Right castle
            if move[2] == "rc":
                board[int(move[1].x) - 1][7] = board[7][7]
                board[7][7] = None

            # Double pawn move
            if move[2] == "d":
                board[int(move[1].x)][int(move[1].y)] += 4

            # En passant
            else:
                board[int(move[1].x)][int(move[0].y)] = None

        # Handle any possible promotions
        for x, column in enumerate(board):
            if column[0] != None and column[0] < 10:
                board[x][0] = promote * 10 + column[0]

        # Rotate the board
        [row.reverse() for row in board]
        board.reverse()
        return board

    # Since both speed and space are important for this method, rather than calling fake move and setting the board attribute to that for this method,
    # it will just run the same process but with the attribute instead of a copy, to save an (albeit very small) amount of time with a saved function call,
    # but a bigger amount of space with the avoidance of generating a new board list - which in turn will save time.
    def makeMove(self, move: tuple, promote: int=4) -> None:
        """Make a move on the current board.
        
        The format of the move parameter is a tuple, containing first the starting position,
        then the ending position, and finally any special flags where necessary.
        The move is assumed to be acting on a piece whose turn it currently is, but there are no checks for this.

        Args:
            move (tuple): The move which is to be processed and made.

        Kwargs:
            promote (int) = 4: The piece value to which the pawn should be promoted.

        Returns:
            None
        """
        logger.debug("VirtualBoard move made")
        # Deal with the simplest part - moving the piece in question
        self.__board[int(move[1].x)][int(move[1].y)] = self.__board[int(move[0].x)][int(move[0].y)]
        self.__board[int(move[0].x)][int(move[0].y)] = None

        # If the piece has a moved ever attribute, add 2 if it has not already been moved
        if (self.__board[int(move[1].x)][int(move[1].y)] // 10 in (0, 1, 5)) and (((self.__board[int(move[1].x)][int(move[1].y)] % 10) // 2) % 2 == 0):
            self.__board[int(move[1].x)][int(move[1].y)] += 2

        # Reset all double moved attributes
        for x, column in enumerate(self.__board):
            for y, piece in enumerate(column):
                if piece != None and piece // 10 == 0:
                    self.__board[x][y] %= 4

        # Deal with any specialty if there is any
        if len(move) == 3:
            # Left castle
            if move[2] == "lc":
                self.__board[int(move[1].x) + 1][7] = self.__board[0][7]
                self.__board[0][7] = None

            # Right castle
            if move[2] == "rc":
                self.__board[int(move[1].x) - 1][7] = self.__board[7][7]
                self.__board[7][7] = None

            # Double pawn move
            if move[2] == "d":
                self.__board[int(move[1].x)][int(move[1].y)] += 4

            # En passant
            else:
                self.__board[int(move[1].x)][int(move[0].y)] = None

        # Handle any possible promotions
        for x, column in enumerate(self.__board):
            if column[0] != None and column[0] < 10:
                self.__board[x][0] = promote * 10 + column[0]

        # Rotate the board
        self.rotateBoard()

        # Swap the turns
        self.__turn = not self.__turn

    def getPieces(self) -> tuple:
        """Return a tuple containing lists of all pieces organised into white and black teams only containing value, for quick material analysis."""
        white = []
        black = []
        [[white, black][piece % 2].append(piece // 10) for column in self.__board for piece in column if piece != None]

        return (white, black)
    
    def getCheck(self, board: bool | list = False, turnOffset: bool = False) -> bool:
        """Return whether the king whose turn it is is under attack."""
        # The simulated turn is the stored turn XORed with the turn offset, since if there is an offset the turn is flipped
        turn = self.__turn ^ turnOffset

        if not board:
            board = copy.deepcopy(self.__board)
        
        # Return whether or not the list of all moves whose destinations intersect the king is empty
        return bool([None for move in self.getAllMoves(turn, board) if (board[int(move[1].x)][int(move[1].y)] != None) and (board[int(move[1].x)][int(move[1].y)] % 2 != turn) and (board[int(move[1].x)][int(move[1].y)] // 10 == 5)])
    

# Define a function to
def algebraicNotation(start: pg.Vector2, end: pg.Vector2, piece: pie.Piece, special: str | None=None) -> str:
    """Parse a move and return its representation in official Chess algebraic notation, slightly modified for efficiency."""
    # Create the rank array
    ranks = ["a", "b", "c", "d", "e", "f", "g", "h"]
    if piece.getTeam():
        ranks.reverse()
    # As a slight modification, instead of leaving the source square out except in case of possible ambiguity, just include it regardless to avoid having to search through the board
    source = ranks[int(start.x)] + str(int(abs(((not piece.getTeam()) * 9) - (start.y + 1))))
    dest = ranks[int(end.x)] + str(int(abs(((not piece.getTeam()) * 9) - (end.y + 1))))
    # Castles have special notations
    if special == ("lc" or "rc"):
        strOut = ["O-O", "O-O-O"][piece.getTeam() ^ (special == "lc")]
    else:
        # Add "ep" if it is an en passant
        strOut = ["", "R", "N","B", "Q", "K"][piece.getValue()] + source + dest
        if special == "e":
            strOut += "ep"
    return strOut