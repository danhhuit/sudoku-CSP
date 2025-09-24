import statistics as stats
import time
import math
import heapq
import random as rand
import copy as cpy
# from tabnanny import check

# import numpy as np
from collections import deque
# from typing import List, Dict, Tuple, Any
# from abc import ABC, abstractmethod

class SudokuAlgorithm:

    def __init__(self, board, grid_size=9):
        self.box_size = None
        self.board = cpy.deepcopy(board)
        self.grid_size = grid_size
        self.box_size = 3

        self.execution_time = 0
        self.states_explored = 0
        self.max_states_in_memory = 0
        self.h_value = float('inf')
        self.g_value = 0
        self.f_value = float('inf')

        self.solution = None
        self.is_solved = False

    def solve(self):
        raise NotImplementedError("") #

    #ktra buoc di chuyen
    def is_valid_move(self, row, col, num):
        for j in range(self.grid_size):
            if self.board[row][j] == num:
                return False

        for i in range(self.grid_size):
            if self.board[i][col] == num:
                return False

        box_row, box_col = self.box_size * (row // self.box_size), self.box_size * (col // self.box_size)
        for i in range(box_row, box_row+self.box_size):
            for j in range(box_col, box_col+self.box_size):
                if self.board[i][j] == num:
                    return False

        return True

    #tim o trong, i = row, j=col
    def is_empty(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    return i, j
        return None

    #dem o trong
    def count_empty(self):
        count = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    count += 1
        return count

    #dem so xung dot (ktra so lan xuat hien nhieu hon 1 lan trong hang/cot/mtran(box))
    def count_conflicts(self):
        conflicts = 0
        #ktra hang & cot

        for index in range(self.grid_size):
            row_values = [0] * (self.grid_size+1)
            col_values = [0] * (self.grid_size+1)

            for k in range(self.grid_size):
                # ktr hang (index, k)
                if self.board[index][k] != 0:
                    row_values[self.board[index][k]] += 1
                # ktr cot (k, index)
                if self.board[k][index] != 0:
                    col_values[self.board[k][index]] += 1
            # dem conflicts trong hang
            for val in row_values:
                if val > 1:
                    conflicts += val - 1

            # dem conflicts trong cot
            for val in col_values:
                if val > 1:
                    conflicts += val - 1

        #ktra hop
        for box_row in range(0, self.grid_size, self.box_size):
            for box_col in range(0, self.grid_size, self.box_size):
                values = [0] * (self.grid_size + 1)
                for i in range(box_row, box_row+self.box_size):
                    for j in range(box_col, box_col+self.box_size):
                        if self.board[i][j] != 0:
                            values[self.board[i][j]] += 1
                for val in values:
                    if val > 1:
                        conflicts += val - 1
        return conflicts

    #tinh gia tri heuristic h(n)
    def calculate_heuristic(self):
        empty_cells = self.count_empty()
        conflicts = self.count_conflicts()
        return empty_cells + conflicts * 10

    # tim nhung vi tri co the dien vao o (row, col)
    def get_possible_values(self, row ,col):
        possible_values = []
        for num in range(1, self.grid_size +1):
            if self.is_valid_move(row, col, num):
                possible_values.append(num)
        return possible_values

    #thong so hieu suat cua thuat toan
    def get_performance_algorithm(self):
        return {
            'execution_time': self.execution_time,
            'states_explored': self.states_explored,
            'max_states_in_memory': self.max_states_in_memory,
            'h_value': self.h_value,
            'g_value': self.g_value,
            'f_value': self.f_value,
            'is_solved': self.is_solved
        }

class DFSAlgorithm(SudokuAlgorithm):
    #giai bang thuat toan DFS
    def solve(self):
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._dfs()

        self.execution_time = time.time() - start_time
        self.is_solved = True
        self.solution = cpy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        return result
    #giai bang de quy
    def _dfs(self):
        self.states_explored += 1

        empty_cells = self.is_empty()
        #neu k co o nao trong => da hoan thanh
        if not empty_cells: return True
        #lay toa do o trong
        row, col = empty_cells

        possible_values = self.get_possible_values(row, col)

        #thu tung gia tri trong (possible_values) dat vao o trong
        #dong thoi tang g de the hien so buoc da di
        #goi de quy _dfs() de thu cac o con lai
        #neu thanh cong => true
        #neu that bai => false => gan lai 0, giam g
        for num in possible_values:
            self.board[row][col] = num
            self.g_value += 1

            if self._dfs(): return True

            self.board[row][col] = 0
            self.g_value -= 1
        return False

class BFSAlgorithm(SudokuAlgorithm):
    #giai bang thuat toan BFS
    def solve(self):
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._bfs()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = cpy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        #f(n)=g(n)+h(n)
        self.f_value=self.g_value+self.h_value

        return result
    #BFS su dung hang doi
    def _bfs(self):

        empty_cells = self.is_empty()
        if not empty_cells: return True
        #luu trang thai
        queue = deque([(cpy.deepcopy(self.board),0)])#(board, g_value=0)

        visited = set()

        while queue:
            self.max_states_in_memory = max(self.max_states_in_memory, len(queue))
            #lay trang thai tu dau hang doi (FIFO-first in first out)
            current_board, g_value = queue.popleft()
            self.states_explored += 1

            board_str = str(current_board)
            #dung visited de ktra trang thai, tranh duyet lai trang thai da duyet
            if board_str in visited:
                continue
            visited.add(board_str)
            #cap nhat trang thai hien tai
            self.board = cpy.deepcopy(current_board)
            self.g_value += g_value

            check_empty_cells = self.is_empty()
            if not check_empty_cells: return True #done


            #lay 1 o trong, tim tat ca gia tri hop le
            #voi moi gtri, tao 1 board moi va dua vao queue de duyet
            #nhung board co cung g_value se dc xet trc
            row, col = check_empty_cells

            possible_values = self.get_possible_values(row, col)

            for num in possible_values:
                new_board = cpy.deepcopy(current_board)
                new_board[row][col] = num
                queue.append((new_board, g_value+1))

        return False

class BackTrackingAlgorithm(SudokuAlgorithm):
    #giai bang thuat toan quay lui (backtracking)
    def solve(self):
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 1

        result = self._backtracking()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = cpy.deepcopy(self.board) if result else None

        if result:
            self.h_value = 0
        else:
            self.h_value = self.calculate_heuristic()

        self.f_value=self.g_value+self.h_value

        return result

    #tim o trong voi it gia tri nhat (MRV-Minimun Remaining Values).
    def _find_best_empty_cell(self):
        min_possibilities = self.grid_size+1
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
                            return i,j,best_values
        if best_cell:
            return *best_cell, best_values
        return None

    def _backtracking(self):
        self.states_explored += 1

        best_empty_cell = self._find_best_empty_cell()
        if not best_empty_cell: return True

        row, col, possible_values = best_empty_cell

        if not possible_values: return False

        for num in possible_values:
            self.board[row][col] = num
            self.g_value += 1

            if self._backtracking(): return True

            self.board[row][col] = 0
            self.g_value -= 1
        return False

class AStarAlgorithm(SudokuAlgorithm):
    #giai bang giai thuat A*
    def solve(self):
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 0

        result = self._astar()

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = cpy.deepcopy(self.board) if result else None

        if result: self.h_value = 0
        else: self.h_value = self.calculate_heuristic()
        self.f_value=self.g_value+self.h_value
        return result

    def _astar(self):
        empty_cells = self.is_empty()
        if not empty_cells: return True

        priority_queue = [(self.calculate_heuristic(), 0, cpy.deepcopy(self.board))]
        heapq.heapify(priority_queue)

        visited = set()

        while priority_queue:
            self.max_states_in_memory = max(self.max_states_in_memory, len(priority_queue))
            f_value, g_value, current_board = heapq.heappop(priority_queue)
            self.states_explored += 1

            board_str=str(current_board)
            if board_str in visited: continue
            visited.add(board_str)

            self.board = cpy.deepcopy(current_board)
            self.g_value += g_value

            empty_cells = self.is_empty()
            if not empty_cells: return True

            row, col = empty_cells
            possible_values = self.get_possible_values(row, col)

            for num in possible_values:
                new_board = cpy.deepcopy(current_board)
                new_board[row][col] = num

                self.board=new_board
                h_value = self.calculate_heuristic()
                new_g_value = g_value+1
                f_value=h_value+new_g_value
                heapq.heappush(priority_queue, (f_value, new_g_value, new_board))
        return False
#giai bang giai thuat mo phong luyen kim ***
class SimulatedAnnealing(SudokuAlgorithm):
    def solve(self):
        start_time = time.time()
        self.states_explored = 0
        self.max_states_in_memory = 1

        fixed_cells = self._create_fixed_cells()
        list_of_blocks = self._create_list_of_blocks()
        self._randomly_fill_blocks(fixed_cells, list_of_blocks)

        result = self._simulated_annealing(fixed_cells, list_of_blocks)

        self.execution_time = time.time() - start_time
        self.is_solved = result
        self.solution = cpy.deepcopy(self.board) if result else None

        if result: self.h_value = 0
        else: self.h_value = self._calculate_number_of_errors()

        self.f_value=self.g_value+self.h_value
        return result

    #tao mtran danh dau cac o co dinh trong bang Sudoku
    def _create_fixed_cells(self):
        fixed_cells = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] != 0:
                    fixed_cells[i][j] = 1
        return fixed_cells

    #tao danh sach cac khoi trong bang sudoku
    def _create_list_of_blocks(self):
        final_list = []
        block_size = self.grid_size
        for r in range(0, self.grid_size):
            tmp_list = []
            #b1:block 1, b2: block 2
            b1 = [i+block_size *(r%block_size) for i in range(0, block_size)]
            b2 = [i + block_size * math.trunc(r / block_size) for i in range(0, block_size)]
            for i in b1:
                for j in b2:
                    tmp_list.append([i,j])
            final_list.append(tmp_list)
        return final_list

    #dien ngau nhien cac gtri vao cac khoi
    def _randomly_fill_blocks(self, fixed_cells, list_of_blocks):
        #block:bl, box:bx
        for bl in list_of_blocks:
            for bx in bl:
                if self.board[bx[0]][bx[1]] == 0:
                    current_block_values = []
                    for b in bl:
                        current_block_values.append(self.board[b[0]][b[1]])
                    possible_values = [i for i in range(1, self.grid_size+1) if i not in current_block_values]
                    if possible_values:
                        self.board[bx[0]][bx[1]] = rand.choice(possible_values)

    #tinh tong so loi tren toan bo bang
    def _calculate_number_of_errors(self):
        error_count=0
        for i in range(self.grid_size):
            error_count+=self._calculate_number_row_col(i,i)
        return error_count
    #tinh so loi
    def _calculate_number_row_col(self, row, col):
        col_values=\
            [self.board[i][col] for i in range(self.grid_size) if self.board[i][col]!=0]
        unique_col_values = set(col_values)
        col_er = len(col_values)-len(unique_col_values)

        row_values = \
            [self.board[row][j] for j in range(self.grid_size) if self.board[row][j] != 0]
        unique_row_values = set(row_values)
        row_er = len(row_values) - len(unique_row_values)

        return col_er + row_er
    #chon ngau nhien hai o k co dinh trong 1 khoi
    def _two_random_boxes_within_block(self, fixed_cells, block):
        non_fixed_boxes = \
            [box for box in block if fixed_cells[box[0]][box[1]]!=1]
        if len(non_fixed_boxes)<2: return None
        first_box = rand.choice(non_fixed_boxes)
        second_box = rand.choice([box for box in non_fixed_boxes if box != first_box])
        return [first_box, second_box]

    #hoan doi vi tri 2box
    def _flip_boxes(self, boxes):
        proposed_board = cpy.deepcopy(self.board)
        temp = proposed_board[boxes[0][0]][boxes[0][1]]
        proposed_board[boxes[0][0]][boxes[0][1]] = proposed_board[boxes[1][0]][boxes[1][1]]
        proposed_board[boxes[1][0]][boxes[1][1]] = temp
        return proposed_board

    #tao trang thai de xuat (hoan doi 2 box k co dinh trong 1 block)
    def _proposed_state(self, fixed_cells, list_of_blocks):
        shuffled_block = rand.sample(list_of_blocks, len(list_of_blocks))

        for rand_block in shuffled_block:
            fixed_count=sum(fixed_cells[box[0]][box[1]] for box in rand_block)
            max_fixed = 6 if self.grid_size == 9 else 12
            if fixed_count > max_fixed: continue
            boxes_to_flip = self._two_random_boxes_within_block(fixed_cells, rand_block)
            if boxes_to_flip:
                proposed_board = self._flip_boxes(boxes_to_flip)
                return proposed_board, boxes_to_flip
        return self.board, None

    #tao trang thai moi theo chi phi va nhiet do
    #sigma: nhiet do htai
    def _choose_new_state(self, fixed_cells, list_of_blocks, sigma):
        (proposed_board,
         boxes_to_flip)= self._proposed_state(fixed_cells, list_of_blocks)
        if boxes_to_flip is None: return self.board, 0
        cur_board = cpy.deepcopy(self.board)
        cur_cost = 0
        for box in boxes_to_flip:
            cur_cost+=self._calculate_number_of_errors(box[0], box[1])
        self.board=proposed_board
        new_cost = 0
        for box in boxes_to_flip:
            new_cost+=self._calculate_number_of_errors(box[0], box[1])

        cost_diff = new_cost - cur_cost
        rho = math.exp(-cost_diff/sigma)

        if rand.uniform(0,1) < rho: return proposed_board, boxes_to_flip
        else:
            self.board=cur_board
            return cur_board, 0

    #tinh gtri sigma ban dau (dua tren do lech chuan cua cac chi phi)
    def _calculate_initial_sigma(self, fixed_cells, list_of_blocks):
        list_of_diff = []
        # cur_board = cpy.deepcopy(self.board)
        tmp_board = cpy.deepcopy(self.board)

        for i in range(10):
            (proposed_board,
             boxes_to_flip) = self._proposed_state(fixed_cells, list_of_blocks)
            if boxes_to_flip:
                self.board=proposed_board
                list_of_diff.append(self._calculate_number_of_errors())
        self.board = tmp_board

        if len(list_of_diff)>1: return stats.pstdev(list_of_diff)
        else: return 1.0

    #tinh so lan lap dua tren so o co dinh
    def _choose_number_of_iterations(self, fixed_cells):
        fixed_count=sum(sum(row) for row in fixed_cells)
        base_iterations=100
        if self.grid_size == 16: base_iterations=200
        return max(fixed_count, base_iterations)

    #thuat toan mo phong luyen kim
    def _simulated_annealing(self, fixed_cells, list_of_blocks):
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

def get_solver(algorithm, board, grid_size=9):
    if algorithm == 'BFS': return BFSAlgorithm(board, grid_size)
    elif algorithm == 'DFS': return DFSAlgorithm(board, grid_size)
    elif algorithm == 'BackTracking': return BackTrackingAlgorithm(board, grid_size)
    elif algorithm == 'SimulatedAnnealing': return SimulatedAnnealing(board, grid_size)
    elif algorithm == 'A*': return AStarAlgorithm(board, grid_size)
    else: return ValueError(f"Algorithm {algorithm} not recognized")