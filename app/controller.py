import time
import copy as cpy

class SudokuController:
    def __init__(self, model, view, app):
        self.model = model
        self.view = view
        self.app = app
        self.init_board = cpy.deepcopy(model.board)
        self.view.set_controller(self)
        self._update_view()
        self.view.update_lives_display(self.model.lives)
    # cap nhat view voi trang thai model hien tai
    def _update_view(self):
        original_cells = set()
        for i in range(self.model.grid_size):
            for j in range(self.model.grid_size):
                if self.model.board[i][j] != 0:
                    original_cells.add((i,j))
        self.view.update_cells(self.model.board, original_cells)

    #bat dau tro choi moi
    def new_game(self, difficulty, grid_size=9):
        self.model.grid_size = grid_size
        self.model.generate_puzzule(difficulty)
        self._update_view()
        self.view.update_lives_display(self.model.lives)
        self.init_board = cpy.deepcopy(self.model.board)

    #thuc hien nuoc di & cap nhat view
    def move(self, row, col, num):
        if (row, col) in self.view.original_cells:
            return
        if self.model.game_over():
            self.view.show_error("Game Over",
                                 "Trò chơi đã kết thúc")
            return
        if self.model.is_correct_move(row, col, num):
            self.model.board[row][col] = num
            self.view.highlight_cell(row, col, self.view.success_color)
            if self.model.is_solved():
                self.model.end_time = time.time()
                self.model.completion_time = self.model.end_time - self.model.start_time
                self.view.show_success(self.model.completion_time)

        else:
            self.model.lives -= 1
            self.view.update_lives_display(self.model.lives)

            self.view.highlight_cell(row, col, self.view.error_color)

            if self.model.game_over():
                self.view.show_game_over()
            else:
                lives_message = f"Số không đúng! Bạn còn {self.model.lives} mạng."
                self.view.show_error("Số không đúng", lives_message)

            self.view.master.after(1500, lambda: self.clear_cell(row, col))

    #xoa o cu the
    def clear_cell(self, row, col):
        if (row, col) not in self.view.original_cells:
            self.model.board[row][col] = 0
            self.view.cell_vars[row][col].set("")
            self.view.highlight_cell(row, col, "white")

    #cung cap goi y
    def get_hint(self):
        if self.model.game_over():
            self.view.show_error("Game Over",
                                 "Trò chơi đã kết thúc")
            return

        hint = self.model.get_hint()
        if hint:
            row, col, value = hint
            self.view.cell_vars[row][col].set(str(value))

            self.model.board[row][col] = value
            self.view.hightlight_cell(row, col, self.view.highlight_color)

            self.view.update_status(f"Gợi ý: Đặt {value} tại vị trí ({row+1}, {col+1})")

            if self.model.is_solved():
                self.model.end_time = time.time()
                self.model.completion_time = self.model.end_time - self.model.start_time
                self.view.show_success(self.model.completion_time)

        else:
            self.view.show_message("Không có gợi ý",
                                   "Không còn ô trống để cung cấp gợi ý.")

    #kiem tra giai phap va danh dau loi
    def check_solution(self):
        flag = False
        for i in range(self.model.grid_size):
            for j in range(self.model.grid_size):
                if self.model.board[i][j] != 0 or (i, j) in self.view.original_cells:
                    continue

                if not self.model.is_correct_move(i, j, self.model.board[i][j]):
                    self.view.highlight_cell(i, j, self.view.error_color)
                    flag = True

        if flag:
            self.view.show_message( "Kết quả kiểm tra",
                                    "Có lỗi trong cách giải của bạn." +
                                    "Các ô không đúng được đánh dấu màu đỏ.")
        else:
            if self.model.is_solved():
                self.model.end_time = time.time()
                self.model.completion_time = self.model.end_time - self.model.start_time
                self.view.show_success(self.model.completion_time)
            else:
                self.view.show_message("Kết quả kiểm tra",
                                       "Không tìm thấy lỗi trong cách giải của bạn.")

    #giai toan bo cau do
    def solve_puzzle(self):
        if self.view.cofirm_dialog("Hiển thị kết quả",
                                   "Bạn chắc chắn muốn xem kết quả?"):
            for i in range(self.model.grid_size):
                for j in range(self.model.grid_size):
                    if self.model.board[i][j] == 0:
                        value = self.model.solution[i][j]
                        self.model.board[i][j] = value

                        self.view.cell_vars[i][j].set(str(value))
                        self.view.highlight_cell(i, j, self.view.hightlight_color)

            self.model.game_active = False
            self.view.update_status("Kết quả đã được hiển thị. Bắt đầu trò chơi mới.")

    #xoa input & algorithm, khoi phuc bang
    def clear_board(self):
        if self.view.confirm_dialog("Xóa bảng",
                                    "Bạn chắc chắn muốn xóa bảng?"):
            self.model.board = cpy.deepcopy(self.model.board)
            self._update_view()
            self.view.update_status("Đã khôi phục bảng về trạng thái ban đầu.")

    #giai bang thuat toan (backtracking, forward checking, dfs, bfs, A* search)
    def solve_with_algorithm(self, algorithm):
        if self.model.game_over():
            self.view.show_error("Game Over",
                                 "Trò chơi đã kết thúc.")
            return

        self.view.update_status(f"Đang giải bằng thuật toán {algorithm}")

        solution, metrics = self.model.sole_with_algorithm(algorithm)

        if solution:
            self.model.board = solution
            self._update_view()
            self.view.update_status(f"Đã giải xong bằng thuật toán {algorithm}")
            self.view.show_algorithm_comparison(metrics)
        else:
            self.view.show_error("Không tìm thấy lời giải",
                                 f"Thuật toán {algorithm} không có lời giải cho câu đố này")
