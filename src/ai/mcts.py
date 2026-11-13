import math
import random
from config import MCTS_EXPLORATION, MCTS_ITERATION


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

    def update(self, winner):
        """Updates visit count and win score based on the simulated winner."""
        self.visits += 1
        if self.parent is None:
            return

        player_who_moved = self.parent.state.curr_player
        if winner == player_who_moved:
            self.wins += 1.0
        elif winner == 0:  # Draw
            self.wins += 0.5


def heuristic_rollout(state):
    """Simulates a game using tiered domain heuristics for Dots and Boxes."""
    current = state.copy()
    while not current.is_game_over():
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
    return current.get_winner()


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
    capturing_moves = state.get_capturing_moves()
    if capturing_moves:
        return random.choice(capturing_moves)

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
            winner = heuristic_rollout(node.state)
        else:
            current = node.state.copy()
            while not current.is_game_over():
                current.make_move(random.choice(current.get_legal_moves()))
            winner = current.get_winner()

        # 4. Backpropagation
        while node is not None:
            node.update(winner)
            node = node.parent

    if not root.children:
        return random.choice(legal_moves)

    # Robust decision: select child with highest visit count
    most_visited_child = max(root.children, key=lambda c: c.visits)
    return most_visited_child.move


# Convenience aliases
mcts_search = get_mcts_move
find_best_move = get_mcts_move
