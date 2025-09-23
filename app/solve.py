import statistics as stats
import time
import math
import heapq
import random as rand
import copy as cpy
from tabnanny import check

import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Any
from abc import ABC, abstractmethod

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
                    return (i, j)
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

        self.execution_time = time - start_time
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
                            return (i,j,best_values)
        if best_cell:
            return (*best_cell, best_values)
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
                f_value=h_value+new_g_val
                heapq.heappush(priority_queue, (f_value, new_g_value, new_board))
        return False