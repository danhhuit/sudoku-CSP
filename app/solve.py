import statistics
import time
import math
import heapq
import random
import copy
from collections import deque
import numpy as np
from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod


class SudokuSolver:
    """
    Lớp cơ sở cho các thuật toán giải Sudoku.
    Chứa các phương thức chung và thuộc tính để theo dõi hiệu suất.
    """

    def __init__(self, board, grid_size=9):
        """
        Khởi tạo giải thuật với bảng Sudoku và kích thước lưới.

        Args:
            board: Bảng Sudoku 2D (list of lists)
            grid_size: Kích thước lưới (9 hoặc 16)
        """
        self.board = copy.deepcopy(board)
        self.grid_size = grid_size
        self.box_size = 3 if grid_size == 9 else 4

        self.execution_time = 0
        self.states_explored = 0
        self.max_states_in_memory = 0
        self.h_value = float('inf')
        self.g_value = 0
        self.f_value = float('inf')

        self.solution = None
        self.is_solved = False

    def solve(self):
        """
        Phương thức giải Sudoku cần được ghi đè bởi các lớp con.
        """
        raise NotImplementedError("Phương thức này cần được ghi đè bởi lớp con")

    def is_valid_move(self, row, col, num):
        """
        Kiểm tra xem việc đặt 'num' tại vị trí (row, col) có hợp lệ không.

        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            num: Giá trị cần kiểm tra

        Returns:
            bool: True nếu hợp lệ, False nếu không
        """
        for j in range(self.grid_size):
            if self.board[row][j] == num:
                return False

        for i in range(self.grid_size):
            if self.board[i][col] == num:
                return False

        box_row, box_col = self.box_size * (row // self.box_size), self.box_size * (col // self.box_size)
        for i in range(box_row, box_row + self.box_size):
            for j in range(box_col, box_col + self.box_size):
                if self.board[i][j] == num:
                    return False

        return True

    def find_empty(self):
        """
        Tìm một ô trống trong bảng.

        Returns:
            tuple: (row, col) nếu tìm thấy ô trống, None nếu không có ô trống
        """
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def count_empty_cells(self):
        """
        Đếm số ô trống trong bảng.

        Returns:
            int: Số ô trống
        """
        count = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    count += 1
        return count

    def calculate_heuristic(self):
        """
        Tính giá trị heuristic h(n) dựa trên số ô trống và số xung đột.

        Returns:
            int: Giá trị heuristic
        """
        empty_cells = self.count_empty_cells()
        conflicts = self.count_conflicts()
        return empty_cells + conflicts * 10

    def count_conflicts(self):
        """
        Đếm số xung đột trong bảng (số lần một giá trị xuất hiện nhiều hơn một lần trong hàng/cột/hộp).

        Returns:
            int: Số xung đột
        """
        conflicts = 0

        for i in range(self.grid_size):
            values = [0] * (self.grid_size + 1)
            for j in range(self.grid_size):
                if self.board[i][j] != 0:
                    values[self.board[i][j]] += 1
            for val in values:
                if val > 1:
                    conflicts += val - 1

        for j in range(self.grid_size):
            values = [0] * (self.grid_size + 1)
            for i in range(self.grid_size):
                if self.board[i][j] != 0:
                    values[self.board[i][j]] += 1
            for val in values:
                if val > 1:
                    conflicts += val - 1

        for box_row in range(0, self.grid_size, self.box_size):
            for box_col in range(0, self.grid_size, self.box_size):
                values = [0] * (self.grid_size + 1)
                for i in range(box_row, box_row + self.box_size):
                    for j in range(box_col, box_col + self.box_size):
                        if self.board[i][j] != 0:
                            values[self.board[i][j]] += 1
                for val in values:
                    if val > 1:
                        conflicts += val - 1

        return conflicts

    def get_possible_values(self, row, col):
        """
        Lấy danh sách các giá trị có thể điền vào ô (row, col).

        Args:
            row: Chỉ số hàng
            col: Chỉ số cột

        Returns:
            list: Danh sách các giá trị hợp lệ
        """
        possible_values = []
        for num in range(1, self.grid_size + 1):
            if self.is_valid_move(row, col, num):
                possible_values.append(num)
        return possible_values

    def get_performance_metrics(self):
        """
        Trả về các thông số hiệu suất của thuật toán.

        Returns:
            dict: Từ điển chứa các thông số hiệu suất
        """
        return {
            'execution_time': self.execution_time,
            'states_explored': self.states_explored,
            'max_states_in_memory': self.max_states_in_memory,
            'h_value': self.h_value,
            'g_value': self.g_value,
            'f_value': self.f_value,
            'is_solved': self.is_solved
        }


class DFSSolver(SudokuSolver):
    """
    Giải Sudoku bằng thuật toán tìm kiếm theo chiều sâu (DFS).
    """

    def solve(self):
        """
        Giải Sudoku bằng DFS.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._dfs()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = copy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        self.f_value = self.g_value + self.h_value

        return result

    def _dfs(self):
        """
        Thuật toán DFS đệ quy.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        self.states_explored += 1

        # Tìm ô trống
        empty_cell = self.find_empty()
        if not empty_cell:
            return True

        row, col = empty_cell

        possible_values = self.get_possible_values(row, col)

        for num in possible_values:
            self.board[row][col] = num
            self.g_value += 1

            if self._dfs():
                return True

            self.board[row][col] = 0
            self.g_value -= 1

        return False


class BFSSolver(SudokuSolver):
    """
    Giải Sudoku bằng thuật toán tìm kiếm theo chiều rộng (BFS).
    """

    def solve(self):
        """
        Giải Sudoku bằng BFS.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._bfs()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = copy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        self.f_value = self.g_value + self.h_value

        return result

    def _bfs(self):
        """
        Thuật toán BFS sử dụng hàng đợi.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        empty_cell = self.find_empty()
        if not empty_cell:
            return True

        queue = deque([(copy.deepcopy(self.board), 0)])  # (board, g_value)

        visited = set()

        while queue:
            self.max_states_in_memory = max(self.max_states_in_memory, len(queue))

            current_board, g_value = queue.popleft()
            self.states_explored += 1

            board_str = str(current_board)
            if board_str in visited:
                continue

            visited.add(board_str)

            self.board = copy.deepcopy(current_board)
            self.g_value = g_value

            empty_cell = self.find_empty()
            if not empty_cell:
                return True

            row, col = empty_cell

            possible_values = self.get_possible_values(row, col)

            for num in possible_values:
                new_board = copy.deepcopy(current_board)
                new_board[row][col] = num
                queue.append((new_board, g_value + 1))

        return False


class BacktrackingSolver(SudokuSolver):
    """
    Giải Sudoku bằng thuật toán quay lui (Backtracking) với tối ưu hóa.
    """

    def solve(self):
        """
        Giải Sudoku bằng Backtracking.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 1

        result = self._backtrack()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = copy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        self.f_value = self.g_value + self.h_value

        return result

    def _find_best_empty_cell(self):
        """
        Tìm ô trống với ít giá trị có thể nhất (MRV - Minimum Remaining Values).

        Returns:
            tuple: (row, col, possible_values) hoặc None nếu không có ô trống
        """
        min_possibilities = self.grid_size + 1
        best_cell = None
        best_values = []

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    possible_values = self.get_possible_values(i, j)
                    num_possibilities = len(possible_values)

                    if num_possibilities < min_possibilities:
                        min_possibilities = num_possibilities
                        best_cell = (i, j)
                        best_values = possible_values

                        if num_possibilities == 1:
                            return (i, j, best_values)

        if best_cell:
            return (*best_cell, best_values)
        return None

    def _backtrack(self):
        """
        Thuật toán Backtracking với tối ưu hóa MRV.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        self.states_explored += 1

        best_empty = self._find_best_empty_cell()
        if not best_empty:
            return True

        row, col, possible_values = best_empty

        if not possible_values:
            return False

        for num in possible_values:
            self.board[row][col] = num
            self.g_value += 1

            if self._backtrack():
                return True

            self.board[row][col] = 0
            self.g_value -= 1

        return False


class SimulatedAnnealingSolver(SudokuSolver):
    """
    Giải Sudoku bằng thuật toán mô phỏng luyện kim (Simulated Annealing).
    Thuật toán này dựa trên việc tối ưu hóa bằng cách chấp nhận cả những thay đổi làm tăng chi phí
    với một xác suất nhất định, giúp tránh bị mắc kẹt ở cực tiểu cục bộ.
    """

    def solve(self):
        """
        Giải Sudoku bằng Simulated Annealing.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 1

        fixed_cells = self._create_fixed_cells()

        list_of_blocks = self._create_list_of_blocks()

        self._randomly_fill_blocks(fixed_cells, list_of_blocks)

        result = self._simulated_annealing(fixed_cells, list_of_blocks)

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = copy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self._calculate_number_of_errors()

        self.f_value = self.g_value + self.h_value

        return result

    def _create_fixed_cells(self):
        """
        Tạo ma trận đánh dấu các ô cố định trong bảng Sudoku.
        Giá trị 1 cho biết ô đó đã có giá trị ban đầu, 0 cho biết ô trống.

        Returns:
            list: Ma trận đánh dấu các ô cố định
        """
        fixed_cells = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] != 0:
                    fixed_cells[i][j] = 1
        return fixed_cells

    def _create_list_of_blocks(self):
        """
        Tạo danh sách các khối trong bảng Sudoku (3x3 cho lưới 9x9, 4x4 cho lưới 16x16).

        Returns:
            list: Danh sách các khối
        """
        final_list_of_blocks = []
        block_size = self.box_size

        for r in range(0, self.grid_size):
            tmp_list = []
            block1 = [i + block_size * ((r) % block_size) for i in range(0, block_size)]
            block2 = [i + block_size * math.trunc((r) / block_size) for i in range(0, block_size)]
            for x in block1:
                for y in block2:
                    tmp_list.append([x, y])
            final_list_of_blocks.append(tmp_list)
        return final_list_of_blocks

    def _randomly_fill_blocks(self, fixed_cells, list_of_blocks):
        """
        Điền ngẫu nhiên các giá trị vào các khối của bảng Sudoku.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            list_of_blocks: Danh sách các khối
        """
        for block in list_of_blocks:
            for box in block:
                if self.board[box[0]][box[1]] == 0:
                    current_block_values = []
                    for b in block:
                        current_block_values.append(self.board[b[0]][b[1]])

                    possible_values = [i for i in range(1, self.grid_size + 1) if i not in current_block_values]
                    if possible_values:
                        self.board[box[0]][box[1]] = random.choice(possible_values)

    def _calculate_number_of_errors(self):
        """
        Tính tổng số lỗi trên toàn bộ bảng Sudoku (số xung đột trong hàng và cột).

        Returns:
            int: Tổng số lỗi
        """
        number_of_errors = 0
        for i in range(self.grid_size):
            number_of_errors += self._calculate_errors_row_column(i, i)
        return number_of_errors

    def _calculate_errors_row_column(self, row, column):
        """
        Tính số lỗi (số phần tử trùng lặp) trong một hàng và một cột.

        Args:
            row: Chỉ số hàng
            column: Chỉ số cột

        Returns:
            int: Số lỗi trong hàng và cột
        """
        col_values = [self.board[i][column] for i in range(self.grid_size) if self.board[i][column] != 0]
        unique_col_values = set(col_values)
        col_errors = len(col_values) - len(unique_col_values)

        row_values = [self.board[row][j] for j in range(self.grid_size) if self.board[row][j] != 0]
        unique_row_values = set(row_values)
        row_errors = len(row_values) - len(unique_row_values)

        return col_errors + row_errors

    def _two_random_boxes_within_block(self, fixed_cells, block):
        """
        Chọn ngẫu nhiên hai ô không cố định trong một khối.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            block: Danh sách các ô trong một khối

        Returns:
            list: Hai ô được chọn hoặc None nếu không tìm thấy
        """
        non_fixed_boxes = [box for box in block if fixed_cells[box[0]][box[1]] != 1]

        if len(non_fixed_boxes) < 2:
            return None

        first_box = random.choice(non_fixed_boxes)
        second_box = random.choice([box for box in non_fixed_boxes if box != first_box])

        return [first_box, second_box]

    def _flip_boxes(self, boxes_to_flip):
        """
        Hoán đổi giá trị của hai ô.

        Args:
            boxes_to_flip: Hai ô cần hoán đổi

        Returns:
            list: Bảng Sudoku sau khi hoán đổi
        """
        proposed_board = copy.deepcopy(self.board)

        place_holder = proposed_board[boxes_to_flip[0][0]][boxes_to_flip[0][1]]
        proposed_board[boxes_to_flip[0][0]][boxes_to_flip[0][1]] = proposed_board[boxes_to_flip[1][0]][
            boxes_to_flip[1][1]]
        proposed_board[boxes_to_flip[1][0]][boxes_to_flip[1][1]] = place_holder

        return proposed_board

    def _proposed_state(self, fixed_cells, list_of_blocks):
        """
        Tạo trạng thái đề xuất bằng cách hoán đổi hai ô không cố định trong một khối.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            list_of_blocks: Danh sách các khối

        Returns:
            tuple: (bảng mới, các ô đã hoán đổi) hoặc (bảng hiện tại, None) nếu không thể tạo trạng thái mới
        """
        shuffled_blocks = random.sample(list_of_blocks, len(list_of_blocks))

        for random_block in shuffled_blocks:
            fixed_count = sum(fixed_cells[box[0]][box[1]] for box in random_block)
            max_fixed = 6 if self.grid_size == 9 else 12
            if fixed_count > max_fixed:
                continue
            boxes_to_flip = self._two_random_boxes_within_block(fixed_cells, random_block)
            if boxes_to_flip:
                proposed_board = self._flip_boxes(boxes_to_flip)
                return proposed_board, boxes_to_flip
        return self.board, None

    def _choose_new_state(self, fixed_cells, list_of_blocks, sigma):
        """
        Quyết định chấp nhận trạng thái mới hay không dựa trên chi phí và nhiệt độ.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            list_of_blocks: Danh sách các khối
            sigma: Nhiệt độ hiện tại

        Returns:
            tuple: (bảng mới, thay đổi chi phí)
        """
        proposed_board, boxes_to_flip = self._proposed_state(fixed_cells, list_of_blocks)

        if boxes_to_flip is None:
            return self.board, 0

        current_board = copy.deepcopy(self.board)

        current_cost = 0
        for box in boxes_to_flip:
            current_cost += self._calculate_errors_row_column(box[0], box[1])

        self.board = proposed_board

        new_cost = 0
        for box in boxes_to_flip:
            new_cost += self._calculate_errors_row_column(box[0], box[1])

        cost_difference = new_cost - current_cost

        rho = math.exp(-cost_difference / sigma)

        if random.uniform(0, 1) < rho:
            return proposed_board, cost_difference
        else:
            self.board = current_board
            return current_board, 0

    def _calculate_initial_sigma(self, fixed_cells, list_of_blocks):
        """
        Tính giá trị sigma ban đầu dựa trên độ lệch chuẩn của các chi phí khác nhau.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            list_of_blocks: Danh sách các khối

        Returns:
            float: Giá trị sigma ban đầu
        """
        list_of_differences = []
        current_board = copy.deepcopy(self.board)

        tmp_board = copy.deepcopy(self.board)

        for i in range(10):
            proposed_board, boxes_to_flip = self._proposed_state(fixed_cells, list_of_blocks)

            if boxes_to_flip:
                self.board = proposed_board
                list_of_differences.append(self._calculate_number_of_errors())

        self.board = tmp_board

        if len(list_of_differences) > 1:
            return statistics.pstdev(list_of_differences)
        else:
            return 1.0

    def _choose_number_of_iterations(self, fixed_cells):
        """
        Xác định số lần lặp dựa trên số ô cố định.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định

        Returns:
            int: Số lần lặp
        """
        fixed_count = sum(sum(row) for row in fixed_cells)
        base_iterations = 100
        if self.grid_size == 16:
            base_iterations = 200

        return max(fixed_count, base_iterations)

    def _simulated_annealing(self, fixed_cells, list_of_blocks):
        """
        Thuật toán Simulated Annealing để giải Sudoku.

        Args:
            fixed_cells: Ma trận đánh dấu các ô cố định
            list_of_blocks: Danh sách các khối

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        solution_found = False
        attempts = 0
        max_attempts = 3

        while not solution_found and attempts < max_attempts:
            attempts += 1
            self.states_explored += 1

            if attempts > 1:
                self.board = [[0 if fixed_cells[i][j] == 0 else self.board[i][j]
                               for j in range(self.grid_size)]
                              for i in range(self.grid_size)]
                self._randomly_fill_blocks(fixed_cells, list_of_blocks)

            decrease_factor = 0.99
            stuck_count = 0

            sigma = self._calculate_initial_sigma(fixed_cells, list_of_blocks)

            score = self._calculate_number_of_errors()

            iterations = self._choose_number_of_iterations(fixed_cells)

            if score <= 0:
                solution_found = True
                break

            max_loops = 500
            current_loop = 0

            while not solution_found and current_loop < max_loops:
                current_loop += 1
                previous_score = score

                for i in range(iterations):
                    new_board, score_diff = self._choose_new_state(fixed_cells, list_of_blocks, sigma)

                    self.board = new_board
                    score += score_diff

                    self.states_explored += 1
                    self.g_value += 1 if score_diff != 0 else 0

                    if score <= 0:
                        solution_found = True
                        break

                sigma *= decrease_factor

                if score <= 0:
                    solution_found = True
                    break

                if score >= previous_score:
                    stuck_count += 1
                else:
                    stuck_count = 0

                if stuck_count > 80:
                    sigma += 2

                if self._calculate_number_of_errors() == 0:
                    solution_found = True
                    break

                if sigma < 0.001:
                    break

        return solution_found


class AStarSolver(SudokuSolver):
    """
    Giải Sudoku bằng thuật toán A*.
    Sử dụng hàm heuristic để tìm đường đi tối ưu nhất đến lời giải.
    """

    def solve(self):
        """
        Giải Sudoku bằng A*.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._astar()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = copy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        self.f_value = self.g_value + self.h_value

        return result

    def _astar(self):
        """
        Thuật toán A* sử dụng hàng đợi ưu tiên.

        Returns:
            bool: True nếu tìm thấy lời giải, False nếu không
        """
        empty_cell = self.find_empty()
        if not empty_cell:
            return True

        priority_queue = [(self.calculate_heuristic(), 0, copy.deepcopy(self.board))]
        heapq.heapify(priority_queue)

        visited = set()

        while priority_queue:
            self.max_states_in_memory = max(self.max_states_in_memory, len(priority_queue))

            f_value, g_value, current_board = heapq.heappop(priority_queue)
            self.states_explored += 1

            board_str = str(current_board)
            if board_str in visited:
                continue

            visited.add(board_str)

            self.board = copy.deepcopy(current_board)
            self.g_value = g_value

            empty_cell = self.find_empty()
            if not empty_cell:
                return True

            row, col = empty_cell

            possible_values = self.get_possible_values(row, col)

            for num in possible_values:
                new_board = copy.deepcopy(current_board)
                new_board[row][col] = num

                self.board = new_board
                h_value = self.calculate_heuristic()
                new_g_value = g_value + 1
                f_value = h_value + new_g_value

                heapq.heappush(priority_queue, (f_value, new_g_value, new_board))

        return False

class SudokuSolver(ABC):
    def __init__(self, board: List[List[int]], grid_size: int):
        self.board = [row[:] for row in board]
        self.grid_size = grid_size
        self.box_size = 3 if grid_size == 9 else 4
        self.states_explored = 0
        self.max_states_in_memory = 0
        self.execution_time = 0
        self.solution = None
        self.h_value = 0
        self.g_value = 0
        self.f_value = 0
        self.is_solved = False

    @abstractmethod
    def solve(self) -> bool:
        pass

    def get_performance_metrics(self) -> Dict[str, Any]:
        return {
            "is_solved": self.is_solved,
            "execution_time": self.execution_time,
            "states_explored": self.states_explored,
            "max_states_in_memory": self.max_states_in_memory,
            "h_value": self.h_value,
            "g_value": self.g_value,
            "f_value": self.f_value
        }

    def is_valid_move(self, row: int, col: int, num: int) -> bool:
        if self.board[row][col] != 0:
            return False
        for i in range(self.grid_size):
            if self.board[row][i] == num:
                return False
        for i in range(self.grid_size):
            if self.board[i][col] == num:
                return False
        box_row, box_col = self.box_size * (row // self.box_size), self.box_size * (col // self.box_size)
        for i in range(box_row, box_row + self.box_size):
            for j in range(box_col, box_col + self.box_size):
                if self.board[i][j] == num:
                    return False
        return True

    def is_board_valid(self) -> bool:
        for row in range(self.grid_size):
            nums = [self.board[row][col] for col in range(self.grid_size) if self.board[row][col] != 0]
            if len(nums) != len(set(nums)):
                return False
        for col in range(self.grid_size):
            nums = [self.board[row][col] for row in range(self.grid_size) if self.board[row][col] != 0]
            if len(nums) != len(set(nums)):
                return False
        for box_row in range(0, self.grid_size, self.box_size):
            for box_col in range(0, self.grid_size, self.box_size):
                nums = []
                for row in range(box_row, box_row + self.box_size):
                    for col in range(box_col, box_col + self.box_size):
                        if self.board[row][col] != 0:
                            nums.append(self.board[row][col])
                if len(nums) != len(set(nums)):
                    return False
        return True

def get_solver(algorithm, board, grid_size=9):
    """
    Trả về đối tượng giải thuật tương ứng với thuật toán được chọn.

    Args:
        algorithm: Tên thuật toán ('dfs', 'bfs', 'backtracking', 'simulated_annealing', 'A*')
        board: Bảng Sudoku 2D
        grid_size: Kích thước lưới (9 hoặc 16)

    Returns:
        SudokuSolver: Đối tượng giải thuật
    """
    if algorithm == 'DFS':
        return DFSSolver(board, grid_size)
    elif algorithm == 'BFS':
        return BFSSolver(board, grid_size)
    elif algorithm == 'BackTracking':
        return BacktrackingSolver(board, grid_size)
    elif algorithm == 'SimulatedAnnealing':
        return SimulatedAnnealingSolver(board, grid_size)
    elif algorithm == 'A*':
        return AStarSolver(board, grid_size)
    else:
        raise ValueError(f"Thuật toán không hợp lệ: {algorithm}")