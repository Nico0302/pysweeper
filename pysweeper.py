from tkinter import Tk, Frame, Label, Button, messagebox, DISABLED, NORMAL, LEFT, RIGHT
from random import randint

# gameplay constants
FIELD_WIDTH = 16
FIELD_HEIGHT = 16
MINE_COUNT = 40
FLAG_COUNT = MINE_COUNT
# graphic constats
SYMBOL_FONT = ("Wingdings", "15")
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
            gamemanager.unflag(self)
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
        self.time = 0

    def create_field(self, master, update_flaglabel, start_timer, stop_timer, reset_timer):
        """Create the game field."""
        self.update_flaglabel = lambda: update_flaglabel(FLAG_COUNT-self.flags)
        self.start_timer = start_timer
        self.stop_timer = stop_timer
        self.reset_timer = reset_timer
        self.field = [[Box(master, row, column) for column in range(FIELD_WIDTH)] for row in range(FIELD_HEIGHT)]

    def init_round(self):
        """Initialize new game round."""
        self.stop_timer()
        self.reset_timer()
        self.mined = False
        self.flags = 0
        self.flagged = 0
        self.time = 0
        for row in self.field:
            for box in row:
                box.init_round()
        self.update_flaglabel()
    
    def win_round(self):
        """Player won round procedure."""
        self.stop_timer()
        messagebox.showinfo("GAME OVER", "Du hast gewonnen!!!")
        self.init_round()

    def loose_round(self):
        """Player lost round procedure."""
        self.stop_timer()
        for row in self.field:
            for box in row:
                if box.mine:
                    box.detonate()
        messagebox.showerror("GAME OVER", "Du hast verloren!!!")
        self.init_round()

    def for_sourrounding(self, row, column, command):
        """Execute a function for sourrounding boxes."""
        for shift in self.BOX_SOUROUNDING_SHIFT:
            shifted_row = row+shift[0]
            shifted_column = column+shift[1]
            try:
                if shifted_row < 0 or shifted_column < 0:
                    raise IndexError
                command(self.field[shifted_row][shifted_column])
            except IndexError:
                # ignore out of range error
                pass

    def reveal_box(self, box):
        """Reveal empty sourrounding boxes by flood fill."""
        if not box.revealed:
            if box.flagged:
                self.flags -= 1
                self.update_flaglabel()
            box.reveal()
            if box.score == 0:
                self.for_sourrounding(box.row, box.column, lambda neighbor: self.reveal_box(neighbor))

    def generate_mines(self, excluded_row, excluded_column):
        """Generat random mines in mine field with excluded box."""
        for _ in range(MINE_COUNT):
            self.place_random_mine(excluded_row, excluded_column)
        self.mined = True
        self.start_timer()

    def increment_box_score(self, row, column):
        """Increment box mine score for sourunding boxes."""
        self.for_sourrounding(row, column, lambda neighbor: neighbor.increment_score())

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
            self.update_flaglabel()
            if box.mine:
                self.flagged += 1
            if self.flagged >= MINE_COUNT:
                self.win_round()
            if self.flags >= FLAG_COUNT:
                self.loose_round()

    def unflag(self, box):
        """Unflag box."""
        box.unflag()
        self.flags -= 1
        if box.mine:
            self.flagged -= 1
        self.update_flaglabel()

    def increment_time(self):
        """Increment time with one second."""
        self.time += 1

class Application:
    def __init__(self, root):
        self.root = root
        root.title("pysweeper")
        root.iconbitmap("icon.ico")
        self.timerrunning = False
        # tkinter frames
        menuframe = Frame(master=root)
        menuframe.pack()
        fieldframe = Frame(master=root)
        fieldframe.pack()
        flagicon = Label(master=menuframe, text="P", foreground=FLAGGED_FORGROUND, font=SYMBOL_FONT)
        flagicon.pack(side=LEFT)
        self.flaglabel = Label(master=menuframe, text=str(FLAG_COUNT))
        self.flaglabel.pack(side=LEFT)
        resetbutton = Button(master=menuframe, text="Neustart", command=gamemanager.init_round)
        resetbutton.pack(side=LEFT, padx=32, pady=4)
        self.timerlabel = Label(master=menuframe, text="00:00")
        self.timerlabel.pack(side=LEFT)
        # gamemanager
        gamemanager.create_field(fieldframe, self.update_flaglabel, self.start_timer, self.stop_timer, self.reset_timer)
        gamemanager.init_round()

    def update_flaglabel(self, count):
        """Update flag label."""
        self.flaglabel.config(text=str(count))

    def start_timer(self):
        """Start Timer"""
        self.timerrunning = True
        self.tick_timer()

    def reset_timer(self):
        """Reset timer label."""
        self.timerlabel.config(text="00:00")

    def stop_timer(self):
        """Stop timer and update label."""
        self.timerrunning = False

    def tick_timer(self):
        """Run timer in second interval."""
        if self.timerrunning:
            gamemanager.increment_time()
            m, s = divmod(gamemanager.time, 60)
            self.timerlabel.config(text="{:02d}:{:02d}".format(m, s))
            self.root.after(1000, self.tick_timer)

root = Tk()
gamemanager = Gamemanager()

Application(root)

root.mainloop()
