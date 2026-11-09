import numpy as np
from config import ROW, COL, EMPTY, P1, P2

HORIZONTAL = 'H'
VERTICAL = 'V'

class GameState:
    def __init__(self, row = ROW, col = COL):
        self.row = row
        self.col = col
        self.h_line = np.zeros((row + 1, col), dtype=np.int8)
        self.v_line = np.zeros((row, col + 1), dtype=np.int8)
        self.box_owner = np.zeros((row, col), dtype=np.int8)
        self.curr_player = P1
        self.score = {P1: 0, P2: 0}
        self.last_move = None

    def copy(self): #Salinan state untuk dipakai AI
        new = GameState.__new__(GameState)
        new.row = self.row
        new.col = self.col
        new.h_line = self.h_line.copy()
        new.v_line = self.v_line.copy()
        new.box_owner = self.box_owner.copy()
        new.curr_player = self.curr_player
        new.score = dict(self.score)
        new.last_move = self.last_move
        return new

    def get_next_state(self, move): #Membuat salinan untuk AI
        #Return state baru setelah move tanpa ubah state ini
        new_state = self.copy()
        new_state.make_move(move)
        return new_state

    def is_valid_move(self, move):
        try:
            edge_type, row, col = move
        except (TypeError, ValueError):
            return False

        if edge_type == HORIZONTAL:
            return (0 <= row <= self.row and 0 <= col < self.col 
                    and self.h_line[row, col] == EMPTY)
        elif edge_type == VERTICAL:
            return (0 <= row < self.row and 0 <= col <= self.col 
                    and self.v_line[row, col] == EMPTY)
        else:
            return False

    def get_legal_moves(self): #Kemungkinan langkah untuk AI
        move = []
        for row in range(self.row + 1):
            for col in range(self.col):
                if self.h_line[row, col] == EMPTY:
                    move.append((HORIZONTAL, row, col))
        for row in range(self.row):
            for col in range(self.col + 1):
                if self.v_line[row, col] == EMPTY:
                    move.append((VERTICAL, row, col))
        return move

    def make_move(self, move):
        if self.is_game_over():
            raise ValueError("Permainan sudah selesai.")
        if not self.is_valid_move(move):
            raise ValueError(f"Langkah tidak valid: {move}")

        edge_type, row, col = move
        player = self.curr_player

        if edge_type == HORIZONTAL:
            self.h_line[row, col] = player
        elif edge_type == VERTICAL:
            self.v_line[row, col] = player

        completed = 0
        for br, bc in self._adjacent_boxes(move):
            if self.box_owner[br, bc] == EMPTY and self.count_box_sides(br, bc) == 4:
                self.box_owner[br, bc] = player
                completed += 1

        self.score[player] += completed
        self.last_move = move

        if completed == 0:
            self.curr_player = P2 if player == P1 else P1
        return completed

    def is_game_over(self):
        return self.score[P1] + self.score[P2] == self.row * self.col

    def get_winner(self):
        if not self.is_game_over():
            return None
        if self.score[P1] > self.score[P2]:
            return P1
        if self.score[P2] > self.score[P1]:
            return P2
        
        return 0 #draw

    def get_score_diff(self, player):
        return self.score[player] - self.score[self.get_opponent(player)]

    def get_opponent(player):
        return P2 if player == P1 else P1

    # cbs, gcp, dan gsm sebagai helper heuristik AI
    def count_box_sides(self, row, col):
        #Jumlah sisi kotak yang sudah digambar
        return (int(self.h_line[row, col] != EMPTY) +
                int(self.h_line[row + 1, col] != EMPTY) +
                int(self.v_line[row, col] != EMPTY) +
                int(self.v_line[row, col + 1] != EMPTY))

    def get_capturing_moves(self):
        #Langkah yang lansgsung mendapat min 1 kotak
        return [m for m in self.get_legal_moves() 
                if any(self.count_box_sides(br, bc) == 3 
                       for br, bc in self._adjacent_boxes(m))]

    def get_safe_moves(self):
        #Langkah yang tidak membuat lawan mendapat kotak
        return [m for m in self.get_legal_moves() 
                if all(self.count_box_sides(br, bc) < 2
                       for br, bc in self._adjacent_boxes(m))]

    def _adjacent_boxes(self, move):
        #Kotak (max 2) yang berdekatan dengan garis yang digambar
        edge_type, row, col = move
        boxes = []
        if edge_type == HORIZONTAL:
            if row > 0:
                boxes.append((row - 1, col))
            if row < self.row:
                boxes.append((row, col))
        elif edge_type == VERTICAL:
            if col > 0:
                boxes.append((row, col - 1))
            if col < self.col:
                boxes.append((row, col))
        return boxes

    def __str__(self):
        line = []
        for r in range(self.row + 1):
            row = '+'
            for c in range(self.col):
                row += ('---' if self.h_line[r, c] != EMPTY else '   ') + '+'
            line.append(row)

            if r < self.row:
                row = ''
                for c in range(self.col + 1):
                    row += ('|' if self.v_line[r, c] != EMPTY else ' ') + '   '
                line.append(row)
        return '\n'.join(line)

if __name__ == "__main__":

    import random

    state = GameState()
    while not state.is_game_over():
        state.make_move(random.choice(state.get_legal_moves()))
    print(state)
    print('Skor:', state.score, '| Pemenang:', state.get_winner())