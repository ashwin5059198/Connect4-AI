import random
import math

# A window is a list of any 4 consecutive positions in the board (horizontal, vertical, diagonal(+ve and -ve))

# red is 1
# yellow is 2
ROWS = 6
COLS = 7

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

LENGTH = 4


def is_valid_column(board, col):
    """ Check if a piece can be dropped in that column of given configuration
        * Helper function for func: get_valid_locations
    """
    return board[-1][col] == EMPTY


def get_valid_locations(board):
    """ Returns a list of valid column indices to drop a piece """
    valid_locations = []
    for col in range(COLS):
        if is_valid_column(board, col):
            valid_locations.append(col)
    return valid_locations


def drop_piece(board, row, col, piece):
    """ Drop a piece in the given position of given board configuration """
    board[row][col] = piece


def get_next_open_row(board, col):
    """ Find the row index of empty position in the given column, in given board configuration """
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r


def winning_configuration(board, piece):
    """ Check if the given board configuration is a win for the given piece """
    # Check each row for 4 consecutive pieces
    for c in range(COLS-3):
        for r in range(ROWS):
            positions = [board[r][c + i] for i in range(LENGTH)]
            if all(map(lambda x: x == piece, positions)):
                return True

    # Check each column for 4 consecutive pieces
    for c in range(COLS):
        for r in range(ROWS-3):
            positions = [board[r + i][c] for i in range(LENGTH)]
            if all(map(lambda x: x == piece, positions)):
                return True

    # Check diagonals with +ve slope
    for c in range(COLS-3):
        for r in range(ROWS-3):
            positions = [board[r + i][c + i] for i in range(LENGTH)]
            if all(map(lambda x: x == piece, positions)):
                return True

    # Check diagonals with -ve slope
    for c in range(COLS-3):
        for r in range(3, ROWS):
            positions = [board[r - i][c + i] for i in range(LENGTH)]
            if all(map(lambda x: x == piece, positions)):
                return True

    return False


def evaluate_window(window, piece):
    """ Given a window, evaluate score with respect to given piece """
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_configuration(board, piece):
    """ Score a particular board configuration with respect to given piece """
    score = 0

    # Score middle column
    center_array = [int(i) for i in list(board[r][COLS//2] for r in range(ROWS))]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score for each row
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r])]
        for c in range(COLS-3):
            window = row_array[c:c+LENGTH]
            score += evaluate_window(window, piece)

    # Score for each column
    for c in range(COLS):
        col_array = [int(i) for i in list(board[r][c] for r in range(ROWS))]
        for r in range(ROWS-3):
            window = col_array[r:r+LENGTH]
            score += evaluate_window(window, piece)

    # Score for each positively sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(LENGTH)]
            score += evaluate_window(window, piece)

    # Score for each negatively sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    """ A terminal node is a board configuration where no more moves are possible i.e, Game Over !"""
    # If player wins
    cond1 = winning_configuration(board, PLAYER_PIECE)

    # If AI wins
    cond2 = winning_configuration(board, AI_PIECE)

    # Draw (no more valid locations to drop a piece)
    cond3 = not len(get_valid_locations(board))

    return cond1 or cond2 or cond3


def minimax(board, depth, alpha, beta, maximizingPlayer):
    """ Use minimax and find optimal move """
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_configuration(board, AI_PIECE):
                return None, 100000000000000
            elif winning_configuration(board, PLAYER_PIECE):
                return None, -10000000000000
            else:  # Game is over, no more valid moves
                return None, 0
        else:  # Depth is zero
            return None, score_configuration(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score: tuple = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
