# MaggieColumns Model

# This module implements the rules of the game of columns.
"""
Features that work so far:
 - Falling
 - Random Column Picking
 - Random Piece Generation
 - Rotation
 - Moving
 - Matching
 - Falling after matching
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
    
    def __str__(self):
        return self._sticker

    def sticker(self):
        return self._sticker
    
    # Methods for changing the state of the piece.
    # [1:-1] slicing is to access the 'middle' of the piece, which is the letter that designates its color.
    def land(self):
        """Update bool values and sticker to indicate that the piece has landed."""
        self._falling = False
        self._landed = True
        self._sticker = f'|{self._sticker[1:-1]}|'
    
    def unland(self):
        """Update bool values and sticker to indicate that the piece has been 'un-landed'."""
        self._landed = False
        self._falling = True
        self._sticker = f'[{self._sticker[1:-1]}]'
    
    def freeze(self):
        """Update bool values and sticker to indicate that the piece has frozen in place."""
        self._landed = False
        self._frozen = True
        self._sticker = f' {self._sticker[1:-1]} '
    
    def match(self):
        """Update bool values and sticker to indicate that the piece has been matched to adjacent pieces."""
        self._frozen = False
        self._matched = True
        self._sticker = f'*{self._sticker[1:-1]}*'

    def _pick_sticker(self):
        """Randomly select an integer to use as a key to the MAGGIE_JEWELS dictionary to pick a sticker for the piece."""
        random_number = randint(1, 7)
        self._sticker = f'[{MAGGIE_JEWELS[random_number]}]'
        

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
        # If the bottom index is 5, it means that all 3 pieces of the faller are visible on the board. Index 5 means the 6th row, or the third visible row.
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

    The additional 3 spaces are where the faller is placed upon creation. The faller is invisible to the
    player in this state, but becomes visible when it has fallen once. If any part of the faller is
    still in these extra 3 spaces and the faller freezes, the game will end.

    The board has the ability to detect matches between pieces, delete the matched pieces, and make floating pieces fall.
    """
    def __init__(self):
        self._board = self._generate_new_board()
        self._matched_pieces = []

    def board(self) -> [[int]]:
        """Return the 2D list that this object represents."""
        return self._board
    
    def find_matches(self) -> None:
        """Detect pieces that are matched on the board. Then make any 'floating' pieces fall to fill in the gaps."""
        # Search the board in all directions.
        self._search_all_directions()
    
    def handle_match_process(self) -> bool:
        """Delete matched pieces on the board, and make any floating pieces fall downward. Return true if matches were deleted."""
        if self._delete_matched_pieces(): # If pieces were deleted, then we need to check for any floating pieces.
            self._apply_gravity()
            return True
    
    def _search_all_directions(self) -> None:
        """Search up, down, left, right, and diagonally for matches."""
        for col in range(NUMBER_OF_COLUMNS):
            for row in range(NUMBER_OF_ROWS + 3):
                cell = self._board[col][row]
                if (cell, col, row) in self._matched_pieces: 
                    continue # If a piece was already found to be matched, then we don't need to search for it again. Skip.
                if cell != 0:
                    self._search_direction_for_matches(col, row, 0, 1)   # Up
                    self._search_direction_for_matches(col, row, 0, -1)  # Down
                    self._search_direction_for_matches(col, row, -1, 0)  # Left
                    self._search_direction_for_matches(col, row, 1, 0)   # Right
                    self._search_direction_for_matches(col, row, -1, 1)  # Diagonal Up Left
                    self._search_direction_for_matches(col, row, 1, 1)   # Diagonal Up Right  
                    self._search_direction_for_matches(col, row, -1, -1) # Diagonal Down Left
                    self._search_direction_for_matches(col, row, 1, -1)  # Diagonal Down Right     

    def _search_direction_for_matches(self, col: int, row: int, col_delta: int, row_delta:int) -> None:
        """Using a starting location for a piece, given in coordinates (col, row), find all matches in a single direction.

        col_delta and row_delta should be -1, 0, or 1 to indicate left, no, or rightward motion.
        
        col_delta = 1 indicates rightward searching. -1 means leftward.
        row_delta = 1 indicates upward searching. -1 means downward.
        A combination of both can be used to search for matches diagonally.
        """
        search_location = self._board[col][row] # Starting point for the search. We will look in one directin starting from here.
        found_pieces = [(search_location, col, row)] # Pieces found that have the same sticker. Col/row included to find for deletion.
        while True:
            col += col_delta # Shift the search to
            row += row_delta # the next column and row.
            # Test to make sure the column and row indexes are within the bounds of the board. Subtract 1 because indexing starts at 0. 
            if not (0 <= col <= NUMBER_OF_COLUMNS - 1) or not (0 <= row <= (NUMBER_OF_ROWS + 3) - 1): # NUMBER_OF_ROWS + 3 to account for top 3 rows.
                break
            search_location = self._board[col][row]
            if search_location == 0 or search_location.sticker() != found_pieces[-1][0].sticker(): # If we reach an empty cell or
                break                                                                              # this piece does not match the last, stop search.
            else:
                found_pieces.append((search_location, col, row)) # Otherwise, we found a matching piece. Keep track of its col and row.
        # After searching in that direction, if 3 or more pieces were found, then we match them.
        if len(found_pieces) >= 3:
            for piece, col, row in found_pieces:
                piece.match()
                self._matched_pieces.append((piece, col, row)) # Add the piece and its col/row to the list of matched pieces.

    def _delete_matched_pieces(self) -> bool:
        """Delete all pieces that are currently in the matched state. Return true if pieces were deleted."""
        if self._matched_pieces: # Only attempt to delete matches if matches exist.
            for matched_piece, col, row in self._matched_pieces:
                self._board[col][row] = 0 # Set to 0 to indicate erasure of the matched piece.
            self._matched_pieces = []
            return True
    
    def _apply_gravity(self) -> None:
        """Make any floating pieces fall."""
        floating_pieces = self._search_for_floaters()
        while floating_pieces: # Repeatedly search for new falling pieces, and make those pieces fall.
            self._make_pieces_fall(floating_pieces)
            floating_pieces = self._search_for_floaters()
    
    def _search_for_floaters(self) -> [(Piece, int, int)]:
        """Return a list of triples representing every floating piece in the board."""
        floating_pieces = []
        for col in range(NUMBER_OF_COLUMNS):
            for row in range(NUMBER_OF_ROWS + 3):
                cell = self._board[col][row]
                if cell != 0 and self._space_below(cell, col, row): # If the cell is not empty and there is space underneath.
                    floating_pieces.append((cell, col, row))
        return floating_pieces
    
    def _make_pieces_fall(self, floating_pieces: [(Piece, int, int)]) -> None:
        """Make all floating pieces fall one cell."""
        for piece, col, row in floating_pieces:
            self._board[col][row] = 0
            self._board[col][row + 1] = piece

    def _space_below(self, cell, col, row) -> bool:
        """Return True if the cell beneath the piece is empty."""
        try:
            if self._board[col][row + 1] == 0:
                return True
            else:
                return False
        except IndexError:
            return False
    
    def _generate_new_board(self):
        """Create a new game board."""
        two_dimensional_list = []
        for column in range(NUMBER_OF_COLUMNS):
            two_dimensional_list.append([])
            for row in range(NUMBER_OF_ROWS + 3): # The +3 here adds an additional 3 rows to each column, where the faller will be initialized.
                two_dimensional_list[-1].append(0)
        return two_dimensional_list
