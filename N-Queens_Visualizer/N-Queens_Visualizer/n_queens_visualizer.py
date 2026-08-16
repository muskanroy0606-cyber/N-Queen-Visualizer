import tkinter as tk
from tkinter import ttk, messagebox
import time
import sqlite3   
import hashlib    
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

class NQueensVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Visual Solver - Advanced UI")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2e") # Dark theme base
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Professional Modern Theme Colors
        self.colors = {
            "bg": "#0f172a",
            "panel": "#1e293b",
            "text": "#f8fafc",
            "subtext": "#94a3b8",
            "accent": "#38bdf8",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "board_light": "#cbd5e1",
            "board_dark": "#475569",
            "trying": "#f59e0b",
            "conflict": "#ef4444",
            "safe": "#10b981",
            "backtrack": "#ec4899",
            "placed": "#06b6d4"
        }
        self.root.configure(bg=self.colors["bg"])
        
        self.n = 8
        self.board = [-1] * self.n
        self.generator = None
        self.auto_solve_id = None
        self.delay = 0.5  # seconds
        self.is_running = False
        
        self.queen_chars = ["♛", "♕", "👑", "Q", "★"]
        self.selected_queen = self.queen_chars[0]
        
        self.cell_size = 60
        self.solutions = []
        self.start_time = 0
        
        self.setup_ui()
        self.draw_board()

    def setup_ui(self):
        # --- Top Header ---
        header = tk.Frame(self.root, bg=self.colors["panel"], pady=10)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="N-Queens Backtracking Visualizer", font=("Segoe UI", 18, "bold"), fg=self.colors["accent"], bg=self.colors["panel"]).pack()

        # --- Main Layout ---
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors["bg"], bd=0, sashwidth=4)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- LEFT PANEL: Controls & Algorithm ---
        left_frame = tk.Frame(main_paned, bg=self.colors["panel"], width=250)
        main_paned.add(left_frame, minsize=250)
        
        # Controls Section
        tk.Label(left_frame, text="Controls", font=("Segoe UI", 14, "bold"), fg=self.colors["text"], bg=self.colors["panel"]).pack(pady=(10,5))
        
        # N Selection
        ctrl_frame1 = tk.Frame(left_frame, bg=self.colors["panel"])
        ctrl_frame1.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(ctrl_frame1, text="Board Size (N):", fg=self.colors["text"], bg=self.colors["panel"]).pack(side=tk.LEFT)
        self.n_var = tk.IntVar(value=self.n)
        self.n_spinbox = ttk.Spinbox(ctrl_frame1, from_=4, to_=20, textvariable=self.n_var, width=5, command=self.on_n_change)
        self.n_spinbox.pack(side=tk.RIGHT)
        self.n_spinbox.bind("<KeyRelease>", lambda e: self.on_n_change())
        
        # Queen Icon Selection
        ctrl_frame2 = tk.Frame(left_frame, bg=self.colors["panel"])
        ctrl_frame2.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(ctrl_frame2, text="Queen Style:", fg=self.colors["text"], bg=self.colors["panel"]).pack(side=tk.LEFT)
        self.queen_combo = ttk.Combobox(ctrl_frame2, values=self.queen_chars, state="readonly", width=5)
        self.queen_combo.current(0)
        self.queen_combo.pack(side=tk.RIGHT)
        self.queen_combo.bind("<<ComboboxSelected>>", self.on_queen_change)
        
        # Speed Selection
        tk.Label(left_frame, text="Animation Speed:", fg=self.colors["text"], bg=self.colors["panel"]).pack(fill=tk.X, padx=10, pady=(10,0))
        self.speed_scale = ttk.Scale(left_frame, from_=0.001, to=1.5, orient=tk.HORIZONTAL)
        self.speed_scale.set(self.delay)
        self.speed_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # Action Buttons
        btn_frame = tk.Frame(left_frame, bg=self.colors["panel"])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Start / Reset", command=self.reset_and_start, bg=self.colors["accent"], fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=8, cursor="hand2")
        self.start_btn.pack(fill=tk.X, pady=4)
        
        self.next_btn = tk.Button(btn_frame, text="Next Step", command=self.step_forward, bg="#0891b2", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=8, state=tk.DISABLED, cursor="hand2")
        self.next_btn.pack(fill=tk.X, pady=4)
        
        self.auto_btn = tk.Button(btn_frame, text="Auto Solve", command=self.toggle_auto_solve, bg=self.colors["warning"], fg="black", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=8, state=tk.DISABLED, cursor="hand2")
        self.auto_btn.pack(fill=tk.X, pady=4)
        
        self.fast_btn = tk.Button(btn_frame, text="Solve Instantly", command=self.solve_instantly, bg=self.colors["success"], fg="#fff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=8, cursor="hand2")
        self.fast_btn.pack(fill=tk.X, pady=4)

        # Apply hover effects
        self.add_hover_effect(self.start_btn, self.colors["accent"], "#0ea5e9")
        self.add_hover_effect(self.next_btn, "#0891b2", "#06b6d4")
        self.add_hover_effect(self.auto_btn, self.colors["warning"], "#d97706")
        self.add_hover_effect(self.fast_btn, self.colors["success"], "#059669")

        # Pseudocode Panel
        tk.Label(left_frame, text="Algorithm Logic", font=("Segoe UI", 12, "bold"), fg=self.colors["accent"], bg=self.colors["panel"]).pack(pady=(20,5))
        self.code_text = tk.Text(left_frame, height=12, width=30, bg="#020617", fg=self.colors["text"], font=("Consolas", 10), bd=0, padx=10, pady=10, state=tk.NORMAL)
        self.code_text.pack(fill=tk.X, padx=10)
        self.setup_pseudocode()

        # --- CENTER PANEL: Canvas ---
        center_frame = tk.Frame(main_paned, bg=self.colors["bg"])
        main_paned.add(center_frame, stretch="always")
        self.canvas = tk.Canvas(center_frame, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", self.on_resize)
        
        # --- RIGHT PANEL: Status & Output ---
        right_frame = tk.Frame(main_paned, bg=self.colors["panel"], width=250)
        main_paned.add(right_frame, minsize=250)
        
        tk.Label(right_frame, text="Execution Log", font=("Segoe UI", 14, "bold"), fg=self.colors["text"], bg=self.colors["panel"]).pack(pady=10)
        
        self.status_var = tk.StringVar(value="Ready. Choose N and start.")
        tk.Label(right_frame, textvariable=self.status_var, font=("Segoe UI", 11), fg=self.colors["success"], bg=self.colors["panel"], wraplength=230, justify=tk.LEFT).pack(pady=5, padx=10, fill=tk.X)
        
        self.explanation_text = tk.Text(right_frame, font=("Consolas", 9), bg="#020617", fg=self.colors["text"], bd=0, padx=10, pady=10, state=tk.DISABLED)
        self.explanation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Bottom Status ---
        self.bottom_status = tk.StringVar(value="Status: Idle")
        tk.Label(self.root, textvariable=self.bottom_status, bg=self.colors["bg"], fg=self.colors["subtext"], font=("Segoe UI", 9), anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def add_hover_effect(self, widget, normal_color, hover_color):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color) if widget['state'] != tk.DISABLED else None)
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color) if widget['state'] != tk.DISABLED else None)

    def setup_pseudocode(self):
        pseudocode = (
            "def solve(row):\n"
            "  if row == N:\n"
            "    save_solution()\n"
            "    return\n"
            "  for col = 0 to N-1:\n"
            "    if is_safe(row, col):\n"
            "      board[row] = col\n"
            "      solve(row + 1)\n"
            "      board[row] = -1\n"
        )
        self.code_text.insert("1.0", pseudocode)
        self.code_text.config(state=tk.DISABLED)
        # Setup tags for highlighting line
        self.code_text.tag_configure("highlight", background=self.colors["accent"], foreground="black")

    def highlight_code_line(self, line_num):
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        if line_num > 0:
            start = f"{line_num}.0"
            end = f"{line_num}.end"
            self.code_text.tag_add("highlight", start, end)

    def on_n_change(self):
        """Called when user changes N in spinbox before algorithm starts to redraw dynamically."""
        if self.generator is None:
            try:
                new_n = int(self.n_var.get())
                if 4 <= new_n <= 20:
                    self.n = new_n
                    self.board = [-1] * self.n
                    self.draw_board()
            except ValueError:
                pass

    def on_queen_change(self, event=None):
        self.selected_queen = self.queen_combo.get()
        self.draw_board()

    def log_explanation(self, msg):
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.insert(tk.END, msg + "\n")
        self.explanation_text.see(tk.END)
        self.explanation_text.config(state=tk.DISABLED)

    def on_resize(self, event):
        self.draw_board()

    def draw_board(self, highlights=None):
        if not highlights:
            highlights = {}
            
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            return
            
        board_size_px = min(canvas_width, canvas_height) - 20
        self.cell_size = board_size_px // self.n
        
        offset_x = (canvas_width - (self.cell_size * self.n)) // 2
        offset_y = (canvas_height - (self.cell_size * self.n)) // 2
        
        for r in range(self.n):
            for c in range(self.n):
                x1 = offset_x + c * self.cell_size
                y1 = offset_y + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Base checkered color
                color = self.colors["board_light"] if (r + c) % 2 == 0 else self.colors["board_dark"]
                
                # Highlight overrides color completely
                if (r, c) in highlights:
                    color = highlights[(r, c)]
                    
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#282a36", width=2)
                
                # Draw queen
                if self.board[r] == c:
                    font_size = max(10, int(self.cell_size * 0.5))
                    color_fg = "#000000" if color == self.colors["board_light"] else "#ffffff"
                    # If heavily highlighted red/safe usually black text is fine
                    if (r,c) in highlights: color_fg = "#000000"
                    
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, 
                                            text=self.selected_queen, fill=color_fg, font=("Segoe UI Symbol", font_size))

    def reset_and_start(self):
        try:
            self.n = int(self.n_var.get())
            if self.n < 4:
                messagebox.showerror("Error", "N must be at least 4")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer")
            return
            
        self.board = [-1] * self.n
        self.solutions = []
        self.generator = self.solve_n_queens_visual()
        self.is_running = False
        self.start_time = time.time()
        
        if self.auto_solve_id:
            self.root.after_cancel(self.auto_solve_id)
            self.auto_solve_id = None
            
        self.auto_btn.config(text="Auto Solve", state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.n_spinbox.config(state=tk.DISABLED)
        self.fast_btn.config(state=tk.NORMAL)
        
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        
        self.status_var.set(f"Target: Layout for N={self.n}\nClick 'Next Step'")
        self.bottom_status.set(f"Search started for N={self.n}")
        self.draw_board()
        self.log_explanation("--- Backtracking Started ---")
        self.highlight_code_line(1)

    def solve_instantly(self):
        """Bypasses GUI delay and completely calculates all solutions immediately"""
        if self.auto_solve_id:
            self.root.after_cancel(self.auto_solve_id)
            self.auto_solve_id = None
        self.is_running = False
        self.generator = None
        self.auto_btn.config(text="Auto Solve", state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        
        try:
            self.n = int(self.n_var.get())
            if self.n < 4:
                return
        except ValueError:
            return
            
        start = time.time()
        self.board = [-1] * self.n
        self.solutions = []
        self._solve_fast(0)
        elapsed = round(time.time() - start, 4)
        
        self.board = self.solutions[-1] if self.solutions else [-1]*self.n
        
        self.status_var.set(f"Instantly found {len(self.solutions)} solutions in {elapsed}s")
        self.bottom_status.set(f"Fast Solve Completed in {elapsed}s")
        
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(tk.END, f"Found {len(self.solutions)} solutions instantly.\nFinal board displayed.\nTime taken: {elapsed}s\n")
        self.explanation_text.config(state=tk.DISABLED)
        
        self.highlight_code_line(0)
        self.draw_board({(r, self.board[r]): self.colors["placed"] for r in range(self.n) if self.board[r] != -1})
        self.generator = None

    def _solve_fast(self, row):
        if row == self.n:
            self.solutions.append(list(self.board))
            return
        for col in range(self.n):
            if self.is_safe(row, col):
                self.board[row] = col
                self._solve_fast(row + 1)
                self.board[row] = -1

    def is_safe(self, row, col):
        for i in range(row):
            if self.board[i] == col or abs(self.board[i] - col) == abs(i - row):
                return False
        return True

    def toggle_auto_solve(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.auto_btn.config(text="Pause Auto", bg=self.colors["danger"])
            self.next_btn.config(state=tk.DISABLED)
            self.auto_step()
            self.log_explanation("\n[Auto Solve Running]")
        else:
            self.auto_btn.config(text="Auto Solve", bg=self.colors["warning"])
            self.next_btn.config(state=tk.NORMAL)
            if self.auto_solve_id:
                self.root.after_cancel(self.auto_solve_id)
                self.auto_solve_id = None
            self.log_explanation("\n[Auto Solve Paused]")

    def is_safe_detailed(self, row, col):
        for i in range(row):
            if self.board[i] == col:
                return False, (i, col)
            if abs(self.board[i] - col) == abs(i - row):
                return False, (i, self.board[i])
        return True, None

    def solve_n_queens_visual(self):
        def solve(row):
            self.highlight_code_line(1)
            if row == self.n:
                self.solutions.append(list(self.board))
                yield {"action": "SOLUTION", "row": -1, "col": -1, "line": 3}
                return
            
            for col in range(self.n):
                yield {"action": "TRYING", "row": row, "col": col, "line": 5}
                
                safe, conflict_pos = self.is_safe_detailed(row, col)
                if not safe:
                    yield {"action": "CONFLICT", "row": row, "col": col, "conflict": conflict_pos, "line": 6}
                    continue
                
                yield {"action": "SAFE", "row": row, "col": col, "line": 6}
                
                self.board[row] = col
                yield {"action": "PLACED", "row": row, "col": col, "line": 7}
                
                yield {"action": "RECURSE", "row": row, "col": col, "line": 8}
                yield from solve(row + 1)
                
                yield {"action": "BACKTRACK", "row": row, "col": col, "line": 9}
                self.board[row] = -1
                
        yield from solve(0)
        yield {"action": "DONE", "line": 0}

    def handle_step(self, step):
        act = step["action"]
        line = step.get("line", 0)
        r, c = step.get("row"), step.get("col")
        highlights = {}
        
        self.highlight_code_line(line)
        
        if act == "TRYING":
            highlights[(r, c)] = self.colors["trying"]
            self.status_var.set(f"Trying Row {r+1}, Col {c+1}")
            self.log_explanation(f"-> Testing ({r},{c})")
            
        elif act == "CONFLICT":
            conf = step["conflict"]
            highlights[(r, c)] = self.colors["conflict"]
            highlights[conf] = self.colors["conflict"]
            self.status_var.set(f"Conflict at ({r},{c}) with ({conf[0]},{conf[1]})")
            
        elif act == "SAFE":
            highlights[(r, c)] = self.colors["safe"]
            self.status_var.set(f"Position ({r},{c}) is safe!")
            
        elif act == "PLACED":
            highlights[(r, c)] = self.colors["placed"]
            self.status_var.set(f"Placed Queen at ({r},{c})")
            
        elif act == "RECURSE":
            highlights[(r, c)] = self.colors["placed"]
            self.status_var.set(f"Proceeding to row {r+2}...")
            
        elif act == "BACKTRACK":
            highlights[(r, c)] = self.colors["backtrack"]
            self.status_var.set(f"Removed Queen from ({r},{c})")
            self.log_explanation(f"<- Backtracking from ({r},{c})")
            
        elif act == "SOLUTION":
            self.status_var.set(f"Solution #{len(self.solutions)} Found!")
            self.log_explanation(f"\n*** Solution #{len(self.solutions)} Found ***\n")
            for i in range(self.n):
                highlights[(i, self.board[i])] = self.colors["placed"]
            self.bottom_status.set(f"Solutions so far: {len(self.solutions)}")
            
            if self.is_running:
                # Pause at solution
                self.toggle_auto_solve()
                
        elif act == "DONE":
            time_taken = round(time.time() - self.start_time, 2)
            self.status_var.set(f"Process Complete! {len(self.solutions)} Solutions")
            self.log_explanation(f"\n--- Process Complete ---\nTime: {time_taken}s")
            self.bottom_status.set(f"Finished. Total solutions: {len(self.solutions)} | Time: {time_taken}s")
            
            self.next_btn.config(state=tk.DISABLED)
            self.auto_btn.config(state=tk.DISABLED)
            self.n_spinbox.config(state=tk.NORMAL)
            self.fast_btn.config(state=tk.NORMAL)
            self.generator = None
            if self.is_running:
                self.toggle_auto_solve()

        self.draw_board(highlights)

    def step_forward(self):
        if not self.generator:
            return
        try:
            step = next(self.generator)
            self.handle_step(step)
        except StopIteration:
            pass

    def auto_step(self):
        if not self.is_running or not self.generator:
            return
        try:
            step = next(self.generator)
            self.handle_step(step)
            if self.is_running:
                delay_ms = int(self.speed_scale.get() * 1000)
                if delay_ms < 1: delay_ms = 1
                self.auto_solve_id = self.root.after(delay_ms, self.auto_step)
        except StopIteration:
            self.is_running = False
            self.auto_btn.config(text="Auto Solve", state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Auth Window ---
class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens - Login / Register")
        self.root.geometry("400x500")
        self.root.configure(bg="#1e1e2e")
        
        self.colors = {
            "bg": "#0f172a", "panel": "#1e293b", "text": "#f8fafc", "subtext": "#94a3b8",
            "accent": "#38bdf8", "success": "#10b981", "danger": "#ef4444"
        }
        
        try:
            self.root.eval('tk::PlaceWindow . center')
        except:
            pass
        
        # UI Setup - Modern Card Layout
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Decorative side accent (simulated)
        accent_bar = tk.Frame(container, bg=self.colors["accent"], width=5)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        main_frame = tk.Frame(container, bg=self.colors["panel"], padx=40, pady=40)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Header
        tk.Label(main_frame, text="N-Queens Visualizer", font=("Segoe UI", 20, "bold"), fg=self.colors["accent"], bg=self.colors["panel"]).pack(pady=(0, 5))
        tk.Label(main_frame, text="Secure Access Portal", font=("Segoe UI", 10), fg=self.colors["subtext"], bg=self.colors["panel"]).pack(pady=(0, 30))
        
        # Inputs
        label_font = ("Segoe UI", 9, "bold")
        entry_font = ("Segoe UI", 11)
        
        tk.Label(main_frame, text="GMAIL / USERNAME", font=label_font, fg=self.colors["subtext"], bg=self.colors["panel"]).pack(anchor=tk.W)
        self.user_entry = tk.Entry(main_frame, font=entry_font, bg="#0f172a", fg="#fff", insertbackground="#fff", relief=tk.FLAT, bd=8)
        self.user_entry.pack(fill=tk.X, pady=(5, 20))
        
        tk.Label(main_frame, text="PASSWORD", font=label_font, fg=self.colors["subtext"], bg=self.colors["panel"]).pack(anchor=tk.W)
        self.pass_entry = tk.Entry(main_frame, show="*", font=entry_font, bg="#0f172a", fg="#fff", insertbackground="#fff", relief=tk.FLAT, bd=8)
        self.pass_entry.pack(fill=tk.X, pady=(5, 30))
        
        # Buttons
        btn_font = ("Segoe UI", 11, "bold")
        
        self.login_btn = tk.Button(main_frame, text="SIGN IN", font=btn_font, bg=self.colors["accent"], fg="#fff", activebackground="#0ea5e9", activeforeground="#fff", relief=tk.FLAT, cursor="hand2", command=self.login, pady=8)
        self.login_btn.pack(fill=tk.X, pady=(0, 10))
        
        self.reg_btn = tk.Button(main_frame, text="CREATE ACCOUNT", font=btn_font, bg=self.colors["panel"], fg=self.colors["subtext"], activebackground=self.colors["panel"], activeforeground=self.colors["accent"], relief=tk.FLAT, cursor="hand2", command=self.register)
        self.reg_btn.pack(fill=tk.X)
        
        # Footer
        tk.Label(main_frame, text="© 2026 DAA Project Team", font=("Segoe UI", 8), fg="#475569", bg=self.colors["panel"]).pack(pady=(30, 0))

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please fill all fields")
            return
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == self.hash_password(password):
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.start_app()
        else:
            messagebox.showerror("Error", "Invalid Gmail or password")

    def register(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please fill all fields")
            return
            
        hashed_pw = self.hash_password(password)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now login.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Gmail already exists")
        finally:
            conn.close()

    def start_app(self):
        # Destroy current window elements
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Reset window size and configure for main app
        self.root.geometry("1200x800")
        try:
            self.root.eval('tk::PlaceWindow . center')
        except:
            pass
        
        # Launch main app
        app = NQueensVisualizer(self.root)

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    auth = AuthWindow(root)
    root.mainloop()
