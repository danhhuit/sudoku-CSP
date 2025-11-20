import tkinter as tk
from tkinter import ttk, messagebox, StringVar, Frame, Label, Button, Entry, Toplevel
import os
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from pathlib import Path

from app import controller


class SelectionScreen:
    """Màn hình chọn kích thước lưới và độ khó"""

    def __init__(self, master, start_callback):
        self.master = master
        self.start_callback = start_callback

        self.style = ttkb.Style(theme="flatly")
        self.master.configure(bg=self.style.colors.bg)

        container = ttkb.Frame(self.master, padding=20)
        container.pack(expand=True)
        try:
            script_dir = Path(__file__).parent
            icon_path = script_dir.parent / "assets" / "sudoku-icon.png"
            print(f"Đang tải icon từ: {icon_path}")

            pil_image = Image.open(icon_path)
            pil_image = pil_image.resize((65, 65), Image.Resampling.LANCZOS)
            icon_image = ImageTk.PhotoImage(pil_image)

        except Exception as e:
            print(f"Không thể tải icon: {e}")
            icon_image = None
        title_label = ttkb.Label(
            container,
            text="UDOKU",
            font=("Courier New", 36, "bold"),
            bootstyle="primary",
            image=icon_image,
            compound="left"
        )
        title_label.pack(pady=(0, 30))
        if icon_image:
            title_label.image = icon_image
        options_frame = ttkb.LabelFrame(container, text="Tùy chọn trò chơi", padding=15,
                                        bootstyle="info")
        options_frame.pack(fill="x", pady=10)

        grid_frame = ttkb.Frame(options_frame)
        grid_frame.pack(fill="x", pady=10)

        ttkb.Label(grid_frame, text="Kích thước lưới:", font=("Courier New", 14, "bold")).pack(side="left")
        self.grid_size_var = tk.StringVar(value="9x9")
        grid_menu = ttkb.Combobox(grid_frame, textvariable=self.grid_size_var,
                                  values=["9x9", "16x16"], state="readonly",
                                  bootstyle="primary", width=10)
        grid_menu.pack(side="left", padx=10)

        difficulty_frame = ttkb.Frame(options_frame)
        difficulty_frame.pack(fill="x", pady=10)

        ttkb.Label(difficulty_frame, text="Độ khó:", font=("Courier New", 14, "bold")).pack(side="left")
        self.difficulty_var = tk.StringVar(value="Medium")
        self.difficulty_map = {
            "Super Easy": "super_easy", "Easy": "easy", "Medium": "medium",
            "Difficult": "difficult", "Expert": "expert"
        }
        difficulty_menu = ttkb.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                        values=list(self.difficulty_map.keys()), state="readonly",
                                        bootstyle="primary", width=12)
        difficulty_menu.pack(side="left", padx=10)

        start_button = ttkb.Button(container, text="Bắt Đầu Chơi", command=self._start_game,
                                   bootstyle="success-outline", padding=(20, 10))
        start_button.pack(pady=30)

        instructions = """Hướng dẫn:\n1. Chọn kích thước lưới (9x9 hoặc 16x16)\n2. Chọn độ khó phù hợp\n3. Nhấn "Bắt Đầu Chơi" để bắt đầu"""
        ttkb.Label(container, text=instructions, font=("Courier New", 10),
                   bootstyle="").pack(pady=10, anchor="w")

    def _start_game(self):
        grid_size_text = self.grid_size_var.get()
        grid_size = 9 if grid_size_text == "9x9" else 16
        difficulty_display = self.difficulty_var.get()
        difficulty = self.difficulty_map[difficulty_display]
        self.start_callback(grid_size, difficulty, difficulty_display)


class GameScreen:
    """Giao diện chơi game Sudoku"""

    def __init__(self, master, grid_size=9):
        self.master = master
        self.master.title("Sudoku Game")

        # Bảng màu tinh gọn, dễ nhìn
        self.bg_color = "#F7F9FC"
        self.fg_color = "#2C3E50"
        self.highlight_color = "#FFF3BF"   # vàng nhạt
        self.error_color = "#F8D7DA"       # đỏ nhạt
        self.success_color = "#D4EDDA"     # xanh nhạt
        self.original_cell_color = "#E9ECEF"  # xám nhạt

        self.master.configure(bg=self.bg_color)

        self.cells = []
        self.cell_vars = []
        self.original_cells = set()
        self.timer_var = StringVar(value="Thời gian: 00:00")
        self.lives_var = StringVar(value="Mạng: 3")
        self.timer_running = False

        self.grid_size = grid_size

        # Icon images cache
        self._icon_cache = {}
        self._load_icons()

        self._create_header()
        self._create_info_panel()
        self._create_board()
        self._create_controls()
        self.controller = None
        self._create_status_bar()
        self._update_timer()

    def set_controller(self, controller):
        self.controller = controller

    def _load_icons(self):
        """Tải icon từ thư mục assets, nếu không có sẽ bỏ qua và dùng text"""

        # --- ĐỊNH NGHĨA KÍCH THƯỚC ICON MONG MUỐN ---
        # Bạn có thể thay đổi (24, 24) thành kích thước bạn muốn
        # Ví dụ: (20, 20) hoặc (32, 32)
        ICON_SIZE = (25, 25)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        icon_map = {
            'help': ['help.png'],
            'hint': ['hint.png'],
            'check': ['check.png'],
            'solve': ['solve.png'],
            'clear': ['clear.png'],
            'new': ['new.png'],
            'pause': ['pause.png'],
            'resume': ['play.png'],
            'back': ['back.png']
        }

        if not hasattr(self, '_icon_cache'):
            self._icon_cache = {}

        for key, names in icon_map.items():
            for name in names:
                path = os.path.join(assets_dir, name)
                if os.path.exists(path):
                    try:
                        pil_image = Image.open(path)
                        pil_image = pil_image.resize(ICON_SIZE, Image.Resampling.LANCZOS)
                        img = ImageTk.PhotoImage(pil_image)
                        self._icon_cache[key] = img
                        break
                    except Exception as e:
                        print(f"Lỗi khi tải hoặc resize ảnh {path}: {e}")
                        continue
    def _get_icon(self, key):
        """Lấy tk.PhotoImage theo key nếu có"""
        return self._icon_cache.get(key)

    def _create_header(self):
        """Tạo phần header với tiêu đề và nút quay lại"""
        header_frame = Frame(self.master, bg=self.bg_color)
        header_frame.pack(fill="x", padx=16, pady=(10, 0))

        back_icon = self._get_icon('back')
        self.back_button = ttkb.Button(header_frame,
                                       text=("Quay lại"),
                                       image=back_icon, command=self._on_back, bootstyle="danger-outline", compound="left")
        self.back_button.pack(side="left")

        try:
            script_dir = Path(__file__).parent
            icon_path = script_dir.parent / "assets" / "sudoku-icon.png"
            print(f"Đang tải icon từ: {icon_path}")

            pil_image = Image.open(icon_path)
            pil_image = pil_image.resize((65, 65), Image.Resampling.LANCZOS)
            icon_image = ImageTk.PhotoImage(pil_image)

        except Exception as e:
            print(f"Không thể tải icon: {e}")
            icon_image = None
        ttkb.Label(header_frame, text="UDOKU", image=icon_image, font=("Comic Sans MS", 30, "bold"),
                   bootstyle="primary", compound="left").pack(side="top", padx=6)
        if icon_image:
            ttkb.image = icon_image

    def _create_info_panel(self):
        """Tạo panel hiển thị thời gian và mạng"""
        info_frame = Frame(self.master, bg=self.bg_color)
        info_frame.pack(fill="x", padx=16, pady=6)

        timer_label = ttkb.Label(info_frame, textvariable=self.timer_var,
                                 font=("Courier New", 12, "bold"), bootstyle="info")
        timer_label.pack(side="left")

        lives_label = ttkb.Label(info_frame, textvariable=self.lives_var,
                                 font=("Courier New", 12, "bold"), bootstyle="danger")
        lives_label.pack(side="right")

    def _create_board(self):
        """Tạo bảng Sudoku (9x9 hoặc 16x16) với giao diện dễ nhìn hơn cho 16x16"""
        # Nếu board_frame đã tồn tại, xóa nó
        if hasattr(self, 'board_frame'):
            self.board_frame.destroy()

        # Khung chứa bảng để dễ canh giữa và giữ đúng tỉ lệ
        board_container = Frame(self.master, bg=self.bg_color)
        board_container.pack(fill="both", expand=True)

        self.board_frame = Frame(board_container, bg="#212529", padx=3, pady=3)
        self.board_frame.pack(pady=8)

        self.cells = []
        self.cell_vars = []

        box_size = 3 if self.grid_size == 9 else 4

        # Kích thước được chọn để tỉ lệ ô vuông đẹp mắt
        cell_font_size = 22 if self.grid_size == 9 else 20
        cell_width = 2
        cell_pixel_width = 60 if self.grid_size == 9 else 50
        cell_pixel_height = 60 if self.grid_size == 9 else 50

        for i in range(self.grid_size):
            row_cells = []
            row_vars = []

            for j in range(self.grid_size):
                cell_frame = Frame(self.board_frame,
                                   bg="#212529",
                                   width=cell_pixel_width,
                                   height=cell_pixel_height,
                                   padx=0, pady=0)
                cell_frame.grid(row=i, column=j, padx=0, pady=0)

                if i % box_size == 0 and i > 0:
                    cell_frame.grid(pady=(15, 0))
                if j % box_size == 0 and j > 0:
                    cell_frame.grid(padx=(15, 0))
                if i % box_size == 0 and i > 0 and j % box_size == 0 and j > 0:
                    cell_frame.grid(padx=(15, 0), pady=(15, 0))

                cell_var = StringVar()

                cell = Entry(cell_frame, width=cell_width, font=("Comic Sans MS", cell_font_size, "bold"),
                             justify="center", textvariable=cell_var,
                             borderwidth=0, highlightthickness=1,
                             highlightbackground="#999933")

                cell.pack(fill="both", expand=True)

                cell.position = (i, j)

                cell.bind("<FocusIn>", lambda e, pos=(i, j): self._on_cell_focus(pos))
                cell.bind("<KeyRelease>", lambda e, pos=(i, j): self._on_cell_input(e, pos))

                row_cells.append(cell)
                row_vars.append(cell_var)

            self.cells.append(row_cells)
            self.cell_vars.append(row_vars)

        # Cửa sổ lớn hơn để bảng cân đối và thoáng hơn
        if self.grid_size == 16:
            self.master.geometry("1400x1300")
        else:
            self.master.geometry("1400x880")

    def _create_controls(self):
        """Tạo các nút điều khiển"""
        controls_frame = ttkb.Labelframe(self.master, text="Điều khiển", padding=10)
        controls_frame.configure(bootstyle="secondary")
        controls_frame.pack(fill="x", padx=16, pady=8)

        help_icon = self._get_icon('help')
        help_btn = ttkb.Button(controls_frame, text=("Hướng dẫn"),
                               image=help_icon, command=self._show_instructions,
                               bootstyle="info-outline", compound="left")
        help_btn.pack(side="left", padx=10)

        hint_icon = self._get_icon('hint')
        hint_btn = ttkb.Button(controls_frame, text=("Gợi ý"),
                               image=hint_icon, command=self._on_hint,
                               bootstyle="warning-outline", compound="left" )
        hint_btn.pack(side="left", padx=10)

        check_icon = self._get_icon('check')
        check_btn = ttkb.Button(controls_frame, text=("Kiểm tra"),
                                image=check_icon, command=self._on_check,
                                bootstyle="primary-outline", compound="left")
        check_btn.pack(side="left", padx=10)

        ttkb.Label(controls_frame, text="Thuật toán:", font=("Arial", 12)).pack(side="left", padx=10)

        self.algorithm_var = StringVar(value="BackTracking")
        algorithm_menu = ttk.Combobox(controls_frame, textvariable=self.algorithm_var,
                                      values=["DFS", "BFS", "BackTracking", "SimulatedAnnealing", "A*"],
                                      state="readonly", width=15)
        algorithm_menu.pack(side="left", padx=5, pady=5)

        solve_icon = self._get_icon('solve')
        solve_btn = ttkb.Button(controls_frame, text=("Giải"),
                                image=solve_icon, command=self._on_solve,
                                bootstyle="success-outline", compound="left")
        solve_btn.pack(side="left", padx=10)

        clear_icon = self._get_icon('clear')
        clear_btn = ttkb.Button(controls_frame, text=("Xóa"),
                                image=clear_icon, command=self._on_clear,
                                bootstyle="danger-outline", compound="left")
        clear_btn.pack(side="left", padx=10)

        new_icon = self._get_icon('new')
        new_game_btn = ttkb.Button(controls_frame, text=("Mới" ),
                                   image=new_icon, command=self._on_new_game,
                                   bootstyle="success-outline", compound="left")
        new_game_btn.pack(side="left", padx=10)

        # Nút Tạm dừng / Tiếp tục (icon)
        pause_icon = self._get_icon('pause')
        self.pause_btn = ttkb.Button(controls_frame,
                                     text=("Tạm dừng" ),
                                     image=pause_icon,
                                     command=self._toggle_pause, bootstyle="secondary-outline", compound="left")
        self.pause_btn.pack(side="left", padx=10)

        #nút chat AI
        self.ai_chat_button = ttkb.Button(
            controls_frame,
            text="AI Chat",
            bootstyle="info",
            command=lambda: self.controller.open_ai_chat_window() if self.controller else None
        )
        self.ai_chat_button.pack(side="left", padx=10)

    def _create_status_bar(self):
        """Tạo thanh trạng thái"""
        self.status_frame = Frame(self.master, bg="#E9ECEF", height=28)
        self.status_frame.pack(side="bottom", fill="x")

        self.status_var = StringVar(value="Sẵn sàng. Bắt đầu điền số vào các ô trống.")
        self.status_label = Label(self.status_frame, textvariable=self.status_var,
                                  font=("Arial", 10), bg="#E9ECEF", fg=self.fg_color,
                                  anchor="w", padx=12)
        self.status_label.pack(fill="x")

    def _update_timer(self):
        """Cập nhật hiển thị thời gian"""
        if self.controller and self.controller.model.game_active:
            elapsed_time = self.controller.model.get_elapsed_time()
            minutes, seconds = divmod(int(elapsed_time), 60)
            self.timer_var.set(f"Thời gian: {minutes:02d}:{seconds:02d}")

        self.master.after(1000, self._update_timer)

    def _toggle_pause(self):
        """Chuyển trạng thái tạm dừng/tiếp tục, làm mờ bảng khi tạm dừng"""
        if not hasattr(self, 'controller'):
            return
        model = self.controller.model
        if not getattr(model, 'is_paused', False):
            # Pause
            model.pause()
            # Overlay mờ trên bảng để chặn thao tác
            self._pause_overlay = tk.Canvas(self.board_frame, bg='#FFFFFF', highlightthickness=0)
            self._pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            # Vẽ lớp mờ bán trong suốt (tk không có alpha, dùng stipple)
            self.board_frame.update_idletasks()
            w = self.board_frame.winfo_width() or 1
            h = self.board_frame.winfo_height() or 1
            step = 4
            for x in range(0, w, step):
                self._pause_overlay.create_rectangle(x, 0, x+2, h, fill='#000000', outline='', stipple='gray25')
            # Nhãn tạm dừng
            self._pause_overlay.create_text(w//2, h//2, text='TẠM DỪNG', font=('Arial', 28, 'bold'),
                                            fill='#FFFFFF')
            resume_icon = self._get_icon('resume')
            if resume_icon is not None:
                self.pause_btn.config(text='Tiếp tục', image=resume_icon, compound="left")
                # giữ tham chiếu để tránh bị GC
                self.pause_btn.image = resume_icon
            else:
                self.pause_btn.config(text='Tiếp tục')
            self.pause_btn.config(bootstyle='secondary-outline')
            self.update_status('Đã tạm dừng trò chơi')
        else:
            # Resume
            model.resume()
            if hasattr(self, '_pause_overlay') and self._pause_overlay:
                self._pause_overlay.destroy()
                self._pause_overlay = None
            pause_icon = self._get_icon('pause')
            if pause_icon is not None:
                self.pause_btn.config(text='Tạm dừng', image=pause_icon, compound="left")
                self.pause_btn.image = pause_icon
            else:
                self.pause_btn.config(text='Tạm dừng')
            self.pause_btn.config(bootstyle='secondary-outline')
            self.update_status('Tiếp tục trò chơi')

    def _on_back(self):
        """Xử lý khi người dùng nhấn nút quay lại"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'app'):
            if self.confirm_dialog("Quay lại",
                                   "Bạn có chắc muốn quay lại màn hình chọn? Tiến trình hiện tại sẽ bị mất."):
                self.controller.app.show_selection_screen()

    def _on_new_game(self):
        """Xử lý khi người dùng nhấn nút trò chơi mới"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'app'):
            if self.confirm_dialog("Trò chơi mới",
                                   "Bạn có chắc muốn bắt đầu trò chơi mới? Tiến trình hiện tại sẽ bị mất."):
                self.controller.app.show_selection_screen()

    def _show_instructions(self):
        """Hiển thị hướng dẫn chơi game"""
        instructions_window = Toplevel(self.master)
        instructions_window.title("Hướng dẫn chơi")
        instructions_window.geometry("500x720")
        instructions_window.resizable(False, False)

        instructions_window.configure(bg=self.bg_color)

        instructions_window.transient(self.master)
        instructions_window.grab_set()

        instructions_window.geometry("+%d+%d" % (
            self.master.winfo_rootx() + self.master.winfo_width() // 2 - 250,
            self.master.winfo_rooty() + self.master.winfo_height() // 2 - 250
        ))
        instructions_window.geometry("780x1100")

        Label(instructions_window, text="HƯỚNG DẪN CHƠI",
              font=("Courier New", 20, "bold"),
              bg=self.bg_color, fg=self.fg_color).pack(anchor="center", pady=10)

        content_frame = Frame(instructions_window, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        grid_info = "1-9" if self.grid_size == 9 else "1-16"
        box_info = "3×3" if self.grid_size == 9 else "4×4"

        instructions_text = (
            f"1. Điền vào lưới sao cho mỗi hàng, cột và hộp {box_info} đều chứa các số {grid_info} không lặp lại.\n\n"
            "2. Nhấp vào ô trống và gõ số để thực hiện nước đi.\n"
            "Ô màu xám là các ô được điền sẵn và không thể thay đổi.\n"
            "Ô màu xanh lá cây cho biết số đúng.\n"
            "Ô màu đỏ cho biết số sai.\n\n"
            "3. Bạn có 3 mạng cho mỗi trò chơi. Mỗi nước đi sai sẽ mất 1 mạng.\n"
            "Khi hết mạng, trò chơi kết thúc.\n\n"
            "4. Bộ đếm thời gian hiển thị thời gian chơi. Hãy cố gắng giải càng nhanh càng tốt.\n\n"
            "5. Phím tắt:\n"
            f"   Số {grid_info}: Nhập giá trị\n"
            "Delete hoặc Backspace: Xóa ô\n\n"
            "6. Sử dụng các nút bên dưới bảng:\n"
            "Trợ giúp: Hiển thị màn hình hướng dẫn này.\n"
            "Gợi ý: Hiển thị một số đúng trong một ô trống ngẫu nhiên.\n"
            "Kiểm tra: Kiểm tra tiến trình hiện tại và đánh dấu các lỗi.\n"
            "Giải: Hiển thị toàn bộ lời giải cho câu đố.\n"
            "Xóa: Xóa tất cả các đầu vào của người dùng khỏi bảng.\n"
            "Trò chơi mới: Quay lại màn hình chọn để bắt đầu trò chơi mới.\n"
            "Quay lại: Quay lại màn hình chọn."
        )

        instructions_content = Label(content_frame, text=instructions_text,
                                     font=("Courier New", 12), justify="left",
                                     bg=self.bg_color, fg=self.fg_color,
                                     wraplength=740)
        instructions_content.pack(anchor="w", pady=20)

        legend_frame = Frame(content_frame, bg=self.bg_color, pady=5)
        legend_frame.pack(fill="x")

        # Label(legend_frame, text="MÃ MÀU:", font=("Arial", 10, "bold"),
        #       bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        #
        # color_samples = [
        #     ("Ô gốc", "#E9ECEF"),
        #     ("Số đúng", "#D4EDDA"),
        #     ("Số sai", "#F8D7DA"),
        #     ("Gợi ý", "#FFF3BF")
        # ]
        #
        # for i, (label_text, color) in enumerate(color_samples):
        #     sample_frame = Frame(legend_frame, bg=self.bg_color)
        #     sample_frame.pack(anchor="w", pady=2)
        #
        #     color_box = Frame(sample_frame, bg=color, width=20, height=20)
        #     color_box.pack(side="left", padx=5)
        #
        #     Label(sample_frame, text=label_text, font=("Arial", 9),
        #           bg=self.bg_color, fg=self.fg_color).pack(side="left")

        close_button = Button(instructions_window, text="Đóng", font=("Arial", 10, "bold"),
                              command=instructions_window.destroy, bg="#3498DB", fg="white", width=10)
        close_button.pack(pady=15)

    def set_controller(self, controller):
        """Thiết lập controller cho view này"""
        self.controller = controller

    def update_board(self, board, original_cells):
        """Cập nhật giao diện với trạng thái bảng mới"""
        self.original_cells = original_cells

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell = self.cells[i][j]
                value = board[i][j]

                if value == 0:
                    self.cell_vars[i][j].set("")
                    cell.config(bg="white", state="normal")
                else:
                    if self.grid_size == 16 and value > 9:
                        self.cell_vars[i][j].set(chr(ord('A') + value - 10))
                    else:
                        self.cell_vars[i][j].set(str(value))

                    if (i, j) in original_cells:
                        cell.config(bg=self.original_cell_color, state="readonly")
                    else:
                        cell.config(bg="white", state="normal")

    def highlight_cell(self, row, col, color):
        """Tô sáng một ô cụ thể với màu cho trước"""
        if row < self.grid_size and col < self.grid_size:
            self.cells[row][col].config(bg=color)

    def update_lives_display(self, lives):
        """Cập nhật hiển thị mạng"""
        self.lives_var.set(f"Mạng: {lives}")

    def show_message(self, title, message):
        """Hiển thị thông báo"""
        messagebox.showinfo(title, message)
        self.update_status(message)

    def show_error(self, title, message):
        """Hiển thị thông báo lỗi"""
        self.update_status(f"LỖI: {message}", is_error=True)

        error_window = Toplevel(self.master)
        error_window.title(title)
        error_window.geometry("300x100")
        error_window.resizable(False, False)

        error_window.geometry("+%d+%d" % (
            self.master.winfo_rootx() + self.master.winfo_width() // 2 - 150,
            self.master.winfo_rooty() + self.master.winfo_height() // 2 - 50
        ))

        Label(error_window, text=message, wraplength=280, pady=10).pack(expand=True)

        error_window.after(1500, error_window.destroy)

    def show_success(self, completion_time=None):
        """Hiển thị thông báo thành công khi giải xong câu đố"""
        if completion_time:
            minutes, seconds = divmod(int(completion_time), 60)
            time_text = f"Thời gian hoàn thành: {minutes:02d}:{seconds:02d}"
            messagebox.showinfo("Chúc mừng!", f"Bạn đã giải thành công câu đố Sudoku!\n\n{time_text}")
            self.update_status(f"Hoàn thành thành công! {time_text}")
        else:
            messagebox.showinfo("Chúc mừng!", "Bạn đã giải thành công câu đố Sudoku!")
            self.update_status("Hoàn thành thành công! Bắt đầu trò chơi mới để chơi tiếp.")

    def show_game_over(self):
        """Hiển thị thông báo kết thúc trò chơi khi hết mạng"""
        messagebox.showinfo("Game Over", "Bạn đã hết mạng! Hãy thử lại.")
        self.update_status("Trò chơi kết thúc! Hết mạng. Bắt đầu trò chơi mới để chơi tiếp.")

    def confirm_dialog(self, title, message):
        """Hiển thị hộp thoại xác nhận"""
        return messagebox.askyesno(title, message)

    def update_status(self, message, is_error=False):
        """Cập nhật thanh trạng thái với thông báo"""
        self.status_var.set(message)
        if is_error:
            self.status_label.config(fg="#CC0000")
        else:
            self.status_label.config(fg=self.fg_color)

        self.master.after(3000, lambda: self.status_var.set("Sẵn sàng. Bắt đầu điền số vào các ô trống."))
        self.master.after(3000, lambda: self.status_label.config(fg=self.fg_color))

    def _on_cell_focus(self, position):
        """Xử lý khi ô được focus"""
        if not hasattr(self, 'controller'):
            return

        row, col = position
        box_size = 3 if self.grid_size == 9 else 4

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in self.original_cells and self.controller.model.board[i][j] == 0:
                    self.highlight_cell(i, j, "white")

                if (i == row or j == col or
                    (i // box_size == row // box_size and j // box_size == col // box_size)) and (i, j) != (row, col):
                    if (i, j) not in self.original_cells and self.controller.model.board[i][j] == 0:
                        self.highlight_cell(i, j, "#F8F8F8")

    def _on_cell_input(self, event, position):
        """Xử lý khi người dùng nhập vào ô"""
        if hasattr(self, 'controller'):
            row, col = position

            if (row, col) in self.original_cells:
                return

            value = self.cell_vars[row][col].get()

            if not value and event.keysym in ('BackSpace', 'Delete'):
                self.controller.clear_cell(row, col)
                return

            if self.grid_size == 16 and value.upper() in "ABCDEFG":
                num_val = ord(value.upper()) - ord('A') + 10
                self.cell_vars[row][col].set(value.upper())
                self.controller.make_move(row, col, num_val)
                return

            if not value.isdigit() or int(value) == 0:
                self.controller.clear_cell(row, col)
                return

            max_value = self.grid_size
            if int(value) > max_value:
                value = value[-1]
                self.cell_vars[row][col].set(value)

            self.controller.make_move(row, col, int(value))

    def _on_hint(self):
        """Xử lý khi người dùng nhấn nút gợi ý"""
        if hasattr(self, 'controller'):
            self.controller.get_hint()

    def _on_check(self):
        """Xử lý khi người dùng nhấn nút kiểm tra"""
        if hasattr(self, 'controller'):
            self.controller.check_solution()

    def _on_solve(self):
        """Xử lý khi người dùng nhấn nút giải"""
        if not hasattr(self, 'controller'):
            return

        algorithm = self.algorithm_var.get()

        self.controller.solve_with_algorithm(algorithm)

    def _on_clear(self):
        """Xử lý khi người dùng nhấn nút xóa"""
        if hasattr(self, 'controller'):
            self.controller.clear_board()

    def show_algorithm_comparison(self, metrics):
        """
        Hiển thị kết quả so sánh thuật toán.

        Args:
            metrics: Từ điển chứa các thông số hiệu suất của thuật toán
        """
        comparison_window = Toplevel(self.master)
        comparison_window.title("Kết quả thuật toán")
        comparison_window.geometry("1700x1180")
        comparison_window.resizable(True, True)

        comparison_window.configure(bg=self.bg_color)

        info_frame = Frame(comparison_window, bg=self.bg_color, padx=20, pady=20)
        info_frame.pack(fill="both", expand=True)

        algorithm_name = self.algorithm_var.get()
        Label(info_frame, text=f"Thuật toán: {algorithm_name}",
              font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=10)

        result_text = "Thành công" if metrics['is_solved'] else "Không tìm thấy lời giải"
        result_color = "#27AE60" if metrics['is_solved'] else "#E74C3C"
        Label(info_frame, text=f"Kết quả: {result_text}",
              font=("Arial", 14, "bold"), bg=self.bg_color, fg=result_color).pack(pady=5)

        metrics_frame = Frame(info_frame, bg=self.bg_color)
        metrics_frame.pack(fill="x", pady=10)

        columns = ("Thông số", "Giá trị")
        metrics_table = ttk.Treeview(metrics_frame, columns=columns, show="headings", height=6)
        metrics_table.heading("Thông số", text="Thông số")
        metrics_table.heading("Giá trị", text="Giá trị")
        metrics_table.column("Thông số", width=150)
        metrics_table.column("Giá trị", width=150)

        metrics_table.insert("", "end", values=("Thời gian thực thi (giây)", f"{metrics['execution_time']:.6f}"))
        metrics_table.insert("", "end", values=("Số trạng thái đã khám phá", f"{metrics['states_explored']}"))
        metrics_table.insert("", "end",
                             values=("Số trạng thái tối đa trong bộ nhớ", f"{metrics['max_states_in_memory']}"))
        metrics_table.insert("", "end", values=("Giá trị heuristic h(n)", f"{metrics['h_value']}"))
        metrics_table.insert("", "end", values=("Số bước thực hiện g(n)", f"{metrics['g_value']}"))
        metrics_table.insert("", "end", values=("Tổng chi phí f(n) = g(n) + h(n)", f"{metrics['f_value']}"))

        metrics_table.pack(fill="x", padx=10, pady=10)

        chart_frame = Frame(info_frame, bg=self.bg_color)
        chart_frame.pack(fill="both", expand=True, pady=10)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.bar(['Thời gian (s)'], [metrics['execution_time']], color='#3498DB')
        ax1.set_title('Thời gian thực thi')
        ax1.set_ylabel('Giây')

        ax2.bar(['Trạng thái đã khám phá', 'Trạng thái tối đa trong bộ nhớ'],
                [metrics['states_explored'], metrics['max_states_in_memory']],
                color=['#9B59B6', '#E67E22'])
        ax2.set_title('Không gian trạng thái')
        ax2.set_ylabel('Số lượng')

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        Button(comparison_window, text="Đóng", font=("Arial", 12, "bold"),
               command=comparison_window.destroy, bg="#3498DB", fg="white", width=15).pack(pady=15)
class AIChatWindow(tk.Toplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("ChatBot")
        self.geometry("500x900")
        self.resizable(False, False)
        self.configure(bg="white")

        # Khung hiển thị chat
        self.chat_display = tk.Text(self, wrap="word", state="disabled", width=52, height=22, bg="#f8f9fa")
        self.chat_display.pack(padx=10, pady=10, fill="both", expand=True)
        self.chat_display.tag_config("user_tag", foreground="#2980B9", font=("Arial", 10, "bold"))  # Xanh dương
        self.chat_display.tag_config("ai_tag", foreground="#27AE60", font=("Arial", 10, "bold"))  # Xanh lá

        # Ô nhập
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5, fill="x")

        self.entry = tk.Entry(entry_frame, width=40)
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.entry.focus_set()

        # Nút gửi
        send_button = tk.Button(entry_frame, text="Gửi", command=self.send_message,
        font=("Courier New", 10, "bold"),
        width=8,
        height=1)
        send_button.pack(side="left", padx=5)

    def add_message(self, sender, message):
        self.chat_display.configure(state="normal")

        # 1. Xác định tag và màu
        if sender == "Bạn":
            tag_name = "user_tag"
        elif sender == "AI":
            tag_name = "ai_tag"
        else:
            tag_name = ""

        # 2. Chèn tên người gửi với tag màu
        self.chat_display.insert("end", f"{sender}", tag_name)

        # 3. Chèn dấu hai chấm và nội dung tin nhắn (không có tag)
        self.chat_display.insert("end", f": {message}\n")

        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self.entry.delete(0, "end")

        self.add_message("Bạn", user_msg)

        # Gọi AI
        self.controller.process_ai_message(user_msg)
