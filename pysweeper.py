from tkinter import Tk, Frame, Button, font, messagebox, DISABLED, NORMAL
from random import randint

# gameplay constants
FIELD_WIDTH = 10
FIELD_HEIGHT = 12
MINE_COUNT = int(FIELD_WIDTH*FIELD_HEIGHT * 0.15)
FLAG_COUNT = MINE_COUNT*2
# graphic constats
DEFAULT_FORGROUND = "black"
FLAGGED_FORGROUND = "red"
DEFAULT_BACKGROUND = "SystemButtonFace"
REVEALED_BACKGROUND = "#CACACA"
MINE_BACKGROUND = "red"
SCORE_FOREGROUND = [
    None,
    "blue",
    "green",
    "red",
    "purple",
    "black",
    "maroon",
    "gray",
    "turquoise"
]

class Box:
    def __init__(self, master, row, column):
        self.master = master
        self.row = row
        self.column = column
        self.button = Button(master=master, text="", width=2, height=1, foreground=DEFAULT_FORGROUND, disabledforeground=DEFAULT_FORGROUND, command=self.on_press)
        self.button.grid(row=row, column=column)
        self.button.bind("<Button-3>", self.on_toggle_flag)

    def init_round(self):
        """Initialize box for new game round."""
        self.flagged = False
        self.revealed = False
        self.mine = False
        self.score = 0
        self.cover()

    def on_press(self):
        """Callback for button press."""
        if self.flagged:
            self.unflag()
        else:
            if self.mine:
                gamemanager.loose_round()
            else:
                if not gamemanager.mined:
                    gamemanager.generate_mines(self.row, self.column)
                gamemanager.reveal_box(self)

    def on_toggle_flag(self, _):
        """Callback for toggle flag."""
        if not self.revealed:
            if self.flagged:
                gamemanager.unflag(self)
            else:
                gamemanager.flag(self)

    def reveal(self):
        """Make box appear revealed."""
        text = ""
        if self.score > 0:
            text = str(self.score)
        self.button.config(state=DISABLED, background=REVEALED_BACKGROUND, text=text, disabledforeground=SCORE_FOREGROUND[self.score])
        self.revealed = True
        self.flagged = False

    def cover(self):
        """Make box appear covered."""
        self.button.config(state=NORMAL, foreground=DEFAULT_FORGROUND, disabledforeground=DEFAULT_FORGROUND, background=DEFAULT_BACKGROUND, text="")

    def detonate(self):
        """Make box appear detonated."""
        self.button.config(state=DISABLED, text="X", background=MINE_BACKGROUND)
        self.revealed = True

    def flag(self):
        """Place flag."""
        self.button.config(text="P", foreground=FLAGGED_FORGROUND)
        self.flagged = True

    def unflag(self):
        """Remove flag."""
        self.button.config(text="", foreground=DEFAULT_FORGROUND)
        self.flagged = False

    def place_mine(self):
        """Place mine on box."""
        self.mine = True

    def increment_score(self):
        """Increment mine score."""
        self.score += 1

class Gamemanager:
    # shift in rows and columns for sourrounding boxes
    BOX_SOUROUNDING_SHIFT = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self):
        self.field = []
        self.mined = False
        self.flags = 0
        self.flagged = 0

    def create_field(self, master):
        """Create the game field."""
        self.field = [[Box(master, row, column) for column in range(FIELD_WIDTH)] for row in range(FIELD_HEIGHT)]

    def init_round(self):
        """Initialize new game round."""
        self.mined = False
        self.flags = 0
        self.flagged = 0
        for row in self.field:
            for box in row:
                box.init_round()
    
    def win_round(self):
        """Player won round procedure."""
        messagebox.showinfo("GAME OVER", "Du hast gewonnen!!!")
        self.init_round()

    def loose_round(self):
        """Player lost round procedure."""
        for row in self.field:
            for box in row:
                if box.mine:
                    box.detonate()
        messagebox.showinfo("GAME OVER", "Du hast verloren!!!")
        self.init_round()

    def reveal_box(self, box):
        """Reveal empty sourrounding boxes by flood fill."""
        if not box.revealed:
            box.reveal()
            if box.flagged:
                self.flags -= 1
            if box.score == 0:
                # keep in bounds
                if box.row < FIELD_HEIGHT-1:
                    self.reveal_box(self.field[box.row+1][box.column])
                if box.row > 0:
                    self.reveal_box(self.field[box.row-1][box.column])
                if box.column < FIELD_WIDTH-1:
                    self.reveal_box(self.field[box.row][box.column+1])
                if box.column > 0:
                    self.reveal_box(self.field[box.row][box.column-1])

    def generate_mines(self, excluded_row, excluded_column):
        """Generat random mines in mine field with excluded box."""
        for _ in range(MINE_COUNT):
            self.place_random_mine(excluded_row, excluded_column)
        self.mined = True

    def increment_box_score(self, row, column):
        """Increment box mine score for sourunding boxes."""
        for shift in self.BOX_SOUROUNDING_SHIFT:
            shifted_row = row+shift[0]
            shifted_column = column+shift[1]
            try:
                self.field[shifted_row][shifted_column].increment_score()
            except IndexError:
                # ignore out of range error
                pass

    def place_random_mine(self, excluded_row, excluded_column):
        """Place random mine on field with excluded box."""
        row = randint(0, FIELD_HEIGHT-1)
        column = randint(0, FIELD_WIDTH-1)
        # prevent mine in radius from first press
        if row <= excluded_row+1 and row >= excluded_row-1 and \
           column <= excluded_column+1 and column >= excluded_column-1 or \
           self.field[row][column].mine:
            self.place_random_mine(excluded_row, excluded_column)
        else:
            self.field[row][column].place_mine()
            self.increment_box_score(row, column)

    def flag(self, box):
        """Flag box."""
        if self.flags < FLAG_COUNT:
            box.flag()
            self.flags += 1
            if box.mine:
                self.flagged += 1
            if self.flagged >= MINE_COUNT:
                self.win_round()

    def unflag(self, box):
        """Unflag box."""
        box.unflag()
        self.flags -= 1
        if box.mine:
            self.flagged -= 1     

class Application:
    def __init__(self, root):
        self.root = root
        root.title("pysweeper")
        # tkinter frames
        menuframe = Frame(master=root)
        menuframe.pack()
        fieldframe = Frame(master=root)
        fieldframe.pack()
        resetbutton = Button(master=menuframe, text="Neustart", command=gamemanager.init_round)
        resetbutton.pack()
        # gamemanager
        gamemanager.create_field(fieldframe)
        gamemanager.init_round()

root = Tk()
gamemanager = Gamemanager()

Application(root)

root.mainloop()
