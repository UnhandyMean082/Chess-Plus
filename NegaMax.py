"""A negamax algorithm which plays chess.

This module contains the NegaMax class, and is to be used within the PlayGame module.
It handles the move timings and move choices, using a tree and the minimax algorithm,
optimised to employ alpha-beta pruning, while working with a set of virtual boards.

Classes:
    NegaMax: The chess bot.

Functions:
    None
"""

# Import modules and libraries
from loguru import logger
import mouse
import pygame as pg
import time

import Board as boa


# Create the minimax class
class NegaMax:
    """A chess engine using the negamax evaluation algorithm to identify the optimal moves.
    
    As a variation on minimax, this algorithm generates all possible boards and then goes through evaluating each one,
    assuming that each player is wanting to maximise their own points and minimise the opponent's (as chess is a zero-sum game).
    When the best board state is found, the move which lead to that branch of the decision tree is taken.

    Constructor:
        __init__(): Initialise self and attributes.

    Public Methods:
        stopThinking: Reset attributes and stop processes.
        weaponsTight: Mutator method for the __ROE and __maxDepth attributes, which changes the time constraints on when moves can be made to be more time pressured, as well as the evaluation depth.
        weaponsFree: Mutator method for the __ROE and __maxDepth attributes, which changes the time constraints on when moves can be made to be more time pressured, as well as the evaluation depth.
        takeTurn: The main method of this class, which handles all relevant others and calculates the best moves.

    Attributes:
        __piecePoints (dict): The number of points awarded in the evaluation function per piece of this type, keyed by value.
        __posPoints (dict): The number of additional points to be awarded for having pieces on corresponding squares, keyed by value.
        __possiblityPoints (int): The number of points awarded per legal move (to reward greater mobility/versatility).
        __plusPoints (dict): The number of points awarded for each specific scenario which occurs on the board.
        __perilPoints (int): The number of points added for having your own king be in check (the integer is negative).
        __thinkingTime (float): The time at which the object started thinking about the best moves to make.
        __moveComplete (bool): Whether or not a move has been made this cycle.
        __moveMade (bool): Whether the move itself has been processed.
        __bestMove (tuple): The current most effective move.
        __ROE (int): The rules of engagement, i.e. the time constraints.
        __maxDepth (int): 1 less than the maximum depth within the recursive part of the takeTurn method.
    """

    # The evaluation metrics should remain static, so they are being defined as class attributes
    # The number of pieces of each type should be multiplied by this metric to give the material score
    __piecePoints: dict = {
        4: 900,
        3: 300,
        2: 320,
        1: 500,
        0: 100
    }

    # Every piece of each team which occupies a space on the board claims a certain number of points attributed to that space depending on piece, representing control over the board
    __posPoints: dict = {
        5: [
            [-65,  23,  16, -15, -56, -34,   2,  13],
            [ 29,  -1, -20,  -7,  -8,  -4, -38, -29],
            [ -9,  24,   2, -16, -20,   6,  22, -22],
            [-17, -20, -12, -27, -30, -25, -14, -36],
            [-49,  -1, -27, -39, -46, -44, -33, -51],
            [-14, -14, -22, -46, -44, -30, -15, -27],
            [  1,   7,  -8, -64, -43, -16,   9,   8],
            [-15,  36,  12, -54,   8, -28,  24,  14]
        ],
        4: [
            [-28,   0,  29,  12,  59,  44,  43,  45],
            [-24, -39,  -5,   1, -16,  57,  28,  54],
            [-13, -17,   7,   8,  29,  56,  47,  57],
            [-27, -27, -16, -16,  -1,  17,  -2,   1],
            [ -9, -26,  -9, -10,  -2,  -4,   3,  -3],
            [-14,   2, -11,  -2,  -5,   2,  14,   5],
            [-35,  -8,  11,   2,   8,  15,  -3,   1],
            [ -1, -18,  -9,  10, -15, -25, -31, -50]
        ],
        3: [
            [-29,   4, -82, -37, -25, -42,   7,  -8],
            [-26,  16, -18, -13,  30,  59,  18, -47],
            [-16,  37,  43,  40,  35,  50,  37,  -2],
            [ -4,   5,  19,  50,  37,  37,   7,  -2],
            [ -6,  13,  13,  26,  34,  12,  10,   4],
            [  0,  15,  15,  15,  14,  27,  18,  10],
            [  4,  15,  16,   0,   7,  21,  33,   1],
            [-33,  -3, -14, -21, -13, -12, -39, -21]
        ],
        2: [
            [-167, -89, -34, -49,  61, -97, -15, -107],
            [ -73, -41,  72,  36,  23,  62,   7,  -17],
            [ -47,  60,  37,  65,  84, 129,  73,   44],
            [  -9,  17,  19,  53,  37,  69,  18,   22],
            [ -13,   4,  16,  13,  28,  19,  21,   -8],
            [ -23,  -9,  12,  10,  19,  17,  25,  -16],
            [ -29, -53, -12,  -3,  -1,  18, -14,  -19],
            [-105, -21, -58, -33, -17, -28, -19,  -23]
        ],
        1: [
            [ 32,  42,  32,  51, 63,  9,  31,  43],
            [ 27,  32,  58,  62, 80, 67,  26,  44],
            [ -5,  19,  26,  36, 17, 45,  61,  16],
            [-24, -11,   7,  26, 24, 35,  -8, -20],
            [-36, -26, -12,  -1,  9, -7,   6, -23],
            [-45, -25, -16, -17,  3,  0,  -5, -33],
            [-44, -16, -20,  -9, -1, 11,  -6, -71],
            [-19, -13,   1,  17, 16,  7, -37, -26]
        ],
        0: [
            [  0,   0,   0,   0,   0,   0,  0,   0],
            [ 98, 134,  61,  95,  68, 126, 34, -11],
            [ -6,   7,  26,  31,  65,  56, 25, -20],
            [-14,  13,   6,  21,  23,  12, 17, -23],
            [-27,  -2,  -5,  12,  17,   6, 10, -25],
            [-26,  -4,  -4, -10,   3,   3, 33, -12],
            [-35,  -1, -20, -23, -15,  24, 38, -22],
            [  0,   0,   0,   0,   0,   0,  0,   0]
        ]
    }

    # The length of the legal moves list is multiplied by this metric to give the mobility/move possibility score
    __possibilityPoints: int = 10

    # A dictionary of all "bonus" point gains and losses:
    # Index 0: both bishops on the board
    # Index 1: both rooks on the board
    # Index 2: doubled pawns
    # Index 3: isolated pawns
    # Index 4: multiplied by number of central pawns (centre 4 files)
    __plusPoints: dict = {
        "b": 50,
        "r": -30,
        "d": -50,
        "i": -70,
        "c": 30,
    }

    # There is a flat point deficit of 300 if the king is in check
    __perilPoints: int = -300

    # Initialise an object of this class when called
    def __init__(self):
        logger.info("NegaMax created")
        # Define attributes
        self.__thinkingTime: float = 0
        self.__moveComplete: bool = True
        self.__moveMade: bool = True
        self.__bestMove: tuple = ()
        self.__ROE: int = 10
        self.__maxDepth: int = 2

    def __startThinking(self, board: boa.VirtualBoard) -> None:
        """Set the thinking time attribute as the current time and the paused attribute to False."""
        logger.info("Thread started")
        self.__thinkingTime = time.perf_counter()
        self.__moveComplete = False
        self.__moveMade = False
        self.__bestMove = board.getAllLegalMoves()[0]
        logger.debug(f"Default best move: {self.__bestMove}")

    def stopThinking(self) -> None:
        """Reset all attributes and stop all current processes."""
        logger.info("Thread stopped")
        self.__thinkingTime = 0
        self.__moveComplete = True
        self.__moveMade = True

    def weaponsTight(self) -> None:
        """Set the rules of engagement attribute to 10 seconds and depth to 2."""
        self.__ROE = 10
        self.__maxDepth = 2

    def weaponsFree(self) -> None:
        """Set the rules of engagement attribute to 3 seconds and depth to 1."""
        self.__ROE = 3
        self.__maxDepth = 1

    def __boardEval(self, board: boa.VirtualBoard, speed: bool) -> int:
        """Given a virtual board and a speed, make an evaluation of the current board position.
        
        In this evaluation, positive and negative depend on the turn.
        The returned value can be seen as an arbitrary measure of the likelihood of white to win.
        Since this is one of the most crucial methods to be efficient, due to the large number of times it will be run
        and the fact that it will be run in a very time-pressured situation, code readability will have to be sacrificed for efficiency.

        Args:
            board (boa.VirtualBoard): The board whose position is being evaluated.
            speed (bool): True for fast, which only considers piece possibility and peril, and False for a full evaluation.

        Kwargs:
            None

        Returns:
            The integer evaluation of the board position.
        """
        # Start at -10000 as the score since the presence of the king adds this amount - any board without a king therefore would be massively negative and not likely to be chosen
        eval = -10000

        # Run different operations based on the speed required
        if speed:
            # Iterate through every board square
            for column in board.getBoard():
                for piece in column:
                    
                    # Only bother with the subsequent actions if the square contains a piece
                    if piece != None:

                        # Add score if the piece is friendly, and subtract it if it is not
                        if piece % 2 == board.getTurn():
                            if piece < 50:
                                eval += self.__piecePoints[piece // 10]
                            else:
                                eval += 10000
                        else:
                            if piece < 50:
                                eval -= self.__piecePoints[piece // 10]

            # Add an arbitrary 100 to balance against the full evaluation
            eval += self.__possibilityPoints * len(board.getAllLegalMoves()) + self.__perilPoints * (board.getCheck() - board.getCheck(turnOffset=True)) + 100

        else:
            bishops = 0
            rooks = 0
            pawnRows = []
            # Iterate through every board square
            for x, column in enumerate(board.getBoard()):
                for y, piece in enumerate(column):

                    # Only bother with the subsequent actions if the square contains a piece
                    if piece != None:

                        # Add score if the piece is friendly, and subtract it if it is not
                        if piece % 2 == board.getTurn():
                            eval += self.__posPoints[piece // 10][y][x]

                            # Alter the additional variables if the piece is not a king
                            if piece < 50:
                                eval += self.__piecePoints[piece // 10]
                                if piece // 10 == 3:
                                    bishops += 1
                                elif piece < 20:
                                    if piece < 10:
                                        pawnRows.append(x)
                                    else:
                                        rooks += 1
                            else:
                                eval += 10000
                        else:
                            if piece < 50:
                                eval -= self.__piecePoints[piece // 10]

            # Handle all of the additional variables
            if bishops == 2:
                eval += self.__plusPoints["b"]
            if rooks == 2:
                eval += self.__plusPoints["r"]
            prev = -1
            solo = -1

            # Iterate through the pawn rows list
            for row in pawnRows:

                # Check whether the row is one of the central ones, in order to add that bonus
                if row in [2, 3, 4, 5]:
                    eval += self.__plusPoints["c"]

                # Check whether there are multiple pawns on the same line
                if prev == row:
                    eval += self.__plusPoints["d"]
                
                # Check for isolated pawns using the solo pointer
                elif prev < row - 1:
                    if prev == solo:
                        eval += self.__plusPoints["i"]
                    solo = row

                # If there are 2 consecutive rows, reset solo
                else:
                    solo = -1

                prev = row

            # Add the extras
            eval += self.__possibilityPoints * len(board.getAllLegalMoves()) + self.__perilPoints * (board.getCheck() - board.getCheck(turnOffset=True))

        logger.debug(f"Board evaluation: {eval}")
        return eval

    def __makeAMove(self, boardPos: pg.Vector2, squareSize: pg.Vector2, promotion: bool) -> None:
        """Use the mouse library to control the mouse and make the move for black when ready."""
        logger.info(f"Move made at {time.perf_counter()}")
        # Only run this if the move has not already been made
        if not self.__moveMade:
            # Find the centre of the starting square and the ending square
            centrePos = lambda square: boardPos + ((square.elementwise() + 0.5) * squareSize.x)
            start = centrePos(self.__bestMove[0])
            end = centrePos(self.__bestMove[1])

            # Since threading is in effect, all commands can be done at once and the inputs will still all register
            mouse.move(start.x, start.y, True, 0.1)
            time.sleep(0.05)
            mouse.press()
            time.sleep(0.05)
            mouse.release()
            time.sleep(0.05)
            mouse.move(end.x, end.y, True, 0.1)
            time.sleep(0.05)
            mouse.press()
            time.sleep(0.05)
            mouse.release()

            # If a promotion needs to occur, select the queen
            if promotion:
                logger.debug("Promotion should occur")
                time.sleep(0.5)
                mouse.move((boardPos.x + 2.5 * squareSize.x), (boardPos.y - 0.5 * squareSize.y), True, 0.1)
                time.sleep(0.05)
                mouse.press()
                time.sleep(0.05)
                mouse.release()

    def __orderMoves(self, board: boa.VirtualBoard, moves: list) -> list:
        """Take a moves list and order it roughly based on how likely the move is to be good (best to worst).
        
        Sort the moves of a moves list based on potential piece captures, specialty and proximity to the centre of the board
        to get a rough idea of the moves most likely to produce the best results.
        
        Args:
            board (boa.VirtualBoard): The current board state.
            moves (list): The current legal move list.

        Kwargs:
            None

        Returns:
            The sorted moves list.    
        """
        # Start by sorting based on taken piece value
        taken = {
            5: [],
            4: [],
            3: [],
            2: [],
            1: [],
            0: [],
            None: []
        }
        for move in moves:
            if board[int(move[1].x)][int(move[1].y)] == None:
                # Account for en passant taking a pawn but not looking like it does
                if len(move) == 3 and move[2] == "e":
                    taken[0].append(move)
                else:
                    taken[None].append(move)
            else:
                taken[board[int(move[1].x)][int(move[1].y)] // 10].append(move)

        final = []
        # If the move is a special move, it will more often than not produce a better-than-average result
        for takesPiece in taken:
            special = []
            regular = []
            for move in taken[takesPiece]:
                if len(move) == 3:
                    special.append(move)
                else:
                    regular.append(move)

            # Get the distance between the move's file and the centre of the board, and use this to roughly sort the rest, since typically moves closer to the centre produce better results
            prox = lambda move: abs(((move[0].x + move[1].x) / 2) - 3.5)
            special.sort(key=prox)
            regular.sort(key=prox)

            # Add the lists to final
            final += special
            final += regular
        return final

    def takeTurn(self, boardPos: pg.Vector2, squareSize: pg.Vector2, board: boa.VirtualBoard, depth: None | int=None, alpha: int=-10000, beta: int=10000) -> None:
        """Generate and evaluate all possible moves to get the best one, while routinely checking the process against the time limit.
        
        Run checks depending on the depth, as well as checking against the time limit to decide whether a move needs to be forced,
        before reaching the main part of the negamax algorithm - the recursive part - which uses the fact that max(a, b) == - min(-a, -b)
        to efficiently evaluate the best moves for either side and be able to set the __bestMove attribute.

        Args:
            boardPos (pg.Vector2): The position of the board on the screen in pixels.
            squareSize (pg.Vector2): The size of each square, and thus piece, in pixels.
            board (boa.VirtualBoard): The current board state.

        Kwargs:
            depth (None | int) = None: The current layer/recursion depth that this function has been called at.
            alpha (int): The maximum pointer - the minimum possible score black (the computer) is guaranteed to get currently.
            beta (int): The minimum pointer - the maximum possible score white (the player) is guaranteed to get currently.

        Returns:
            None
        """
        # If depth was not passed, set it to the maximum depth
        if depth == None:
            depth = self.__maxDepth
        logger.debug(f"The depth is {depth} and the current board is {board.getBoard()}")

        # If this is the first call, start the thinking time
        if depth == self.__maxDepth:
            self.__startThinking(board)

        # Check the thinking time against the time limit
        if time.perf_counter() - self.__thinkingTime >= self.__ROE:
            # Forcibly make the move with the best current move
            # If there is a pawn at the move's starting positiona dn the ending position is at y = 0, promote should be True
            if board.getBoard()[int(self.__bestMove[0].x)][int(self.__bestMove[0].y)] < 10 and self.__bestMove[1].y == 0:
                promote = True
            else:
                promote = False
            self.__makeAMove(boardPos, squareSize, promote)
            self.stopThinking()

        # If this is the final call, simply return the position evaluation
        if depth == 0:
            # Depending on the ROE and remaining time, decide whether to use the heuristic method or the very heuristic method
            if time.perf_counter() - self.__thinkingTime > self.__ROE - 0.5:
                speed = True
            else:
                speed = False
            return self.__boardEval(board, speed)
        
        # Move making and recursive logic
        if not self.__moveComplete:
            maxScore = -10000

            # Iterate through every possible move and generate a new board of it with which to call negamax again
            for move in self.__orderMoves(board.getBoard(), board.getAllLegalMoves()):
                logger.debug(f"The depth is {depth} and the current move is {move}")
                newBoard = boa.VirtualBoard(board.getTurn())
                newBoard.setBoard(board.getBoard())
                newBoard.makeMove(move)
                score = - self.takeTurn(boardPos, squareSize, newBoard, depth - 1, -beta, -alpha)

                # If the current score is higher than the maximum, change the maximum and if it is the first move, change the first move
                logger.debug(f"Score: {score}, maxScore: {maxScore}")
                if score > maxScore:
                    maxScore = score
                    if depth == self.__maxDepth:
                        self.__bestMove = move

                # Prune the rest of the branch if it will never occur
                alpha = max(alpha, maxScore)
                if alpha >= beta:
                    break

            if depth != self.__maxDepth:
                return maxScore
        else:
            return -10000

        logger.info(f"Move found at {time.perf_counter()}")

        # If this is the outermost layer, stop thinking and make the move as long as the 3 second time limit has been reached
        # Give a delay if processing for the frame finished early
        time.sleep(max(3 + self.__thinkingTime - time.perf_counter(), 0))
        # If there is a pawn at the move's starting positiona dn the ending position is at y = 0, promote should be True
        if board.getBoard()[int(self.__bestMove[0].x)][int(self.__bestMove[0].y)] < 10 and self.__bestMove[1].y == 0:
            promote = True
        else:
            promote = False
        self.__makeAMove(boardPos, squareSize, promote)
        self.stopThinking()
