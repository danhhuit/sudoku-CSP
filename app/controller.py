import time
import copy
from openai import OpenAI
client = OpenAI(api_key="open ai key")


class SudokuController:
    """Controller class điều phối giữa model và view"""

    def __init__(self, model, view, app):
        self.model = model
        self.view = view
        self.app = app

        self.initial_board = copy.deepcopy(model.board)

        self.view.set_controller(self)

        self._update_view()

        self.view.update_lives_display(self.model.lives)

    def open_ai_chat_window(self):
        from view import AIChatWindow
        if hasattr(self, 'ai_window') and self.ai_window.winfo_exists():
            self.ai_window.lift()
            self.ai_window.focus_set()
            return

            # Nếu chưa, tạo mới
        self.ai_window = AIChatWindow(self.view.master, self)

        # --- BƯỚC KHẮC PHỤC QUAN TRỌNG NHẤT ---
        # Đảm bảo cửa sổ Toplevel nổi lên và nhận focus
        self.ai_window.lift()
        self.ai_window.focus_set()
        """self.ai_window.grab_set()  # Ngăn tương tác với cửa sổ cha (tùy chọn)
        self.view.master.wait_window(self.ai_window)"""

    def process_ai_message(self, message):
        """Xử lý câu hỏi gửi đến AI"""

        # Lấy trạng thái Sudoku hiện tại
        board_text = ""
        for row in self.model.board:
            board_text += " ".join(str(x) for x in row) + "\n"

        prompt = f"""
    Bạn là trợ lý AI trong trò chơi Sudoku.

    Dưới đây là trạng thái Sudoku hiện tại (0 là ô trống):

    {board_text}

    Người chơi hỏi: "{message}"

    Hãy trả lời rõ ràng, ngắn gọn, tiếng Việt.
    Nếu được, giải thích bước tiếp theo cần làm.
    """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý AI siêu giỏi về Sudoku."},
                    {"role": "user", "content": prompt}
                ]
            )

            ai_reply = response.choices[0].message.content

        except Exception as e:
            ai_reply = f"Lỗi API: {str(e)}"
            print(f"LỖI KẾT NỐI AI: {e}")

        # Gửi trả lời vào cửa sổ chat
        if hasattr(self, "ai_window"):
            self.ai_window.add_message("AI", ai_reply)

    def new_game(self, difficulty="medium", grid_size=9):
        """Bắt đầu trò chơi mới với độ khó và kích thước lưới chỉ định"""
        self.model.grid_size = grid_size
        self.model.generate_puzzle(difficulty)
        self.initial_board = copy.deepcopy(self.model.board)
        self._update_view()
        self.view.update_lives_display(self.model.lives)

    def make_move(self, row, col, num):
        """Thực hiện nước đi và cập nhật view"""
        if getattr(self.model, 'is_paused', False):
            return
        if (row, col) in self.view.original_cells:
            return

        if self.model.game_over():
            self.view.show_error("Game Over", "Bạn đã hết mạng. Hãy bắt đầu trò chơi mới.")
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

    def _update_view(self):
        """Cập nhật view với trạng thái model hiện tại"""
        original_cells = set()
        for i in range(self.model.grid_size):
            for j in range(self.model.grid_size):
                if self.model.board[i][j] != 0:
                    original_cells.add((i, j))

        self.view.update_board(self.model.board, original_cells)

    def get_hint(self):
        """Cung cấp gợi ý cho người dùng"""
        if self.model.game_over():
            self.view.show_error("Game Over", "Bạn đã hết mạng. Hãy bắt đầu trò chơi mới.")
            return

        hint = self.model.get_hint()
        if hint:
            row, col, value = hint
            if self.model.grid_size == 16 and value > 9:
                display_value = chr(ord('A') + value - 10)
                self.view.cell_vars[row][col].set(display_value)
            else:
                self.view.cell_vars[row][col].set(str(value))

            self.model.board[row][col] = value
            self.view.highlight_cell(row, col, self.view.highlight_color)

            display_value = value if value <= 9 else chr(ord('A') + value - 10)
            self.view.update_status(f"Gợi ý: Đặt {display_value} tại vị trí ({row + 1},{col + 1})")

            if self.model.is_solved():
                self.model.end_time = time.time()
                self.model.completion_time = self.model.end_time - self.model.start_time
                self.view.show_success(self.model.completion_time)
        else:
            self.view.show_message("Không có gợi ý", "Không còn ô trống để cung cấp gợi ý.")

    def check_solution(self):
        """Kiểm tra giải pháp hiện tại và đánh dấu lỗi"""
        errors_found = False
        for i in range(self.model.grid_size):
            for j in range(self.model.grid_size):
                if self.model.board[i][j] == 0 or (i, j) in self.view.original_cells:
                    continue

                if not self.model.is_correct_move(i, j, self.model.board[i][j]):
                    self.view.highlight_cell(i, j, self.view.error_color)
                    errors_found = True

        if errors_found:
            self.view.show_message("Kết quả kiểm tra",
                                   "Có lỗi trong giải pháp của bạn. Các ô không đúng được đánh dấu màu đỏ.")
        else:
            if self.model.is_solved():
                self.model.end_time = time.time()
                self.model.completion_time = self.model.end_time - self.model.start_time
                self.view.show_success(self.model.completion_time)
            else:
                self.view.show_message("Kết quả kiểm tra", "Tốt! Không tìm thấy lỗi trong giải pháp hiện tại của bạn.")

    def solve_puzzle(self):
        """Giải toàn bộ câu đố"""
        if self.view.confirm_dialog("Giải câu đố",
                                    "Bạn có chắc muốn xem lời giải? Điều này sẽ kết thúc trò chơi hiện tại."):
            for i in range(self.model.grid_size):
                for j in range(self.model.grid_size):
                    if self.model.board[i][j] == 0:
                        value = self.model.solution[i][j]
                        self.model.board[i][j] = value

                        if self.model.grid_size == 16 and value > 9:
                            self.view.cell_vars[i][j].set(chr(ord('A') + value - 10))
                        else:
                            self.view.cell_vars[i][j].set(str(value))

                        self.view.highlight_cell(i, j, self.view.highlight_color)

            self.model.game_active = False
            self.view.update_status("Câu đố đã được giải. Bắt đầu trò chơi mới để chơi lại.")

    def clear_board(self):
        """Xóa tất cả đầu vào của người dùng và thuật toán, khôi phục bảng ban đầu"""
        if self.view.confirm_dialog("Xóa bảng", "Bạn có chắc muốn xóa tất cả đầu vào và khôi phục bảng ban đầu?"):
            self.model.board = copy.deepcopy(self.initial_board)
            self._update_view()
            self.view.update_status("Đã khôi phục bảng về trạng thái ban đầu.")

    def clear_cell(self, row, col):
        """Xóa một ô cụ thể"""
        if getattr(self.model, 'is_paused', False):
            return
        if (row, col) not in self.view.original_cells:
            self.model.board[row][col] = 0
            self.view.cell_vars[row][col].set("")
            self.view.highlight_cell(row, col, "white")

    def solve_with_algorithm(self, algorithm):
        """
        Giải Sudoku bằng thuật toán được chọn.
        """
        if self.model.game_over():
            self.view.show_error("Game Over", "Bạn đã hết mạng. Hãy bắt đầu trò chơi mới.")
            return

        self.view.update_status(f"Đang giải bằng thuật toán {algorithm}...")

        solution, metrics = self.model.solve_with_algorithm(algorithm)

        if solution:
            self.model.board = solution
            self._update_view()
            self.view.update_status(f"Đã giải thành công bằng thuật toán {algorithm}!")
            self.view.show_algorithm_comparison(metrics)
        else:
            self.view.show_error("Không tìm thấy lời giải",
                                 f"Thuật toán {algorithm} không tìm thấy lời giải cho câu đố này.")