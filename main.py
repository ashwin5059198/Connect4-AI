from ppadb.client import Client
from PIL import Image
from algo import minimax
import math
import numpy as np
from time import sleep
from tabulate import tabulate


# red is 1
# yellow is 2
YELLOW = (255, 243, 0)
RED = (222, 0, 0)
X0, Y0 = (84, 633)
DELTA = 94
ROWS, COLS = (6, 7)

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2


class AI:
    def __init__(self):
        self.device = None
        self.board = None
        self.image = None

    def set_device(self, dev):
        """ Set android device """
        self.device = dev

    def show_board(self):
        """ Prints board to stdout, meant for debugging"""
        sleep(1)
        self.update_board()
        board = self.board.copy()
        board: list = np.flip(board, 0).tolist()

        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == 1:
                    board[r][c] = "R"
                elif board[r][c] == 2:
                    board[r][c] = "Y"
                else:
                    board[r][c] = " "
        print(tabulate(board, tablefmt="grid"))

    def put_piece(self, col_index):
        """ Tap on a column given index """
        self.device.shell(f"input tap {X0 + col_index * DELTA} {Y0}")

    def is_my_turn(self):
        """If rgb value of (165, 216) is white, not our turn"""
        # left 216, 165
        # right 211, 554
        return not all(map(lambda x: x == 255, self.image[216][165][:3]))

    def update_image(self):
        """ Take screenshot and save """
        scn_image = self.device.screencap()
        with open("screenshot.png", "wb") as fp:
            fp.write(scn_image)
        img = Image.open("screenshot.png")
        self.image = np.array(img, dtype=np.uint8)

    def update_board(self):
        """ Figure out board configuration from screenshot """
        self.update_image()
        # Initialise board to 0
        self.board = [[0 for _ in range(COLS)] for __ in range(ROWS)]
        for i in range(ROWS):
            for j in range(COLS):
                # find pieces from red component of pixel
                r = self.image[Y0 + i * DELTA][X0 + j * DELTA][0]
                if r == 255:
                    self.board[i][j] = 2
                elif r == 222:
                    self.board[i][j] = 1
        self.board = np.flip(self.board, 0)

    def play_one_move(self):
        """ Wait till turn and play best move """
        print("checking if my turn...", end=" ")
        while True:
            self.update_image()
            if self.is_my_turn():
                print("yes")
                break
            else:
                sleep(2)

        print("thinking...")
        self.update_board()
        # load minimax here
        col, minimax_score = minimax(self.board, 6, -math.inf, math.inf, True)
        print("selected column ", col)
        self.put_piece(col_index=col)

        self.show_board()

    def start(self):
        while True:
            self.play_one_move()


def main():
    adb = Client(host='127.0.0.1', port=5037)
    devices = adb.devices()
    if len(devices) == 0:
        print("No devices found.")
        quit(0)

    device = devices[0]

    player = AI()
    player.set_device(device)
    player.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n------Exiting-------")
