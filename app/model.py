import random
import copy
import time
from solve import get_solver


class SudokuModel:
    """Model class xử lý logic trò chơi và xác thực"""

    DIFFICULTY_LEVELS = {
        "super_easy": (20, 30),
        "easy": (30, 40),
        "medium": (40, 50),
        "difficult": (50, 60),
        "expert": (60, 70)
    }

    DIFFICULTY_LEVELS_16X16 = {
        "super_easy": (70, 100),
        "easy": (100, 130),
        "medium": (130, 160),
        "difficult": (160, 190),
        "expert": (190, 220)
    }

    def __init__(self, difficulty="medium", max_lives=3, grid_size=9):
        self.difficulty = difficulty
        self.board = None
        self.solution = None
        self.max_lives = max_lives
        self.lives = max_lives
        self.start_time = None
        self.end_time = None
        self.completion_time = None
        self.game_active = False
        self.grid_size = grid_size
        # Trạng thái tạm dừng
        self.is_paused = False
        self._pause_start_time = None
        self._paused_accumulated = 0.0
        self.generate_puzzle(difficulty)

    def generate_puzzle(self, difficulty):
        """Tạo câu đố Sudoku mới với độ khó chỉ định"""
        if self.grid_size == 9:
            self._generate_9x9_puzzle(difficulty)
        else:
            self._generate_16x16_puzzle(difficulty)

        self.lives = self.max_lives
        self.start_time = time.time()
        self.end_time = None
        self.completion_time = None
        self.game_active = True
        # Reset trạng thái tạm dừng khi tạo mới
        self.is_paused = False
        self._pause_start_time = None
        self._paused_accumulated = 0.0

    def _generate_9x9_puzzle(self, difficulty):
        """Tạo câu đố Sudoku 9x9"""
        base = 3
        side = base * base

        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        def shuffle(s):
            return random.sample(s, len(s))

        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        self.solution = [[nums[pattern(r, c)] for c in cols] for r in rows]

        self.board = copy.deepcopy(self.solution)

        squares = side * side
        min_empty, max_empty = self.DIFFICULTY_LEVELS.get(difficulty, (40, 50))
        empties = random.randint(min_empty, max_empty)

        coords = [(i, j) for i in range(side) for j in range(side)]
        random.shuffle(coords)

        for i in range(empties):
            if i < len(coords):
                x, y = coords[i]
                self.board[x][y] = 0

    def _generate_16x16_puzzle(self, difficulty):
        """Tạo câu đố Sudoku 16x16"""

        self.board = [[0 for _ in range(16)] for _ in range(16)]
        self.solution = [[0 for _ in range(16)] for _ in range(16)]

        self._fill_diagonal_boxes()
        self._solve_sudoku(self.solution, 4)

        self.board = copy.deepcopy(self.solution)

        min_empty, max_empty = self.DIFFICULTY_LEVELS_16X16.get(difficulty, (130, 160))
        empties = random.randint(min_empty, max_empty)

        coords = [(i, j) for i in range(16) for j in range(16)]
        random.shuffle(coords)

        for i in range(empties):
            if i < len(coords):
                x, y = coords[i]
                self.board[x][y] = 0

    def _fill_diagonal_boxes(self):
        """Điền các hộp chéo của bảng 16x16 (các hộp không phụ thuộc lẫn nhau)"""
        box_size = 4
        # Điền các hộp chéo
        for i in range(0, 16, box_size):
            self._fill_box(i, i)

    def _fill_box(self, row, col):
        """Điền một hộp 4x4 với các số 1-16 ngẫu nhiên"""
        box_size = 4
        nums = list(range(1, 17))
        random.shuffle(nums)

        index = 0
        for i in range(box_size):
            for j in range(box_size):
                self.solution[row + i][col + j] = nums[index]
                index += 1

    def _solve_sudoku(self, board, base):
        """Giải câu đố Sudoku sử dụng thuật toán backtracking"""
        side = base * base

        row, col = self._find_empty(board, side)
        if row is None:
            return True

        numbers = list(range(1, side + 1))
        random.shuffle(numbers)
        for num in numbers:
            if self._is_valid_placement(board, row, col, num, base):
                board[row][col] = num

                if self._solve_sudoku(board, base):
                    return True

                board[row][col] = 0

        return False

    def _find_empty(self, board, side):
        """Tìm một ô trống trong bảng"""
        for i in range(side):
            for j in range(side):
                if board[i][j] == 0:
                    return i, j
        return None, None

    def _is_valid_placement(self, board, row, col, num, base):
        """Kiểm tra xem việc đặt 'num' tại vị trí (row, col) có hợp lệ không"""
        side = base * base

        for j in range(side):
            if board[row][j] == num:
                return False

        for i in range(side):
            if board[i][col] == num:
                return False

        box_row, box_col = base * (row // base), base * (col // base)
        for i in range(box_row, box_row + base):
            for j in range(box_col, box_col + base):
                if board[i][j] == num:
                    return False

        return True

    def is_valid_move(self, row, col, num):
        """Kiểm tra xem việc đặt 'num' tại vị trí (row, col) có hợp lệ theo quy tắc Sudoku không"""
        if self.board[row][col] != 0:
            return False

        for i in range(self.grid_size):
            if self.board[row][i] == num:
                return False

        for i in range(self.grid_size):
            if self.board[i][col] == num:
                return False

        box_size = 3 if self.grid_size == 9 else 4
        box_row, box_col = box_size * (row // box_size), box_size * (col // box_size)
        for i in range(box_row, box_row + box_size):
            for j in range(box_col, box_col + box_size):
                if self.board[i][j] == num:
                    return False

        return True

    def is_correct_move(self, row, col, num):
        """Kiểm tra xem nước đi có khớp với giải pháp không"""
        return self.solution[row][col] == num

    def is_solved(self):
        """Kiểm tra xem câu đố đã được giải chưa"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0 or self.board[i][j] != self.solution[i][j]:
                    return False
        return True

    def game_over(self):
        """Kiểm tra xem trò chơi đã kết thúc do hết mạng chưa"""
        return self.lives <= 0

    def get_hint(self):
        """Cung cấp gợi ý bằng cách hiển thị một ô đúng"""
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    empty_cells.append((i, j))

        if not empty_cells:
            return None

        row, col = random.choice(empty_cells)
        value = self.solution[row][col]

        return (row, col, value)

    def get_elapsed_time(self):
        """Lấy thời gian đã trôi qua kể từ khi bắt đầu trò chơi"""
        if not self.start_time:
            return 0
        # Nếu đã kết thúc
        if self.end_time:
            return max(0, self.end_time - self.start_time - self._paused_accumulated)
        # Nếu đang tạm dừng
        if self.is_paused and self._pause_start_time:
            return max(0, self._pause_start_time - self.start_time - self._paused_accumulated)
        # Đang chạy bình thường
        return max(0, time.time() - self.start_time - self._paused_accumulated)

    def pause(self):
        """Tạm dừng đếm thời gian và trò chơi"""
        if not self.is_paused:
            self.is_paused = True
            self._pause_start_time = time.time()

    def resume(self):
        """Tiếp tục trò chơi và tiếp tục đếm thời gian"""
        if self.is_paused:
            if self._pause_start_time:
                self._paused_accumulated += max(0, time.time() - self._pause_start_time)
            self._pause_start_time = None
            self.is_paused = False

    def solve_with_algorithm(self, algorithm):
        """
        Giải Sudoku bằng thuật toán được chỉ định.

        Args:
            algorithm: Tên thuật toán ('dfs', 'bfs', 'backtracking', 'hill_climbing')

        Returns:
            tuple: (solved_board, metrics) nếu tìm thấy lời giải, (None, metrics) nếu không
        """
        solver = get_solver(algorithm, self.board, self.grid_size)

        solved = solver.solve()

        metrics = solver.get_performance_metrics()

        if solved:
            return (solver.solution, metrics)
        else:
            return (None, metrics)