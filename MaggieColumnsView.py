# MaggieColumnsView
# This module implements the pygame UI for the game.

import MaggieColumnsModel
import pygame
import random
from math import floor

class MaggieGame:
    """This class controls the process of running the MaggieColumns game.
    
    The code consists of a loop that operates as follows:

    while running:
        handle events
        redraw frame
    """


    def __init__(self):
        # Define Initial Values.
        self._running = True
        self._faller_active = False
        self._current_faller = None
        self._next_faller = None
        self._looking_for_matches = False
        self._surface_size = (1120, 630) # Initial window size.
        self._cell_size = (45, 45)
        self._faller_controller = 0 # Controls when the faller falls.
        self._game_board = MaggieColumnsModel.Board()
        # Create image dictionary containing filenames.
        self._initialize_image_names()
        # Initialize pygame.
        pygame.init()
        self._clock = pygame.time.Clock()
        self._surface = pygame.display.set_mode(self._surface_size, pygame.RESIZABLE)
        # Load the background image and scale it to match the surface.
        self._background_image = pygame.image.load(f"./assets/{self._images['BG']}")
        self._background_image_scaled = pygame.transform.scale(self._background_image, self._surface_size)
        # Blit the background image onto the surface.
        self._surface.blit(self._background_image_scaled, (0, 0)) # (0, 0) places it in the upper right corner.
    
    def run(self) -> None:
        """Run the MaggieColumns game."""
        self._create_new_faller()
        
        while self._running:
            self._handle_framerate()
            self._handle_events()
            self._redraw_frame()

    # Private methods called to start the game.
    def _create_new_faller(self) -> None:
        """Cycle to the next faller, or create both a current and next faller if starting the game."""
        # if self._next_faller: # If there is a next faller, cycle it to be the current faller and generate a new 'next' faller.
        #     self._current_faller = self._next_faller
        #     # Insert faller in random column.
        #     self._next_faller = MaggieColumnsModel.Faller(self._game_board.board(), random.randint(0, 5))
        # else:
        #     self._current_faller = MaggieColumnsModel.Faller(self._game_board.board(), random.randint(0, 5))
        #     self._next_faller = MaggieColumnsModel.Faller(self._game_board.board(), random.randint(0, 5))
        self._current_faller = MaggieColumnsModel.Faller(self._game_board.board(), random.randint(0, 5))
        self._faller_active = True



    # Private methods called by main game loop.
    def _handle_framerate(self) -> None:
        """Tick the clock, and advance the faller controller value."""
        self._clock.tick(60) # 60 Frames per second.
        self._faller_controller = (self._faller_controller + 1) % 60
    
    def _handle_events(self) -> None:
        """Handle pygame events and player inputs. Call functions to handle the landing and cycling of fallers."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                self._resize_surface(event.size)
            elif event.type == pygame.KEYDOWN:
                if self._faller_active:
                    if event.key == pygame.K_LEFT: # Left Arrow Key
                        self._current_faller.move(self._current_faller.column_num - 1)

                    if event.key == pygame.K_RIGHT: # Right arrow key.
                        self._current_faller.move(self._current_faller.column_num + 1)

                    if event.key == pygame.K_DOWN: # Down arrow key.
                        self._current_faller.fall()

                    if event.key == pygame.K_SPACE: # Space bar.
                        self._current_faller.rotate()
        
        if self._faller_active:
            self._advance_faller()
            if self._current_faller.frozen: # If after advancing, the faller has reached it's landed state,
                self._delete_current_faller()
        else: # Faller is not active.
            self._process_matches()

    def _redraw_frame(self) -> None:
        """Draw the background image, and all the pieces on top of it."""
        # First, draw the background image.
        self._surface.blit(self._background_image_scaled, (0, 0))
        # Then, draw all the pieces.
        for row in range(3, MaggieColumnsModel.NUMBER_OF_ROWS + 3): # +3 because we want rows 3 through 16. 0 through 2 are hidden.
            for col in range(MaggieColumnsModel.NUMBER_OF_COLUMNS):
                if type(self._game_board.board()[col][row]) == MaggieColumnsModel.Piece:
                    self._draw_piece(col, row - 3, self._game_board.board()[col][row]) # To account for hidden rows when drawing.
        pygame.display.flip()
    
    # Private methods called upon initialization.
    def _initialize_image_names(self) -> None:
        """Create a dictionary containing all the file names used in the game."""
        self._images = {
            'BG': 'BG_work.png',
            'H' : 'Smile.png',
            'S' : 'Pout.png',
            'M' : 'Moustache.png',
            'R' : 'Rude.png',
            'G' : 'Sparkle.png',
            'L' : 'Lick.png',
            'B' : 'BlownUp.png',
            'O' : 'Donut.png'
        }

    # Private methods called by the _handle_events method.
    def _resize_surface(self, new_size:(int, int)) -> None:
        """Change the _surface_size instance variable and re-define surface to be resized."""
        self._surface_size = new_size
        self._cell_size = (floor((45/1120) * self._surface_size[0]), floor((45/630) * self._surface_size[1]))
        self._surface = pygame.display.set_mode(self._surface_size, pygame.RESIZABLE) # Updated _surface_size.
        self._background_image_scaled = pygame.transform.scale(self._background_image, self._surface_size)

    def _advance_faller(self) -> None:
        """Advance the faller."""
        if self._faller_controller == 0:
            self._current_faller.fall()

    def _delete_current_faller(self) -> None:
        """Delete current faller and change related bool values."""
        print(f'Deleting faller {[s.sticker() for s in self._current_faller._faller]}')
        del self._current_faller
        self._faller_active = False
        self._looking_for_matches = True
    
    def _process_matches(self) -> None:
        """Handle the match process. Tell the game board to start looking for matches. Reinstate the faller once finished."""
        if self._looking_for_matches:
                self._game_board.find_matches()
                self._looking_for_matches = False
        else: # No longer looking for matches, the previous if statement found them all.
            if self._game_board.handle_match_process(): # Deletes matched pieces (if any) and returns True if some were deleted.
                self._looking_for_matches = True # Begin looking again, because if pieces fall, new matches can arise.
            else: # If nothing was deleted, then we can insert another faller.
                self._create_new_faller()


    # Private method to draw pieces.
    def _draw_piece(self, col: int, row: int, piece: MaggieColumnsModel.Piece) -> None:
        """Draw the piece using the specified column and row."""
        # Find the coordinates for the piece.
        x_coord = floor((290 / 1120) * self._surface_size[0] + col * self._cell_size[0])
        y_coord = floor((22.5 / 630) * self._surface_size[1] + row * self._cell_size[1])
        # Load the image for the piece, and scale it appropriately.
        piece_image = pygame.image.load(f"./assets/{self._images[piece.sticker()[1]]}")
        piece_image_scaled = pygame.transform.scale(piece_image, self._cell_size) # Scales the image to fit the cells.
        # Blit the image onto the surface.
        # print(x_coord, y_coord)
        self._surface.blit(piece_image_scaled, (x_coord, y_coord))

    





if __name__ == '__main__':
    MaggieGame().run()

