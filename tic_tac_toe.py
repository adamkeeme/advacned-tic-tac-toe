"""
main logic for classic and ultimate ttt game modes:
- defines the game board structures (SmallBoard, UltimateBoard) and core mechanics
- board state, moves, win/loss/draw conditions
- game loop for both classic and ultimate modes


without UI, start the game with:
python tic_tac_toe.py classic easy/medium/hard
python tic_tac_toe.py ultimate easy/medium/hard

"""
from __future__ import annotations

import sys
from typing import Optional, Tuple, List

import ai_bots
from constants import PLAYER_X, PLAYER_O

# classic 3×3 board
class SmallBoard:
    WIN_CONDITIONS: Tuple[Tuple[int, int, int], ...] = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # win thru rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6),             # diagonals
    )

    def __init__(self):
        # initializes an empty 3x3 board with numbered squares.
        self.squares: List[str] = [str(i + 1) for i in range(9)]
        self.winner: Optional[str] = None

    def is_empty(self, idx: int) -> bool:
        #checks if the square at the given index is empty (not marked X or O)
        return self.squares[idx] not in (PLAYER_X, PLAYER_O)

    def mark_square(self, idx: int, player: str):
        # marks a square and checks for a win or draw
        if self.winner is not None or not self.is_empty(idx):
            return

        self.squares[idx] = player
        for line in self.WIN_CONDITIONS:
            if all(self.squares[i] == player for i in line):
                self.winner = player
                return
        if all(not self.is_empty(i) for i in range(9)):
            self.winner = "D"

    def get_empty_square_indices(self) -> List[int]:
        #returns a list of 0-based indices of empty squares
        return [i for i, _ in enumerate(self.squares) if self.is_empty(i)]

    def print_console(self):
        # prints the board to the console
        for r in range(3):
            print(" ".join(f"{str(self.squares[r*3+c]):>2}" for c in range(3)))
        print()

    def clone(self) -> SmallBoard:
        # creates a copy of the board for ai's internal calculations
        c = SmallBoard()
        c.squares = self.squares[:]
        c.winner = self.winner
        return c



'''ULTIMATE BOARD'''

class UltimateBoard:
    def __init__(self):
        self.small_boards: List[SmallBoard] = [SmallBoard() for _ in range(9)]
        self.overall_winner: Optional[str] = None

    def get_available_small_board_indices(self, forced_board_idx: Optional[int]) -> List[int]:
        # returns indices of small boards available for the next move
        if forced_board_idx is None or self.small_boards[forced_board_idx].winner is not None:
            return [i for i, b in enumerate(self.small_boards) if b.winner is None]
        return [forced_board_idx]

    def make_move(self, small_board_idx: int, square_idx: int, player: str) -> Optional[int]:
        # makes a move, updates winners, and returns the next forced board index
        if self.overall_winner: return None

        target_board = self.small_boards[small_board_idx]
        
        target_board.mark_square(square_idx, player)
        self._update_overall_winner(player)
        return square_idx

    def _update_overall_winner(self, player_who_moved: str): 
        # checks for an overall winner or a draw on the main grid
        if self.overall_winner: return

        for line in SmallBoard.WIN_CONDITIONS:
            if all(self.small_boards[i].winner == player_who_moved for i in line):
                self.overall_winner = player_who_moved
                return
        
        if all(b.winner is not None for b in self.small_boards):
            self.overall_winner = "D"

    def clone(self) -> UltimateBoard:
        # creates a copy of the board. needed for ai's internal simulation to explore moves at different depths
        new_ub = UltimateBoard()
        new_ub.small_boards = [b.clone() for b in self.small_boards]
        new_ub.overall_winner = self.overall_winner
        return new_ub

    def print_console(self):
        #prints the ultimate board to the console
        sep = "═" * 25
        print("\nUltimate Board State:")
        for R in range(3):
            for r in range(3):
                row_parts = []
                for C in range(3):
                    board = self.small_boards[3 * R + C]
                    row_parts.append(" ".join(f"{str(board.squares[r*3+c]):>2}" for c in range(3)))
                print(" ║ ".join(row_parts))
            if R < 2:
                print(sep)
        
        print("\nSmall Board Winners:")
        winners_summary = [b.winner if b.winner else "." for b in self.small_boards]
        for r_idx in range(3):
            print(" ".join(f"{winners_summary[r_idx*3+c_idx]:>2}" for c_idx in range(3)))
        if self.overall_winner:
            print(f"Overall Game Winner: {self.overall_winner}")
        print("-" * 25 + "\n")


# terminal input handling for classic and ultimate modes
def _get_valid_console_input(prompt: str, valid_0_indices: List[int]) -> int:
    valid_1_options_disp = sorted([i + 1 for i in valid_0_indices])
    while True:
        try:
            val = int(input(f"{prompt} {valid_1_options_disp}: ")) - 1
            if val in valid_0_indices: return val
        except ValueError: pass
        print("Invalid input. Try again.")


# game loop for classic and ultimate modes
def play_classic_console(ai_level: str):
    board = SmallBoard()
    current_player = PLAYER_X
    print("\n--- Classic Tic-Tac-Toe (Console) ---")
    while board.winner is None:
        board.print_console()
        print(f"Player {current_player}'s turn.")
        if current_player == PLAYER_X:
            move = _get_valid_console_input("Choose square", board.get_empty_square_indices())
        else:
            move = ai_bots.choose_move_small(board, ai_level)
            print(f"AI ({ai_level}) plays {move + 1}")
        board.mark_square(move, current_player)
        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X
    board.print_console()
    outcome = "Draw" if board.winner == "D" else f"Player {board.winner} wins"
    print(f"Game Over: {outcome}!")

# main function to run the game in console mode
def play_ultimate_console(ai_level: str):
    ub = UltimateBoard()
    current_player, forced_idx = PLAYER_X, None
    print("\n--- Ultimate Tic-Tac-Toe (Console) ---")
    while ub.overall_winner is None:
        ub.print_console()
        print(f"Player {current_player}'s turn.")
        
        available_boards = ub.get_available_small_board_indices(forced_idx)
        if forced_idx is not None and ub.small_boards[forced_idx].winner is None:
            print(f"Forced to play in small board {forced_idx + 1}.")
            b_idx = forced_idx
        else:
            b_idx = _get_valid_console_input("Choose board", available_boards)

        print(f"Selected small board {b_idx + 1}:")
        ub.small_boards[b_idx].print_console()

        if current_player == PLAYER_X:
            s_idx = _get_valid_console_input("Choose square", ub.small_boards[b_idx].get_empty_square_indices())
        else:
            print(f"AI ({ai_level}) is thinking...")
            b_idx, s_idx = ai_bots.choose_move(ub, forced_idx, ai_level)
            print(f"AI plays in board {b_idx + 1}, square {s_idx + 1}")
        
        forced_idx = ub.make_move(b_idx, s_idx, current_player)
        current_player = PLAYER_O if current_player == PLAYER_X else PLAYER_X
    
    ub.print_console()
    outcome = "Draw" if ub.overall_winner == "D" else f"Player {ub.overall_winner} wins"
    print(f"Ultimate Game Over: {outcome}!")

def run_tests_console():
    print("Running basic tests...")
    sb = SmallBoard(); sb.mark_square(0, PLAYER_X); sb.mark_square(1, PLAYER_X); sb.mark_square(2, PLAYER_X)
    assert sb.winner == PLAYER_X, "Test SmallBoard Win FAILED"
    print("SmallBoard Win: OK")
    ub = UltimateBoard(); ub.make_move(4,4,PLAYER_X)
    b, s = ai_bots.choose_move(ub, 4, "easy")
    assert ub.get_available_small_board_indices(4) == [4], "Forced board not available for AI"
    assert ub.small_boards[b].is_empty(s), f"AI chose non-empty square {s} in board {b}"
    assert b == 4 or ub.small_boards[4].winner is not None, "Test Ultimate AI move in forced board FAILED"
    print("UltimateBoard AI move (easy): OK")
    print("Basic tests completed.")

if __name__ == "__main__":
    args = sys.argv[1:]
    mode, level = "ultimate", "medium"

    if args:
        if args[0].lower() == "test": run_tests_console(); sys.exit()
        mode = args[0].lower()
        if len(args) > 1: level = args[1].lower()

    if mode not in ("classic", "ultimate"): mode = "ultimate"; print("Invalid mode, using 'ultimate'.")
    if level not in ("easy", "medium", "hard"): level = "medium"; print("Invalid level, using 'medium'.")
    
    print(f"\nStarting {mode} Tic-Tac-Toe against {level} AI...")
    (play_classic_console if mode == "classic" else play_ultimate_console)(level)