import pygame
from solver import solve_board
import time

pygame.font.init()

EASY = "easy"
MEDIUM = "medium"
HARD = "hard"


#def generate_board(starting_numbers):
#    board = []
#    for i in range(9):
#        board[i] =
#        for j in range(9)
#    pass


def create_board(difficulty):
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]
    if difficulty == EASY:
        return generate_board(40)
    elif difficulty == MEDIUM:
        return generate_board(30)
    elif difficulty == HARD:
        return generate_board(20)
    else:
        return board

class Grid:
    """
    Class representing the Sudoku grid.
    """

    def __init__(self, rows, cols, width, height, difficulty):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.board = create_board(difficulty)
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.model = None
        self.selected = None

    def update_model(self):
        """
        Keep track of the current board status.
        """
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def draw(self, win):
        """
        Draw the board.

        :param win: Window of drawing.
        """
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            # Draw square cells thicker
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw the Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

    def select(self, row, col):
        """
        Select a cell.

        :param row: row number.
        :param col: col number.
        """
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        # Set selected as this current position
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def sketch(self, val):
        """
        Set temporary value in selected cell.

        :param val: value to set.
        """
        # Sketch to set a temporary small value in the corner
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def place(self, val):
        """
        Set permanent value in selected cell.
        If it's wrong you will have a mistake.

        :param val: value to set.
        """
        # Place the value as non temporary
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            # Try to solve the board, recursively, if an exception raise it means we tried all combi while backtracking
            # And found nothing, so it's wrong
            try:
                solve_board(self.model)
                return True
            except IndexError:
                # Unsolvable, we reset the value
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def clear(self):
        """
        Remove a temporary value from selected cell.
        """
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        Return coordinate where clicked.

        :param pos: position in pixel clicked.

        :return: col and row position of the board.
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return int(y), int(x)
        else:
            return None

    def is_finished(self):
        """
        Check if the board is complete.

        :return: True if complete, else False.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        # if we have a temporary value and the value inside the cell is not set
        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x + 5, y + 5))
        # else, we replace it
        elif not (self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

        # If we select a cell, we highlight it in Red
        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw(win)


def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


def button(screen, position, text):
    font = pygame.font.SysFont("comicsansms", 50)
    text_render = font.render(text, 1, (0, 0, 0))
    x, y, w, h = text_render.get_rect()
    x, y = position

    # Stolen from the internet because i'm bad at this
    pygame.draw.line(screen, (150, 150, 150), (x, y), (x + w, y), 5)
    pygame.draw.line(screen, (150, 150, 150), (x, y - 2), (x, y + h), 5)
    pygame.draw.line(screen, (50, 50, 50), (x, y + h), (x + w, y + h), 5)
    pygame.draw.line(screen, (50, 50, 50), (x + w, y + h), [x + w, y], 5)
    pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h))
    return screen.blit(text_render, (x, y))


def main():
    # Pygame window game
    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku")
    difficulty = None

    # Setting difficulty
    while difficulty is None:
        # Difficulty setting
        win.fill((255, 255, 255))
        # it's actually easier to
        button1 = button(win, (20, 250), "Easy")
        button2 = button(win, (175, 250), "Medium")
        button3 = button(win, (400, 250), "Hard")
        pygame.display.update()

        # when a key is pressed or a button is collided
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                difficulty = False
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button1.collidepoint(pygame.mouse.get_pos()):
                    difficulty = EASY
                elif button2.collidepoint(pygame.mouse.get_pos()):
                    difficulty = MEDIUM
                elif button3.collidepoint(pygame.mouse.get_pos()):
                    difficulty = HARD

    board = Grid(9, 9, 540, 540, difficulty)
    key = None
    run = True
    start = time.time()
    strikes = 0

    while run:
        # Calculate playtime
        play_time = round(time.time() - start)
        # when a key is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")
                            run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
