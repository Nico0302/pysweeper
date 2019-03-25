from tkinter import Tk, Button, font, DISABLED
from random import randint

# global constants
MINE_COUNT = 200
MINE_PERCENTAGE = 0.2
FLAG_COUNT = 40
FIELD_WIDTH = 50
FIELD_HEIGHT = 30
BOX_SIZE = 10

class Box:
    def __init__(self, master, row, column):
        self.master = master
        self.row = row
        self.column = column
        self.flagged = False
        self.revealed = False
        self.score = gamemanager.get_score(row, column)
        self.button = Button(master=master, text="", width=2, height=1, command=self.on_press)
        self.button.grid(row=row, column=column)
        self.button.bind("<Button-3>", self.toggle_flag)

    def on_press(self):
        """button press callback"""
        if self.flagged:
            self.unflag()
        else:
            self.button.config(state=DISABLED, background="lightgrey")
            if self.score == -1:
                self.button.config(text="X", background="red", fg="black")
            if self.score > 0:
                self.button.config(text=str(self.score))
            self.revealed = True

    def toggle_flag(self, _):
        """toggles flag"""
        if not self.revealed:
            if self.flagged:
                self.unflag()
            else:
                self.flag()

    def flag(self):
        """places flag"""
        self.button.config(text="P")
        self.flagged = True

    def unflag(self):
        """removes flag"""
        self.button.config(text="")
        self.flagged = False

class Mine:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.falgged = False

    def flag(self):
        """falggs mine"""
        self.falgged = True

    def unflag(self):
        """unflaggs mine"""
        self.falgged = False

    def detonate(self):
        """detonates mine"""
        print("Game Over")

class Gamemanager:
    BOX_SOUROUNDING_SHIFT = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] # shift in rows and columns for sourrounding boxes

    def __init__(self):
        self.mines = []

    def init_game(self):
        """initializes game"""
        self.field = [0] * (FIELD_WIDTH*FIELD_HEIGHT)
        self.generate_mines()
        self.generate_scores()

    def generate_mines(self):
        """generats random mines in field"""
        for _ in range(MINE_COUNT):
            self.add_mine()

    def generate_scores(self):
        """generats scores base on mines in field"""
        for index, value in enumerate(self.field):
            if value == 0:
                row = index//FIELD_WIDTH
                column = index%FIELD_WIDTH
                self.field[index] = self.calculate_box_score(row, column)

    def calculate_box_score(self, row, column):
        """returns the number of surrounding mines"""
        score = 0
        for shift in self.BOX_SOUROUNDING_SHIFT:
            shifted_row = row+shift[0]
            shifted_column = column+shift[1]

            # prevent overflow and underflow
            if shifted_row < FIELD_HEIGHT and shifted_column < FIELD_WIDTH and \
               shifted_row >= 0 and shifted_column >= 0 and \
               self.check_for_mine(shifted_row, shifted_column):
                score += 1
        return score
                
    def check_for_mine(self, row, column):
        """check if box contains mine"""
        return self.get_score(row, column) < 0

    def add_mine(self):
        """adds mine at random position in field"""
        index = randint(0, FIELD_WIDTH*FIELD_HEIGHT-1)
        # check if mine exists
        if self.field[index] >= 0:
            self.field[index] = -1
        else:
            self.add_mine()

    def get_score(self, row, column):
        """returns box by row and column"""
        return self.field[column + row*FIELD_WIDTH]

class Application:
    def __init__(self, root):
        self.root = root
        self.boxes = []
        gamemanager.init_game()
        self.build_field(root)

    def build_field(self, master):
        """builds field boxes"""
        self.boxes = [] # clear list
        for row in range(FIELD_HEIGHT):
            for column in range(FIELD_WIDTH):
                box = Box(master, row, column)
                self.boxes.append(box)

root = Tk()
gamemanager = Gamemanager()

# Create tkInter dependent global constants
SYMBOL_FONT = font.Font(family='Wingdings', size=16)

Application(root)

root.mainloop()
