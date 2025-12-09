# main.py   (updated + modular + recording + replay)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from game_logic import SimpleSOSGame, GeneralSOSGame
import random
from abc import ABC, abstractmethod
import json
import time


# ---------------- Player Classes ----------------
class BasePlayer(ABC):
    def __init__(self, name, color):
        self.name = name
        self.color = color

    @abstractmethod
    def choose_move(self, game):
        pass


class HumanPlayer(BasePlayer):
    """
    Human player now has behavior (professor requirement):
    Returns intended letter based on GUI.
    GUI uses this method indirectly.
    """
    def choose_move(self, game):
        return None

    def get_preferred_letter(self, gui):
        """Return 'S' or 'O' based on radio buttons in GUI."""
        return gui.red_letter_var.get() if self.color == "red" else gui.blue_letter_var.get()


class ComputerPlayer(BasePlayer):
    def choose_move(self, game):
        empty_cells = [(r, c) for r in range(game.board_size)
                              for c in range(game.board_size) if game.cell_empty(r,c)]
        if not empty_cells:
            return None
        r, c = random.choice(empty_cells)
        letter = random.choice(["S","O"])
        return (r, c, letter)


# ---------------- SOS GUI ----------------
class SOSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SOS Game")
        self.is_replaying = False
        self.create_widgets()
        self.on_start_new_game()

    # =======================
    # Modular Widget Creation
    # =======================
    def create_widgets(self):
        self.create_player_frames()
        self.create_center_controls()
        self.create_info_labels()
        self.create_board_frame()

    def create_player_frames(self):
        self.top_frame = ttk.Frame(self.root, padding=8)
        self.top_frame.grid(row=0, column=0, sticky="ew")

        # --- Red Player Frame ---
        red = ttk.LabelFrame(self.top_frame, text="Red Player", padding=6)
        red.grid(row=0, column=0, padx=(4, 20))

        self.red_letter_var = tk.StringVar(value="S")
        ttk.Radiobutton(red, text="S", variable=self.red_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(red, text="O", variable=self.red_letter_var, value="O").grid(row=0, column=1)

        self.red_type_var = tk.StringVar(value="human")
        ttk.Radiobutton(red, text="Human", variable=self.red_type_var, value="human").grid(row=1, column=0)
        ttk.Radiobutton(red, text="Computer", variable=self.red_type_var, value="computer").grid(row=1, column=1)

        # --- Blue Player Frame ---
        blue = ttk.LabelFrame(self.top_frame, text="Blue Player", padding=6)
        blue.grid(row=0, column=2, padx=(20, 4))

        self.blue_letter_var = tk.StringVar(value="S")
        ttk.Radiobutton(blue, text="S", variable=self.blue_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(blue, text="O", variable=self.blue_letter_var, value="O").grid(row=0, column=1)

        self.blue_type_var = tk.StringVar(value="human")
        ttk.Radiobutton(blue, text="Human", variable=self.blue_type_var, value="human").grid(row=1, column=0)
        ttk.Radiobutton(blue, text="Computer", variable=self.blue_type_var, value="computer").grid(row=1, column=1)

    def create_center_controls(self):
        center = ttk.Frame(self.top_frame)
        center.grid(row=0, column=1)

        ttk.Label(center, text="Board size:").grid(row=0, column=0)
        self.size_var = tk.IntVar(value=3)
        ttk.Spinbox(center, from_=3, to=12, width=5, textvariable=self.size_var).grid(row=0, column=1, padx=(5, 15))

        ttk.Label(center, text="Mode:").grid(row=0, column=2)
        self.mode_var = tk.StringVar(value="simple")
        ttk.Radiobutton(center, text="Simple", variable=self.mode_var, value="simple").grid(row=0, column=3)
        ttk.Radiobutton(center, text="General", variable=self.mode_var, value="general").grid(row=0, column=4)

        ttk.Button(center, text="New Game", command=self.on_start_new_game).grid(row=0, column=5, padx=(15, 0))

        # Recording controls
        ttk.Button(center, text="Record Game", command=self.on_save_game).grid(row=1, column=3, padx=(5, 5))
        ttk.Button(center, text="Load Game", command=self.on_load_game).grid(row=1, column=4, padx=(5, 5))
        ttk.Button(center, text="Replay", command=self.on_replay_file).grid(row=1, column=5, padx=(5, 0))

    def create_info_labels(self):
        self.turn_label = ttk.Label(self.root, text="", font=("Arial", 11, "bold"))
        self.turn_label.grid(row=1, column=0, pady=(4, 4))

        self.score_label = ttk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.score_label.grid(row=2, column=0, pady=(0, 4))

    def create_board_frame(self):
        self.board_frame = ttk.Frame(self.root, padding=8)
        self.board_frame.grid(row=3, column=0)

    # =======================
    # Game Logic Handlers
    # =======================
    def on_start_new_game(self):
        if self.is_replaying:
            # cancel replay state if starting a new game
            self.is_replaying = False

        mode = self.mode_var.get()
        size = self.size_var.get()
        self.game = SimpleSOSGame(size) if mode == "simple" else GeneralSOSGame(size)

        # Player creation
        self.red_player = HumanPlayer("Red","red") if self.red_type_var.get()=="human" else ComputerPlayer("Red","red")
        self.blue_player = HumanPlayer("Blue","blue") if self.blue_type_var.get()=="human" else ComputerPlayer("Blue","blue")
        self.players = {"red": self.red_player, "blue": self.blue_player}

        self.build_board_ui()
        self.check_computer_turn()

    def build_board_ui(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        size = self.game.board_size
        self.cell_size = 60
        self.cell_buttons = [[None]*size for _ in range(size)]

        self.canvas = tk.Canvas(self.board_frame,
                               width=size*self.cell_size,
                               height=size*self.cell_size,
                               bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=size, rowspan=size)

        for r in range(size):
            for c in range(size):
                btn = tk.Button(self.board_frame, text="", width=4, height=2,
                                font=("Arial", 12, "bold"),
                                command=lambda rr=r, cc=c: self.on_cell_clicked(rr, cc))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.cell_buttons[r][c] = btn

        self.update_turn_label()
        self.update_score_label()

    def on_cell_clicked(self, r, c):
        player = self.players[self.game.current_turn]
        if isinstance(player, ComputerPlayer) or self.game.game_over or self.is_replaying:
            return

        # NEW BEHAVIOR: HumanPlayer logic
        letter = player.get_preferred_letter(self)

        if self.game.make_move(r, c, letter):
            self.update_cell_ui(r, c)
            self.update_turn_label()
            self.update_score_label()

            if self.game.last_sos_lines:
                self.draw_sos_lines(self.game.last_sos_lines, self.game.last_move_player)

            if self.game.game_over:
                self.handle_game_over()
            else:
                self.check_computer_turn()

    def check_computer_turn(self):
        # Called whenever it may be a computer's turn; continues until a human turn or game over.
        player = self.players[self.game.current_turn]
        if isinstance(player, ComputerPlayer) and not self.game.game_over and not self.is_replaying:
            move = player.choose_move(self.game)
            if move:
                r, c, letter = move
                # make_move handles recording inside game_logic
                ok = self.game.make_move(r, c, letter)
                if ok:
                    self.update_cell_ui(r, c)
                    self.update_turn_label()
                    self.update_score_label()

                    if self.game.last_sos_lines:
                        self.draw_sos_lines(self.game.last_sos_lines, self.game.last_move_player)

            if self.game.game_over:
                self.handle_game_over()
            else:
                # schedule next check to allow UI to update and to avoid freezing
                self.root.after(350, self.check_computer_turn)

    def update_cell_ui(self, r, c):
        val = self.game.get_cell(r, c)
        btn = self.cell_buttons[r][c]
        btn.config(text=val if val else "")

        owner = self.game.get_cell_owner(r, c)
        if owner == "red":
            btn.config(fg="red")
        elif owner == "blue":
            btn.config(fg="blue")
        else:
            btn.config(fg="black")

    def draw_sos_lines(self, lines, player):
        color = "blue" if player == "blue" else "red"
        for r1, c1, r2, c2 in lines:
            x1 = c1 * self.cell_size + self.cell_size // 2
            y1 = r1 * self.cell_size + self.cell_size // 2
            x2 = c2 * self.cell_size + self.cell_size // 2
            y2 = r2 * self.cell_size + self.cell_size // 2
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)

    def update_turn_label(self):
        self.turn_label.config(text=f"Current turn: {self.game.current_turn}")

    def update_score_label(self):
        if isinstance(self.game, GeneralSOSGame):
            self.score_label.config(text=f"Blue: {self.game.scores['blue']} | Red: {self.game.scores['red']}")
        else:
            self.score_label.config(text="")

    def handle_game_over(self):
        if isinstance(self.game, SimpleSOSGame):
            if self.game.winner:
                messagebox.showinfo("Game Over", f"{self.game.winner.capitalize()} wins!")
            else:
                messagebox.showinfo("Game Over", "Draw!")
        else:
            self.show_general_result()

        self.disable_board()

    def show_general_result(self):
        blue, red = self.game.scores["blue"], self.game.scores["red"]
        if blue > red:
            winner = "Blue"
        elif red > blue:
            winner = "Red"
        else:
            winner = None

        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
        else:
            messagebox.showinfo("Game Over", "Draw!")

        self.disable_board()

    def disable_board(self):
        for row in self.cell_buttons:
            for btn in row:
                btn.config(state="disabled")

    # ----------------- Save / Load / Replay -----------------
    def on_save_game(self):
        if not hasattr(self, "game"):
            messagebox.showwarning("No game", "There's no game to save.")
            return

        # Build payload from game
        try:
            payload = {
                "mode": "simple" if isinstance(self.game, SimpleSOSGame) else "general",
                "board_size": self.game.board_size,
                "move_history": self.game.move_history,
            }
            if isinstance(self.game, GeneralSOSGame):
                payload["scores"] = self.game.scores
            if isinstance(self.game, SimpleSOSGame):
                payload["winner"] = self.game.winner

            fpath = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files","*.*")])
            if not fpath:
                return
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            messagebox.showinfo("Saved", f"Game saved to {fpath}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def on_load_game(self):
        fpath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files","*.*")])
        if not fpath:
            return
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            messagebox.showerror("Load error", f"Failed to load: {e}")
            return

        # create game instance matching the file
        mode = payload.get("mode", "simple")
        size = int(payload.get("board_size", 3))
        self.mode_var.set(mode)
        self.size_var.set(size)

        self.game = SimpleSOSGame(size) if mode == "simple" else GeneralSOSGame(size)
        # clear UI and rebuild
        self.build_board_ui()

        # import moves into the game object (doesn't play them)
        moves = payload.get("move_history", [])
        # normalize sos entries to tuples
        self.game.move_history = []
        for mv in moves:
            mv2 = {
                "player": mv["player"],
                "r": int(mv["r"]),
                "c": int(mv["c"]),
                "letter": mv["letter"],
                "sos": [list(x) for x in mv.get("sos", [])]
            }
            self.game.move_history.append(mv2)

        # if general, load scores if present (optional)
        if mode == "general" and "scores" in payload:
            try:
                sc = payload["scores"]
                self.game.scores = {"blue": int(sc.get("blue", 0)), "red": int(sc.get("red", 0))}
            except Exception:
                pass

        messagebox.showinfo("Loaded", "Game file loaded. Click Replay to play it back.")

    def on_replay_file(self):
        # ask file then start replay (separate from on_load_game for convenience)
        fpath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files","*.*")])
        if not fpath:
            return
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            messagebox.showerror("Load error", f"Failed to load: {e}")
            return

        # prepare game for replay based on payload
        mode = payload.get("mode", "simple")
        size = int(payload.get("board_size", 3))
        moves = payload.get("move_history", [])

        # normalize moves
        normalized = []
        for mv in moves:
            normalized.append({
                "player": mv["player"],
                "r": int(mv["r"]),
                "c": int(mv["c"]),
                "letter": mv["letter"],
                "sos": [tuple(x) for x in mv.get("sos", [])]
            })

        # create fresh game and UI
        self.mode_var.set(mode)
        self.size_var.set(size)
        self.game = SimpleSOSGame(size) if mode == "simple" else GeneralSOSGame(size)
        self.build_board_ui()

        # disable controls while replaying
        self.is_replaying = True
        self.disable_all_controls()

        # replay moves with animation using root.after
        def replay_moves(idx=0):
            if idx >= len(normalized) or not self.is_replaying:
                self.is_replaying = False
                # optionally set final scores from file for general mode
                if mode == "general" and payload.get("scores"):
                    try:
                        sc = payload["scores"]
                        self.game.scores = {"blue": int(sc.get("blue", 0)), "red": int(sc.get("red", 0))}
                    except Exception:
                        pass
                self.update_score_label()
                self.update_turn_label()
                self.enable_all_controls()
                messagebox.showinfo("Replay finished", "Replay finished.")
                return

            mv = normalized[idx]
            # apply the move to the game without relying on player objects
            player = mv["player"]
            r, c, letter = mv["r"], mv["c"], mv["letter"]
            # ensure current_turn matches the move's player before calling make_move
            self.game.current_turn = player
            self.game.make_move(r, c, letter)

            # update UI
            self.update_cell_ui(r, c)
            self.update_turn_label()
            self.update_score_label()
            if self.game.last_sos_lines:
                self.draw_sos_lines(self.game.last_sos_lines, self.game.last_move_player)

            # schedule next
            self.root.after(500, lambda: replay_moves(idx + 1))

        # start replay
        self.root.after(500, lambda: replay_moves(0))

    def disable_all_controls(self):
        # disable the top control widgets while replaying
        for child in self.top_frame.winfo_children():
            try:
                child.config(state="disabled")
            except Exception:
                pass

    def enable_all_controls(self):
        for child in self.top_frame.winfo_children():
            try:
                child.config(state="normal")
            except Exception:
                pass

def main():
    root = tk.Tk()
    app = SOSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
