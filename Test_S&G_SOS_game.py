# Test_S&G_SOS_game.py
import unittest
from game_logic import SimpleSOSGame, GeneralSOSGame

class TestSOSGame(unittest.TestCase):

    def setUp(self):
        self.simple_game = SimpleSOSGame(board_size=3)
        self.general_game = GeneralSOSGame(board_size=3)

    # ----------------- Simple Mode Tests -----------------
    def test_simple_place_move(self):
        self.assertTrue(self.simple_game.make_move(0, 0, "S"))
        self.assertEqual(self.simple_game.get_cell(0, 0), "S")
        # Turn toggles after move
        self.assertEqual(self.simple_game.current_turn, "red")

    def test_simple_sos_winner(self):
        # Blue forms SOS
        self.simple_game.make_move(0, 0, "S")  # Blue
        self.simple_game.make_move(1, 0, "S")  # Red
        self.simple_game.make_move(0, 1, "O")  # Blue
        self.simple_game.make_move(1, 1, "O")  # Red
        self.simple_game.make_move(0, 2, "S")  # Blue forms SOS

        self.assertTrue(self.simple_game.game_over)
        self.assertEqual(self.simple_game.winner, "blue")
        self.assertEqual(self.simple_game.get_cell(0, 2), "S")

    # ----------------- General Mode Tests -----------------
    def test_general_place_move_and_score(self):
        game = self.general_game
        game.make_move(0, 0, "S")  # Blue
        self.assertEqual(game.current_turn, "red")
        game.make_move(1, 0, "S")  # Red
        self.assertEqual(game.current_turn, "blue")

        # Blue forms SOS
        game.make_move(0, 1, "O")
        game.make_move(1, 1, "O")  # Red
        game.make_move(0, 2, "S")  # Blue SOS
        # Turn toggles even after SOS
        self.assertEqual(game.current_turn, "red")
        self.assertEqual(game.scores["blue"], 1)

if __name__ == "__main__":
    unittest.main()
