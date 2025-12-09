# game_logic.py
from typing import List, Optional, Dict, Any
import json
from copy import deepcopy


# ---------------- Base Class ----------------
class BaseSOSGame:
    """Common functionality for all SOS games"""

    def __init__(self, board_size: int = 3):
        self.board_size = max(3, int(board_size))
        self.reset_game()

    def reset_game(self):
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.current_turn = "blue"
        self.move_count = 0
        self.game_over = False
        self.last_sos_lines: List[tuple] = []
        self.last_move_player: Optional[str] = None
        self.owner_board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        # Move history: list of dicts: {player, r, c, letter, sos_lines}
        self.move_history: List[Dict[str, Any]] = []

    def in_bounds(self, r, c):
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def cell_empty(self, r, c):
        return self.in_bounds(r, c) and self.board[r][c] is None

    def toggle_turn(self):
        self.current_turn = "red" if self.current_turn == "blue" else "blue"

    def get_cell(self, r, c):
        return None if not self.in_bounds(r, c) else self.board[r][c]

    def get_cell_owner(self, r, c):
        if not self.in_bounds(r, c):
            return None
        return self.owner_board[r][c]

    def check_for_sos(self, r, c) -> List[tuple]:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        sos_lines = []

        for dr, dc in directions:
            if self.form_sos(r, c, dr, dc):
                sos_lines.append((r, c, r + 2*dr, c + 2*dc))
            if self.form_sos(r, c, -dr, -dc):
                sos_lines.append((r, c, r - 2*dr, c - 2*dc))
        # Remove duplicates if any (some directions might duplicate)
        unique = []
        for s in sos_lines:
            if s not in unique:
                unique.append(s)
        return unique

    def form_sos(self, r, c, dr, dc) -> bool:
        if not (
            self.in_bounds(r, c)
            and self.in_bounds(r + dr, c + dc)
            and self.in_bounds(r + 2*dr, c + 2*dc)
        ):
            return False
        return (
            self.board[r][c] == "S"
            and self.board[r+dr][c+dc] == "O"
            and self.board[r+2*dr][c+2*dc] == "S"
        )

    def is_board_full(self) -> bool:
        return self.move_count >= self.board_size * self.board_size

    # ---------- Recording / serialization ----------
    def record_move(self, player: str, r: int, c: int, letter: str, sos_lines: List[tuple]):
        # convert tuples to lists for JSON friendliness
        self.move_history.append({
            "player": player,
            "r": int(r),
            "c": int(c),
            "letter": letter,
            "sos": [list(x) for x in sos_lines]
        })

    def export_record(self) -> str:
        """Return a JSON string representing the game and moves. Include mode via subclass."""
        payload = {
            "board_size": self.board_size,
            "move_history": deepcopy(self.move_history),
        }
        # subclasses should add mode/scores/winner when saving by building their own dict
        return json.dumps(payload)

    def import_record(self, payload: Dict[str, Any]):
        """Load record (moves) into the game object (but doesn't play them)."""
        self.reset_game()
        self.board_size = int(payload.get("board_size", self.board_size))
        moves = payload.get("move_history", [])
        # normalizing sos entries to tuples
        for mv in moves:
            mv_copy = deepcopy(mv)
            mv_copy["sos"] = [tuple(x) for x in mv_copy.get("sos", [])]
            self.move_history.append(mv_copy)


# ---------------- Simple Game ----------------
class SimpleSOSGame(BaseSOSGame):
    """Simple mode: first player to form SOS wins"""
    
    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.winner: Optional[str] = None

    def make_move(self, r, c, letter: str) -> bool:
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        # place
        self.board[r][c] = letter
        self.move_count += 1
        # record owner immediately (for UI)
        self.owner_board[r][c] = self.current_turn
        # remember who made the move BEFORE toggling
        self.last_move_player = self.current_turn

        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines

        # record the move (important to use last_move_player)
        self.record_move(self.last_move_player, r, c, letter, sos_lines)

        if sos_lines:
            self.winner = self.last_move_player
            self.game_over = True
            return True

        # no sos -> toggle turn
        self.toggle_turn()

        # if board full it's draw
        if self.is_board_full():
            self.game_over = True

        return True

    def export_record(self) -> str:
        base = json.loads(super().export_record())
        base.update({
            "mode": "simple",
            "winner": self.winner,
        })
        return json.dumps(base)


# ---------------- General Game ----------------
class GeneralSOSGame(BaseSOSGame):
    """General mode: score points for each SOS formed"""

    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.scores = {"blue": 0, "red": 0}

    def make_move(self, r, c, letter: str) -> bool:
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        self.board[r][c] = letter
        self.move_count += 1
        self.owner_board[r][c] = self.current_turn
        self.last_move_player = self.current_turn

        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines

        # update scores for the player who actually moved
        if sos_lines:
            self.scores[self.last_move_player] += len(sos_lines)

        # record move (use last_move_player)
        self.record_move(self.last_move_player, r, c, letter, sos_lines)

        # toggle after recording and scoring (General rule)
        self.toggle_turn()

        if self.move_count >= self.board_size * self.board_size:
            self.game_over = True

        return True

    def export_record(self) -> str:
        base = json.loads(super().export_record())
        base.update({
            "mode": "general",
            "scores": deepcopy(self.scores),
        })
        return json.dumps(base)

    def import_record(self, payload: Dict[str, Any]):
        # ensure scores reset
        super().import_record(payload)
        sc = payload.get("scores")
        if isinstance(sc, dict):
            self.scores = {"blue": int(sc.get("blue", 0)), "red": int(sc.get("red", 0))}
