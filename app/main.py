import ttkbootstrap as tkb
import matplotlib as mpl
mpl.use('TkAgg')

from model import SudokuModel
# from view import SelectionScreen, GameScreen
from controller import SudokuController
# from solve import SudokuAlgorithm

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.style = tkb.Style(theme="flatly")
        self.root.title("Sudoku Game")
        self.root.geometry("650x650")
        self.root.configure(bg=self.style.colors.bg)

        try: self.root.iconbitmap("sudoku-icon.ico")
        except: pass
        self.model = None
        self.show_selection_screen()

    def show_selection_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.show_selection_screen=SelectionScreen(self.root, self.start_game)

    def start_game(self, grid_size, difficulty_display):
        for widget in self.root.winfo_children(): widget.destroy()

        self.model = SudokuModel(difficulty=difficulty_display, grid_size=grid_size)
        self.game_screen = GameScreen(self.root, grid_size)
        self.controller = SudokuController(self.model, self.game_screen, self)
        self.root.tittle(f"Sudoku Game - {difficulty_display} ({grid_size}x{grid_size})")

def main():
    root = tkb.Window(title="Sudoku Game", themename="flatly")
    app = SudokuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

