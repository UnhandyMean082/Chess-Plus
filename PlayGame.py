"""The played part of a chess game, which is where users make moves and actually play the game.

This module contains the PlayGame class, and is to be used within the Game class in the Game module.
It displays a screen whose colour matches the turn, with the game board, relevant buttons and all captured pieces.
It contains an exit button, which causes the program to quit, a restart button, which resets the game,
and a surrender button, which ends the game and signals the Game class to switch to the menu state on next click.
It contains a Board object from the Board module as well, on which pieces are moved and which is displayed.

Classes:
    PlayGame: The class which handles the game logic and its image.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import os
import pygame as pg
import threading

import Board as boa
import Frame as fme
import Input as inp
import NegaMax as nMax
import Piece as pie
import Stack as stk


# Create the play game class
class PlayGame:
    """Handles the actual chess part of the chess game and manages the board.
    
    This class functions as the outer layer in the game itself, taking care of everything which happens outside the confines of the board,
    such as displaying of dead pieces, displaying of messages, handling of buttons and even facilitating of promotions.
    This class also takes care of the higher-level, interface-related aspects of the game such as switching between PlayGame and Menu.

    Constructor:
        __init__(screenSize (pg.Vector2)): Initialise self and attributes, and create buttons.

    Public methods:
        getGameOver: Accessor method for the __gameOver attribute.
        gameOverFalse: Mutator method for the __gameOver attribute to set it to False.
        setOpp: Mutator method for the __opponent attribute, and also change other aspects of the class to reflect the opponent.
        restart: Reset most attributes to their state at object instantiation, mostly resetting the class.
        update: Process the user inputs, the board, and create the frame image.

    Attributes:
        __gameOver (bool): Whether the game is over and the game state should change back to the Menu or not.
        __gameWon (bool): Whether a player has won the game.
        __winner (None | bool): The winner of the game.
        __size (pg.Vector2): The size of the screen in pixels.
        __image (pg.surface.Surface): The current frame image.
        __turn (bool): The team whose turn it currently is.
        __boardSize (pg.Vector2): The size of the board in pixels.
        __boardPos (pg.Vector2): The position of the board on the screen.
        __board (boa.Board): The board object, which stores the pieces and handles a lot of GUI and move logic.
        __buttons (pg.sprite.Group): A sprite group for all of the buttons which will be displayed at the side of the screen.
        __opponent (bool): True for a computer opponent and False for a human one.
        __negaMax (None | nMax.NegaMax): Either None if there is a human opponent, or the NegaMax object if there is a computer opponent, since it will be this which controls those moves.
        __negaMaxCalled (bool): Whether the __negaMax attribute's turn method has been called yet this turn.
        __negaMaxThread (None | threading.Thread): Either None if there is a human opponent, or a Thread object to run the negamax algorithm in parallel with the main one.
        __exitButton (inp.Button): The button which controls quitting the program.
        __restartButton (inp.button): The button which controls restarting the game.
        __surrenderButton (inp.Button): The button which allows a player to forfeit the game.
        __undoButton (inp.Button): The button which allows the most recent move to be undone.
        __readyButton (inp.Button): The button which sets the AI to operate on a 3 second time limit.
        __timeButton (inp.Button): The button which sets the AI to make a move when ready if 3 seconds have been passed, but be forced to make a move by 10 if it still has not finished processing.
        __pieceSize (pg.Vector2): The size of each piece, and thus each square on the board, in pixels.
        __whitePieces (list): A list of the images of all white pieces.
        __whiteDead (list): A list to store all dead pieces which used to be on the white team.
        __blackPieces (list): A list of the images of all black pieces.
        __blackDead (list): A list to store all dead pieces which used to be on the black team.
        __whiteCheck (pg.surface.Surface): The image displayed when the white king is in check.
        __blackCheck (pg.surface.Surface): The image displayed when the black king is in check.
        __whiteCheckmate (pg.surface.Surface): The image displayed when white is checkmated.
        __blackCheckmate (pg.surface.Surface): The image displayed when black is checkmated.
        __whiteWon (pg.surface.Surface): The image displayed when white wins due to black surrender.
        __blackWon (pg.surface.Surface): The image displayed when black wins due to white surrender.
        __stalemate (pg.Vector2): The image displayed when a stalemate occurs.
        __promotion (bool): Whether or not a promotion is currently being decided.
        __queen (None | inp.Button): A potential future button for selecting the queen when making a promotion.
        __bishop (None | inp.Button): A potential future button for selecting the bishop when making a promotion.
        __knight (None | inp.Button): A potential future button for selecting the knight when making a promotion.
        __rook (None | inp.Button): A potential future button for selecting the rook when making a promotion.
        __promoButtons (pg.sprite.Group): A sprite group to hold all buttons displayed when offering options for a promotion.
        __pastMoves (stk.Stack): The stack of all past move frames.
        __frame (fme.Frame): A frame of the current game state.
    """
    
    # Initialise an object of this class when called
    def __init__(self, screenSize: pg.Vector2) -> None:
        logger.info("PlayGame created")
        # Define basic attributes
        self.__gameOver: bool = False
        self.__gameWon: bool = False
        self.__winner: None | bool = None
        self.__size: pg.Vector2 = screenSize
        self.__image: pg.surface.Surface = pg.surface.Surface(self.__size)
        self.__turn: bool = False
        boardWidth = self.__size.y * 2 / 3
        self.__boardSize: pg.Vector2 = pg.Vector2(boardWidth, boardWidth)
        self.__boardPos: pg.Vector2 = pg.Vector2((self.__size - self.__boardSize) / 2)
        self.__board: boa.Board = boa.Board(self.__boardSize, self.__boardPos)
        self.__buttons: pg.sprite.Group = pg.sprite.Group()
        self.__opponent: bool = False
        self.__negaMax: None | nMax.NegaMax = None
        self.__negaMaxCalled: bool = False
        self.__negaMaxThread: None | threading.Thread = None

        # Define the variables for changing the surfaces
        buttonSize = (self.__size.elementwise() / pg.Vector2(4, 10))
        buttonDarkener = pg.surface.Surface(buttonSize, pg.SRCALPHA)
        buttonDarkener.fill((100, 100, 100))

        # Define the buttons
        exitButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Exit Button.png").convert_alpha(), buttonSize)
        exitButtonHovering = exitButtonIdle.copy()
        exitButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        exitButtonClicked = exitButtonHovering.copy()
        exitButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__exitButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), self.__boardPos.y), exitButtonIdle, exitButtonHovering, exitButtonClicked)
        self.__buttons.add(self.__exitButton)
        restartButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Restart Button.png").convert_alpha(), buttonSize)
        restartButtonHovering = restartButtonIdle.copy()
        restartButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        restartButtonClicked = restartButtonHovering.copy()
        restartButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__restartButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), (self.__boardPos.y + (buttonSize.y * 3/2))), restartButtonIdle, restartButtonHovering, restartButtonClicked)
        self.__buttons.add(self.__restartButton)
        surrenderButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Surrender Button.png").convert_alpha(), buttonSize)
        surrenderButtonHovering = surrenderButtonIdle.copy()
        surrenderButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        surrenderButtonClicked = surrenderButtonHovering.copy()
        surrenderButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__surrenderButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), (self.__boardPos.y + (buttonSize.y * 3))), surrenderButtonIdle, surrenderButtonHovering, surrenderButtonClicked)
        self.__buttons.add(self.__surrenderButton)
        undoButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Undo Button.png").convert_alpha(), buttonSize)
        undoButtonHovering = undoButtonIdle.copy()
        undoButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        undoButtonClicked = undoButtonHovering.copy()
        undoButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
        self.__undoButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), (self.__boardPos.y + (buttonSize.y * 9/2))), undoButtonIdle, undoButtonHovering, undoButtonClicked)
        self.__buttons.add(self.__undoButton)
        self.__readyButton: None | inp.Button = None
        self.__timeButton: None | inp.Button = None

        # Define piece-related attributes
        self.__pieceSize: pg.Vector2 = self.__boardSize / 8
        self.__whitePieces: list = [pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Pawn.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Rook.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Knight.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Bishop.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Queen.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White King.png").convert_alpha(), self.__pieceSize)]
        self.__whiteDead: list = []
        self.__blackPieces: list = [pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Pawn.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Rook.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Knight.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Bishop.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Queen.png").convert_alpha(), self.__pieceSize),
                              pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black King.png").convert_alpha(), self.__pieceSize)]
        self.__blackDead: list = []
        self.__whiteCheck: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Check!.png").convert_alpha(), buttonSize)
        self.__blackCheck: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Check!.png").convert_alpha(), buttonSize)
        self.__whiteCheckmate: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Checkmate!.png").convert_alpha(), buttonSize)
        self.__blackCheckmate: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Checkmate!.png").convert_alpha(), buttonSize)
        self.__whiteWon: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\White Won!.png").convert_alpha(), buttonSize)
        self.__blackWon: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Black Won!.png").convert_alpha(), buttonSize)
        self.__stalemate: pg.surface.Surface = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\Stalemate!.png").convert_alpha(), buttonSize)
        self.__promotion: bool = False
        self.__queen: None | inp.Button = None
        self.__bishop: None | inp.Button = None
        self.__knight: None | inp.Button = None
        self.__rook: None | inp.Button = None
        self.__promoButtons: pg.sprite.Group = pg.sprite.Group()
        self.__pastMoves: stk.Stack = stk.Stack(20)
        self.__frame: fme.Frame = self.__createFrame()

    def getGameOver(self) -> bool:
        """Return the game over attribute."""
        return self.__gameOver
    
    def gameOverFalse(self) -> None:
        """Set the game over attribute to False."""
        self.__gameOver = False

    def setOpp(self, opponent: bool) -> None:
        """Set the opponent attribute and make the necessary changes to reflect this setting."""
        self.__opponent = opponent
        # If there is a computer opponent, create the minimax and add buttons for having it move when ready or when the buffer time elapses
        if self.__opponent:
            self.__negaMax = nMax.NegaMax()

            # Define the variables for changing the surfaces
            buttonSize = (self.__size.elementwise() / pg.Vector2(4, 10))
            buttonDarkener = pg.surface.Surface(buttonSize, pg.SRCALPHA)
            buttonDarkener.fill((100, 100, 100))

            # Define the buttons
            readyButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\AI Ready Button.png").convert_alpha(), buttonSize)
            readyButtonHovering = readyButtonIdle.copy()
            readyButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
            readyButtonClicked = readyButtonHovering.copy()
            readyButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
            self.__readyButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), (self.__boardPos.y + (buttonSize.y * 6))), readyButtonIdle, readyButtonHovering, readyButtonClicked)
            self.__buttons.add(self.__readyButton)
            timeButtonIdle = pg.transform.scale(pg.image.load(os.path.dirname(os.path.abspath(__file__)) + "\\Assets\\AI Time Button.png").convert_alpha(), buttonSize)
            timeButtonHovering = timeButtonIdle.copy()
            timeButtonHovering.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
            timeButtonClicked = timeButtonHovering.copy()
            timeButtonClicked.blit(buttonDarkener, pg.Vector2(0, 0), special_flags=pg.BLEND_MULT)
            self.__timeButton: inp.Button = inp.Button(buttonSize, (((self.__boardPos.x - buttonSize.x) / 2), (self.__boardPos.y + (buttonSize.y * 6))), timeButtonIdle, timeButtonHovering, timeButtonClicked)

        else:
            self.__negaMax = None
            if self.__readyButton != None:
                self.__readyButton.kill()
            if self.__timeButton != None:
                self.__timeButton.kill()

    def __createFrame(self) -> fme.Frame:
        """Create a frame object, to be used to facilitate the undo functionality, to store a previous game state."""
        # Take copies of the dead lists otherwise they will change since they are only going to be stored as pointers
        return fme.Frame(self.__board.createVBoard(self.__turn), [self.__whiteDead.copy(), self.__blackDead.copy()])

    def __setFrame(self, frame: None | fme.Frame) -> None:
        """Change the current board state to reflect a board frame."""
        if frame != None:
            [self.__whiteDead, self.__blackDead] = frame.getDead()
            
            # Decode the pieces back into objects, adding them to their sprite groups
            pieces = pg.sprite.Group()
            kings = pg.sprite.Group()
            # Decode every value on the board which is not none and add them all to the pieces sprite group, while using an or statement for a secondary selection to identify the kings and add them to the kings sprite group
            [pieces.add(pieceObj) for x, column in enumerate(frame.getBoard().getBoard()) for y, pieceInt in enumerate(column) if pieceInt != None and (pieceObj := pie.decodeInt(pieceInt, pg.Vector2(x, y), self.__board.getSquareSize())) and ((not isinstance(pieceObj, pie.King)) or kings.add(pieceObj) == None)]

            # Create the board
            board = [[None] * 8 for y in range(8)]
            for piece in pieces:
                square = piece.getSquare()
                board[int(square[0])][int(square[1])] = piece

            # Replace the board's sprite groups and board list with the new ones
            self.__board.setBoard(board)
            self.__board.setPieces(pieces)
            self.__board.setKings(kings)

    def restart(self) -> None:
        """Reset most aspects of the object so that the game can be played fresh with nothing gameplay-wise carrying over from last time."""
        logger.info("PlayGame restarting")
        boardWidth = self.__size.y * 2 / 3
        self.__boardSize = pg.Vector2(boardWidth, boardWidth)
        self.__board = boa.Board(self.__boardSize, self.__boardPos)
        self.__turn = False
        self.__gameOver = False
        self.__gameWon = False
        self.__winner = None
        self.__whiteDead = []
        self.__blackDead = []
        self.__promotion = False
        self.__promoButtons = pg.sprite.Group()
        self.__frame = self.__createFrame()
        self.__pastMoves = stk.Stack(20)
        self.__negaMaxCalled = False
        if self.__opponent:
            self.__negaMax.stopThinking()
            self.__negaMax = nMax.NegaMax()
        else:
            self.__negaMax = None
        
    def __wonGame(self, events: list) -> None:
        """If the game has been won and a click occurs, signifying the player's intent to move on, the __gameOver attribute is set to True."""
        self.__image.blit([self.__whiteCheckmate, self.__blackCheckmate, self.__stalemate, self.__whiteWon, self.__blackWon][self.__winner], pg.Vector2((self.__size.x * 3/8), ((self.__boardPos.y - (self.__size.y / 10)) / 2)))
        self.__image.blit(self.__board.getImage(), self.__boardPos)
        if [None for event in events if event.type == pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT]:
            self.__gameOver = True
        
    def __updateButtons(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> None:
        """Update the buttons on the side of the screen, executing all of their intended functions if they were pressed.
        
        Go through every button at the side of the screen, doing the following upon each one's being pressed:
        - Exit: quit the game.
        - Restart: call the restart method and reset the game to a fresh state.
        - Surrender: assign the opponent as the game winner and cause the game to be over.
        - Undo: use the __pastMoves stack to return to a previous board state.
        - Ready: only run if __opponent is True, set the negamax rules of engagement to weapons free (3 seconds) and swap displayed button.
        - Time: only run if __opponent is True, set the negamax rules of engagement to weapons tight (between 3-10 seconds) and swap displayed button.

        Args:
            events (list): The current frame's events queue.
            mousePos (pg.Vector2): The current position of the mouse.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed.

        Kwargs:
            None

        Returns:
            None
        """
        # Update and display the buttons
        self.__buttons.update(events, mousePos, leftMousePressed)

        # Quit the game if the exit button is pressed
        if self.__exitButton.getPressed():
            quit("Thanks for playing!")

        # Restart the game and board if the restart button is pressed
        if self.__restartButton.getPressed():
            self.restart()
            self.__restartButton.pressedFalse()

        # End the game and set the winner as the opposing player if the surrender button is pressed
        if self.__surrenderButton.getPressed():
            self.__gameWon = True
            self.__winner = (not self.__turn) + 3
            logger.success(f"{["White", "Black"][not self.__turn]} player won by opponent surrender!")
            self.__surrenderButton.pressedFalse()

        # Set the game to the previous state if the undo button is pressed
        if self.__undoButton.getPressed():
            if not self.__pastMoves.isEmpty():
                logger.success("Move undone!")

                # Reset the frames
                self.__setFrame(self.__pastMoves.pop())

                # Ensure that if the game was won, this is changed to allow for replay of final moves
                if self.__gameWon:
                    if self.__winner > 2:
                        self.__turn = not self.__turn
                    self.__gameOver = False
                    self.__gameWon = False
                    self.__winner = None

                else:
                    # Do not swap the turn if the game was already won since this would have happened automatically
                    if self.__promotion:
                        self.__promotion = False
                        self.__board.toPromoteNone()
                    else:
                        self.__turn = not self.__turn

                    # If there is a computer opponent and it is black's turn, run the negamax algorithm, and otherwise reset the called attribute
                    if self.__opponent:
                        if self.__turn and not self.__negaMaxCalled:
                            if self.__negaMax != None and self.__negaMaxThread.is_alive():
                                self.__negaMax.stopThinking()
                            vBoard = self.__board.createVBoard(self.__turn)
                            # Make this a daemon thread, so that if somehow the main thread finishes, the negaMax thread will automatically end, since the game would be over so there would be no point in its continued existence
                            self.__negaMaxThread = threading.Thread(target=self.__negaMax.takeTurn, args=(self.__boardPos, self.__pieceSize, vBoard), daemon=True)
                            self.__negaMaxThread.start()
                        else:
                            self.__negaMaxCalled = False
                            self.__negaMax.stopThinking()

                # Reset the frames
                self.__frame = self.__createFrame()
                self.__board.updateMoves(self.__turn)
            self.__undoButton.pressedFalse()
        self.__buttons.draw(self.__image)

        # Change the ROE and swap buttons based on whichever of the AI type buttons were pressed
        if self.__opponent:
            if self.__readyButton.getPressed():
                self.__buttons.add(self.__timeButton)
                self.__negaMax.weaponsFree()
                self.__readyButton.kill()
                self.__readyButton.pressedFalse()

            if self.__timeButton.getPressed():
                self.__buttons.add(self.__readyButton)
                self.__negaMax.weaponsTight()
                self.__timeButton.kill()
                self.__timeButton.pressedFalse()

    def __displayDead(self) -> None:
        """Display all of the pieces on the dead lists."""
        if self.__whiteDead != [] or self.__blackDead != []:
            # Decide based on the turn which colour's dead are where
            if self.__turn:
                deadLists = [self.__whiteDead, self.__blackDead]
                imageLists = [self.__whitePieces, self.__blackPieces]
            else:
                deadLists = [self.__blackDead, self.__whiteDead]
                imageLists = [self.__blackPieces, self.__whitePieces]

            # Iterate through all pieces on both dead lists and, using the turn, calculate which pieces to display where, displaying them in rows of 4 with the opponent's pieces at the top and friendly pieces at the bottom
            [[self.__image.blit(imageLists[y][piece], (self.__boardPos + pg.Vector2((self.__boardSize.x + (self.__pieceSize.x * (x % 4))), (((x // 4) + (y * 4)) * self.__pieceSize.y)))) for x, piece in enumerate(colourDead)] for y, colourDead in enumerate(deadLists)]

    def __winConditions(self, swapTurn: bool=False) -> None:
        """Check if there is either a checkmate or a stalemate, and carry out the appropriate procedures for each."""
        # Check if the promotion caused a game over, and swap the parameter if swapTurn is True (i.e. take the XOR of both)
        if self.__board.getCheckmate(not (self.__turn ^ swapTurn)):
            self.__gameWon = True
            if self.__opponent:
                self.__negaMax.stopThinking()
            if swapTurn:
            # Change the turn to show the correct-coloured background if the turn is to be swapped
                self.__turn = not self.__turn
            self.__winner = self.__turn
            logger.success(f"{["White", "Black"][self.__turn]} player won by checkmate!")

        elif self.__board.getStalemate(self.__turn ^ swapTurn):
            self.__gameWon = True
            if self.__opponent:
                self.__negaMax.stopThinking()
            self.__winner = 2
            logger.success("The game ended by stalemate!")

    def __foundPromo(self) -> None:
        """If there has just been a promotion, change __promotion and generate the promotion buttons.
        
        Depending on the turn, create buttons of each piece other than pawns and kings for either colour,
        and then create buttons based on each of these images, adding them to the __promoButtons sprite group.

        Args:
            None

        Kwargs:
            None

        Returns:
            None
        """
        self.__promotion = True
        # Create the promotion buttons
        if self.__turn:
            images = [self.__blackPieces[i] for i in range(1, 5)]
        else:
            images = [self.__whitePieces[i] for i in range(1, 5)]

        # Create the image filters
        colourFilter = pg.surface.Surface(self.__pieceSize, pg.SRCALPHA)
        colourFilter.fill((191, 161, 0, 50))
        hoveringImages = [image.copy() for image in images]
        [image.blit(colourFilter, (0, 0)) for image in hoveringImages]
        clickedImages = [image.copy() for image in hoveringImages]
        [image.blit(colourFilter, (0, 0)) for image in clickedImages]

        # Go through all promotion buttons and add them to the __promoButtons Group (this is done the long way since it requires attributes to be changed as well, so iteration over a list would not work)
        offset = self.__boardPos + pg.Vector2(2 * self.__pieceSize.x, -self.__pieceSize.y)
        self.__queen = inp.Button(self.__pieceSize, offset, images[3], hoveringImages[3], clickedImages[3])
        self.__promoButtons.add(self.__queen)
        self.__bishop = inp.Button(self.__pieceSize, (offset + pg.Vector2(self.__pieceSize.x, 0)), images[2], hoveringImages[2], clickedImages[2])
        self.__promoButtons.add(self.__bishop)
        self.__knight = inp.Button(self.__pieceSize, (offset + pg.Vector2(2 * self.__pieceSize.x, 0)), images[1], hoveringImages[1], clickedImages[1])
        self.__promoButtons.add(self.__knight)
        self.__rook = inp.Button(self.__pieceSize, (offset + pg.Vector2(3 * self.__pieceSize.x, 0)), images[0], hoveringImages[0], clickedImages[0])
        self.__promoButtons.add(self.__rook)

    # Define a method to handle a current promotion
    def __currentPromo(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> None:
        """Handle a current promotion.
        
        Update the promotion buttons to get which piece the pawn will be promoted to,
        before then manually calling the board's move swap methods for it since the typical way of swapping moves has been skipped.

        Args:
            events (list): The current frame's events queue.
            mousePos (pg.Vector2): The current position of the mouse.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed.

        Kwargs:
            None

        Returns:
            None
        """
        # Go through every piece, checking for promotion
        promoted = False
        self.__promoButtons.update(events, mousePos, leftMousePressed)
        if self.__queen.getPressed():
            promoted = True
            value = 0
        elif self.__bishop.getPressed():
            promoted = True
            value = 1
        elif self.__knight.getPressed():
            promoted = True
            value = 2
        elif self.__rook.getPressed():
            promoted = True
            value = 3

        # If a promotion occurred, change attributes and update the board
        if promoted:
            self.__promotion = False
            self.__board.promoteTo(value)
            self.__board.toPromoteNone()
            self.__board.updateMoves(self.__turn)

            # Check for game won
            self.__winConditions()

            # If not, handle anything which the board class would have handled had the move progressed normally, as well as handling check
            if not self.__gameWon:
                self.__turn = not self.__turn
                self.__board.rotateBoard()
                self.__board.updateMoves(self.__turn)

                # If there is a computer opponent and it is black's turn, run the negamax algorithm, and otherwise reset the called attribute
                if self.__opponent:
                    if self.__turn and not self.__negaMaxCalled:
                        # Make this a daemon thread, so that if somehow the main thread finishes, the negaMax thread will automatically end, since the game would be over so there would be no point in its continued existence
                        self.__negaMaxThread = threading.Thread(target=self.__negaMax.takeTurn, args=(self.__boardPos, self.__pieceSize, self.__board.createVBoard(self.__turn)), daemon=True)
                        self.__negaMaxThread.start()
                    else:
                        self.__negaMaxCalled = False

        self.__promoButtons.draw(self.__image)
        self.__image.blit(self.__board.update(self.__turn, events, mousePos, leftMousePressed), self.__boardPos)

    # Define a method to update the game
    def update(self, events: list, mousePos: pg.Vector2, leftMousePressed: bool) -> pg.surface.Surface:
        """Process the user inputs, make the necessary changes to the game logic, and create and return the screen image.
        
        Decide on background colour, before checking if the game is over, and then finally if not,
        update the board and use this to update both the image and the logic.

        Args:
            events (list): The current frame's events queue.
            mousePos (pg.Vector2): The current position of the mouse.
            leftMousePressed (bool): Whether or not the left mouse button is currently being pressed.

        Kwargs:
            None

        Returns:
            The screen image that will be displayed by this object.
        """
        # Depending on whose turn it is, fill the image with their respecive colour
        if self.__turn:
            self.__image.fill("grey20")
        else:
            self.__image.fill("grey80")

        # If the game has been won, a different process will take place
        if self.__gameWon:
            self.__wonGame(events)

        elif self.__promotion:
            self.__currentPromo(events, mousePos, leftMousePressed)
            # Check if the promotion caused a game over
            self.__winConditions(True)

        else:
            # Update the board and display it onto the game image
            self.__image.blit(self.__board.update(self.__turn, events, mousePos, leftMousePressed), self.__boardPos)

            # Handle turns changing
            if self.__board.getMoved():
                # Check if there is anything which the play game class needs to handle
                self.__winConditions()

                if not self.__gameWon:
                    if self.__board.getToPromote() != None:
                        self.__foundPromo()

                    else:
                        self.__turn = not self.__turn

                # Handle any dead pieces created this turn
                dead = self.__board.getDead()
                if dead != None:
                    # If there is a list of dead, iterate through it
                    if not isinstance(dead, list):
                        [self.__whiteDead, self.__blackDead][dead[0]].append(dead[1])
                        self.__board.deadNone()
                    else:
                        [[self.__whiteDead, self.__blackDead][singleDead[0]].append(singleDead[1]) for singleDead in dead]
                        self.__board.deadNone()

                # Add the old frame to the past moves stack and create a new one
                self.__pastMoves.push(self.__frame)
                self.__frame = self.__createFrame()

                # If there is a computer opponent and it is black's turn, run the negamax algorithm, and otherwise reset the called attribute
                if self.__opponent:
                    if self.__turn and not self.__negaMaxCalled:
                        # Make this a daemon thread, so that if somehow the main thread finishes, the negaMax thread will automatically end, since the game would be over so there would be no point in its continued existence
                        self.__negaMaxThread = threading.Thread(target=self.__negaMax.takeTurn, args=(self.__boardPos, self.__pieceSize, self.__board.createVBoard(self.__turn)), daemon=True)
                        self.__negaMaxThread.start()
                    else:
                        self.__negaMax.stopThinking()
                        self.__negaMaxCalled = False

                self.__board.movedFalse()
        
        # Display the check message if necessary
        if self.__board.getCheck(self.__turn) and not self.__gameWon:
            self.__image.blit([self.__whiteCheck, self.__blackCheck][self.__turn], pg.Vector2((self.__size.x * 3/8), ((self.__boardPos.y - (self.__size.y / 10)) / 2)))

        self.__updateButtons(events, mousePos, leftMousePressed)
        self.__displayDead()
        return self.__image
