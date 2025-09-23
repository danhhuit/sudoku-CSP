import random as rnd
import copy as cpy
import time
from solve import get_solution

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
    self.generate_puzzule(difficulty)
