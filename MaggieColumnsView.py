# MaggieColumnsView
# This module implements the pygame UI for the game.

import MaggieColumnsModel
import pygame
import random
from math import floor, ceil

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
        self._score_surface = None # The score is a pygame Font object that is a pygame surface.
        pygame.display.set_caption('Maggie Columns')
        # Blit the background image onto the surface.
        self._surface.blit(self._images['BG'], (0, 0)) # (0, 0) places it in the upper right corner.
        # Load Sounds
        pygame.mixer.music.load('./assets/ttm.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1) # The -1 argument causes the music to loop indefinitely.
        self._rotate_sound = pygame.mixer.Sound('./assets/swish.wav')
        self._rotate_sound.set_volume(0.25) # Lower the volume, relative to the other sounds.
        self._landed_sound = pygame.mixer.Sound('./assets/landed.wav')
        self._match_sound = pygame.mixer.Sound('./assets/match.wav')

    
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
        if self._next_faller: # If there is a next faller. At the start, this is None.
            # The next faller becomes the current faller. And the new next faller is initialized (but not inserted).
            self._current_faller, self._next_faller = self._next_faller, MaggieColumnsModel.Faller()
            self._current_faller.insert(self._game_board.board(), random.randint(0, 5))
        else:
            # Create two fallers to be the current and next faller.
            self._current_faller, self._next_faller = MaggieColumnsModel.Faller(), MaggieColumnsModel.Faller()
            self._current_faller.insert(self._game_board.board(), random.randint(0, 5)) # Insert the current faller.
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
                        self._rotate_sound.play()
        
        if self._faller_active:
            self._advance_faller()
            if self._current_faller.frozen: # If after advancing, the faller has reached it's landed state,
                self._landed_sound.play()
                self._delete_current_faller()
        else: # Faller is not active.
            self._process_matches()

    def _redraw_frame(self) -> None:
        """Draw the background image, and all the pieces on top of it."""
        # First, draw the background image.
        self._surface.blit(self._images['BG'], (0, 0))
        # Then, draw all the pieces.
        for row in range(3, MaggieColumnsModel.NUMBER_OF_ROWS + 3): # +3 because we want rows 3 through 16. 0 through 2 are hidden.
            for col in range(MaggieColumnsModel.NUMBER_OF_COLUMNS):
                if type(self._game_board.board()[col][row]) == MaggieColumnsModel.Piece:
                    self._draw_piece(col, row - 3, self._game_board.board()[col][row]) # To account for hidden rows when drawing.
        # Draw the "next" faller.
        self._draw_next_faller()
        # Draw the score.
        self._draw_score()

        pygame.display.flip()
    
    # Private methods called upon initialization.
    def _initialize_image_names(self) -> None:
        self._images = {
            'BG': pygame.transform.scale(pygame.image.load(f"./assets/BG_work.png"), self._surface_size),
            'H' : pygame.transform.scale(pygame.image.load(f"./assets/Smile.png"), self._cell_size),
            'S' : pygame.transform.scale(pygame.image.load(f"./assets/Pout.png"), self._cell_size),
            'M' : pygame.transform.scale(pygame.image.load(f"./assets/Moustache.png"), self._cell_size),
            'R' : pygame.transform.scale(pygame.image.load(f"./assets/Rude.png"), self._cell_size),
            'G' : pygame.transform.scale(pygame.image.load(f"./assets/Sparkle.png"), self._cell_size),
            'L' : pygame.transform.scale(pygame.image.load(f"./assets/Lick.png"), self._cell_size),
            'B' : pygame.transform.scale(pygame.image.load(f"./assets/BlownUp.png"), self._cell_size),
            'O' : pygame.transform.scale(pygame.image.load(f"./assets/Donut.png"), self._cell_size),
            'Falling': pygame.transform.scale(pygame.image.load(f"./assets/Falling.png"), self._cell_size),
            'Landed' : pygame.transform.scale(pygame.image.load(f"./assets/Landed.png"), self._cell_size),
            'Matched': pygame.transform.scale(pygame.image.load(f"./assets/Matched.png"), self._cell_size)
        }

    # Private methods called by the _handle_events method.
    def _resize_surface(self, new_size:(int, int)) -> None:
        """Change the _surface_size instance variable and re-define surface to be resized."""
        self._surface_size = new_size
        self._cell_size = (floor((45/1120) * self._surface_size[0]), floor((45/630) * self._surface_size[1]))
        self._surface = pygame.display.set_mode(self._surface_size, pygame.RESIZABLE) # Updated _surface_size.
        self._initialize_image_names()
        self._reset_cached_score_surface()

    def _advance_faller(self) -> None:
        """Advance the faller."""
        if self._faller_controller == 0:
            self._current_faller.fall()

    def _delete_current_faller(self) -> None:
        """Delete current faller and change the gamestate to be looking for matches."""
        del self._current_faller
        self._faller_active = False
        self._looking_for_matches = True
    
    def _process_matches(self) -> None:
        """Handle the match process. Tell the game board to start looking for matches. Reinstate the faller once finished."""
        while True:
            # This method of the game board marks pieces as matched.
            if self._game_board.find_matches(): # If matches are found (this method of the game board also marks pieces as matched).
                self._redraw_frame() # Redraw to show the matched pieces.
                self._match_sound.play()
                self._clock.tick(1)
                if self._game_board.delete_matched_pieces(): # If any pieces were deleted.
                    self._reset_cached_score_surface()
                    self._redraw_frame() # Draw the frame, showing the gaps where pieces used to be.
                    self._clock.tick(10)
                    self._game_board.apply_gravity() # Make the pieces fall.
                    self._redraw_frame() # Show that they've fallen.
                else:
                    break
            else:
                break
        self._create_new_faller() # After the entire match process is complete, insert a new faller.

    # Private methods for drawing various objects.
    # Note that self._surface_size is a tuple containing the (width, height) of the surface, in pixels.
    # Dividing x and y by 1120 and 630 respectively ensures that the proportions are correct regardless of window size.
    def _draw_piece(self, col: int, row: int, piece: MaggieColumnsModel.Piece) -> None:
        """Draw the piece using the specified column and row."""
        # Find the coordinates for the piece.
        x_coord = floor((290 / 1120) * self._surface_size[0] + col * self._cell_size[0])
        y_coord = floor((22.5 / 630) * self._surface_size[1] + row * self._cell_size[1])
        # Blit the image onto the surface.
        if piece.is_falling():
            self._surface.blit(self._images['Falling'], (x_coord, y_coord))
            self._surface.blit(self._images[piece.sticker()[1]], (x_coord, y_coord))
        elif piece.is_landed():
            self._surface.blit(self._images['Landed'], (x_coord, y_coord))
            self._surface.blit(self._images[piece.sticker()[1]], (x_coord, y_coord))
        elif piece.is_matched():
            self._surface.blit(self._images[piece.sticker()[1]], (x_coord, y_coord))
            self._surface.blit(self._images['Matched'], (x_coord, y_coord))
        else:
            self._surface.blit(self._images[piece.sticker()[1]], (x_coord, y_coord))

    def _draw_next_faller(self) -> None:
        """Draw the pieces of the next faller to the right of the board."""
        top_x_coord = floor((670 / 1120) * self._surface_size[0])
        top_y_coord = floor((155.5 / 630) * self._surface_size[1])
        for index in range(3): # The next faller has 3 pieces.
            self._surface.blit(self._images[f"{self._next_faller[index].sticker()[1]}"], (top_x_coord, top_y_coord))
            top_y_coord += self._cell_size[1]
    
    def _draw_score(self) -> None:
        """Draw the score in the score space to the right of the board."""
        if self._score_surface == None: # If there is no score surface, make a new one.
            self._font_object = pygame.font.Font(None, 40) # None loads pygame default font. Size 40.
            self._score_surface = self._font_object.render(f"{self._game_board.score()}", True, [0, 0, 0])
        
        # Decide where to draw the score, based on the size of the text.
        # The size of the text is obtained using pygame.font.Font.size() which takes a string as an argument, and returns a tuple
        # of the dimensions required to display that text.
        score_txt = f'{self._game_board.score()}'
        score_x_coord = floor((693.5 / 1120) * self._surface_size[0] - (self._font_object.size(score_txt)[0] / 2))
        score_y_coord = floor((450.5 / 630 * self._surface_size[1]) - (self._font_object.size(score_txt)[1] / 2))
        # Blit the score surface onto the main surface.
        self._surface.blit(self._score_surface, (score_x_coord, score_y_coord))
    
    def _reset_cached_score_surface(self) -> None:
        """Delete the cached score font object so that a new one can be created."""
        self._score_surface = None


if __name__ == '__main__':
    MaggieGame().run()

