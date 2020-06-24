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
    while running:
        _print_faller_stats(faller)
        _print_board(game_board)
        move = input('What to do?: ')
        if move == '':
            if faller.landed:
                faller.fall()
                del faller
                faller = _make_new_faller(game_board)
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
    print('Game Ended, Bye')





def _start_game() -> (MaggieColumnsModel.Board, MaggieColumnsModel.Faller):
    """Create a new game board and put a faller in it."""
    board_object = MaggieColumnsModel.Board()
    new_game_board = board_object.board()
    new_faller = MaggieColumnsModel.Faller(new_game_board, randint(0, 5))
    return new_game_board, new_faller


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
                print(col[row].sticker(), end='')
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
                print(col[row].sticker(), end='')
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