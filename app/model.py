import random as rand
import copy as cpy
import time
from solve import get_solver

class SudokuModel:
    DIFFICULTY_LEVELS = {
        "easy": (30, 40),
        "medium": (40, 50),
        "difficult": (50, 60)
    }
    def __init__(self, difficulty, max_lives=3, grid_size=9):
        self.difficulty = difficulty
        self.max_lives = max_lives
        self.lives = max_lives
        self.grid_size = grid_size
        self.board = None
        self.solution = None
        self.start_time = None
        self.end_time = None
        self.completion_time = None
        self.game_active = False
        self.generate_puzzle(difficulty)
    #tao mtran sudoku 9x9
    def _generate_9x9_puzzle(self, difficulty):
        base=3
        side=base*base

        def pattern(r,c): return (base*(r%base)+r//base+c)%side
        def shuffles(s): return rand.sample(s, len(s))
        rBase=range(base)
        rows = [g*base+r for g in shuffles(rBase) for r in shuffles(rBase)]
        cols = [g*base+c for g in shuffles(rBase) for c in shuffles(rBase)]
        nums = shuffles(range(1, base*base+1))

        self.solution = [[nums[pattern(r,c)] for c in cols] for r in rows]
        self.board = cpy.deepcopy(self.solution)

        # squares = side*side
        min_empty, max_empty = self.DIFFICULTY_LEVELS.get(difficulty, (40, 50))
        empties = rand.randint(min_empty, max_empty)
        coords = [(i,j) for i in range(side) for j in range(side)]
        rand.shuffle(coords)

        for i in range(empties):
            if i < len(coords):
                x,y=coords[i]
                self.board[x][y]=0

    def generate_puzzle(self, difficulty):
        self._generate_9x9_puzzle(difficulty)
        self.lives=self.max_lives
        self.start_time=time.time()
        self.end_time=None
        self.completion_time=None
        self.game_active=True

    #giai Sudoku bang backtracking
    #1. tim 1 o trong
    def _find_empty(self, board, side):
        for i in range(side):
            for j in range(side):
                if board[i][j]==0: return i,j
        return None, None
    #2.ktra vi tri hop le
    def _is_valid_placement(self, board, row, col, num, base):
        side=base*base
        for j in range(side):
            if board[row][j]==num: return False
        for i in range(side):
            if board[i][col]==num: return False

        box_row, box_col = base*(row//base), base*(col//base)
        for i in range(box_row, box_row+base):
            for j in range(box_col, box_col+base):
                if board[i][j]==num: return False
        return True
    #3. giai
    def _solve_sudoku(self,board,base):
        side = base*base
        row, col = self._find_empty(board, side)
        if row is None: return True

        nums = list(range(1,side+1))
        rand.shuffle(nums)

        for num in nums:
            if self._is_valid_placement(board, row, col, num, base):
                board[row][col] = num
                if self._solve_sudoku(board, base): return True
                board[row][col]=0
        return False

    #ktra xung dot
    def is_valid_move(self, row,col,num):
        if self.board[row][col]!=0: return False

        for i in range(self.grid_size):
            if self.board[row][i] == num: return False

        for i in range(self.grid_size):
            if self.board[i][col] == num: return False

        box_size=3 if self.grid_size==9 else 4
        (box_row,
         box_col) = box_size*(row//box_size), box_size*(col//box_size)
        for i in range(box_row, box_row+box_size):
            for j in range(box_col, box_col+box_size):
                if self.board[i][j] == num: return False

        return True
    #ktr di chuyen co hop voi giai phap k
    def is_correct_move(self, row,col,num): return self.solution[row][col] == num
    #game ke thuc
    def game_over(self): return self.lives<=0
    #hien thi goi y
    def get_hint(self):
        empty_cells=[]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j]==0: empty_cells.append((i,j))

        if not empty_cells:
            return None

        row, col = rand.choice(empty_cells)
        value=self.solution[row][col]

        return row, col, value

    #lay thoi gian da troi
    def get_elapsed_time(self):
        if not self.start_time: return 0
        if self.end_time: return self.end_time - self.start_time
        return time.time() - self.start_time

    #giai Sudoku bang thuat toan
    def solve_with_algorithm(self, algorithm):
        solver = get_solver(algorithm, self.board, self.grid_size)
        solved=solver.solve()
        metrics=solver.get_performance_metrics()

        if solved: return solver.solution, metrics
        else: return None, metrics
