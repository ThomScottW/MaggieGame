# The purpose of this module is to test the mechanics to 
# the maggiecolumns module
import MaggieColumnsModel
from random import randint


NUMBER_OF_ROWS = 13
NUMBER_OF_COLUMNS = 6

DEBUGGING = False


def test_game() -> None:
    """Run the game of MaggieColumns."""
    game_board, faller = _start_game()
    running = True
    faller_active = True # True when there is currently a faller being controlled by the player.
    finding_matches = False # True when we are handling the match process. Matching and falling.
    # To have a matching animation appear on seperate frames, these bool values control which path the loop takes.
    while running:
        if DEBUGGING and faller_active: _print_faller_stats(faller)
        _print_board(game_board.board())
        move = input('What to do?: ')
        if faller_active:
            if move == '':
                if faller.landed:
                    faller.fall()
                    del faller
                    faller_active = False
                    finding_matches = True # After the faller lands, check for matches on the board.
                else:
                    faller.fall()
            elif move == 'R':
                faller.rotate()
            elif move == '<':
                faller.move(faller.column_num - 1)
            elif move == '>':
                faller.move(faller.column_num + 1)
            elif move == 'Q':
                running = False
        else: # Faller is not active.
            if finding_matches:
                game_board.find_matches()
                finding_matches = False # Done finding matches.
            else: # Matches have been found already. 
                if game_board.handle_match_process(): # Delete the matched pieces.
                    finding_matches = True # If matches were deleted, then we need to re-check for any new matches. (Pieces fall)
                else:
                    faller = _make_new_faller(game_board.board()) # Make a new faller. All in the same frame.
                    faller_active = True
    print('Game Ended, Bye')





def _start_game() -> (MaggieColumnsModel.Board, MaggieColumnsModel.Faller):
    """Create a new game board and put a faller in it."""
    board_object = MaggieColumnsModel.Board()
    new_faller = MaggieColumnsModel.Faller(board_object.board(), randint(0, 5))
    return board_object, new_faller


def _make_new_faller(board:[[int]]) -> MaggieColumnsModel.Faller:
    new_faller = MaggieColumnsModel.Faller(board, randint(0, 5))
    return new_faller


def _print_board(gameboard: [list]) -> None:
    """Print what only the part of the board that will be shown during gameplay."""
    if DEBUGGING:
        _print_top_rows(gameboard)
    for row in range(3, NUMBER_OF_ROWS + 3):
        print('|', end='')
        for col in gameboard:
            if type(col[row]) == MaggieColumnsModel.Piece:
                print(col[row], end='')
            elif col[row] == 0:
                print('   ', end='')
        print('|')
    print(' ', end='')
    print('-' * 3 * NUMBER_OF_COLUMNS, end=' \n')


def _print_top_rows(gameboard: [list]) -> None:
    """Print the top three rows of the board if the global constant is set to true."""
    print(' ', '-' * 3 * NUMBER_OF_COLUMNS, sep='', end='\n')
    for row in range(3):
        print('|', end='')
        for col in gameboard:
            if type(col[row]) == MaggieColumnsModel.Piece:
                print(col[row], end='')
            elif col[row] == 0:
                print('   ', end='')
        print('|')
    print(' ', end='')
    print('-' * 3 * NUMBER_OF_COLUMNS, end=' \n')


def _print_faller_stats(faller: MaggieColumnsModel.Faller) -> None:
    """Print the attributes of the faller."""
    if DEBUGGING:
        print(f'DEBUG: PIECES: {faller._top_piece.sticker()}, {faller._middle_piece.sticker()}, {faller._bottom_piece.sticker()}')
        print(f'DEBUG: COLUMN: {faller._current_column}')
        print(f'DEBUG: BOTTOM_INDEX: {faller._find_bottom_index()}')




if __name__ == '__main__':
    test_game()