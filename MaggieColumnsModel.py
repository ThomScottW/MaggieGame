# MaggieColumns Model

# This module implements the rules of the game of columns.
"""
Features that work so far:
 - Falling
 - Random Column Picking
 - Random Piece Generation
 - Rotation

To do:
 - To do: Moving
 - To do: Matching
 - To do: Falling after matching

"""

from random import randint

NUMBER_OF_ROWS = 13
NUMBER_OF_COLUMNS = 6
MAGGIE_JEWELS = {
    1: 'H', # Happy Maggie. Smiling Sticker.
    2: 'S', # Sad Maggie. Pouting Sticker
    3: 'K', # Kissing Maggie. Kissing face sticker.
    4: 'R', # Rude Magggie. Big Mouth filter with 'rude' written. 
    5: 'G', # Glowing Maggie. Bear Filter with sparkles.
    6: 'L', # Licking Maggie. Tongue sticking out filter.
    7: 'B'  # Blown up Maggie. 
}

class GameOverError(Exception):
    pass


class Piece:
    """The 'jewel' in the game of columns. Randomly generated using randint from random. 

    Each piece has 4 differents states.
    Falling: Upon initialization. Surrounded with '[]'.
    Landed: Upon landing. Surrounded with '||'.
    Frozen: After being 'set' in the board. 
    Matched: Surrounded with '**'. Sparkles in the graphical implementation.

    Jewels are created using numerical values and each have one of seven unique colors/pictures representing them. (Different stickers of Maggie)
    """
    def __init__(self):
        self._pick_sticker()
        # These 4 bool values represent the states of the piece.
        self._falling = True
        self._landed = False
        self._frozen = False
        self._matched = False
    

    def sticker(self):
        """Return the sticker of the piece, formatted according to the piece's current state."""
        if self._falling:
            return f'[{self._sticker}]'
        elif self._landed:
            return f'|{self._sticker}|'
        elif self._frozen:
            return f' {self._sticker} '
        elif self._matched:
            return f'*{self._sticker}*'

    def land(self):
        self._falling = False
        self._landed = True
    
    def unland(self):
        self._landed = False
        self._falling = True
    
    def freeze(self):
        self._landed = False
        self._frozen = True
    
    def matched(self):
        self._frozen = False
        self._matched = True

    def _pick_sticker(self):
        """Randomly select an integer to use as a key to the MAGGIE_JEWELS dictionary to pick a sticker for the piece."""
        random_number = randint(1, 7)
        self._sticker = MAGGIE_JEWELS[random_number]
        

class Faller:
    """This is the part of the MaggieColumns game that the player has control over.
    
    Upon initialization, the faller needs the game board, and the number of the index of the current column.
    Additionally, the _faller attribute of this object is composed of three Jewel object, in the form of a list. Ex: [Jewel1, Jewel2, Jewel3]
    The faller can be acted upon while it is in the falling or landed state. It should be deleted when frozen.
    If the faller freezes before it is fully on the board, then the game ends.
    """
    def __init__(self, game_board:[[int]], column_num:int):
        self._faller = self._assign_pieces()
        # Designate a top, bottom, and middle piece. For the purpose of rotating them.
        self._split_into_parts()
        # Designate the column that the faller currently resides in.
        self.column_num = column_num
        self._current_column = game_board[column_num]
        self._game_board = game_board
        # Insert the faller into the column.
        self._insert_faller()
        # These 3 bool values represent the state of the faller.
        self._falling = True
        self.landed = False
        self.frozen = False
        # This bool is true if the faller is completely visible on the board.
        self._on_board = False
    
    def fall(self):
        """Causes the faller to fall.

        Falling is a multi-step process.

        First, check if there is space below the faller. 
        Additionally, the space below is the bottom of the column, or the one after it is full, the faller lands.
        Second, copy the contents of the faller one space down.
        Third, the space where the 'top piece' of the faller used to be is replaced with a zero.

        If this is called on a landed faller, the faller freezes.

        The fall method will raise a game over error if a faller freezes before being fully visible.
        """
        bottom_index = self._find_bottom_index()
        # If the bottom index is 5, it means that all 3 pieces of the faller are visible on the board.
        if bottom_index == 5:
            self._on_board = True
        # If the faller is already landed, and this method is called, there is special behavior.
        if self.landed:
            # If the faller is on board, then freeze it.
            if self._on_board:
                self._freeze_faller()
                self._replace_faller(bottom_index)
            # Otherwise, freeze the faller, and then end the game. 
            else:
                self._freeze_faller()
                self._replace_faller(bottom_index)
                raise GameOverError
        # Otherwise, follow the normal procedure for falling.
        elif self._space_available():
            if self._faller_is_landing():
                self._land_faller()
            self._current_column[bottom_index - 1:bottom_index + 2] = self._faller # Lower the faller.
            self._current_column[bottom_index - 2] = 0 # Changes the space above the faller back to 0.
    
    def rotate(self) -> None:
        """Rotate the faller. That is, cycle the pieces of the faller so that the bottom is on top, top goes to middle, middle goes to bottom."""
        bottom_index = self._find_bottom_index()
        self._top_piece, self._middle_piece, self._bottom_piece = self._bottom_piece, self._top_piece, self._middle_piece
        self._faller = [self._top_piece, self._middle_piece, self._bottom_piece]
        self._replace_faller(bottom_index)

    def move(self, new_column_num: int) -> None:
        """Move the faller to a new column.

        Check if the new column is empty, then copy the faller to the new column, then set the old faller space back to zeroes.
        This method should do nothing if the faller is on the edges of the board or if there is no space to move the faller.
        """
        # First, the move is checked to ensure the faller is not attempting to move outside the board.
        if self._is_valid_move(new_column_num): 
            # The new column is assigned via indexing the game board.
            new_column = self._game_board[new_column_num]
            # If there is space to move the faller, proceed.
            if self._check_new_column(new_column):
                bottom_index = self._find_bottom_index()
                # Copy the contents of the faller to the next column.
                new_column[bottom_index - 2:bottom_index + 1] = self._faller
                # Set the old faller space to zero.
                self._current_column[bottom_index - 2: bottom_index + 1] = [0, 0, 0]
                # Update the relevant attributes.
                self._current_column = self._game_board[new_column_num]
                self.column_num = new_column_num
                # Refresh the state of the faller in case it needs to be unlanded.
                self._refresh_faller_state()
            else:
                return
        else:
            return




        

    # Methods used by the faller to be aware of its surroundings.
    def _faller_is_landing(self) -> bool:
        bottom_index = self._find_bottom_index()
        if bottom_index == 14:
            return True
        elif self._current_column[bottom_index + 2] != 0:
            return True
        else:
            return False

    def _space_available(self) -> bool:
        """Return true if there is space below the faller. Otherwise, return false."""
        bottom_index = self._find_bottom_index()
        if self._current_column[bottom_index + 1] == 0:
            return True
        else:
            return False
    
    def _check_new_column(self, column: list) -> bool:
        """Return true if there is space in a new column."""
        if column[self._find_bottom_index()] == 0:
            return True
        else:
            return False
    
    def _is_valid_move(self, new_column_num: int) -> bool:
        """Return True if the faller is not on the edge of the board. Otherwise return False."""
        if 0 <= new_column_num <= 5:
            return True
        else:
            return False

    
    # Methods for changing state of faller.
    def _replace_faller(self, bottom_index) -> None:
        """Re-place the faller inside the column."""
        self._current_column[bottom_index - 2:bottom_index + 1] = self._faller
    
    def _refresh_faller_state(self) -> None:
        """Refresh the state of the faller in case it has moved above open space."""
        if self.landed:
            try:
                if self._space_available():
                    # If there is space below the faller, unland the faller and replace it in the column to make sure it displays properly.
                    self._unland_faller()
                    self._replace_faller(self._find_bottom_index())
            except IndexError: # If there is an index error, it means that the faller was on the bottom of the board, and should stay landed.
                return
        else:
            if not self._space_available():
                # If there isn't space available, it means the faller was moved above a taken space, and needs to be landed again.
                self._land_faller()
                self._replace_faller(self._find_bottom_index())

    def _land_faller(self) -> None:
        self._falling = False
        self.landed = True
        for jewel in self._faller:
            jewel.land()
    
    def _unland_faller(self) -> None:
        self.landed = False
        self._falling = True
        for jewel in self._faller:
            jewel.unland()
    
    def _freeze_faller(self) -> None:
        self.landed = False
        self.frozen = True
        for jewel in self._faller:
            jewel.freeze()

    # Utility method. 
    def _find_bottom_index(self) -> int:
        return self._current_column.index(self._faller[2])
    
    # Private methods used during initialization. 
    def _insert_faller(self) -> None:
        """Insert the faller into the first 3 parts of the column."""
        self._current_column[0:3] = self._faller

    def _assign_pieces(self) -> list:
        """Create 3 pieces and append them to a list and return that list."""
        faller = []
        for piece in range(3):
            faller.append(Piece())
        return faller
    
    def _split_into_parts(self) -> None:
        """Create an attribute for each of the pieces of the faller; top, middle, and bottom."""
        self._top_piece = self._faller[0]
        self._middle_piece = self._faller[1]
        self._bottom_piece = self._faller[2]



class Board:
    """The main game board for the game of columns.

    This object represents a 2D list of integers.
    Each column contains 13 + 3 zeros to accomodate a faller of size 3.
    The board has the ability to detect matches between pieces.
    """
    def __init__(self):
        self._board = self._generate_new_board()
    


    def detect_matches(self):
        """Detect matches on the board. and apply them to the pieces."""
        matched_pieces = []
        # recursive adding
        if len(matched_pieces) >= 3:
            for piece in matched_pieces:
                piece.matched()


    def _iterate_through_board(self, row:int, col:int, rowdelta:int, columndelta:int) -> list:
        """Given the row and column of a starting piece, recursively search through the board in one of eight directions."""
        current_piece = self.board[col][row]
        matched_to_this_piece = [current_piece]
        if self.board[col + columndelta][row + rowdelta].color:


        




    def board(self) -> [[int]]:
        """Return the 2D list that this object represents."""
        return self._board

    def _generate_new_board(self):
        """Create a new game board."""
        two_dimensional_list = []
        for column in range(NUMBER_OF_COLUMNS):
            two_dimensional_list.append([])
            for row in range(NUMBER_OF_ROWS + 3): # The +3 here adds an additional 3 rows to each column, where the faller will be initialized.
                two_dimensional_list[-1].append(0)
        return two_dimensional_list