"""The main module of a chess game.

This module handles the game loop and uses the Game class from the Game module for all of the game logic.
It contains a core while loop which runs the game and every cycle it checks for a quit event,
calls the update function of the Game class, which updates both the logic and the screen,
and then displays this screen and handles the timing (framerate).

Classes:
    None

Functions:
    None
"""

# Chess Plus
# Author: Aarav Agarwal

# Import modules and libraries
import ctypes
import datetime
from loguru import logger
import os
import pygame as pg
import sys
import time

import Game as gam

# Start pygame and set up video and window settings
pg.init()
# Ensure the window starts at the centre of the screen
os.environ["SDL_VIDEO_CENTERED"] = "True"

# Define a logging system so that tests are sent to a file
logLevel = 3
# Create a folder called "Logs" if one does not already exist
if not os.path.exists("Logs"):
    os.makedirs("Logs")
# Only log info to file
logger.remove()
# Format the logs
logger.add("Logs/Chess_{time}.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level=["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"][logLevel])
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
logger.info("Running Chess")
# Get the path of the directory this program is in
dirPath = os.path.dirname(os.path.abspath(__file__))
logger.debug(dirPath)
# Enter the "Logs" directory within the directory this program is in
goalDir = os.path.join(dirPath,"Logs")

logger.debug(os.path.abspath(goalDir))
# Iterate through all the files in the goal directory
for file in os.listdir(goalDir):
    if file.endswith(".log"):
        # Get the time since the file was last modified, converting it into struct_time
        modSec = os.path.getmtime(os.path.join(goalDir,file))
        lastModified = time.localtime(modSec)
        # Get the current date
        dt = datetime.datetime(*lastModified[:6])
        # Remove any files older than yesterday
        if (datetime.date.today() - dt.date()).days > 1:
            logger.debug(f"Removing file {os.path.join(goalDir,file)}")
            os.remove(os.path.join(goalDir,file))

# Account for high DPI displays
ctypes.windll.user32.SetProcessDPIAware()
displayInfo = pg.display.Info()
# Use ctypes for high DPI displays
screenSize = pg.Vector2(ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
screen = pg.display.set_mode(screenSize, pg.FULLSCREEN)
pg.display.set_caption("Chess Plus")
pg.display.set_icon(pg.image.load(dirPath + "\\Assets\\Chess Icon.png").convert_alpha())

# Set up game settings
framerate = 60
game = gam.Game(screenSize)

# Run the game loop, ensuring that the it only runs when this file has been opened specifically
if __name__ == "__main__":

    logger.debug("Game loop started")
    while True:

        startFrameTime = time.perf_counter()

        # Define a process to allow the game to be exited
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                quit("Thanks for playing!")

        # Handle updating of the game logic and screen
        game.update(events, screen)
        pg.display.flip()
    
        # Handle timing
        endFrameTime = time.perf_counter()
        # Give a delay if processing for the frame finished early
        time.sleep(max((1.0 / framerate) + startFrameTime - endFrameTime, 0))
