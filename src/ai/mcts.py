import math
import random
from config import MCTS_EXPLORATION, MCTS_ITERATION, MCTS_ROLLOUT_CUTOFF, P1, P2, EMPTY


class MCTSNode:
    """Node in the Monte Carlo search tree representing a GameState snapshot."""

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = state.get_legal_moves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.is_game_over()

    def best_child(self, c_param=MCTS_EXPLORATION):
        """Picks the child maximizing the UCB1 formula."""
        best_score = -float('inf')
        best_nodes = []

        for child in self.children:
            exploit = child.wins / child.visits
            explore = c_param * math.sqrt(math.log(self.visits) / child.visits)
            score = exploit + explore

            if score > best_score:
                best_score = score
                best_nodes = [child]
            elif math.isclose(score, best_score):
                best_nodes.append(child)

        return random.choice(best_nodes)

    def expand(self):
        """Pops an untried legal move and adds a child node to the tree."""
        move = self.untried_moves.pop()
        next_state = self.state.get_next_state(move)
        child_node = MCTSNode(state=next_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def update(self, margin):
        """Updates visit count and win score based on the rollout margin."""
        self.visits += 1
        if self.parent is None:
            return

        player_who_moved = self.parent.state.curr_player
        # P1 is used because get_margin method returns a score from P1's perspective
        reward = 0.5 + 0.5 * (margin if player_who_moved == P1 else -margin)
        self.wins += reward


def count_three_sided_boxes(state):
    """How many capturable one-edge-missing boxes exist right now."""
    threes = 0
    for r in range(state.row):
        for c in range(state.col):
            if state.box_owner[r, c] == EMPTY and state.count_box_sides(r, c) == 3:
                threes += 1
    return threes


def evaluate_position(state):
    """Static position evaluation, from P1's perspective, normalized to [-1, 1].

    Signed box diff so far, plus the boxes the player to move is about to
    bank (every three-sided box is an almost-certain capture), all divided
    by the total number of boxes on the board.
    """
    boxes = state.row * state.col
    margin_boxes = state.score[P1] - state.score[P2]
    side = 1 if state.curr_player == P1 else -1
    adjusted = margin_boxes + side * count_three_sided_boxes(state)
    return max(-1.0, min(1.0, adjusted / boxes))


def heuristic_rollout(state):
    """Simulates a game using tiered domain heuristics for Dots and Boxes.

    Stops early at MCTS_ROLLOUT_CUTOFF plies and statically evaluates the
    position instead of playing to terminal.
    """
    current = state.copy()
    plies = 0
    while not current.is_game_over() and plies < MCTS_ROLLOUT_CUTOFF:
        capturing = current.get_capturing_moves()
        if capturing:
            move = random.choice(capturing)
        else:
            safe = current.get_safe_moves()
            if safe:
                move = random.choice(safe)
            else:
                move = random.choice(current.get_legal_moves())
        current.make_move(move)
        plies += 1
    if current.is_game_over():
        return get_margin(current)
    return evaluate_position(current)

def get_margin(state):
    """Returns the margin of victory for terminal state."""
    boxes = state.row * state.col
    scores = state.score
    return (scores[P1] - scores[P2]) / boxes

def get_mcts_move(state, iterations=MCTS_ITERATION, c_param=MCTS_EXPLORATION, use_heuristic=True):
    """Public entry point for the MCTS AI agent.

    Returns the best move determined after running N iterations of MCTS.
    """
    if state.is_game_over():
        return None

    legal_moves = state.get_legal_moves()
    if not legal_moves:
        return None
    if len(legal_moves) == 1:
        return legal_moves[0]

    # Fast-path optimization: if an immediate capturing move exists, take it
    # capturing_moves = state.get_capturing_moves()
    # if capturing_moves:
    #     return random.choice(capturing_moves)

    root = MCTSNode(state=state.copy())

    for _ in range(iterations):
        node = root

        # 1. Selection
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c_param=c_param)

        # 2. Expansion
        if not node.is_terminal():
            node = node.expand()

        # 3. Simulation
        if use_heuristic:
            margin = heuristic_rollout(node.state)
        else:
            current = node.state.copy()
            plies = 0
            while not current.is_game_over() and plies < MCTS_ROLLOUT_CUTOFF:
                current.make_move(random.choice(current.get_legal_moves()))
                plies += 1
            if current.is_game_over():
                margin = get_margin(current)
            else:
                margin = evaluate_position(current)

        # 4. Backpropagation
        while node is not None:
            node.update(margin)
            node = node.parent

    if not root.children:
        return random.choice(legal_moves)

    # Robust decision: select child with highest visit count
    most_visited_child = max(root.children, key=lambda c: c.visits)
    return most_visited_child.move


# Convenience aliases
mcts_search = get_mcts_move
find_best_move = get_mcts_move
