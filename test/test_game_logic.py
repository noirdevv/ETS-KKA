# CARA PAKAI:
# 1. Install pytest: pip install pytest
# 2. Pergi ke direktori root (ETS-KKA\)
# 3. Execute di terminal: python -m pytest test/test_game_logic.py -v
# 4. Kalau passed semua, logic udah aman

import random

import pytest

from config import ROW, COL, EMPTY, P1, P2
from src.game_logic import GameState, HORIZONTAL as H, VERTICAL as V


#Helper
def total_edges(row, col):
    return (row + 1) * col + row * (col + 1)


def play_random_game(state, seed=0): #Mainin game acak sampe selesai, return state terakhir dan jumlah langkah
    rng = random.Random(seed)
    n = 0
    while not state.is_game_over():
        state.make_move(rng.choice(state.get_legal_moves()))
        n += 1
    return state, n


def box_with_three_sides(): #Papan 2x2 udah berisi 3, sisi yang kurang V(0,1)
    s = GameState(2, 2)
    s.h_line[0, 0] = P1
    s.h_line[1, 0] = P1
    s.v_line[0, 0] = P1
    return s


#State awal
def test_initial_state():
    s = GameState(2, 2)
    assert s.curr_player == P1
    assert s.score == {P1: 0, P2: 0}
    assert s.last_move is None
    assert not s.is_game_over()
    assert len(s.get_legal_moves()) == 12 #3*2 horizontal + 2*3 vertikal


def test_initial_state_default_size():
    assert len(GameState().get_legal_moves()) == total_edges(ROW, COL)


#Validasi langkah
@pytest.mark.parametrize("move, expected", [
    ((H, 0, 0), True),
    ((H, 2, 1), True),  #Garis bawah paling kanan
    ((V, 1, 2), True),  #Garis kanan paling bawah
    ((H, 3, 0), False), #Baris di luar papan
    ((H, 0, 2), False), #Kolom H maksimal cols-1
    ((V, 2, 0), False), #Baris V maksimal rows-1
    ((V, 0, 3), False),
    ((H, -1, 0), False),
    (("X", 0, 0), False), #Tipe garis salah
    ((H, 0), False),  #Format salah
    (None, False),
])
def test_is_valid_move(move, expected):
    assert bool(GameState(2, 2).is_valid_move(move)) == expected


def test_duplicate_move_is_invalid():
    s = GameState(2, 2)
    s.make_move((H, 0, 0))
    assert not s.is_valid_move((H, 0, 0))


def test_invalid_move_raises_and_keeps_state():
    s = GameState(2, 2)
    with pytest.raises(ValueError, match=r"\('H', 9, 9\)"): #Cek f-string
        s.make_move((H, 9, 9))
    assert s.curr_player == P1
    assert len(s.get_legal_moves()) == 12


#Aturan giliran & skor
def test_turn_switches_when_no_box_completed():
    s = GameState(2, 2)
    assert s.make_move((H, 0, 0)) == 0
    assert s.curr_player == P2
    assert s.last_move == (H, 0, 0)
    assert s.h_line[0, 0] == P1 #Garis dicatat atas nama penggambar


def test_completing_box_gives_extra_turn():
    s = GameState(2, 2)
    s.make_move((H, 0, 0))   #P1
    s.make_move((V, 0, 0))   #P2
    s.make_move((H, 1, 0))   #P1
    completed = s.make_move((V, 0, 1)) #P2 menutup kotak (0,0)
    assert completed == 1
    assert s.box_owner[0, 0] == P2
    assert s.score == {P1: 0, P2: 1}
    assert s.curr_player == P2  #Jalan lagi


def test_one_move_completes_two_boxes():
    s = GameState(2, 2)
    for m in [(H, 0, 0), (H, 1, 0), (V, 0, 0), (H, 0, 1), (H, 1, 1), (V, 0, 2)]:
        assert s.make_move(m) == 0  #Gak ada kotak yang selesai
    assert s.curr_player == P1  #6 giliran bergantian -> kembali ke P1
    assert s.make_move((V, 0, 1)) == 2  #Garis tengah menutup 2 kotak
    assert s.score == {P1: 2, P2: 0}
    assert s.box_owner[0, 0] == P1 and s.box_owner[0, 1] == P1
    assert s.curr_player == P1


@pytest.mark.parametrize("move, expected", [
    ((H, 0, 0), [(0, 0)]), #Garis tepi: 1 kotak
    ((H, 1, 0), [(0, 0), (1, 0)]), #Garis dalam: 2 kotak
    ((H, 2, 1), [(1, 1)]),
    ((V, 0, 0), [(0, 0)]),
    ((V, 0, 1), [(0, 0), (0, 1)]),
    ((V, 1, 2), [(1, 1)]),
])
def test_adjacent_boxes(move, expected):
    assert sorted(GameState(2, 2)._adjacent_boxes(move)) == expected


#Copy / Next State
def test_copy_is_independent():
    s = GameState(2, 2)
    c = s.copy()
    c.make_move((H, 0, 0))
    assert s.h_line[0, 0] == EMPTY
    assert s.curr_player == P1
    assert s.last_move is None
    assert c.h_line[0, 0] == P1 and c.curr_player == P2


def test_get_next_state_does_not_mutate_original():
    s = GameState(2, 2)
    n = s.get_next_state((H, 0, 0))
    assert len(s.get_legal_moves()) == 12
    assert len(n.get_legal_moves()) == 11
    assert n.curr_player == P2
    assert s.score is not n.score #Dict skor tidak dipakai bersama


#Akhir permainan
@pytest.mark.parametrize("rows, cols", [(1, 1), (2, 2), (3, 3), (2, 4), (ROW, COL)])
def test_random_full_games(rows, cols):
    for seed in range(50):
        s, n = play_random_game(GameState(rows, cols), seed)
        assert n == total_edges(rows, cols) #Semua garis terpakai
        assert s.get_legal_moves() == []
        assert (s.box_owner != EMPTY).all()
        assert s.score[P1] + s.score[P2] == rows * cols
        assert (s.box_owner == P1).sum() == s.score[P1]
        assert (s.box_owner == P2).sum() == s.score[P2]


def test_cannot_move_after_game_over():
    s, _ = play_random_game(GameState(2, 2))
    with pytest.raises(ValueError, match="selesai"):
        s.make_move((H, 0, 0))


def test_get_winner_none_while_game_running():
    s = GameState(2, 2)
    assert s.get_winner() is None
    s.score = {P1: 1, P2: 0} #Unggul sementara bukan pemenang
    assert s.get_winner() is None


def test_get_winner_p1_p2_and_draw():
    s = GameState(2, 2)
    s.score = {P1: 3, P2: 1}
    assert s.get_winner() == P1
    s.score = {P1: 1, P2: 3}
    assert s.get_winner() == P2
    s.score = {P1: 2, P2: 2}
    assert s.get_winner() == 0 #Seri


#Helper heuristik
def test_count_box_sides():
    s = box_with_three_sides()
    assert s.count_box_sides(0, 0) == 3
    assert s.count_box_sides(1, 0) == 1  #Hanya H(1,0)
    assert s.count_box_sides(1, 1) == 0


def test_get_capturing_moves():
    assert GameState(2, 2).get_capturing_moves() == []
    s = box_with_three_sides()
    #V(0,1) menutup kotak (0,0) walau tetangganya (0,1) masih kosong
    assert s.get_capturing_moves() == [(V, 0, 1)]


def test_get_safe_moves():
    s = GameState(2, 2)
    s.h_line[0, 0] = P1
    s.v_line[0, 0] = P1   #Kotak (0,0) bersisi 2
    safe = s.get_safe_moves()
    assert (H, 1, 0) not in safe  #Akan membuat sisi ke-3
    assert (V, 0, 1) not in safe
    assert (H, 2, 1) in safe
    assert len(safe) == len(s.get_legal_moves()) - 2


#Tampilan teks
def test_str_shows_vertical_line():
    s = GameState(1, 1)
    s.make_move((V, 0, 0))
    out = str(s)
    assert '|' in out
    assert len(out.split('\n')) == 2 * 1 + 1 #2 baris titik + 1 baris tengah


def test_str_shows_horizontal_line():
    s = GameState(1, 1)
    s.make_move((H, 0, 0))
    assert '---' in str(s)