# test_game_logic.py file:
import unittest
from game_logic import SOSGame

class TestSOSGameBasics(unittest.TestCase):

    # 1. Choose a board size
    def test_board_initialization(self):
        game = SOSGame(board_size=10)
        self.assertEqual(len(game.board), 10)
        self.assertTrue(all(cell is None for row in game.board for cell in row))

    # 2. Choose the game mode of a chosen board
    def test_set_game_mode(self):
        game = SOSGame()
        game.set_mode("general")
        self.assertEqual(game.mode, "general")
        with self.assertRaises(ValueError):
            game.set_mode("invalid_mode")

    # 3. Start a new game
    def test_new_game_reset(self):
        game = SOSGame(board_size=4, mode="general")
        game.make_move(0, 0, "S")
        game.make_move(1, 1, "O")
        game.reset_game()
        self.assertTrue(all(cell is None for row in game.board for cell in row))
        self.assertEqual(game.current_turn, "blue")
        self.assertEqual(game.scores, {"blue": 0, "red": 0})
        self.assertEqual(game.move_count, 0)

if __name__ == "__main__":
    unittest.main()
