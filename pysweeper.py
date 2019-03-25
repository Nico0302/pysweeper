from tkinter import Tk, Button, font, DISABLED
from random import randint

# global constants
MINE_COUNT = 20
FLAG_COUNT = 40
FIELD_WIDTH = 10
FIELD_HEIGHT = 8
BOX_SIZE = 10

class Box:
    def __init__(self, master, row, column):
        self.master = master
        self.row = row
        self.column = column
        self.flagged = False
        self.revealed = False

        try:
            self.mine = gamemanager.get_mine(row, column)
        except StopIteration:
            self.mine = False
        self.score = gamemanager.get_box_score(row, column)
        
        self.button = Button(master=master, text="", width=2, height=1, command=self.on_press)
        self.button.grid(row=row, column=column)
        self.button.bind("<Button-3>", self.toggle_flag)

    def on_press(self):
        """button press callback"""
        if self.flagged:
            self.unflag()
        else:
            self.button.config(state=DISABLED)
            self.revealed = True
            if self.mine:
                self.button.config(text="֍", background="#FF0000")
                self.mine.detonate()
            else:
                if self.score > 0:
                    self.button.config(text=str(self.score))
                self.button.config(background="#C0C0C0")

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
        if self.mine:
            self.mine.flag()

    def unflag(self):
        """removes flag"""
        self.button.config(text="")
        self.flagged = False
        if self.mine:
            self.mine.unflag()

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
    BOX_SOUROUNDING_SHIFT = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)] # shift in rows and columns for sourrounding boxes

    def __init__(self):
        self.mines = []

    def init_game(self):
        """initializes game"""
        self.generate_mines()

    def generate_mines(self):
        """generats a random field"""
        for _ in range(MINE_COUNT):
            row = randint(0, FIELD_WIDTH-1)
            column = randint(0, FIELD_HEIGHT-1)
            try:
                self.get_mine(row, column)
            except StopIteration:
                mine = Mine(row, column)
                self.mines.append(mine)

    def get_mine(self, row, column):
        """returns mine by row and column"""
        return next(mine for mine in self.mines if mine.row == row and mine.column == column)

    def get_box_score(self, row, column):
        """returns number of surrounding mines"""
        mine_count = 0
        for shift in self.BOX_SOUROUNDING_SHIFT:
            try:
                gamemanager.get_mine(row+shift[0], column+shift[1])
                mine_count += 1
            except StopIteration:
                pass
        return mine_count

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
