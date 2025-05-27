"""
AIs for classic and ultimate tictactoe

easy: makes random valid moves quickly
medium: uses heuristics for classic. for ultimate, uses minimax with a depth of 3
hard: uses heuristics for classic. for ultimate, uses minimax with a depth of 5 (anything deeper is too slow)

# commented obsolete: uses Minimax with iterative deepening (and improved evaluation) to make stronger moves. not used anymore due to performance issue

"""
from __future__ import annotations

import random
import time
from functools import lru_cache
from typing import List, Optional, Tuple, Dict, TYPE_CHECKING

from constants import PLAYER_X, PLAYER_O

if TYPE_CHECKING:
    from tic_tac_toe import SmallBoard, UltimateBoard


# shared constants for lines in a 3x3 grid
_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # win thru rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)



'''CLASSIC TICTACTOE AI'''

def _get_random_move_small(board: SmallBoard) -> int:
    return random.choice(board.get_empty_square_indices())

def _get_heuristic_move_small(board: SmallBoard) -> int:
    empty_squares = board.get_empty_square_indices()
    if not empty_squares: return -1

    for move_idx in empty_squares: # Win
        temp_board = board.clone(); temp_board.mark_square(move_idx, PLAYER_O)
        if temp_board.winner == PLAYER_O: return move_idx
    for move_idx in empty_squares: # Block
        temp_board = board.clone(); temp_board.mark_square(move_idx, PLAYER_X)
        if temp_board.winner == PLAYER_X: return move_idx
    if 4 in empty_squares: return 4 # Center
    corners = [idx for idx in (0, 2, 6, 8) if idx in empty_squares]
    if corners: return random.choice(corners)
    sides = [idx for idx in (1, 3, 5, 7) if idx in empty_squares]
    if sides: return random.choice(sides)
    return random.choice(empty_squares)

@lru_cache(maxsize=None)
def _minimax_small_board(state_tuple: Tuple[str, ...], current_player_is_O: bool) -> Tuple[int, Optional[int]]:
    def check_winner_on_tuple(current_state: Tuple[str, ...]) -> Optional[str]:
        for r, c, d in _LINES:
            if current_state[r] == current_state[c] == current_state[d] and current_state[r] in (PLAYER_X, PLAYER_O):
                return current_state[r]
        if all(s_val in (PLAYER_X, PLAYER_O) for s_val in current_state): return "D"
        return None

    winner = check_winner_on_tuple(state_tuple)
    if winner is not None:
        if winner == PLAYER_O: return 10, None
        elif winner == PLAYER_X: return -10, None
        else: return 0, None

    possible_moves = [i for i, sq_val in enumerate(state_tuple) if sq_val not in (PLAYER_X, PLAYER_O)]
    best_move_found = None
    if current_player_is_O:
        best_score = -float('inf')
        for move_idx in possible_moves:
            new_state_list = list(state_tuple); new_state_list[move_idx] = PLAYER_O
            score, _ = _minimax_small_board(tuple(new_state_list), False)
            if score > best_score: best_score, best_move_found = score, move_idx
        return best_score, best_move_found
    else:
        best_score = float('inf')
        for move_idx in possible_moves:
            new_state_list = list(state_tuple); new_state_list[move_idx] = PLAYER_X
            score, _ = _minimax_small_board(tuple(new_state_list), True)
            if score < best_score: best_score, best_move_found = score, move_idx
        return best_score, best_move_found

def _get_minimax_move_small(board: SmallBoard) -> int:
    _, move_idx = _minimax_small_board(tuple(board.squares), True)
    return move_idx if move_idx is not None else _get_random_move_small(board)

_SMALL_BOARD_AI_STRATEGIES = {"easy": _get_random_move_small, "medium": _get_heuristic_move_small, "hard": _get_minimax_move_small}
def choose_move_small(board: SmallBoard, level: str = "medium") -> int:
    return _SMALL_BOARD_AI_STRATEGIES.get(level, _get_heuristic_move_small)(board)







'''ULTIMATE TICTACTOE AI'''

_ULTIMATE_TT: Dict[Tuple, Tuple[int, Optional[Tuple[int, int]]]] = {}
_ULTIMATE_MED_DEPTH = 3 
_ULTIMATE_HARD_DEPTH = 5
# _ULTIMATE_MAX_DEPTH_HARD = 10
# _ULTIMATE_TIME_LIMIT_HARD = 8.0

def _generate_ultimate_hash_key(ultimate_board: UltimateBoard, forced_board_idx: Optional[int], is_maximizing_player: bool) -> Tuple:
    flat_board_state: List[str] = []
    for sb in ultimate_board.small_boards: 
        flat_board_state.extend(sb.squares)
        flat_board_state.append(sb.winner if sb.winner is not None else "N")
    return tuple(flat_board_state + [ultimate_board.overall_winner or "N", forced_board_idx, is_maximizing_player])

def _evaluate_ultimate_board_state(ultimate_board: UltimateBoard, player: str) -> int:
    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O
    if ultimate_board.overall_winner == player: return 100000
    if ultimate_board.overall_winner == opponent: return -100000
    if ultimate_board.overall_winner == "D": return 0
    score = 0
    small_board_winners = [sb.winner for sb in ultimate_board.small_boards]
    for line in _LINES:
        player_wins = sum(1 for i in line if small_board_winners[i] == player)
        opponent_wins = sum(1 for i in line if small_board_winners[i] == opponent)
        undecided = sum(1 for i in line if small_board_winners[i] is None or small_board_winners[i] == 'D')
        if player_wins == 2 and undecided == 1: score += 700
        elif opponent_wins == 2 and undecided == 1: score -= 800
        elif player_wins == 1 and undecided == 2: score += 75
        elif opponent_wins == 1 and undecided == 2: score -= 85
    for sb_idx, sb in enumerate(ultimate_board.small_boards):
        weight = 1.5 if sb_idx == 4 else 1.0
        if sb.winner == player: score += int(120 * weight)
        elif sb.winner == opponent: score -= int(130 * weight)
        elif sb.winner is None:
            for s_line in _LINES:
                p_marks = sum(1 for i in s_line if sb.squares[i] == player)
                o_marks = sum(1 for i in s_line if sb.squares[i] == opponent)
                e_marks = sum(1 for i in s_line if sb.is_empty(i)) 
                if p_marks == 2 and e_marks == 1: score += int(25 * weight)
                elif o_marks == 2 and e_marks == 1: score -= int(30 * weight)
            if sb.squares[4] == player: score += int(8 * weight)
            elif sb.squares[4] == opponent: score -= int(8 * weight)
    return score

def _minimax_ultimate(ultimate_board: UltimateBoard, forced_board_idx: Optional[int], current_depth: int, alpha: float, beta: float, is_maximizing_player: bool, max_search_depth: int) -> Tuple[int, Optional[Tuple[int, int]]]:
    state_key = _generate_ultimate_hash_key(ultimate_board, forced_board_idx, is_maximizing_player)
    if state_key in _ULTIMATE_TT: return _ULTIMATE_TT[state_key]

    if ultimate_board.overall_winner is not None or current_depth >= max_search_depth:
        eval_score = _evaluate_ultimate_board_state(ultimate_board, PLAYER_O)
        _ULTIMATE_TT[state_key] = (eval_score, None)
        return eval_score, None

    best_move: Optional[Tuple[int, int]] = None
    player_mark = PLAYER_O if is_maximizing_player else PLAYER_X
    possible_boards = ultimate_board.get_available_small_board_indices(forced_board_idx) 

    if is_maximizing_player:
        max_eval = -float('inf')
        for b_idx in possible_boards:
            for s_idx in ultimate_board.small_boards[b_idx].get_empty_square_indices(): 
                cloned_board = ultimate_board.clone()
                next_forced = cloned_board.make_move(b_idx, s_idx, player_mark) 
                eval_score, _ = _minimax_ultimate(cloned_board, next_forced, current_depth + 1, alpha, beta, False, max_search_depth)
                if eval_score > max_eval: max_eval, best_move = eval_score, (b_idx, s_idx)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            if beta <= alpha: break
        _ULTIMATE_TT[state_key] = (max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for b_idx in possible_boards:
            for s_idx in ultimate_board.small_boards[b_idx].get_empty_square_indices():
                cloned_board = ultimate_board.clone()
                next_forced = cloned_board.make_move(b_idx, s_idx, player_mark)
                eval_score, _ = _minimax_ultimate(cloned_board, next_forced, current_depth + 1, alpha, beta, True, max_search_depth)
                if eval_score < min_eval: min_eval, best_move = eval_score, (b_idx, s_idx)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            if beta <= alpha: break
        _ULTIMATE_TT[state_key] = (min_eval, best_move)
        return min_eval, best_move

def _get_random_move_ultimate(ultimate_board: UltimateBoard, forced_board_idx: Optional[int]) -> Tuple[int, int]:
    available_boards = ultimate_board.get_available_small_board_indices(forced_board_idx)
    if not available_boards:
        for i, sb in enumerate(ultimate_board.small_boards):
            if sb.winner is None:
                empties = sb.get_empty_square_indices()
                if empties: return i, random.choice(empties)
        return 0,0 
    chosen_b_idx = random.choice(available_boards)
    chosen_s_idx = random.choice(ultimate_board.small_boards[chosen_b_idx].get_empty_square_indices())
    return chosen_b_idx, chosen_s_idx

def _get_heuristic_move_ultimate(ultimate_board: UltimateBoard, forced_board_idx: Optional[int]) -> Tuple[int, int]:
    available_boards = ultimate_board.get_available_small_board_indices(forced_board_idx)
    if not available_boards: return _get_random_move_ultimate(ultimate_board, forced_board_idx)
    # check for overall win for 'O'
    for b_idx in available_boards:
        for s_idx in ultimate_board.small_boards[b_idx].get_empty_square_indices():
            temp_ub = ultimate_board.clone(); temp_ub.make_move(b_idx, s_idx, PLAYER_O)
            if temp_ub.overall_winner == PLAYER_O: return b_idx, s_idx
    # win a small board for 'O'
    for b_idx in available_boards:
        for s_idx in ultimate_board.small_boards[b_idx].get_empty_square_indices():
            temp_sb = ultimate_board.small_boards[b_idx].clone(); temp_sb.mark_square(s_idx, PLAYER_O)
            if temp_sb.winner == PLAYER_O: return b_idx, s_idx
    # block 'X' from winning a small board
    for b_idx in available_boards:
        for s_idx in ultimate_board.small_boards[b_idx].get_empty_square_indices():
            temp_sb = ultimate_board.small_boards[b_idx].clone(); temp_sb.mark_square(s_idx, PLAYER_X)
            if temp_sb.winner == PLAYER_X: return b_idx, s_idx
    best_h_move = None; highest_h_score = -float('inf')
    for b_idx in available_boards:
        sb = ultimate_board.small_boards[b_idx]
        potential_s_idx = _get_heuristic_move_small(sb.clone())
        if potential_s_idx != -1 and sb.is_empty(potential_s_idx) :
            current_h_score = 5 if b_idx == 4 else 0 
            if best_h_move is None or current_h_score > highest_h_score :
                highest_h_score, best_h_move = current_h_score, (b_idx, potential_s_idx)
    return best_h_move if best_h_move else _get_random_move_ultimate(ultimate_board, forced_board_idx)

def _get_medium_difficulty_ultimate_move(ultimate_board: UltimateBoard, forced_board_idx: Optional[int]) -> Tuple[int, int]:
    _ULTIMATE_TT.clear()
    _, move = _minimax_ultimate(ultimate_board.clone(), forced_board_idx, 0, -float('inf'), float('inf'), True, _ULTIMATE_MED_DEPTH)
    return move if move else _get_heuristic_move_ultimate(ultimate_board, forced_board_idx)



def _get_hard_difficulty_ultimate_move(ultimate_board: UltimateBoard, forced_board_idx: Optional[int]) -> Tuple[int, int]:
    _ULTIMATE_TT.clear()
    _, move = _minimax_ultimate(ultimate_board.clone(), forced_board_idx, 0, -float('inf'), float('inf'), True, _ULTIMATE_HARD_DEPTH)
    return move if move else _get_heuristic_move_ultimate(ultimate_board, forced_board_idx)



# def _get_hard_difficulty_ultimate_move(ultimate_board: UltimateBoard, forced_board_idx: Optional[int]) -> Tuple[int, int]:
#     _ULTIMATE_TT.clear()
#     start_time = time.time()
#     best_move = _get_heuristic_move_ultimate(ultimate_board, forced_board_idx)
#     for depth in range(1, _ULTIMATE_MAX_DEPTH_HARD + 1):
#         _, move_at_depth = _minimax_ultimate(ultimate_board.clone(), forced_board_idx, 0, -float('inf'), float('inf'), True, depth)
#         if move_at_depth: best_move = move_at_depth
#         if (time.time() - start_time) > _ULTIMATE_TIME_LIMIT_HARD: break
#     return best_move

_ULTIMATE_BOARD_AI_STRATEGIES = {"easy": _get_random_move_ultimate, "medium": _get_medium_difficulty_ultimate_move, "hard": _get_hard_difficulty_ultimate_move}
def choose_move(ultimate_board: UltimateBoard, forced_board_idx: Optional[int], level: str = "medium") -> Tuple[int, int]:
    return _ULTIMATE_BOARD_AI_STRATEGIES.get(level, _get_medium_difficulty_ultimate_move)(ultimate_board, forced_board_idx)