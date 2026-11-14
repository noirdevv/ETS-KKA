# CARA PAKAI:
# 1. Install pytest: pip install pytest
# 2. Pergi ke direktori root (ETS-KKA\)
# 3. Execute di terminal: python -m pytest test/test_mcts.py -v
# 4. Kalau passed semua, logic udah aman

import pytest
from config import P1, P2
from src.game_logic import GameState, HORIZONTAL as H, VERTICAL as V
from src.ai.mcts import MCTSNode, get_mcts_move, heuristic_rollout


def test_mcts_node_init():
    state = GameState(2, 2)
    node = MCTSNode(state)
    assert node.state is state
    assert node.parent is None
    assert node.move is None
    assert node.visits == 0
    assert node.wins == 0.0
    assert not node.is_fully_expanded()
    assert not node.is_terminal()
    assert len(node.untried_moves) == len(state.get_legal_moves())


def test_mcts_node_expansion():
    state = GameState(2, 2)
    node = MCTSNode(state)
    total_moves = len(node.untried_moves)

    child = node.expand()
    assert child.parent is node
    assert child.move is not None
    assert len(node.children) == 1
    assert len(node.untried_moves) == total_moves - 1
    # Parent state must remain unchanged
    assert len(state.get_legal_moves()) == total_moves


def test_mcts_returns_legal_move():
    state = GameState(2, 2)
    move = get_mcts_move(state, iterations=50)
    assert move in state.get_legal_moves()


def test_mcts_terminal_state():
    state = GameState(1, 1)
    state.make_move((H, 0, 0))
    state.make_move((H, 1, 0))
    state.make_move((V, 0, 0))
    state.make_move((V, 0, 1))  # Completed box, game over
    assert state.is_game_over()
    assert get_mcts_move(state, iterations=10) is None


def test_mcts_single_remaining_move():
    state = GameState(1, 1)
    state.make_move((H, 0, 0))
    state.make_move((H, 1, 0))
    state.make_move((V, 0, 0))
    # Only (V, 0, 1) remains
    assert len(state.get_legal_moves()) == 1
    assert get_mcts_move(state, iterations=10) == (V, 0, 1)


def test_mcts_captures_box_when_available():
    # 2x2 board where 3 sides of (0,0) are drawn
    # Missing 4th side to capture is (V, 0, 1)
    state = GameState(2, 2)
    state.h_line[0, 0] = P1
    state.h_line[1, 0] = P1
    state.v_line[0, 0] = P1
    state.curr_player = P2

    move = get_mcts_move(state, iterations=50)
    assert move == (V, 0, 1)


def test_mcts_prefers_safe_moves():
    # Setup state where safe moves exist
    state = GameState(2, 2)
    # Draw (H, 0, 0)
    state.make_move((H, 0, 0))
    # State has safe moves (moves that don't make any box have 3 sides)
    safe_moves = state.get_safe_moves()
    assert len(safe_moves) > 0

    move = get_mcts_move(state, iterations=100)
    assert move in safe_moves
