import math
import time

import config
from src.game_logic import HORIZONTAL as H, VERTICAL as V

MINIMAX_DEPTH = getattr(config, "MINIMAX_DEPTH", 4)
MINIMAX_TIME_LIMIT = getattr(config, "MINIMAX_TIME_LIMIT", None)

WIN_SCORE = 1000.0
THREE_SIDED_WEIGHT = 0.5


class SearchTimeout(Exception):
    pass


def _box_sides(r, c):
    return ((H, r, c), (H, r + 1, c), (V, r, c), (V, r, c + 1))


def _board_size(state):
    return state.v_line.shape[0], state.h_line.shape[1]


def box_stats(state):
    rows, cols = _board_size(state)
    undrawn = set(state.get_legal_moves())
    done = threes = 0
    for r in range(rows):
        for c in range(cols):
            missing = sum(1 for side in _box_sides(r, c) if side in undrawn)
            if missing == 0:
                done += 1
            elif missing == 1:
                threes += 1
    return done, threes


def ordered_children(state, done_before):
    safe = set(state.get_safe_moves())
    children = []
    for move in state.get_legal_moves():
        next_state = state.get_next_state(move)
        done_after, _ = box_stats(next_state)
        children.append((move, next_state, done_after, done_after - done_before))
    children.sort(key=lambda x: (-x[3], x[0] not in safe))
    return children


def evaluate_terminal(state, root_player, diff):
    winner = state.get_winner()
    if winner == root_player:
        return diff + WIN_SCORE
    if winner == 0:  # Draw
        return diff
    return diff - WIN_SCORE


def alphabeta(state, depth, alpha, beta, root_player, diff, done, deadline, stats=None):
    if stats is not None:
        stats["nodes"] += 1

    if deadline is not None and time.perf_counter() > deadline:
        raise SearchTimeout()

    if state.is_game_over():
        return evaluate_terminal(state, root_player, diff)

    maximizing = state.curr_player == root_player

    if depth <= 0:
        _, threes = box_stats(state)
        bonus = THREE_SIDED_WEIGHT * threes
        return diff + (bonus if maximizing else -bonus)

    children = ordered_children(state, done)
    if not children:
        return diff

    best = -math.inf if maximizing else math.inf
    for _, next_state, done_after, gained in children:
        new_diff = diff + (gained if maximizing else -gained)
        next_depth = depth if gained > 0 else depth - 1
        value = alphabeta(next_state, next_depth, alpha, beta, root_player,
                          new_diff, done_after, deadline, stats)
        if maximizing:
            best = max(best, value)
            alpha = max(alpha, best)
        else:
            best = min(best, value)
            beta = min(beta, best)
        if beta <= alpha:
            if stats is not None:
                stats["prunes"] += 1
            break
    return best


def get_minimax_move(state, depth=MINIMAX_DEPTH, time_limit=MINIMAX_TIME_LIMIT, stats=None):
    if stats is not None:
        stats.update({"nodes": 0, "prunes": 0, "depth_reached": 0})

    if state.is_game_over():
        return None

    legal_moves = state.get_legal_moves()
    if not legal_moves:
        return None
    if len(legal_moves) == 1:
        return legal_moves[0]

    deadline = None if time_limit is None else time.perf_counter() + time_limit
    root_player = state.curr_player
    done0, _ = box_stats(state)
    children = ordered_children(state, done0)
    best_move = children[0][0]

    for d in range(1, depth + 1):
        try:
            level_move, level_value = None, -math.inf
            alpha = -math.inf
            for move, next_state, done_after, gained in children:
                next_depth = d if gained > 0 else d - 1
                value = alphabeta(next_state, next_depth, alpha, math.inf,
                                  root_player, gained, done_after, deadline, stats)
                if value > level_value:
                    level_value, level_move = value, move
                alpha = max(alpha, level_value)
            best_move = level_move
            if stats is not None:
                stats["depth_reached"] = d
        except SearchTimeout:
            break

    return best_move


minimax_search = get_minimax_move
find_best_move_minimax = get_minimax_move