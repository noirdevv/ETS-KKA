# CARA PAKAI:
# 1. Install pytest: pip install pytest
# 2. Pergi ke direktori root (ETS-KKA\)
# 3. Execute di terminal: python -m pytest test/test_minimax.py -v
# 4. Kalau passed semua, logic udah aman
import pytest
from config import P1, P2
from src.game_logic import GameState, HORIZONTAL as H, VERTICAL as V
from src.ai.minimax import get_minimax_move


def test_minimax_returns_legal_move():
    state = GameState(2, 2)
    move = get_minimax_move(state, depth=3)
    assert move in state.get_legal_moves()


def test_minimax_does_not_mutate_state():
    state = GameState(2, 2)
    state.make_move((H, 0, 0))
    before = list(state.get_legal_moves())
    player = state.curr_player
    get_minimax_move(state, depth=3)
    assert list(state.get_legal_moves()) == before
    assert state.curr_player == player


def test_minimax_terminal_state():
    state = GameState(1, 1)
    state.make_move((H, 0, 0))
    state.make_move((H, 1, 0))
    state.make_move((V, 0, 0))
    state.make_move((V, 0, 1))
    assert state.is_game_over()
    assert get_minimax_move(state, depth=3) is None


def test_minimax_single_remaining_move():
    state = GameState(1, 1)
    state.make_move((H, 0, 0))
    state.make_move((H, 1, 0))
    state.make_move((V, 0, 0))
    assert len(state.get_legal_moves()) == 1
    assert get_minimax_move(state, depth=3) == (V, 0, 1)


def test_minimax_captures_box_when_available():
    state = GameState(2, 2)
    state.h_line[0, 0] = P1
    state.h_line[1, 0] = P1
    state.v_line[0, 0] = P1
    state.curr_player = P2

    move = get_minimax_move(state, depth=4)
    assert move == (V, 0, 1)


def test_minimax_prefers_safe_moves():
    state = GameState(2, 2)
    state.make_move((H, 0, 0))
    safe_moves = state.get_safe_moves()
    assert len(safe_moves) > 0

    move = get_minimax_move(state, depth=4)
    assert move in safe_moves


def test_minimax_avoids_giving_free_box():
    state = GameState(2, 2)
    state.make_move((H, 0, 0))
    state.make_move((V, 0, 0))
    bad_moves = {(H, 1, 0), (V, 0, 1)}

    move = get_minimax_move(state, depth=4)
    assert move in state.get_legal_moves()
    assert move not in bad_moves


def test_minimax_time_limit_returns_legal_move():
    state = GameState(3, 3)
    move = get_minimax_move(state, depth=10, time_limit=0.3)
    assert move in state.get_legal_moves()
