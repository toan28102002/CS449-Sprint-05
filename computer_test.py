import unittest
import random
from game_logic import SimpleSOSGame, GeneralSOSGame
from main import ComputerPlayer


class TestComputerPlayer(unittest.TestCase):

    def setUp(self):
        random.seed(0)  # Makes tests predictable
        self.comp = ComputerPlayer("CPU", "blue")

    # ------------------------------
    # Test 1: Computer returns a valid move
    # ------------------------------
    def test_computer_returns_move(self):
        game = SimpleSOSGame(3)
        move = self.comp.choose_move(game)

        self.assertIsNotNone(move, "Computer should return a move")
        r, c, letter = move

        # Ensure the move is in bounds
        self.assertTrue(0 <= r < game.board_size)
        self.assertTrue(0 <= c < game.board_size)

        # Ensure the letter is valid
        self.assertIn(letter, ("S", "O"))

    # ------------------------------
    # Test 2: Computer picks only empty cells
    # ------------------------------
    def test_computer_picks_empty_cell(self):
        game = SimpleSOSGame(3)

        # Manually fill a cell
        game.board[0][0] = "S"

        for _ in range(10):
            r, c, _ = self.comp.choose_move(game)
            self.assertNotEqual((r, c), (0, 0), "Computer should avoid filled cells")

    # ------------------------------
    # Test 3: Computer returns None when board is full
    # ------------------------------
    def test_computer_no_move_when_full(self):
        game = SimpleSOSGame(3)

        # Fill the entire board
        for r in range(3):
            for c in range(3):
                game.board[r][c] = "S"

        move = self.comp.choose_move(game)
        self.assertIsNone(move, "Computer must return None when board is full")

    # ------------------------------
    # Test 4: Computer works with GeneralSOSGame
    # ------------------------------
    def test_computer_move_in_general_mode(self):
        game = GeneralSOSGame(4)
        move = self.comp.choose_move(game)

        self.assertIsNotNone(move)
        r, c, letter = move

        self.assertTrue(game.cell_empty(r, c))
        self.assertIn(letter, ("S", "O"))


if __name__ == "__main__":
    unittest.main()
